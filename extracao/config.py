"""
config.py — Configuração central do Monitor de Inflação Brasil.

Tudo o que é "parâmetro de negócio" ou "parâmetro técnico" fica aqui, para que
os demais módulos não tenham números mágicos:

* caminhos do projeto (com espaços e acentos → sempre ``pathlib.Path``);
* parâmetros HTTP (timeout, retry, User-Agent);
* séries do SGS/BCB, tabelas/variáveis/categorias do SIDRA/IBGE e o
  serviço Focus (Olinda/BCB);
* tabela estática e versionada das metas de inflação do CMN;
* tolerâncias das validações.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# =============================================================================
# 1. Caminhos
# =============================================================================
# Todo arquivo texto é lido/escrito em UTF-8; caminhos sempre com pathlib.
ENCODING = "utf-8"


def _resolver_raiz() -> Path:
    """Define a pasta raiz do projeto.

    1. variável de ambiente ``INFLACAO_RAIZ`` (GitHub Actions ou outra máquina);
    2. pasta-mãe de ``extracao/`` (padrão: funciona em qualquer clone do repositório).
    """
    env = os.environ.get("INFLACAO_RAIZ")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1]


PASTA_RAIZ = _resolver_raiz()
PASTA_BRONZE = PASTA_RAIZ / "dados" / "bronze"
PASTA_SILVER = PASTA_RAIZ / "dados" / "silver"
PASTA_CSV = PASTA_SILVER / "csv"
PASTA_LOGS = PASTA_RAIZ / "logs"

# =============================================================================
# 2. HTTP
# =============================================================================
USER_AGENT = "MonitorInflacaoBrasil/1.0 (projeto de estudo Power BI; python-requests)"
TIMEOUT_SEGUNDOS: tuple[float, float] = (10.0, 90.0)  # (conexão, leitura)
TENTATIVAS = 5                                         # retries totais
BACKOFF_FATOR = 1.5                                    # 0s, 3s, 6s, 12s, 24s...
STATUS_RETRY: tuple[int, ...] = (429, 500, 502, 503, 504)

# =============================================================================
# 3. BCB — SGS (Sistema Gerenciador de Séries Temporais)
# =============================================================================
SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
SGS_JANELA_MAX_ANOS = 10  # limite da API: no máximo 10 anos por requisição


@dataclass(frozen=True)
class SerieSGS:
    """Metadados de uma série SGS.

    ``tipo_taxa`` define se a série pode ser composta mês a mês nas medidas DAX:
    * ``Mensal``        → variação % no mês (compõe acumulados);
    * ``Acumulada 12M`` → já vem acumulada (não compor);
    * ``Anualizada``    → taxa % a.a. (não compor).

    ``faixa_valida`` (em %) é a "validação do código": se a série baixada tiver
    valores fora dessa faixa, o código provavelmente não corresponde à série
    descrita e a carga falha com mensagem clara.
    """

    codigo: int
    indicador: str
    categoria: str
    unidade: str
    tipo_taxa: str
    ordem: int
    faixa_valida: tuple[float, float]
    descricao: str
    fonte: str = "BCB-SGS"


SERIES_SGS: tuple[SerieSGS, ...] = (
    SerieSGS(433, "IPCA", "Inflação", "% a.m.", "Mensal", 1, (-2.0, 5.0),
             "IPCA - variação mensal (%) - índice oficial de inflação (IBGE)"),
    SerieSGS(13522, "IPCA 12M (oficial)", "Inflação", "% 12 meses", "Acumulada 12M", 2, (-3.0, 20.0),
             "IPCA - variação acumulada em 12 meses (%) - usada para conferir as medidas DAX"),
    SerieSGS(188, "INPC", "Inflação", "% a.m.", "Mensal", 3, (-2.0, 5.0),
             "INPC - variação mensal (%) - famílias de 1 a 5 salários mínimos"),
    SerieSGS(189, "IGP-M", "Inflação", "% a.m.", "Mensal", 4, (-5.0, 10.0),
             "IGP-M - variação mensal (%) - FGV"),
    SerieSGS(11428, "IPCA Livres", "Inflação", "% a.m.", "Mensal", 5, (-3.0, 5.0),
             "IPCA - itens livres - variação mensal (%)"),
    SerieSGS(4449, "IPCA Monitorados", "Inflação", "% a.m.", "Mensal", 6, (-10.0, 10.0),
             "IPCA - preços administrados/monitorados - variação mensal (%)"),
    SerieSGS(4189, "Selic (% a.a.)", "Juros", "% a.a.", "Anualizada", 7, (0.0, 30.0),
             "Taxa Selic acumulada no mês, anualizada base 252 (% a.a.)"),
    # Série adicional (decisão técnica, ver README): a 4189 é anualizada e não
    # deve ser composta. Para o "Selic 12M" do juro real ex-post usamos a Selic
    # efetiva do mês (% a.m.), que pode ser composta exatamente como o IPCA.
    SerieSGS(4390, "Selic (% a.m.)", "Juros", "% a.m.", "Mensal", 8, (0.0, 3.0),
             "Taxa Selic acumulada no mês (% a.m.) - base do Selic 12M composto"),
)

# =============================================================================
# 4. IBGE — SIDRA (IPCA por grupos)
# =============================================================================
SIDRA_URL = "https://apisidra.ibge.gov.br/values"


@dataclass(frozen=True)
class TabelaSidra:
    """Tabela do SIDRA e o intervalo de meses que ela cobre."""

    numero: int
    inicio: date
    fim: date | None  # None = até o último mês publicado


SIDRA_TABELAS: tuple[TabelaSidra, ...] = (
    TabelaSidra(1419, date(2012, 1, 1), date(2019, 12, 1)),  # opcional: histórico
    TabelaSidra(7060, date(2020, 1, 1), None),                # IPCA desde jan/2020
)

# Variáveis baixadas (todas vão para a bronze; 63 e 66 vão para a silver).
SIDRA_VARIAVEIS: dict[int, str] = {
    63: "VariacaoMensal",
    66: "Peso",
    69: "VariacaoAcumAno",
    2265: "Variacao12M",
}
SIDRA_VARIAVEIS_SILVER: tuple[str, ...] = ("VariacaoMensal", "Peso")
SIDRA_CLASSIFICACAO = 315
CODIGO_INDICE_GERAL = 7169
SIDRA_MESES_POR_REQUISICAO = 12          # fatia anual
SIDRA_LIMITE_VALORES = 50_000            # limite conservador por requisição


@dataclass(frozen=True)
class GrupoIPCA:
    """Grupo do IPCA (classificação c315 do SIDRA)."""

    codigo: int
    grupo: str
    ordem: int
    cor_hex: str


GRUPOS_IPCA: tuple[GrupoIPCA, ...] = (
    GrupoIPCA(7170, "Alimentação e bebidas", 1, "#8064F5"),
    GrupoIPCA(7445, "Habitação", 2, "#5A42D9"),
    GrupoIPCA(7486, "Artigos de residência", 3, "#E7E0FF"),
    GrupoIPCA(7558, "Vestuário", 4, "#C9C8D1"),
    GrupoIPCA(7625, "Transportes", 5, "#B8A6FA"),
    GrupoIPCA(7660, "Saúde e cuidados pessoais", 6, "#3F3D4A"),
    GrupoIPCA(7712, "Despesas pessoais", 7, "#85838F"),
    GrupoIPCA(7766, "Educação", 8, "#D9D0FD"),
    GrupoIPCA(7786, "Comunicação", 9, "#A3A1AD"),
)

# =============================================================================
# 5. BCB — Olinda / Focus (expectativas anuais de mercado)
# =============================================================================
FOCUS_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    "ExpectativasMercadoAnuais"
)
FOCUS_INDICADOR = "IPCA"
FOCUS_COLUNAS: tuple[str, ...] = (
    "Indicador", "Data", "DataReferencia", "Media", "Mediana", "Minimo", "Maximo", "baseCalculo",
)
FOCUS_BASE_CALCULO = 0     # 0 = estatísticas sobre todas as respostas dos últimos 30 dias
FOCUS_PAGINA = 5_000       # $top por página
FOCUS_ANOS_A_FRENTE = 4    # guarda expectativas do ano da coleta até +4 anos

# =============================================================================
# 6. Metas de inflação (CMN) — tabela estática e versionada
# =============================================================================
# (ano_inicial, ano_final, meta %, tolerância p.p., tipo)
# * 2012–2016: 4,50% ± 2,0 p.p.
# * Desde 2017: tolerância de ± 1,5 p.p.
# * Desde 2025: meta contínua de 3,0% (apurada em 12 meses, não só em dezembro).
METAS_CMN: tuple[tuple[int, int, float, float, str], ...] = (
    (2012, 2016, 4.50, 2.0, "Ano-calendário"),
    (2017, 2018, 4.50, 1.5, "Ano-calendário"),
    (2019, 2019, 4.25, 1.5, "Ano-calendário"),
    (2020, 2020, 4.00, 1.5, "Ano-calendário"),
    (2021, 2021, 3.75, 1.5, "Ano-calendário"),
    (2022, 2022, 3.50, 1.5, "Ano-calendário"),
    (2023, 2023, 3.25, 1.5, "Ano-calendário"),
    (2024, 2024, 3.00, 1.5, "Ano-calendário"),
    (2025, 2100, 3.00, 1.5, "Contínua"),
)
METAS_ANOS_FUTUROS = 5  # gera linhas da meta contínua até ano atual + 5
METAS_VERSAO = "2026-10"

# =============================================================================
# 7. Validações
# =============================================================================
TOLERANCIA_PESOS = 0.005           # soma dos pesos dos 9 grupos: 100% ± 0,5 p.p.
TOLERANCIA_12M_ALERTA_PP = 0.01    # alerta (tolerância do enunciado)
TOLERANCIA_12M_ERRO_PP = 0.05      # erro: diferença maior que arredondamento
TOLERANCIA_CONTRIBUICAO_PP = 0.03  # Σ(var × peso) vs índice geral (só alerta)

# =============================================================================
# 8. Arquivos da camada silver
# =============================================================================
ARQ_INDICADORES = "fIndicadores.parquet"
ARQ_GRUPOS = "fIPCAGrupos.parquet"
ARQ_EXPECTATIVAS = "fExpectativas.parquet"
ARQ_META = "dMeta.parquet"
ARQ_DIM_INDICADOR = "dIndicador.parquet"
ARQ_DIM_GRUPO = "dGrupoIPCA.parquet"
ARQ_CONTROLE = "_controle_carga.parquet"
