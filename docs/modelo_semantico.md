# Modelo semântico — tabelas, colunas, relacionamentos e Power Query

## Relacionamentos (todos 1:*, filtro em direção única, chaves inteiras)

| De (muitos) | Para (um) | Cardinalidade | Filtro |
|---|---|---|---|
| `fIndicadores[DataKey]` | `dCalendario[DataKey]` | * → 1 | Único (dimensão → fato) |
| `fIndicadores[CodigoSGS]` | `dIndicador[CodigoSGS]` | * → 1 | Único (dimensão → fato) |
| `fIPCAGrupos[DataKey]` | `dCalendario[DataKey]` | * → 1 | Único (dimensão → fato) |
| `fIPCAGrupos[CodigoGrupo]` | `dGrupoIPCA[CodigoGrupo]` | * → 1 | Único (dimensão → fato) |
| `fExpectativas[DataColetaKey]` | `dCalendario[DataKey]` | * → 1 | Único (dimensão → fato) |

`dMeta` e `_ControleCarga` são **desconectadas** (lidas por medidas).

## Parâmetro `pRepositorio`

```m
"SrMateusVinicius/Inflation/main" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```

## dCalendario — Dimensão

Dimensão de datas MENSAL gerada no Power Query (1 linha por mês, do 1º ao último mês presente nos fatos). Marcada como tabela de datas.

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| Data | dateTime | dd/mm/yyyy | sim | Primeiro dia do mês (chave de data da tabela de datas). |
| DataKey | int64 | 0 | não | Chave inteira aaaammdd (relacionamento com os fatos). |
| Ano | int64 | 0 | sim | Ano civil. |
| MesNum | int64 | 0 | não | Número do mês (1–12); ordena MesAbrev. |
| MesAbrev | string |  | sim | Mês abreviado pt-BR (jan, fev, ...). |
| AnoMes | string |  | sim | Rótulo de eixo no formato 'jan/25'. |
| AnoMesOrdem | int64 | 0 | não | aaaamm numérico; ordena AnoMes. |
| Trimestre | string |  | sim | Trimestre (T1–T4). |
| TrimestreNum | int64 | 0 | não | Número do trimestre; ordena Trimestre. |
| Semestre | string |  | sim | Semestre (S1/S2). |
| SemestreNum | int64 | 0 | não | Número do semestre; ordena Semestre. |
| MesSequencial | int64 | 0 | não | Contador de meses desde o início do calendário (1, 2, 3...). |
| EhUltimoMesDisponivel | boolean |  | sim | TRUE no último mês com IPCA (SGS 433) publicado. |
| EhAnoCorrente | boolean |  | sim | TRUE nos meses do ano do último IPCA publicado. |

```m
let
    // ---------------------------------------------------------------
    // dCalendario MENSAL gerada no Power Query (não em DAX).
    // Intervalo: do menor ao maior mês presente nos três fatos.
    // ---------------------------------------------------------------
    Ind = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/fIndicadores.parquet" ] ) ) ),
    Grp = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/fIPCAGrupos.parquet" ] ) ) ),
    Exp = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/fExpectativas.parquet" ] ) ) ),
    KeyParaData = ( k as number ) as date =>
        #date ( Number.IntegerDivide ( k, 10000 ), Number.Mod ( Number.IntegerDivide ( k, 100 ), 100 ), 1 ),
    Chaves = List.Combine ( { Ind[DataKey], Grp[DataKey], Exp[DataColetaKey] } ),
    Inicio = KeyParaData ( List.Min ( Chaves ) ),
    Fim = KeyParaData ( List.Max ( Chaves ) ),
    UltimoIPCA = KeyParaData ( List.Max ( Table.SelectRows ( Ind, each [CodigoSGS] = 433 )[DataKey] ) ),
    QtdMeses = ( Date.Year ( Fim ) - Date.Year ( Inicio ) ) * 12 + Date.Month ( Fim ) - Date.Month ( Inicio ) + 1,
    Datas = List.Transform ( { 0 .. QtdMeses - 1 }, each Date.AddMonths ( Inicio, _ ) ),
    // nomes fixos em pt-BR (independe do idioma do Windows)
    Meses = { "jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez" },
    Linhas = List.Transform (
        Datas,
        ( d ) => [
            Data = d,
            DataKey = Date.Year ( d ) * 10000 + Date.Month ( d ) * 100 + 1,
            Ano = Date.Year ( d ),
            MesNum = Date.Month ( d ),
            MesAbrev = Meses{ Date.Month ( d ) - 1 },
            AnoMes = Meses{ Date.Month ( d ) - 1 } & "/" & Text.End ( Text.From ( Date.Year ( d ) ), 2 ),
            AnoMesOrdem = Date.Year ( d ) * 100 + Date.Month ( d ),
            Trimestre = "T" & Text.From ( Date.QuarterOfYear ( d ) ),
            TrimestreNum = Date.QuarterOfYear ( d ),
            Semestre = if Date.Month ( d ) <= 6 then "S1" else "S2",
            SemestreNum = if Date.Month ( d ) <= 6 then 1 else 2,
            MesSequencial = ( Date.Year ( d ) - Date.Year ( Inicio ) ) * 12 + Date.Month ( d ) - Date.Month ( Inicio ) + 1,
            EhUltimoMesDisponivel = d = UltimoIPCA,
            EhAnoCorrente = Date.Year ( d ) = Date.Year ( UltimoIPCA )
        ]
    ),
    Tabela = Table.FromRecords (
        Linhas,
        type table [
            Data = date, DataKey = Int64.Type, Ano = Int64.Type, MesNum = Int64.Type, MesAbrev = text,
            AnoMes = text, AnoMesOrdem = Int64.Type, Trimestre = text, TrimestreNum = Int64.Type,
            Semestre = text, SemestreNum = Int64.Type, MesSequencial = Int64.Type,
            EhUltimoMesDisponivel = logical, EhAnoCorrente = logical
        ]
    )
in
    Tabela
```

## dIndicador — Dimensão

Dimensão dos indicadores do SGS/BCB (IPCA, INPC, IGP-M, livres, monitorados, Selic).

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| CodigoSGS | int64 | 0 | não | Código da série no SGS/BCB (chave). |
| Indicador | string |  | sim | Nome curto do indicador. |
| Categoria | string |  | sim | Inflação ou Juros. |
| Fonte | string |  | sim | Origem do dado (BCB-SGS). |
| Unidade | string |  | sim | Unidade original (% a.m., % a.a., % 12 meses). |
| TipoTaxa | string |  | não | Mensal (compõe acumulados), Acumulada 12M ou Anualizada. |
| Ordem | int64 | 0 | não | Ordem de exibição. |
| Descricao | string |  | sim | Descrição completa da série. |

```m
let
    // Leitura do Parquet tipado da camada silver (GitHub raw: URL base fixa + RelativePath, atualiza no Service sem gateway)
    Fonte = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/dIndicador.parquet" ] ) ) ),
    // Mantém só as colunas do modelo (protege contra colunas novas no arquivo)
    Colunas = Table.SelectColumns ( Fonte, { "CodigoSGS", "Indicador", "Categoria", "Fonte", "Unidade", "TipoTaxa", "Ordem", "Descricao" } ),
    // Reafirma os tipos (nenhuma coluna 'any')
    Tipos = Table.TransformColumnTypes (
        Colunas,
        {
            { "CodigoSGS", Int64.Type },
            { "Indicador", type text },
            { "Categoria", type text },
            { "Fonte", type text },
            { "Unidade", type text },
            { "TipoTaxa", type text },
            { "Ordem", Int64.Type },
            { "Descricao", type text }
        }
    )
in
    Tipos
```

## dGrupoIPCA — Dimensão

Dimensão dos 9 grupos do IPCA (classificação c315 do SIDRA), com cor fixa para os visuais.

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| CodigoGrupo | int64 | 0 | não | Código c315 do grupo no SIDRA (chave). |
| Grupo | string |  | sim | Nome do grupo do IPCA. |
| Ordem | int64 | 0 | não | Ordem oficial do IBGE. |
| CorHex | string |  | não | Cor do grupo em hexadecimal (formatação condicional). |

```m
let
    // Leitura do Parquet tipado da camada silver (GitHub raw: URL base fixa + RelativePath, atualiza no Service sem gateway)
    Fonte = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/dGrupoIPCA.parquet" ] ) ) ),
    // Mantém só as colunas do modelo (protege contra colunas novas no arquivo)
    Colunas = Table.SelectColumns ( Fonte, { "CodigoGrupo", "Grupo", "Ordem", "CorHex" } ),
    // Reafirma os tipos (nenhuma coluna 'any')
    Tipos = Table.TransformColumnTypes (
        Colunas,
        {
            { "CodigoGrupo", Int64.Type },
            { "Grupo", type text },
            { "Ordem", Int64.Type },
            { "CorHex", type text }
        }
    )
in
    Tipos
```

## dMeta — Dimensão (desconectada)

Metas de inflação do CMN por ano (frações). DESCONECTADA: lida pelas medidas da pasta 03 Meta (ver README).

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| Ano | int64 | 0 | sim | Ano da meta. |
| Meta | double | 0.00% | sim | Centro da meta (fração: 0,03 = 3%). |
| LimiteInferior | double | 0.00% | sim | Piso do intervalo de tolerância. |
| LimiteSuperior | double | 0.00% | sim | Teto do intervalo de tolerância. |
| Tolerancia | double | 0.00% | sim | Tolerância em fração (0,015 = 1,5 p.p.). |
| TipoMeta | string |  | sim | Ano-calendário (até 2024) ou Contínua (desde 2025). |

```m
let
    // Leitura do Parquet tipado da camada silver (GitHub raw: URL base fixa + RelativePath, atualiza no Service sem gateway)
    Fonte = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/dMeta.parquet" ] ) ) ),
    // Mantém só as colunas do modelo (protege contra colunas novas no arquivo)
    Colunas = Table.SelectColumns ( Fonte, { "Ano", "Meta", "LimiteInferior", "LimiteSuperior", "Tolerancia", "TipoMeta" } ),
    // Reafirma os tipos (nenhuma coluna 'any')
    Tipos = Table.TransformColumnTypes (
        Colunas,
        {
            { "Ano", Int64.Type },
            { "Meta", type number },
            { "LimiteInferior", type number },
            { "LimiteSuperior", type number },
            { "Tolerancia", type number },
            { "TipoMeta", type text }
        }
    )
in
    Tipos
```

## fIndicadores — Fato

Fato mensal em formato longo: 1 linha por mês × série SGS. Valores em fração decimal.

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| DataKey | int64 | 0 | não | Mês (aaaammdd) → dCalendario. |
| CodigoSGS | int64 | 0 | não | Série → dIndicador. |
| Valor | double | 0.00% | não | Valor da série em fração (0,0044 = 0,44%). Use as medidas. |

```m
let
    // Leitura do Parquet tipado da camada silver (GitHub raw: URL base fixa + RelativePath, atualiza no Service sem gateway)
    Fonte = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/fIndicadores.parquet" ] ) ) ),
    // Mantém só as colunas do modelo (protege contra colunas novas no arquivo)
    Colunas = Table.SelectColumns ( Fonte, { "DataKey", "CodigoSGS", "Valor" } ),
    // Reafirma os tipos (nenhuma coluna 'any')
    Tipos = Table.TransformColumnTypes (
        Colunas,
        {
            { "DataKey", Int64.Type },
            { "CodigoSGS", Int64.Type },
            { "Valor", type number }
        }
    )
in
    Tipos
```

## fIPCAGrupos — Fato

Fato mensal do IPCA por grupo (SIDRA 1419/7060): variação mensal e peso, em fração.

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| DataKey | int64 | 0 | não | Mês (aaaammdd) → dCalendario. |
| CodigoGrupo | int64 | 0 | não | Grupo → dGrupoIPCA. |
| VariacaoMensal | double | 0.00% | não | Variação mensal do grupo (fração). |
| Peso | double | 0.00% | não | Peso do grupo no IPCA do mês (fração; soma ≈ 1). |

```m
let
    // Leitura do Parquet tipado da camada silver (GitHub raw: URL base fixa + RelativePath, atualiza no Service sem gateway)
    Fonte = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/fIPCAGrupos.parquet" ] ) ) ),
    // Mantém só as colunas do modelo (protege contra colunas novas no arquivo)
    Colunas = Table.SelectColumns ( Fonte, { "DataKey", "CodigoGrupo", "VariacaoMensal", "Peso" } ),
    // Reafirma os tipos (nenhuma coluna 'any')
    Tipos = Table.TransformColumnTypes (
        Colunas,
        {
            { "DataKey", Int64.Type },
            { "CodigoGrupo", Int64.Type },
            { "VariacaoMensal", type number },
            { "Peso", type number }
        }
    )
in
    Tipos
```

## fExpectativas — Fato

Fato das expectativas Focus para o IPCA anual: última coleta de cada mês × ano de referência.

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| DataColetaKey | int64 | 0 | não | Mês da coleta (aaaammdd) → dCalendario. |
| AnoReferencia | int64 | 0 | sim | Ano para o qual a expectativa foi feita. |
| DataColeta | dateTime | dd/mm/yyyy | sim | Data exata da última coleta do mês. |
| Mediana | double | 0.00% | não | Mediana das projeções (fração). |
| Media | double | 0.00% | não | Média das projeções (fração). |
| Minimo | double | 0.00% | não | Menor projeção (fração). |
| Maximo | double | 0.00% | não | Maior projeção (fração). |

```m
let
    // Leitura do Parquet tipado da camada silver (GitHub raw: URL base fixa + RelativePath, atualiza no Service sem gateway)
    Fonte = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/fExpectativas.parquet" ] ) ) ),
    // Mantém só as colunas do modelo (protege contra colunas novas no arquivo)
    Colunas = Table.SelectColumns ( Fonte, { "DataColetaKey", "AnoReferencia", "DataColeta", "Mediana", "Media", "Minimo", "Maximo" } ),
    // Reafirma os tipos (nenhuma coluna 'any')
    Tipos = Table.TransformColumnTypes (
        Colunas,
        {
            { "DataColetaKey", Int64.Type },
            { "AnoReferencia", Int64.Type },
            { "DataColeta", type date },
            { "Mediana", type number },
            { "Media", type number },
            { "Minimo", type number },
            { "Maximo", type number }
        }
    )
in
    Tipos
```

## _ControleCarga — Técnica (desconectada)

Controle técnico da extração Python: data/hora da carga e último mês por fonte (página Metodologia).

| Coluna | Tipo | Formato | Visível | Descrição |
|---|---|---|---|---|
| Fonte | string |  | sim | Fonte de dados (BCB-SGS, IBGE-SIDRA, BCB-Focus, CMN-Metas). |
| DataHoraCarga | dateTime | dd/mm/yyyy hh:nn | sim | Data e hora da execução do Python. |
| PrimeiroMes | dateTime | mmm/yyyy | sim | Primeiro mês disponível na silver. |
| UltimoMes | dateTime | mmm/yyyy | sim | Último mês disponível na silver. |
| Linhas | int64 | #,0 | sim | Linhas gravadas na silver. |
| Observacao | string |  | sim | Tempo da etapa / versão. |

```m
let
    // Leitura do Parquet tipado da camada silver (GitHub raw: URL base fixa + RelativePath, atualiza no Service sem gateway)
    Fonte = Parquet.Document ( Binary.Buffer ( Web.Contents ( "https://raw.githubusercontent.com", [ RelativePath = pRepositorio & "/dados/silver/_controle_carga.parquet" ] ) ) ),
    // Mantém só as colunas do modelo (protege contra colunas novas no arquivo)
    Colunas = Table.SelectColumns ( Fonte, { "Fonte", "DataHoraCarga", "PrimeiroMes", "UltimoMes", "Linhas", "Observacao" } ),
    // Reafirma os tipos (nenhuma coluna 'any')
    Tipos = Table.TransformColumnTypes (
        Colunas,
        {
            { "Fonte", type text },
            { "DataHoraCarga", type datetime },
            { "PrimeiroMes", type date },
            { "UltimoMes", type date },
            { "Linhas", Int64.Type },
            { "Observacao", type text }
        }
    )
in
    Tipos
```

## _Medidas — tabela de medidas

```m
let
    // Tabela vazia: existe só para hospedar as medidas (coluna oculta)
    Fonte = #table ( type table [ Medidas = text ], {} )
in
    Fonte
```
