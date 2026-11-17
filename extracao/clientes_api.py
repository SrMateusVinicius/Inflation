"""
clientes_api.py — Acesso HTTP às APIs públicas (BCB e IBGE).

Responsabilidades deste módulo (e só delas):
* criar uma ``requests.Session`` com retry/backoff exponencial, timeout
  explícito e User-Agent identificado;
* fatiar/paginar as requisições de cada API;
* gravar a resposta bruta (JSON) na camada **bronze**, com timestamp.

Nenhuma regra de negócio ou tipagem acontece aqui: isso é papel de
``transformacoes.py``.
"""
from __future__ import annotations

import json
import logging
from calendar import monthrange
from datetime import date
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import quote, urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

log = logging.getLogger(__name__)


class ErroAPI(RuntimeError):
    """Falha de comunicação ou resposta inesperada de uma API."""


# =============================================================================
# Sessão HTTP e utilitários
# =============================================================================
def criar_sessao() -> requests.Session:
    """Cria a sessão HTTP compartilhada por todas as fontes.

    * ``urllib3.Retry`` repete GETs em erros de conexão e nos status
      429/500/502/503/504, com backoff exponencial (``BACKOFF_FATOR``) e
      respeitando o cabeçalho ``Retry-After``.
    * ``raise_on_status=False``: depois de esgotar as tentativas, a resposta
      volta para ``get_json``, que gera uma mensagem de erro legível.
    """
    retry = Retry(
        total=config.TENTATIVAS,
        connect=config.TENTATIVAS,
        read=config.TENTATIVAS,
        status=config.TENTATIVAS,
        backoff_factor=config.BACKOFF_FATOR,
        status_forcelist=config.STATUS_RETRY,
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adaptador = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4)
    sessao = requests.Session()
    sessao.mount("https://", adaptador)
    sessao.mount("http://", adaptador)
    sessao.headers.update({"User-Agent": config.USER_AGENT, "Accept": "application/json"})
    return sessao


def get_json(sessao: requests.Session, url: str, *, aceitar_404: bool = False) -> Any:
    """GET com timeout explícito; devolve o JSON ou lança ``ErroAPI``."""
    log.debug("GET %s", url)
    resposta = sessao.get(url, timeout=config.TIMEOUT_SEGUNDOS)
    if aceitar_404 and resposta.status_code == 404:
        log.debug("404 tratado como 'sem dados': %s", url)
        return []
    if resposta.status_code >= 400:
        raise ErroAPI(f"HTTP {resposta.status_code} em {resposta.url} — {resposta.text[:300]!r}")
    try:
        return resposta.json()
    except ValueError as exc:
        raise ErroAPI(f"Resposta não é JSON em {resposta.url} — {resposta.text[:300]!r}") from exc


def montar_url(base: str, params: dict[str, Any]) -> str:
    """Monta a query string com espaços como ``%20`` (e não ``+``).

    O OData do Olinda interpreta ``+`` literalmente em alguns filtros; usar
    ``quote`` evita esse problema. ``$``, aspas simples e vírgulas ficam legíveis.
    """
    query = urlencode(params, quote_via=quote, safe="$,'()")
    return f"{base}?{query}"


def salvar_bronze(fonte: str, nome: str, payload: Any, carimbo: str) -> Path:
    """Grava a resposta bruta em ``dados/bronze/<fonte>/<nome>_<carimbo>.json``.

    A camada bronze é *append-only*: cada execução gera arquivos novos, o que
    permite auditar exatamente o que a API devolveu em cada carga.
    """
    pasta = config.PASTA_BRONZE / fonte
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"{nome}_{carimbo}.json"
    caminho.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding=config.ENCODING)
    return caminho


def ultimo_dia_mes(d: date) -> date:
    """Último dia do mês de ``d``."""
    return date(d.year, d.month, monthrange(d.year, d.month)[1])


def janelas_anos(inicio: date, fim: date, max_anos: int) -> Iterator[tuple[date, date]]:
    """Divide [inicio, fim] em janelas de no máximo ``max_anos`` anos-calendário."""
    atual = inicio
    while atual <= fim:
        limite = min(fim, date(atual.year + max_anos - 1, 12, 31))
        yield atual, limite
        atual = date(limite.year + 1, 1, 1)


def fatias_meses(inicio: date, fim: date, meses: int) -> Iterator[tuple[date, date]]:
    """Divide [inicio, fim] (1º dia dos meses) em fatias de ``meses`` meses."""
    atual = inicio
    while atual <= fim:
        idx = atual.year * 12 + atual.month - 1 + meses - 1
        limite = min(fim, date(idx // 12, idx % 12 + 1, 1))
        yield atual, limite
        idx_prox = limite.year * 12 + limite.month  # mês seguinte ao limite
        atual = date(idx_prox // 12, idx_prox % 12 + 1, 1)


# =============================================================================
# A) BCB — SGS
# =============================================================================
def buscar_serie_sgs(
    sessao: requests.Session, serie: config.SerieSGS, inicio: date, fim: date, carimbo: str
) -> list[dict[str, str]]:
    """Baixa uma série do SGS, em janelas de até 10 anos.

    **Endpoint**: ``https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados``

    **Parâmetros**: ``formato=json``, ``dataInicial=dd/MM/aaaa``,
    ``dataFinal=dd/MM/aaaa``.

    **Paginação**: a API recusa intervalos maiores que 10 anos; o período é
    fatiado em janelas de anos-calendário (``janelas_anos``) e os resultados
    são concatenados. Uma janela sem dados devolve 404 → tratada como vazia.

    **Retorno**: lista de ``{"data": "01/01/2012", "valor": "0.56"}``.
    """
    registros: list[dict[str, str]] = []
    url_base = config.SGS_URL.format(codigo=serie.codigo)
    for ini, fim_janela in janelas_anos(inicio, ultimo_dia_mes(fim), config.SGS_JANELA_MAX_ANOS):
        url = montar_url(url_base, {
            "formato": "json",
            "dataInicial": ini.strftime("%d/%m/%Y"),
            "dataFinal": fim_janela.strftime("%d/%m/%Y"),
        })
        dados = get_json(sessao, url, aceitar_404=True)
        if isinstance(dados, dict):  # a API às vezes devolve {"erro": ...}
            raise ErroAPI(f"SGS {serie.codigo}: resposta inesperada {str(dados)[:200]}")
        salvar_bronze("sgs", f"sgs_{serie.codigo}_{ini:%Y%m}_{fim_janela:%Y%m}", dados, carimbo)
        log.info("SGS %-5s %s → %s: %d registros", serie.codigo, ini, fim_janela, len(dados))
        registros.extend(dados)
    return registros


# =============================================================================
# B) IBGE — SIDRA
# =============================================================================
def buscar_sidra(
    sessao: requests.Session, tabela: config.TabelaSidra, inicio: date, fim: date, carimbo: str
) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Baixa variação, peso, acumulado no ano e 12 meses por grupo do IPCA.

    **Endpoint** (parâmetros no *path*)::

        https://apisidra.ibge.gov.br/values/t/{tabela}/n1/all/v/63,66,69,2265
            /p/{aaaamm}-{aaaamm}/c315/7169,7170,...,7786

    * ``n1/all`` = Brasil; ``v`` = variáveis; ``p`` = períodos;
      ``c315`` = classificação "Geral, grupo, subgrupo, item e subitem".

    **Paginação/limite**: o SIDRA limita a quantidade de valores por consulta;
    o período é fatiado em blocos de ``SIDRA_MESES_POR_REQUISICAO`` meses
    (10 categorias × 4 variáveis × 12 meses = 480 valores por chamada).

    **Cabeçalho**: a 1ª linha da resposta é descritiva (rótulos das colunas);
    ela é separada e devolvida à parte, e só as linhas de dados seguem.

    Meses ainda não publicados no fim do intervalo são tolerados: se a última
    fatia não tiver dados, registra-se um aviso e a carga continua.
    """
    variaveis = ",".join(str(v) for v in config.SIDRA_VARIAVEIS)
    categorias = ",".join(
        [str(config.CODIGO_INDICE_GERAL)] + [str(g.codigo) for g in config.GRUPOS_IPCA]
    )
    qtd_valores = len(config.SIDRA_VARIAVEIS) * (len(config.GRUPOS_IPCA) + 1) * config.SIDRA_MESES_POR_REQUISICAO
    if qtd_valores > config.SIDRA_LIMITE_VALORES:
        raise ValueError("Fatia do SIDRA excede o limite de valores; reduza SIDRA_MESES_POR_REQUISICAO.")

    cabecalho: dict[str, str] = {}
    linhas: list[dict[str, str]] = []
    for ini, fim_fatia in fatias_meses(inicio, fim, config.SIDRA_MESES_POR_REQUISICAO):
        url = (
            f"{config.SIDRA_URL}/t/{tabela.numero}/n1/all/v/{variaveis}"
            f"/p/{ini:%Y%m}-{fim_fatia:%Y%m}/c{config.SIDRA_CLASSIFICACAO}/{categorias}"
        )
        try:
            dados = get_json(sessao, url)
        except ErroAPI as exc:
            if fim_fatia == fim and ini >= date(fim.year - 1, 1, 1):
                log.warning("SIDRA %s %s→%s sem dados publicados (ignorado): %s",
                            tabela.numero, ini, fim_fatia, exc)
                continue
            raise
        salvar_bronze("sidra", f"sidra_{tabela.numero}_{ini:%Y%m}_{fim_fatia:%Y%m}", dados, carimbo)
        if not isinstance(dados, list) or len(dados) < 2:
            log.warning("SIDRA %s %s→%s: resposta vazia", tabela.numero, ini, fim_fatia)
            continue
        cabecalho = cabecalho or dados[0]
        linhas.extend(dados[1:])  # descarta a linha de cabeçalho descritivo
        log.info("SIDRA %s %s → %s: %d linhas", tabela.numero, ini, fim_fatia, len(dados) - 1)
    return cabecalho, linhas


# =============================================================================
# C) BCB — Olinda / Focus
# =============================================================================
def buscar_focus(sessao: requests.Session, inicio: date, fim: date, carimbo: str) -> list[dict[str, Any]]:
    """Baixa as expectativas anuais do IPCA (Relatório Focus).

    **Endpoint**: ``.../olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais``

    **Parâmetros OData**:
    * ``$filter`` = ``Indicador eq 'IPCA' and baseCalculo eq 0 and Data ge ... and Data le ...``
    * ``$select`` = só as colunas necessárias (menos tráfego);
    * ``$orderby=Data``, ``$format=json``.

    **Paginação**: ``$top`` (tamanho da página) + ``$skip`` (deslocamento),
    até uma página vir com menos de ``$top`` registros.
    """
    filtro = (
        f"Indicador eq '{config.FOCUS_INDICADOR}' and baseCalculo eq {config.FOCUS_BASE_CALCULO}"
        f" and Data ge '{inicio:%Y-%m-%d}' and Data le '{ultimo_dia_mes(fim):%Y-%m-%d}'"
    )
    registros: list[dict[str, Any]] = []
    pular = 0
    while True:
        url = montar_url(config.FOCUS_URL, {
            "$filter": filtro,
            "$select": ",".join(config.FOCUS_COLUNAS),
            "$orderby": "Data",
            "$format": "json",
            "$top": config.FOCUS_PAGINA,
            "$skip": pular,
        })
        dados = get_json(sessao, url)
        pagina = dados.get("value", []) if isinstance(dados, dict) else []
        salvar_bronze("focus", f"focus_ipca_skip{pular:07d}", dados, carimbo)
        registros.extend(pagina)
        log.info("Focus página skip=%d: %d registros", pular, len(pagina))
        if len(pagina) < config.FOCUS_PAGINA:
            break
        pular += config.FOCUS_PAGINA
    return registros
