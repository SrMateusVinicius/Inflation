"""
main.py — Orquestração da extração (CLI).

Uso::

    python main.py --inicio 2012-01 --fim atual
    python main.py --inicio 2024-01 --fim 2026-09 --csv
    python main.py --fontes sgs,focus        # reprocessa só algumas fontes

Fluxo:
    1. extrai cada fonte (bronze = JSON bruto com timestamp);
    2. trata e tipa (DataFrames);
    3. mescla com a silver existente (upsert por chave natural);
    4. valida TUDO em memória — se algo falhar, nada é gravado;
    5. grava os Parquets de forma atômica + _controle_carga;
    6. (opcional) exporta CSV pt-BR.

Códigos de saída: 0 = ok · 2 = falha de validação · 3 = falha de API · 1 = outro erro.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date, datetime

import pandas as pd

import clientes_api as api
import config
import transformacoes as tr

log = logging.getLogger("extracao")
FONTES_VALIDAS = ("sgs", "sidra", "focus")


# =============================================================================
# CLI e logging
# =============================================================================
def _mes(texto: str) -> date:
    """'2012-01' → date(2012, 1, 1); 'atual' → 1º dia do mês corrente."""
    if texto.lower() == "atual":
        return tr.hoje_primeiro_dia()
    try:
        return datetime.strptime(texto, "%Y-%m").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Use aaaa-mm ou 'atual' (recebido: {texto!r})") from exc


def ler_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extração do Monitor de Inflação Brasil (BCB + IBGE → Parquet).")
    p.add_argument("--inicio", type=_mes, default=date(2012, 1, 1), help="mês inicial aaaa-mm (padrão 2012-01)")
    p.add_argument("--fim", type=_mes, default=tr.hoje_primeiro_dia(), help="mês final aaaa-mm ou 'atual'")
    p.add_argument("--csv", action="store_true", help="também gera CSV (sep=';', decimal=',') em dados/silver/csv")
    p.add_argument("--fontes", default=",".join(FONTES_VALIDAS), help="sgs,sidra,focus (padrão: todas)")
    p.add_argument("--verbose", action="store_true", help="log em nível DEBUG")
    args = p.parse_args(argv)
    args.fontes = {f.strip().lower() for f in args.fontes.split(",") if f.strip()}
    if not args.fontes <= set(FONTES_VALIDAS):
        p.error(f"--fontes aceita apenas {FONTES_VALIDAS}")
    if args.inicio > args.fim:
        p.error("--inicio deve ser anterior ou igual a --fim")
    return args


def configurar_log(verbose: bool) -> None:
    config.PASTA_LOGS.mkdir(parents=True, exist_ok=True)
    arquivo = config.PASTA_LOGS / f"extracao_{date.today():%Y%m%d}.log"
    formato = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    raiz = logging.getLogger()
    raiz.setLevel(logging.DEBUG if verbose else logging.INFO)
    for antigo in list(raiz.handlers):  # evita log duplicado se main() rodar 2x no mesmo processo
        raiz.removeHandler(antigo)
    for handler in (logging.FileHandler(arquivo, encoding=config.ENCODING), logging.StreamHandler(sys.stdout)):
        handler.setFormatter(formato)
        raiz.addHandler(handler)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# =============================================================================
# Etapas por fonte
# =============================================================================
def etapa_sgs(sessao, inicio: date, fim: date, carimbo: str) -> pd.DataFrame:
    """Extrai, trata e valida as séries SGS; devolve fIndicadores mesclado."""
    frames = []
    for serie in config.SERIES_SGS:
        registros = api.buscar_serie_sgs(sessao, serie, inicio, fim, carimbo)
        df = tr.tratar_sgs(registros, serie)
        tr.validar_faixa_sgs(df, serie)
        log.info("SGS %-5s %-20s %4d linhas (%s → %s)", serie.codigo, serie.indicador,
                 len(df), df["Data"].min(), df["Data"].max())
        frames.append(df)
    fato = tr.upsert(tr.concatenar(frames), config.ARQ_INDICADORES)
    tr.validar_sem_duplicados(fato, ["DataKey", "CodigoSGS"], "fIndicadores")
    tr.validar_sem_lacunas(fato, "DataKey", "CodigoSGS", "fIndicadores")
    conferencia = tr.validar_ipca_12m(fato.assign(Data=tr.key_para_data(fato["DataKey"])))
    if not conferencia.empty:
        destino = config.PASTA_LOGS / f"conferencia_ipca12m_{date.today():%Y%m%d}.csv"
        (conferencia * [100, 100, 1]).round(4).to_csv(destino, sep=";", decimal=",", encoding="utf-8-sig",
                                                      index_label="Mes")
        log.info("Tabela de conferência IPCA 12M (em %%): %s", destino)
    return fato


def etapa_sidra(sessao, inicio: date, fim: date, carimbo: str) -> pd.DataFrame:
    """Extrai as tabelas SIDRA que cobrem o período; devolve fIPCAGrupos mesclado."""
    frames = []
    for tabela in config.SIDRA_TABELAS:
        ini = max(inicio, tabela.inicio)
        fim_tab = min(fim, tabela.fim) if tabela.fim else fim
        if ini > fim_tab:
            continue
        cabecalho, linhas = api.buscar_sidra(sessao, tabela, ini, fim_tab, carimbo)
        frames.append(tr.tratar_sidra(cabecalho, linhas))
    sidra = tr.concatenar(frames)
    if sidra.empty:
        raise tr.ErroValidacao("SIDRA: nenhum dado retornado no período.")
    tr.validar_codigos_sidra(sidra)
    tr.checar_contribuicoes(sidra)
    grupos = sidra[sidra["CodigoGrupo"] != config.CODIGO_INDICE_GERAL].dropna(subset=["VariacaoMensal"])
    log.info("SIDRA grupos: %d linhas (%s → %s)", len(grupos), grupos["Data"].min(), grupos["Data"].max())
    fato = tr.upsert(grupos, config.ARQ_GRUPOS)
    tr.validar_sem_duplicados(fato, ["DataKey", "CodigoGrupo"], "fIPCAGrupos")
    tr.validar_sem_lacunas(fato, "DataKey", "CodigoGrupo", "fIPCAGrupos")
    tr.validar_pesos(fato)
    return fato


def etapa_focus(sessao, inicio: date, fim: date, carimbo: str) -> pd.DataFrame:
    """Extrai o Focus (IPCA anual); devolve fExpectativas mesclado."""
    registros = api.buscar_focus(sessao, inicio, fim, carimbo)
    df = tr.tratar_focus(registros)
    log.info("Focus: %d coletas brutas → %d linhas mensais", len(registros), len(df))
    fato = tr.upsert(df, config.ARQ_EXPECTATIVAS)
    tr.validar_sem_duplicados(fato, ["DataColetaKey", "AnoReferencia"], "fExpectativas")
    return fato


# =============================================================================
# Orquestração
# =============================================================================
def executar(args: argparse.Namespace) -> None:
    inicio_exec = time.perf_counter()
    agora = datetime.now().replace(microsecond=0)
    carimbo = agora.strftime("%Y%m%d_%H%M%S")
    log.info("=== Início da extração | %s → %s | fontes=%s | raiz=%s ===",
             args.inicio, args.fim, sorted(args.fontes), config.PASTA_RAIZ)

    sessao = api.criar_sessao()
    fatos: dict[str, pd.DataFrame] = {}
    controle: list[dict] = []
    etapas = (
        ("sgs", config.ARQ_INDICADORES, "DataKey", "BCB-SGS", etapa_sgs),
        ("sidra", config.ARQ_GRUPOS, "DataKey", "IBGE-SIDRA", etapa_sidra),
        ("focus", config.ARQ_EXPECTATIVAS, "DataColetaKey", "BCB-Focus", etapa_focus),
    )
    for chave, arquivo, col_key, fonte, funcao in etapas:
        if chave not in args.fontes:
            continue
        t0 = time.perf_counter()
        fatos[arquivo] = funcao(sessao, args.inicio, args.fim, carimbo)
        controle.append(tr.linha_controle(fonte, fatos[arquivo], col_key, agora,
                                          f"{time.perf_counter() - t0:.1f}s"))
        log.info("Etapa %s concluída em %.1fs", fonte, time.perf_counter() - t0)

    # --- tudo validado: grava ------------------------------------------------
    dimensoes = {
        config.ARQ_META: tr.montar_dim_meta(date.today().year + config.METAS_ANOS_FUTUROS),
        config.ARQ_DIM_INDICADOR: tr.montar_dim_indicador(),
        config.ARQ_DIM_GRUPO: tr.montar_dim_grupo(),
    }
    controle.append({"Fonte": "CMN-Metas", "DataHoraCarga": agora, "PrimeiroMes": None, "UltimoMes": None,
                     "Linhas": len(dimensoes[config.ARQ_META]), "Observacao": f"versão {config.METAS_VERSAO}"})
    df_controle = pd.DataFrame(controle)
    caminho_controle = config.PASTA_SILVER / config.ARQ_CONTROLE
    if caminho_controle.exists():  # preserva o controle das fontes não reprocessadas
        antigo = pd.read_parquet(caminho_controle)
        df_controle = pd.concat([antigo[~antigo["Fonte"].isin(df_controle["Fonte"])], df_controle],
                                ignore_index=True)

    saidas = {**fatos, **dimensoes, config.ARQ_CONTROLE: df_controle}
    for arquivo, df in saidas.items():
        destino = tr.gravar_parquet(df, arquivo)
        log.info("Gravado %-26s %6d linhas → %s", arquivo, len(df), destino)
        if args.csv:
            tr.gravar_csv(df, arquivo)
    log.info("=== Fim da extração | %.1fs ===", time.perf_counter() - inicio_exec)


def main(argv: list[str] | None = None) -> int:
    args = ler_argumentos(argv)
    configurar_log(args.verbose)
    try:
        executar(args)
        return 0
    except tr.ErroValidacao as exc:
        log.error("FALHA DE VALIDAÇÃO — nada foi gravado na silver. %s", exc)
        return 2
    except api.ErroAPI as exc:
        log.error("FALHA DE API — nada foi gravado na silver. %s", exc)
        return 3
    except Exception:  # noqa: BLE001 — log completo de erros inesperados
        log.exception("Erro inesperado")
        return 1


if __name__ == "__main__":
    sys.exit(main())
