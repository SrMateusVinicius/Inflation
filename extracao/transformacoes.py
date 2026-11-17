"""
transformacoes.py — Limpeza, tipagem, validação e gravação da camada silver.

Regras de tipagem (iguais para todas as fontes):
* datas → ``date`` no **primeiro dia do mês** (grão mensal do modelo);
* percentuais → **fração decimal** (0,44% → 0.0044), para usar o formato %
  nativo do Power BI sem multiplicar/dividir nas medidas;
* chaves → inteiros (``DataKey`` = aaaammdd, ``CodigoSGS``, ``CodigoGrupo``).

As validações lançam ``ErroValidacao`` com uma mensagem que diz *o quê*,
*onde* e *quanto* — a carga é interrompida antes de gravar a silver.
"""
from __future__ import annotations

import logging
import os
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import config

log = logging.getLogger(__name__)


class ErroValidacao(ValueError):
    """Dado inconsistente: a carga deve parar."""


# =============================================================================
# Esquemas explícitos (Parquet tipado → nenhum tipo "any" no Power Query)
# =============================================================================
ESQUEMAS: dict[str, pa.Schema] = {
    config.ARQ_INDICADORES: pa.schema([
        ("DataKey", pa.int32()), ("CodigoSGS", pa.int32()), ("Valor", pa.float64()),
    ]),
    config.ARQ_GRUPOS: pa.schema([
        ("DataKey", pa.int32()), ("CodigoGrupo", pa.int32()),
        ("VariacaoMensal", pa.float64()), ("Peso", pa.float64()),
    ]),
    config.ARQ_EXPECTATIVAS: pa.schema([
        ("DataColetaKey", pa.int32()), ("AnoReferencia", pa.int32()), ("DataColeta", pa.date32()),
        ("Mediana", pa.float64()), ("Media", pa.float64()),
        ("Minimo", pa.float64()), ("Maximo", pa.float64()),
    ]),
    config.ARQ_META: pa.schema([
        ("Ano", pa.int32()), ("Meta", pa.float64()), ("LimiteInferior", pa.float64()),
        ("LimiteSuperior", pa.float64()), ("Tolerancia", pa.float64()), ("TipoMeta", pa.string()),
    ]),
    config.ARQ_DIM_INDICADOR: pa.schema([
        ("CodigoSGS", pa.int32()), ("Indicador", pa.string()), ("Categoria", pa.string()),
        ("Fonte", pa.string()), ("Unidade", pa.string()), ("TipoTaxa", pa.string()),
        ("Ordem", pa.int32()), ("Descricao", pa.string()),
    ]),
    config.ARQ_DIM_GRUPO: pa.schema([
        ("CodigoGrupo", pa.int32()), ("Grupo", pa.string()), ("Ordem", pa.int32()), ("CorHex", pa.string()),
    ]),
    config.ARQ_CONTROLE: pa.schema([
        ("Fonte", pa.string()), ("DataHoraCarga", pa.timestamp("ms")), ("PrimeiroMes", pa.date32()),
        ("UltimoMes", pa.date32()), ("Linhas", pa.int64()), ("Observacao", pa.string()),
    ]),
}

CHAVES_NATURAIS: dict[str, list[str]] = {
    config.ARQ_INDICADORES: ["DataKey", "CodigoSGS"],
    config.ARQ_GRUPOS: ["DataKey", "CodigoGrupo"],
    config.ARQ_EXPECTATIVAS: ["DataColetaKey", "AnoReferencia"],
}


# =============================================================================
# Utilitários de tipagem
# =============================================================================
def para_primeiro_dia(datas: pd.Series) -> pd.Series:
    """Converte datetimes para ``date`` no 1º dia do mês."""
    return pd.to_datetime(datas).dt.to_period("M").dt.to_timestamp().dt.date


def data_para_key(datas: pd.Series) -> pd.Series:
    """``date`` → inteiro aaaammdd (int32)."""
    dt = pd.to_datetime(datas)
    return (dt.dt.year * 10000 + dt.dt.month * 100 + dt.dt.day).astype("int32")


def key_para_data(keys: pd.Series) -> pd.Series:
    """Inteiro aaaammdd → ``date``."""
    return pd.to_datetime(keys.astype(str), format="%Y%m%d").dt.date


def percentual_para_fracao(valores: pd.Series) -> pd.Series:
    """'0.44' / 0.44 → 0.0044. Marcadores do SIDRA ('...', '-', 'X') viram NaN."""
    return pd.to_numeric(valores, errors="coerce") / 100.0


# =============================================================================
# A) SGS
# =============================================================================
def tratar_sgs(registros: list[dict[str, str]], serie: config.SerieSGS) -> pd.DataFrame:
    """Lista ``{"data","valor"}`` → DataFrame [Data, DataKey, CodigoSGS, Valor].

    * ``data`` vem como dd/mm/aaaa (sempre dia 01 nas séries mensais);
    * ``valor`` vem como texto com ponto decimal, em %.
    """
    if not registros:
        return pd.DataFrame(columns=["Data", "DataKey", "CodigoSGS", "Valor"])
    bruto = pd.DataFrame(registros)
    df = pd.DataFrame({
        "Data": para_primeiro_dia(pd.to_datetime(bruto["data"], format="%d/%m/%Y")),
        "CodigoSGS": serie.codigo,
        "Valor": percentual_para_fracao(bruto["valor"]),
    }).dropna(subset=["Valor"])
    df["DataKey"] = data_para_key(df["Data"])
    df["CodigoSGS"] = df["CodigoSGS"].astype("int32")
    return df[["Data", "DataKey", "CodigoSGS", "Valor"]]


def validar_faixa_sgs(df: pd.DataFrame, serie: config.SerieSGS) -> None:
    """'Validação do código': valores fora da faixa plausível indicam série errada."""
    if df.empty:
        raise ErroValidacao(f"SGS {serie.codigo} ({serie.indicador}): nenhum dado retornado.")
    minimo, maximo = (v / 100 for v in serie.faixa_valida)
    fora = df[(df["Valor"] < minimo) | (df["Valor"] > maximo)]
    if not fora.empty:
        raise ErroValidacao(
            f"SGS {serie.codigo} ({serie.indicador}): {len(fora)} valores fora da faixa "
            f"{serie.faixa_valida}% (ex.: {fora.iloc[0]['Data']} = {fora.iloc[0]['Valor']*100:.2f}%). "
            "O código pode não corresponder à série descrita — confira no SGS e corrija config.py."
        )


# =============================================================================
# B) SIDRA
# =============================================================================
def _coluna_por_rotulo(cabecalho: dict[str, str], condicao) -> str:
    for chave, rotulo in cabecalho.items():
        if condicao(str(rotulo)):
            return chave
    raise ErroValidacao(f"SIDRA: coluna não encontrada no cabeçalho {cabecalho}")


def tratar_sidra(cabecalho: dict[str, str], linhas: list[dict[str, str]]) -> pd.DataFrame:
    """Linhas do SIDRA (formato longo) → DataFrame largo por mês e grupo.

    As colunas do SIDRA são genéricas (``D1C``, ``D2C``...) e mudam de ordem
    conforme a URL; por isso são localizadas pelos **rótulos do cabeçalho**
    ("Mês (Código)", "Variável (Código)", "Geral, grupo... (Código)").

    Saída: [Data, DataKey, CodigoGrupo, VariacaoMensal, Peso,
    VariacaoAcumAno, Variacao12M] — percentuais já em fração.
    """
    if not linhas:
        return pd.DataFrame(columns=["Data", "DataKey", "CodigoGrupo", *config.SIDRA_VARIAVEIS.values()])
    col_mes = _coluna_por_rotulo(cabecalho, lambda r: r.startswith("Mês") and r.endswith("(Código)"))
    col_var = _coluna_por_rotulo(cabecalho, lambda r: r.startswith("Variável") and r.endswith("(Código)"))
    col_cat = _coluna_por_rotulo(cabecalho, lambda r: r.startswith("Geral") and r.endswith("(Código)"))

    longo = pd.DataFrame(linhas)
    longo = pd.DataFrame({
        "Data": pd.to_datetime(longo[col_mes], format="%Y%m").dt.date,
        "CodigoGrupo": longo[col_cat].astype("int32"),
        "Variavel": longo[col_var].astype(int).map(config.SIDRA_VARIAVEIS),
        "Valor": percentual_para_fracao(longo["V"]),
    })
    largo = (
        longo.pivot_table(index=["Data", "CodigoGrupo"], columns="Variavel", values="Valor", aggfunc="first")
        .reset_index()
    )
    largo.columns.name = None
    for nome in config.SIDRA_VARIAVEIS.values():
        if nome not in largo:
            largo[nome] = float("nan")
    largo["DataKey"] = data_para_key(largo["Data"])
    return largo[["Data", "DataKey", "CodigoGrupo", *config.SIDRA_VARIAVEIS.values()]]


def validar_codigos_sidra(df: pd.DataFrame) -> None:
    """Confere se todos os códigos c315 configurados vieram na resposta."""
    esperados = {config.CODIGO_INDICE_GERAL} | {g.codigo for g in config.GRUPOS_IPCA}
    faltando = esperados - set(df["CodigoGrupo"].unique())
    if faltando:
        raise ErroValidacao(f"SIDRA: códigos c315 sem dados {sorted(faltando)} — confira GRUPOS_IPCA.")


def validar_pesos(df_grupos: pd.DataFrame) -> None:
    """Soma dos pesos dos 9 grupos deve ser ~100% em cada mês."""
    soma = df_grupos.groupby("DataKey")["Peso"].sum()
    fora = soma[(soma - 1.0).abs() > config.TOLERANCIA_PESOS]
    if not fora.empty:
        exemplos = ", ".join(f"{k}={v*100:.2f}%" for k, v in fora.head(5).items())
        raise ErroValidacao(f"Pesos dos grupos não somam ~100% em {len(fora)} meses: {exemplos}")


def checar_contribuicoes(df_sidra: pd.DataFrame) -> None:
    """Alerta (não falha): Σ(variação × peso) dos grupos ≈ variação do índice geral."""
    grupos = df_sidra[df_sidra["CodigoGrupo"] != config.CODIGO_INDICE_GERAL]
    geral = df_sidra[df_sidra["CodigoGrupo"] == config.CODIGO_INDICE_GERAL].set_index("DataKey")["VariacaoMensal"]
    contrib = (grupos["VariacaoMensal"] * grupos["Peso"]).groupby(grupos["DataKey"]).sum()
    dif_pp = ((contrib - geral).abs() * 100).dropna()
    alertas = dif_pp[dif_pp > config.TOLERANCIA_CONTRIBUICAO_PP]
    if not alertas.empty:
        log.warning("Σ contribuições difere do índice geral em %d meses (máx %.3f p.p.)",
                    len(alertas), alertas.max())


# =============================================================================
# C) Focus
# =============================================================================
def tratar_focus(registros: list[dict]) -> pd.DataFrame:
    """Coletas diárias do Focus → 1 linha por mês de coleta × ano de referência.

    * mantém a **última coleta de cada mês** (grão mensal do modelo; o Focus é
      publicado semanalmente/diariamente);
    * guarda só anos de referência entre o ano da coleta e +4 anos;
    * percentuais → fração.
    """
    colunas = ["DataColetaKey", "AnoReferencia", "DataColeta", "Mediana", "Media", "Minimo", "Maximo"]
    if not registros:
        return pd.DataFrame(columns=colunas)
    df = pd.DataFrame(registros)
    df["DataColeta"] = pd.to_datetime(df["Data"]).dt.date
    df["AnoReferencia"] = pd.to_numeric(df["DataReferencia"], errors="coerce").astype("Int64")
    ano_coleta = pd.to_datetime(df["DataColeta"]).dt.year
    df = df[(df["AnoReferencia"] >= ano_coleta) & (df["AnoReferencia"] <= ano_coleta + config.FOCUS_ANOS_A_FRENTE)].copy()
    df["MesColeta"] = para_primeiro_dia(pd.to_datetime(df["DataColeta"]))
    df = df.sort_values("DataColeta").drop_duplicates(["MesColeta", "AnoReferencia"], keep="last")
    for c in ("Mediana", "Media", "Minimo", "Maximo"):
        df[c] = percentual_para_fracao(df[c])
    df["DataColetaKey"] = data_para_key(df["MesColeta"])
    df["AnoReferencia"] = df["AnoReferencia"].astype("int32")
    return df[colunas].reset_index(drop=True)


# =============================================================================
# Validações genéricas
# =============================================================================
def validar_sem_duplicados(df: pd.DataFrame, chaves: list[str], nome: str) -> None:
    """Nenhuma combinação de chave natural repetida."""
    dup = df[df.duplicated(chaves, keep=False)]
    if not dup.empty:
        raise ErroValidacao(f"{nome}: {len(dup)} linhas duplicadas na chave {chaves}. Ex.: {dup.head(3).to_dict('records')}")


def validar_sem_lacunas(df: pd.DataFrame, col_key: str, col_grupo: str, nome: str) -> None:
    """Para cada série/grupo, todos os meses entre o primeiro e o último existem."""
    for codigo, bloco in df.groupby(col_grupo):
        datas = pd.to_datetime(bloco[col_key].astype(str), format="%Y%m%d")
        esperado = pd.date_range(datas.min(), datas.max(), freq="MS")
        faltando = esperado.difference(datas)
        if len(faltando):
            meses = ", ".join(d.strftime("%Y-%m") for d in faltando[:6])
            raise ErroValidacao(f"{nome} {col_grupo}={codigo}: {len(faltando)} meses faltando ({meses}...)")


def validar_ipca_12m(df_ind: pd.DataFrame) -> pd.DataFrame:
    """Recalcula o IPCA 12M (produto de 1 + taxa) e compara com a série 13522.

    Tolerâncias:
    * ``TOLERANCIA_12M_ALERTA_PP`` (0,01 p.p., a do enunciado) → registra alerta;
    * ``TOLERANCIA_12M_ERRO_PP`` (0,05 p.p.) → falha a carga.

    Motivo das duas faixas: o IBGE calcula o 12M a partir do número-índice com
    muitas casas; o SGS publica as taxas mensais com 2 casas. Compor 12 taxas
    arredondadas pode gerar ±0,01–0,02 p.p. legítimos. Acima de 0,05 p.p. não é
    arredondamento: é dado errado. Devolve a tabela de conferência.
    """
    mensal = df_ind[df_ind["CodigoSGS"] == 433].set_index("Data")["Valor"].sort_index()
    oficial = df_ind[df_ind["CodigoSGS"] == 13522].set_index("Data")["Valor"]
    fator = (1 + mensal).rolling(12).apply(lambda x: x.prod(), raw=True)
    conf = pd.DataFrame({"Calculado12M": fator - 1, "Oficial13522": oficial}).dropna()
    conf["DiferencaPP"] = (conf["Calculado12M"] * 100).round(2) - (conf["Oficial13522"] * 100).round(2)
    if conf.empty:
        log.warning("Validação IPCA 12M: sem meses suficientes para comparar.")
        return conf
    alerta = conf[conf["DiferencaPP"].abs() > config.TOLERANCIA_12M_ALERTA_PP + 1e-9]
    erro = conf[conf["DiferencaPP"].abs() > config.TOLERANCIA_12M_ERRO_PP + 1e-9]
    log.info("Validação IPCA 12M: %d meses comparados; %d acima de %.2f p.p.; máx |dif| = %.2f p.p.",
             len(conf), len(alerta), config.TOLERANCIA_12M_ALERTA_PP, conf["DiferencaPP"].abs().max())
    if not erro.empty:
        raise ErroValidacao(
            f"IPCA 12M recalculado diverge da série 13522 em {len(erro)} meses (> {config.TOLERANCIA_12M_ERRO_PP} p.p.). "
            f"Ex.: {erro.head(3).round(4).to_dict('index')}"
        )
    return conf


# =============================================================================
# Dimensões
# =============================================================================
def montar_dim_indicador() -> pd.DataFrame:
    return pd.DataFrame([{
        "CodigoSGS": s.codigo, "Indicador": s.indicador, "Categoria": s.categoria, "Fonte": s.fonte,
        "Unidade": s.unidade, "TipoTaxa": s.tipo_taxa, "Ordem": s.ordem, "Descricao": s.descricao,
    } for s in config.SERIES_SGS])


def montar_dim_grupo() -> pd.DataFrame:
    return pd.DataFrame([{"CodigoGrupo": g.codigo, "Grupo": g.grupo, "Ordem": g.ordem, "CorHex": g.cor_hex}
                         for g in config.GRUPOS_IPCA])


def montar_dim_meta(ano_final: int) -> pd.DataFrame:
    """Expande a tabela de metas do CMN para uma linha por ano (frações)."""
    linhas = []
    for ano_ini, ano_fim, meta, tol, tipo in config.METAS_CMN:
        for ano in range(ano_ini, min(ano_fim, ano_final) + 1):
            linhas.append({
                "Ano": ano, "Meta": meta / 100, "LimiteInferior": (meta - tol) / 100,
                "LimiteSuperior": (meta + tol) / 100, "Tolerancia": tol / 100, "TipoMeta": tipo,
            })
    df = pd.DataFrame(linhas)
    validar_sem_duplicados(df, ["Ano"], "dMeta")
    return df


def linha_controle(fonte: str, df: pd.DataFrame, col_key: str, agora: datetime, obs: str = "") -> dict:
    """Uma linha da tabela _controle_carga para a fonte informada."""
    datas = key_para_data(df[col_key]) if not df.empty else pd.Series(dtype="object")
    return {
        "Fonte": fonte, "DataHoraCarga": agora,
        "PrimeiroMes": datas.min() if len(datas) else None,
        "UltimoMes": datas.max() if len(datas) else None,
        "Linhas": int(len(df)), "Observacao": obs,
    }


# =============================================================================
# Gravação (idempotente)
# =============================================================================
def upsert(df_novo: pd.DataFrame, arquivo: str) -> pd.DataFrame:
    """Mescla com o Parquet existente, deduplicando pela chave natural.

    Linhas novas **substituem** as antigas com a mesma chave; linhas fora do
    período reprocessado são preservadas. Reexecutar a carga, portanto, nunca
    duplica dados (idempotência).
    """
    chaves = CHAVES_NATURAIS[arquivo]
    caminho = config.PASTA_SILVER / arquivo
    colunas = ESQUEMAS[arquivo].names
    novo = df_novo[colunas]
    if caminho.exists():
        antigo = pd.read_parquet(caminho)[colunas]
        base = pd.concat([antigo, novo], ignore_index=True) if not novo.empty else antigo
        novo = base.drop_duplicates(chaves, keep="last")
    return novo.sort_values(chaves).reset_index(drop=True)


def gravar_parquet(df: pd.DataFrame, arquivo: str) -> Path:
    """Grava com esquema explícito e compressão snappy, de forma atômica.

    Escreve em ``.tmp`` e depois ``os.replace``: se algo falhar no meio, o
    Parquet anterior continua intacto (o Power BI nunca lê arquivo pela metade).
    """
    config.PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    esquema = ESQUEMAS[arquivo]
    tabela = pa.Table.from_pandas(df[esquema.names], schema=esquema, preserve_index=False)
    destino = config.PASTA_SILVER / arquivo
    temporario = destino.with_suffix(".parquet.tmp")
    pq.write_table(tabela, temporario, compression="snappy")
    os.replace(temporario, destino)
    return destino


def gravar_csv(df: pd.DataFrame, arquivo: str) -> Path:
    """CSV opcional para inspeção no Excel (pt-BR: ``;`` e vírgula decimal)."""
    config.PASTA_CSV.mkdir(parents=True, exist_ok=True)
    destino = config.PASTA_CSV / arquivo.replace(".parquet", ".csv")
    df.to_csv(destino, sep=";", decimal=",", index=False, encoding="utf-8-sig")
    return destino


def concatenar(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def hoje_primeiro_dia() -> date:
    h = date.today()
    return date(h.year, h.month, 1)
