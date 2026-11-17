# Catálogo de medidas DAX — Monitor de Inflação Brasil

Total: **95 medidas** na tabela `_Medidas`, em 8 pastas de exibição. As medidas com `_` no início são auxiliares ocultas. Formato p.p.: as medidas já devolvem pontos percentuais (1,24 = 1,24 p.p.), com format string `+0,00 p.p.`.

## Índice

- **01 Base**: `Indicador Mensal %`, `IPCA Mensal %`, `INPC Mensal %`, `IGP-M Mensal %`, `IPCA Livres %`, `IPCA Monitorados %`, `Selic % a.a.`, `Selic Mensal %`, `Último Mês Disponível`
- **02 Acumulados**: `Indicador Acum. Ano %`, `Indicador 12M %`, `Indicador Acum. Período %`, `Indicador Número-Índice`, `IPCA Acum. Ano %`, `IPCA 12M %`, `IPCA Número-Índice`, `INPC Acum. Ano %`, `INPC 12M %`, `INPC Número-Índice`, `IGP-M Acum. Ano %`, `IGP-M 12M %`, `IGP-M Número-Índice`, `IPCA Acum. Período Selecionado %`, `IPCA Livres 12M %`, `IPCA Monitorados 12M %`, `Selic 12M %`, `IPCA 12M % (SGS 13522)`
- **03 Meta**: `Meta Ano %`, `Limite Inferior %`, `Limite Superior %`, `Desvio vs Meta (p.p.)`, `Desvio vs Teto (p.p.)`, `Status Meta`, `Meses Consecutivos Acima do Teto`, `Acima do Teto no Ano (p.p.)`
- **04 Composição**: `Variação Grupo Mensal %`, `Peso Grupo %`, `Contribuição Grupo (p.p.)`, `Contribuição Total (p.p.)`, `Participação na Inflação %`, `Ranking Grupo por Contribuição`, `Grupo de Maior Pressão`, `Contribuição do Grupo de Maior Pressão (p.p.)`
- **05 Comparativos**: `Variação vs Mês Anterior (p.p.)`, `IPCA Mensal Mês Anterior %`, `IPCA 12M Mês Anterior %`, `Δ 12M vs Mês Anterior (p.p.)`, `IPCA 12M Mesmo Mês Ano Anterior`, `Δ 12M vs Ano Anterior (p.p.)`, `IPCA Acum. Ano Mesmo Período Ano Anterior %`, `Δ Acum. Ano vs Ano Anterior (p.p.)`, `Spread IPCA − IGP-M (p.p.)`, `Spread IPCA − INPC (p.p.)`, `Difusão de Alta %`
- **06 Expectativas e Juros**: `Focus Mediana Ano Corrente`, `Focus Mediana Próximo Ano`, `Focus Mediana Início do Ano`, `Focus vs Realizado (p.p.)`, `Juro Real Ex-Post %`
- **07 Textos e HTML**: `Texto Dados Até`, `Texto Mês de Referência`, `Título Visão Geral`, `Título Composição`, `Título Comparativos`, `Título Expectativas`, `Título Metodologia`, `Subtítulo Meta`, `Subtítulo Composição`, `Subtítulo Juro Real`, `Última Carga`, `HTML Card IPCA Mês`, `HTML Card IPCA Acum. Ano`, `HTML Card IPCA 12M`, `HTML Status Meta`, `HTML Tabela Grupos`, `HTML Cabeçalho Narrativo`, `SVG Sparkline 12M`, `Rótulo Acima do Teto`
- **08 Auxiliares**: `_Data Referência`, `_Data Referência Grupos`, `_Data Referência Focus`, `_Data Referência IPCA`, `_Valor Bruto`, `_Indicador Composto`, `Cor Status Meta`, `Cor Coluna Realizado vs Teto`, `Cor Variação`, `Cor Heatmap Grupo`, `Cor Fonte Heatmap Grupo`, `Cor Grupo`, `Cor Juro Real`, `Checagem IPCA 12M (p.p.)`, `Checagem IPCA 12M Status`, `Checagem Meses Divergentes`, `Marcador Último Ponto IPCA 12M`

## 01 Base

### Indicador Mensal %

*Variação mensal do indicador selecionado (dIndicador) no mês de referência.* · formato: `0.00%`

```dax
Indicador Mensal % =
-- =============================================================
-- Indicador Mensal %
-- Objetivo : valor mensal do indicador em contexto (use com dIndicador na legenda).
-- Regra    : lê o valor do mês de referência ([_Data Referência]); num contexto de
--            vários meses (ex.: um ano), devolve o último mês com dado.
-- =============================================================
VAR _Data = [_Data Referência]
RETURN
    IF (
        NOT ISBLANK ( _Data ),
        CALCULATE (
            [_Valor Bruto],
            REMOVEFILTERS ( dCalendario ),
            dCalendario[Data] = _Data
        )
    )
```

### IPCA Mensal %

*Variação mensal do IPCA no mês de referência.* · formato: `0.00%`

```dax
IPCA Mensal % =
-- =============================================================
-- IPCA Mensal %
-- Objetivo : variação mensal do IPCA no mês de referência.
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 433 (IPCA).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 433    -- IPCA
)
```

### INPC Mensal %

*Variação mensal do INPC no mês de referência.* · formato: `0.00%`

```dax
INPC Mensal % =
-- =============================================================
-- INPC Mensal %
-- Objetivo : variação mensal do INPC no mês de referência.
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 188 (INPC).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 188    -- INPC
)
```

### IGP-M Mensal %

*Variação mensal do IGP-M no mês de referência.* · formato: `0.00%`

```dax
IGP-M Mensal % =
-- =============================================================
-- IGP-M Mensal %
-- Objetivo : variação mensal do IGP-M no mês de referência.
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 189 (IGP-M).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 189    -- IGP-M
)
```

### IPCA Livres %

*Variação mensal dos preços livres do IPCA.* · formato: `0.00%`

```dax
IPCA Livres % =
-- =============================================================
-- IPCA Livres %
-- Objetivo : variação mensal dos preços livres do IPCA.
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 11428 (IPCA itens livres).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 11428    -- IPCA itens livres
)
```

### IPCA Monitorados %

*Variação mensal dos preços monitorados do IPCA.* · formato: `0.00%`

```dax
IPCA Monitorados % =
-- =============================================================
-- IPCA Monitorados %
-- Objetivo : variação mensal dos preços monitorados do IPCA.
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 4449 (IPCA monitorados).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 4449    -- IPCA monitorados
)
```

### Selic % a.a.

*Selic acumulada no mês, anualizada (% a.a.).* · formato: `0.00%`

```dax
Selic % a.a. =
-- =============================================================
-- Selic % a.a.
-- Objetivo : Selic acumulada no mês, anualizada (% a.a.).
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 4189 (Selic anualizada).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 4189    -- Selic anualizada
)
```

### Selic Mensal %

*Selic efetiva do mês (% a.m.), base do Selic 12M.* · formato: `0.00%`

```dax
Selic Mensal % =
-- =============================================================
-- Selic Mensal %
-- Objetivo : Selic efetiva do mês (% a.m.), base do Selic 12M.
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 4390 (Selic % a.m.).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 4390    -- Selic % a.m.
)
```

### Último Mês Disponível

*Último mês com IPCA publicado (flag da dCalendario).* · formato: `mmm/yyyy`

```dax
Último Mês Disponível =
-- =============================================================
-- Último Mês Disponível
-- Objetivo : último mês com IPCA publicado, independente dos filtros de período.
-- Regra    : lê a flag EhUltimoMesDisponivel, calculada no Power Query.
-- =============================================================
CALCULATE (
    MAX ( dCalendario[Data] ),
    REMOVEFILTERS ( dCalendario ),
    dCalendario[EhUltimoMesDisponivel] = TRUE ()
)
```


## 02 Acumulados

### Indicador Acum. Ano %

*Acumulado no ano (composto) do indicador em contexto até o mês de referência.* · formato: `0.00%`

```dax
Indicador Acum. Ano % =
-- =============================================================
-- Indicador Acum. Ano %
-- Objetivo : inflação acumulada de janeiro até o mês de referência.
-- Regra    : produto (1 + variação mensal) - 1 — composto, NUNCA somado.
--            REMOVEFILTERS(dCalendario) garante o período correto mesmo com
--            filtros de Mês/Trimestre vindos do visual.
-- =============================================================
VAR _DataFim    = [_Data Referência]
VAR _DataInicio = DATE ( YEAR ( _DataFim ), 1, 1 )
VAR _Fator      =
    CALCULATE (
        PRODUCTX (
            VALUES ( dCalendario[Data] ),
            1 + [_Valor Bruto]
        ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] >= _DataInicio,
        dCalendario[Data] <= _DataFim
    )
RETURN
    IF ( NOT ISBLANK ( _DataFim ) && [_Indicador Composto], _Fator - 1 )
```

### Indicador 12M %

*Acumulado em 12 meses (composto) do indicador em contexto.* · formato: `0.00%`

```dax
Indicador 12M % =
-- =============================================================
-- Indicador 12M %
-- Objetivo : inflação acumulada nos 12 meses até o mês de referência.
-- Regra    : produto (1 + variação mensal) - 1, composto mês a mês.
--            Retorna BLANK se não houver 12 meses completos (evita valor enganoso).
-- Nota     : no exemplo do enunciado, NOT ISBLANK([medida]) era usado como filtro
--            do CALCULATE — isso não é permitido; aqui a contagem usa FILTER.
-- =============================================================
VAR _DataFim    = [_Data Referência]
VAR _DataInicio = EDATE ( _DataFim, -11 )
VAR _QtdMeses   =
    CALCULATE (
        COUNTROWS (
            FILTER (
                VALUES ( dCalendario[Data] ),
                NOT ISBLANK ( [_Valor Bruto] )
            )
        ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] >= _DataInicio,
        dCalendario[Data] <= _DataFim
    )
VAR _Fator      =
    CALCULATE (
        PRODUCTX (
            VALUES ( dCalendario[Data] ),
            1 + [_Valor Bruto]
        ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] >= _DataInicio,
        dCalendario[Data] <= _DataFim
    )
RETURN
    IF ( _QtdMeses = 12 && [_Indicador Composto], _Fator - 1 )
```

### Indicador Acum. Período %

*Acumulado (composto) dos meses selecionados nos filtros.* · formato: `0.00%`

```dax
Indicador Acum. Período % =
-- =============================================================
-- Indicador Acum. Período %
-- Objetivo : inflação acumulada exatamente no período filtrado (ex.: mar/23 a ago/25).
-- Regra    : produto (1 + taxa) - 1 sobre os meses visíveis no contexto.
-- =============================================================
VAR _Ultima = [_Data Referência]
VAR _Fator  =
    PRODUCTX (
        FILTER (
            VALUES ( dCalendario[Data] ),
            dCalendario[Data] <= _Ultima
        ),
        1 + [_Valor Bruto]
    )
RETURN
    IF ( NOT ISBLANK ( _Ultima ) && [_Indicador Composto], _Fator - 1 )
```

### Indicador Número-Índice

*Número-índice base 100 na primeira data do filtro.* · formato: `#,0.0`

```dax
Indicador Número-Índice =
-- =============================================================
-- Indicador Número-Índice
-- Objetivo : evolução de preços em número-índice, base 100 no 1º mês selecionado.
-- Regra    : 100 × produto (1 + taxa) dos meses APÓS a base até o mês do ponto.
--            No mês-base o produto é vazio → COALESCE devolve 100.
-- =============================================================
VAR _DataFim  = [_Data Referência]
VAR _DataBase =
    CALCULATE ( MIN ( dCalendario[Data] ), ALLSELECTED ( dCalendario ) )
VAR _Fator    =
    CALCULATE (
        PRODUCTX (
            VALUES ( dCalendario[Data] ),
            1 + [_Valor Bruto]
        ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] > _DataBase,
        dCalendario[Data] <= _DataFim
    )
RETURN
    IF (
        NOT ISBLANK ( _DataFim ) && [_Indicador Composto],
        100 * COALESCE ( _Fator, 1 )
    )
```

### IPCA Acum. Ano %

*IPCA acumulado no ano (composto).* · formato: `0.00%`

```dax
IPCA Acum. Ano % =
-- =============================================================
-- IPCA Acum. Ano %
-- Objetivo : IPCA acumulado no ano (composto).
-- Regra    : aplica [Indicador Acum. Ano %] fixando a série SGS 433 (IPCA).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Acum. Ano %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 433    -- IPCA
)
```

### IPCA 12M %

*IPCA acumulado em 12 meses (composto).* · formato: `0.00%`

```dax
IPCA 12M % =
-- =============================================================
-- IPCA 12M %
-- Objetivo : IPCA acumulado em 12 meses (composto).
-- Regra    : aplica [Indicador 12M %] fixando a série SGS 433 (IPCA).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador 12M %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 433    -- IPCA
)
```

### IPCA Número-Índice

*IPCA em número-índice base 100.* · formato: `#,0.0`

```dax
IPCA Número-Índice =
-- =============================================================
-- IPCA Número-Índice
-- Objetivo : IPCA em número-índice base 100.
-- Regra    : aplica [Indicador Número-Índice] fixando a série SGS 433 (IPCA).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Número-Índice],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 433    -- IPCA
)
```

### INPC Acum. Ano %

*INPC acumulado no ano (composto).* · formato: `0.00%`

```dax
INPC Acum. Ano % =
-- =============================================================
-- INPC Acum. Ano %
-- Objetivo : INPC acumulado no ano (composto).
-- Regra    : aplica [Indicador Acum. Ano %] fixando a série SGS 188 (INPC).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Acum. Ano %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 188    -- INPC
)
```

### INPC 12M %

*INPC acumulado em 12 meses (composto).* · formato: `0.00%`

```dax
INPC 12M % =
-- =============================================================
-- INPC 12M %
-- Objetivo : INPC acumulado em 12 meses (composto).
-- Regra    : aplica [Indicador 12M %] fixando a série SGS 188 (INPC).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador 12M %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 188    -- INPC
)
```

### INPC Número-Índice

*INPC em número-índice base 100.* · formato: `#,0.0`

```dax
INPC Número-Índice =
-- =============================================================
-- INPC Número-Índice
-- Objetivo : INPC em número-índice base 100.
-- Regra    : aplica [Indicador Número-Índice] fixando a série SGS 188 (INPC).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Número-Índice],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 188    -- INPC
)
```

### IGP-M Acum. Ano %

*IGP-M acumulado no ano (composto).* · formato: `0.00%`

```dax
IGP-M Acum. Ano % =
-- =============================================================
-- IGP-M Acum. Ano %
-- Objetivo : IGP-M acumulado no ano (composto).
-- Regra    : aplica [Indicador Acum. Ano %] fixando a série SGS 189 (IGP-M).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Acum. Ano %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 189    -- IGP-M
)
```

### IGP-M 12M %

*IGP-M acumulado em 12 meses (composto).* · formato: `0.00%`

```dax
IGP-M 12M % =
-- =============================================================
-- IGP-M 12M %
-- Objetivo : IGP-M acumulado em 12 meses (composto).
-- Regra    : aplica [Indicador 12M %] fixando a série SGS 189 (IGP-M).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador 12M %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 189    -- IGP-M
)
```

### IGP-M Número-Índice

*IGP-M em número-índice base 100.* · formato: `#,0.0`

```dax
IGP-M Número-Índice =
-- =============================================================
-- IGP-M Número-Índice
-- Objetivo : IGP-M em número-índice base 100.
-- Regra    : aplica [Indicador Número-Índice] fixando a série SGS 189 (IGP-M).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Número-Índice],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 189    -- IGP-M
)
```

### IPCA Acum. Período Selecionado %

*IPCA acumulado no período filtrado.* · formato: `0.00%`

```dax
IPCA Acum. Período Selecionado % =
-- =============================================================
-- IPCA Acum. Período Selecionado %
-- Objetivo : IPCA acumulado no período filtrado.
-- Regra    : aplica [Indicador Acum. Período %] fixando a série SGS 433 (IPCA).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Acum. Período %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 433    -- IPCA
)
```

### IPCA Livres 12M %

*Preços livres acumulados em 12 meses.* · formato: `0.00%`

```dax
IPCA Livres 12M % =
-- =============================================================
-- IPCA Livres 12M %
-- Objetivo : preços livres acumulados em 12 meses.
-- Regra    : aplica [Indicador 12M %] fixando a série SGS 11428 (Livres).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador 12M %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 11428    -- Livres
)
```

### IPCA Monitorados 12M %

*Preços monitorados acumulados em 12 meses.* · formato: `0.00%`

```dax
IPCA Monitorados 12M % =
-- =============================================================
-- IPCA Monitorados 12M %
-- Objetivo : preços monitorados acumulados em 12 meses.
-- Regra    : aplica [Indicador 12M %] fixando a série SGS 4449 (Monitorados).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador 12M %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 4449    -- Monitorados
)
```

### Selic 12M %

*Selic efetiva acumulada em 12 meses (composta a partir da 4390).* · formato: `0.00%`

```dax
Selic 12M % =
-- =============================================================
-- Selic 12M %
-- Objetivo : Selic efetiva acumulada em 12 meses (composta a partir da 4390).
-- Regra    : aplica [Indicador 12M %] fixando a série SGS 4390 (Selic % a.m.).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador 12M %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 4390    -- Selic % a.m.
)
```

### IPCA 12M % (SGS 13522)

*IPCA 12M oficial publicado no SGS (conferência).* · formato: `0.00%`

```dax
IPCA 12M % (SGS 13522) =
-- =============================================================
-- IPCA 12M % (SGS 13522)
-- Objetivo : IPCA 12M oficial publicado no SGS (conferência).
-- Regra    : aplica [Indicador Mensal %] fixando a série SGS 13522 (IPCA 12M oficial).
--            A lógica fica na medida genérica (uma única fonte de verdade).
-- =============================================================
CALCULATE (
    [Indicador Mensal %],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 13522    -- IPCA 12M oficial
)
```


## 03 Meta

### Meta Ano %

*Meta de inflação do CMN para o ano do mês de referência.* · formato: `0.00%`

```dax
Meta Ano % =
-- =============================================================
-- Meta Ano %
-- Objetivo : meta de inflação do CMN para o ano do mês de referência.
-- Regra    : dMeta é desconectada (ver README); o ano vem do mês de referência
--            do IPCA, então funciona em eixos mensais, anuais e em cartões.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
VAR _Ano  = YEAR ( _Data )
RETURN
    IF (
        NOT ISBLANK ( _Data ),
        CALCULATE ( MAX ( dMeta[Meta] ), dMeta[Ano] = _Ano )
    )
```

### Limite Inferior %

*Piso do intervalo de tolerância da meta.* · formato: `0.00%`

```dax
Limite Inferior % =
-- =============================================================
-- Limite Inferior %
-- Objetivo : piso do intervalo de tolerância da meta.
-- Regra    : dMeta é desconectada (ver README); o ano vem do mês de referência
--            do IPCA, então funciona em eixos mensais, anuais e em cartões.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
VAR _Ano  = YEAR ( _Data )
RETURN
    IF (
        NOT ISBLANK ( _Data ),
        CALCULATE ( MAX ( dMeta[LimiteInferior] ), dMeta[Ano] = _Ano )
    )
```

### Limite Superior %

*Teto do intervalo de tolerância da meta.* · formato: `0.00%`

```dax
Limite Superior % =
-- =============================================================
-- Limite Superior %
-- Objetivo : teto do intervalo de tolerância da meta.
-- Regra    : dMeta é desconectada (ver README); o ano vem do mês de referência
--            do IPCA, então funciona em eixos mensais, anuais e em cartões.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
VAR _Ano  = YEAR ( _Data )
RETURN
    IF (
        NOT ISBLANK ( _Data ),
        CALCULATE ( MAX ( dMeta[LimiteSuperior] ), dMeta[Ano] = _Ano )
    )
```

### Desvio vs Meta (p.p.)

*IPCA 12M menos a meta, em pontos percentuais.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Desvio vs Meta (p.p.) =
-- =============================================================
-- Desvio vs Meta (p.p.)
-- Objetivo : distância do IPCA 12M para o centro da meta.
-- Regra    : (IPCA 12M - Meta) × 100 → resultado já em p.p. (ex.: 1,24).
--            Desde 2025 a meta é contínua e apurada em 12 meses.
-- =============================================================
VAR _IPCA = [IPCA 12M %]
VAR _Meta = [Meta Ano %]
RETURN
    IF ( NOT ISBLANK ( _IPCA ) && NOT ISBLANK ( _Meta ), ( _IPCA - _Meta ) * 100 )
```

### Desvio vs Teto (p.p.)

*IPCA 12M menos o teto da meta, em p.p.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Desvio vs Teto (p.p.) =
-- =============================================================
-- Desvio vs Teto (p.p.)
-- Objetivo : IPCA 12M menos o teto da meta, em p.p.
-- =============================================================
VAR _IPCA = [IPCA 12M %]
VAR _Teto = [Limite Superior %]
RETURN
    IF ( NOT ISBLANK ( _IPCA ) && NOT ISBLANK ( _Teto ), ( _IPCA - _Teto ) * 100 )
```

### Status Meta

*Dentro / Acima do teto / Abaixo do piso, com base no IPCA 12M.* · formato: `texto/HTML`

```dax
Status Meta =
-- =============================================================
-- Status Meta
-- Objetivo : Dentro / Acima do teto / Abaixo do piso, com base no IPCA 12M.
-- =============================================================
VAR _IPCA = [IPCA 12M %]
VAR _Piso = [Limite Inferior %]
VAR _Teto = [Limite Superior %]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _IPCA ) || ISBLANK ( _Teto ), BLANK (),
        _IPCA > _Teto, "Acima do teto",
        _IPCA < _Piso, "Abaixo do piso",
        "Dentro"
    )
```

### Meses Consecutivos Acima do Teto

*Sequência atual de meses com IPCA 12M acima do teto.* · formato: `0`

```dax
Meses Consecutivos Acima do Teto =
-- =============================================================
-- Meses Consecutivos Acima do Teto
-- Objetivo : há quantos meses seguidos o IPCA 12M está acima do teto.
-- Regra    : acha o último mês que NÃO estava acima do teto e conta os meses
--            posteriores até o mês de referência. 0 = hoje está dentro/abaixo.
--            Custo controlado: ~180 meses, só em cartão/tooltip.
-- =============================================================
VAR _Ref    = [_Data Referência IPCA]
VAR _Tabela =
    CALCULATETABLE (
        ADDCOLUMNS (
            VALUES ( dCalendario[Data] ),
            "@Acima", [IPCA 12M %] > [Limite Superior %]
        ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] <= _Ref
    )
VAR _UltimoMesDentro =
    MAXX ( FILTER ( _Tabela, NOT [@Acima] ), dCalendario[Data] )
VAR _Qtd    =
    COUNTROWS ( FILTER ( _Tabela, dCalendario[Data] > _UltimoMesDentro ) )
RETURN
    IF ( NOT ISBLANK ( _Ref ), _Qtd + 0 )
```

### Acima do Teto no Ano (p.p.)

*Quanto o IPCA acumulado do ano superou o teto (anos que estouraram).* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Acima do Teto no Ano (p.p.) =
-- =============================================================
-- Acima do Teto no Ano (p.p.)
-- Objetivo : rótulo/realce do gráfico Realizado × Meta por ano.
-- Regra    : IPCA acumulado no ano - teto; BLANK quando não estourou.
-- =============================================================
VAR _Realizado = [IPCA Acum. Ano %]
VAR _Teto      = [Limite Superior %]
VAR _Excesso   = ( _Realizado - _Teto ) * 100
RETURN
    IF ( _Excesso > 0, _Excesso )
```


## 04 Composição

### Variação Grupo Mensal %

*Variação mensal do grupo do IPCA.* · formato: `0.00%`

```dax
Variação Grupo Mensal % =
-- =============================================================
-- Variação Grupo Mensal %
-- Objetivo : variação mensal do grupo do IPCA.
-- Regra    : exige um único grupo (somar variações/pesos de grupos não faz sentido).
-- =============================================================
VAR _Data = [_Data Referência Grupos]
RETURN
    IF (
        HASONEVALUE ( dGrupoIPCA[CodigoGrupo] ) && NOT ISBLANK ( _Data ),
        CALCULATE (
            SUM ( fIPCAGrupos[VariacaoMensal] ),
            REMOVEFILTERS ( dCalendario ),
            dCalendario[Data] = _Data
        )
    )
```

### Peso Grupo %

*Peso do grupo no IPCA do mês.* · formato: `0.00%`

```dax
Peso Grupo % =
-- =============================================================
-- Peso Grupo %
-- Objetivo : peso do grupo no IPCA do mês.
-- Regra    : exige um único grupo (somar variações/pesos de grupos não faz sentido).
-- =============================================================
VAR _Data = [_Data Referência Grupos]
RETURN
    IF (
        HASONEVALUE ( dGrupoIPCA[CodigoGrupo] ) && NOT ISBLANK ( _Data ),
        CALCULATE (
            SUM ( fIPCAGrupos[Peso] ),
            REMOVEFILTERS ( dCalendario ),
            dCalendario[Data] = _Data
        )
    )
```

### Contribuição Grupo (p.p.)

*Contribuição do grupo para o IPCA do mês: Σ(variação × peso), em p.p.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Contribuição Grupo (p.p.) =
-- =============================================================
-- Contribuição Grupo (p.p.)
-- Objetivo : quantos p.p. do IPCA do mês vieram de cada grupo.
-- Regra    : Σ (variação mensal × peso) no mês de referência, × 100.
--            Somada nos 9 grupos ≈ IPCA do mês (diferença só de arredondamento).
--            SUMX itera ~9 linhas (mês filtrado): custo desprezível.
-- =============================================================
VAR _Data    = [_Data Referência Grupos]
VAR _Contrib =
    CALCULATE (
        SUMX ( fIPCAGrupos, fIPCAGrupos[VariacaoMensal] * fIPCAGrupos[Peso] ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = _Data
    )
RETURN
    IF ( NOT ISBLANK ( _Data ), _Contrib * 100 )
```

### Contribuição Total (p.p.)

*Soma das contribuições dos 9 grupos (≈ IPCA do mês).* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Contribuição Total (p.p.) =
-- =============================================================
-- Contribuição Total (p.p.)
-- Objetivo : soma das contribuições dos 9 grupos (≈ IPCA do mês).
-- =============================================================
CALCULATE (
    [Contribuição Grupo (p.p.)],
    REMOVEFILTERS ( dGrupoIPCA )
)
```

### Participação na Inflação %

*Fatia do IPCA do mês explicada pelo grupo.* · formato: `0.0%`

```dax
Participação na Inflação % =
-- =============================================================
-- Participação na Inflação %
-- Objetivo : participação do grupo na inflação do mês.
-- Regra    : contribuição do grupo ÷ contribuição total (pode ser negativa).
-- =============================================================
DIVIDE (
    [Contribuição Grupo (p.p.)],
    [Contribuição Total (p.p.)]
)
```

### Ranking Grupo por Contribuição

*Posição do grupo (1 = maior pressão de alta).* · formato: `0`

```dax
Ranking Grupo por Contribuição =
-- =============================================================
-- Ranking Grupo por Contribuição
-- Objetivo : ranking dos grupos pela contribuição no mês.
-- Regra    : ALL(dGrupoIPCA) (tabela inteira) evita o problema de 'ordenar por
--            coluna' (Grupo ordenado por Ordem), que quebraria o RANKX.
-- =============================================================
IF (
    HASONEVALUE ( dGrupoIPCA[CodigoGrupo] ),
    RANKX (
        ALL ( dGrupoIPCA ),
        [Contribuição Grupo (p.p.)],
        ,
        DESC,
        DENSE
    )
)
```

### Grupo de Maior Pressão

*Nome do grupo com a maior contribuição no mês.* · formato: `texto/HTML`

```dax
Grupo de Maior Pressão =
-- =============================================================
-- Grupo de Maior Pressão
-- Objetivo : nome do grupo com a maior contribuição no mês.
-- =============================================================
VAR _Top =
    TOPN ( 1, ALL ( dGrupoIPCA ), [Contribuição Grupo (p.p.)], DESC )
RETURN
    MAXX ( _Top, dGrupoIPCA[Grupo] )
```

### Contribuição do Grupo de Maior Pressão (p.p.)

*Contribuição (p.p.) do grupo líder.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Contribuição do Grupo de Maior Pressão (p.p.) =
-- =============================================================
-- Contribuição do Grupo de Maior Pressão (p.p.)
-- Objetivo : contribuição (p.p.) do grupo líder.
-- =============================================================
VAR _Top =
    TOPN ( 1, ALL ( dGrupoIPCA ), [Contribuição Grupo (p.p.)], DESC )
RETURN
    MAXX ( _Top, [Contribuição Grupo (p.p.)] )
```


## 05 Comparativos

### Variação vs Mês Anterior (p.p.)

*IPCA mensal menos o IPCA do mês anterior, em p.p.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Variação vs Mês Anterior (p.p.) =
-- =============================================================
-- Variação vs Mês Anterior (p.p.)
-- Objetivo : IPCA mensal menos o IPCA do mês anterior, em p.p.
-- =============================================================
VAR _Data     = [_Data Referência IPCA]
VAR _Atual    = [IPCA Mensal %]
VAR _Anterior =
    CALCULATE (
        [IPCA Mensal %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = EDATE ( _Data, -1 )
    )
RETURN
    IF ( NOT ISBLANK ( _Atual ) && NOT ISBLANK ( _Anterior ), ( _Atual - _Anterior ) * 100 )
```

### IPCA Mensal Mês Anterior %

*IPCA do mês anterior ao de referência.* · formato: `0.00%`

```dax
IPCA Mensal Mês Anterior % =
-- =============================================================
-- IPCA Mensal Mês Anterior %
-- Objetivo : IPCA do mês anterior ao de referência.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
RETURN
    CALCULATE (
        [IPCA Mensal %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = EDATE ( _Data, -1 )
    )
```

### IPCA 12M Mês Anterior %

*IPCA 12M no mês anterior ao de referência.* · formato: `0.00%`

```dax
IPCA 12M Mês Anterior % =
-- =============================================================
-- IPCA 12M Mês Anterior %
-- Objetivo : IPCA 12M no mês anterior ao de referência.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
RETURN
    CALCULATE (
        [IPCA 12M %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = EDATE ( _Data, -1 )
    )
```

### Δ 12M vs Mês Anterior (p.p.)

*Variação do IPCA 12M contra o mês anterior, em p.p.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Δ 12M vs Mês Anterior (p.p.) =
-- =============================================================
-- Δ 12M vs Mês Anterior (p.p.)
-- Objetivo : variação do IPCA 12M contra o mês anterior, em p.p.
-- =============================================================
VAR _Atual    = [IPCA 12M %]
VAR _Anterior = [IPCA 12M Mês Anterior %]
RETURN
    IF ( NOT ISBLANK ( _Atual ) && NOT ISBLANK ( _Anterior ), ( _Atual - _Anterior ) * 100 )
```

### IPCA 12M Mesmo Mês Ano Anterior

*IPCA 12M no mesmo mês do ano anterior.* · formato: `0.00%`

```dax
IPCA 12M Mesmo Mês Ano Anterior =
-- =============================================================
-- IPCA 12M Mesmo Mês Ano Anterior
-- Objetivo : IPCA 12M no mesmo mês do ano anterior.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
RETURN
    CALCULATE (
        [IPCA 12M %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = EDATE ( _Data, -12 )
    )
```

### Δ 12M vs Ano Anterior (p.p.)

*IPCA 12M atual menos o de 12 meses antes, em p.p.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Δ 12M vs Ano Anterior (p.p.) =
-- =============================================================
-- Δ 12M vs Ano Anterior (p.p.)
-- Objetivo : IPCA 12M atual menos o de 12 meses antes, em p.p.
-- =============================================================
VAR _Atual    = [IPCA 12M %]
VAR _Anterior = [IPCA 12M Mesmo Mês Ano Anterior]
RETURN
    IF ( NOT ISBLANK ( _Atual ) && NOT ISBLANK ( _Anterior ), ( _Atual - _Anterior ) * 100 )
```

### IPCA Acum. Ano Mesmo Período Ano Anterior %

*Acumulado no ano até o mesmo mês do ano anterior.* · formato: `0.00%`

```dax
IPCA Acum. Ano Mesmo Período Ano Anterior % =
-- =============================================================
-- IPCA Acum. Ano Mesmo Período Ano Anterior %
-- Objetivo : acumulado no ano até o mesmo mês do ano anterior.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
RETURN
    CALCULATE (
        [IPCA Acum. Ano %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = EDATE ( _Data, -12 )
    )
```

### Δ Acum. Ano vs Ano Anterior (p.p.)

*Acumulado do ano menos o mesmo período do ano anterior.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Δ Acum. Ano vs Ano Anterior (p.p.) =
-- =============================================================
-- Δ Acum. Ano vs Ano Anterior (p.p.)
-- Objetivo : acumulado do ano menos o mesmo período do ano anterior.
-- =============================================================
VAR _Atual    = [IPCA Acum. Ano %]
VAR _Anterior = [IPCA Acum. Ano Mesmo Período Ano Anterior %]
RETURN
    IF ( NOT ISBLANK ( _Atual ) && NOT ISBLANK ( _Anterior ), ( _Atual - _Anterior ) * 100 )
```

### Spread IPCA − IGP-M (p.p.)

*IPCA 12M menos IGP-M 12M, alinhados no mês do IPCA.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Spread IPCA − IGP-M (p.p.) =
-- =============================================================
-- Spread IPCA − IGP-M (p.p.)
-- Objetivo : diferença entre inflação ao consumidor (IPCA) e IGP-M (atacado/aluguéis).
-- Regra    : ambos em 12M, com o IGP-M lido NO MÊS DO IPCA (o IGP-M sai antes
--            e teria um mês a mais; sem alinhar, o spread misturaria meses).
-- =============================================================
VAR _Data = [_Data Referência IPCA]
VAR _IPCA = [IPCA 12M %]
VAR _IGPM =
    CALCULATE (
        [IGP-M 12M %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = _Data
    )
RETURN
    IF ( NOT ISBLANK ( _IPCA ) && NOT ISBLANK ( _IGPM ), ( _IPCA - _IGPM ) * 100 )
```

### Spread IPCA − INPC (p.p.)

*IPCA 12M menos INPC 12M, em p.p.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Spread IPCA − INPC (p.p.) =
-- =============================================================
-- Spread IPCA − INPC (p.p.)
-- Objetivo : IPCA 12M menos INPC 12M, em p.p.
-- =============================================================
VAR _Data = [_Data Referência IPCA]
VAR _IPCA = [IPCA 12M %]
VAR _INPC =
    CALCULATE (
        [INPC 12M %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = _Data
    )
RETURN
    IF ( NOT ISBLANK ( _IPCA ) && NOT ISBLANK ( _INPC ), ( _IPCA - _INPC ) * 100 )
```

### Difusão de Alta %

*% dos 9 grupos do IPCA com variação positiva no mês.* · formato: `0.0%`

```dax
Difusão de Alta % =
-- =============================================================
-- Difusão de Alta %
-- Objetivo : quão espalhada está a alta de preços entre os grupos.
-- Regra    : grupos com variação > 0 ÷ grupos com dado. Atenção: é a difusão por
--            GRUPO (9 itens), não o índice oficial de difusão por subitens do BCB.
-- =============================================================
VAR _Tabela =
    ADDCOLUMNS (
        ALL ( dGrupoIPCA ),
        "@Var", [Variação Grupo Mensal %]
    )
VAR _ComDado = COUNTROWS ( FILTER ( _Tabela, NOT ISBLANK ( [@Var] ) ) )
VAR _EmAlta  = COUNTROWS ( FILTER ( _Tabela, [@Var] > 0 ) )
RETURN
    DIVIDE ( _EmAlta, _ComDado )
```


## 06 Expectativas e Juros

### Focus Mediana Ano Corrente

*Mediana Focus do IPCA para o ano da coleta (última coleta do mês).* · formato: `0.00%`

```dax
Focus Mediana Ano Corrente =
-- =============================================================
-- Focus Mediana Ano Corrente
-- Objetivo : expectativa de mercado para o IPCA do próprio ano da coleta.
-- Regra    : fExpectativas guarda 1 linha por mês de coleta × ano de referência
--            (a última coleta de cada mês), então MAX apenas lê o valor.
-- =============================================================
VAR _Coleta = [_Data Referência Focus]
RETURN
    IF (
        NOT ISBLANK ( _Coleta ),
        CALCULATE (
            MAX ( fExpectativas[Mediana] ),
            REMOVEFILTERS ( dCalendario ),
            dCalendario[Data] = _Coleta,
            fExpectativas[AnoReferencia] = YEAR ( _Coleta )
        )
    )
```

### Focus Mediana Próximo Ano

*Mediana Focus do IPCA para o ano seguinte ao da coleta.* · formato: `0.00%`

```dax
Focus Mediana Próximo Ano =
-- =============================================================
-- Focus Mediana Próximo Ano
-- Objetivo : mediana Focus do IPCA para o ano seguinte ao da coleta.
-- =============================================================
VAR _Coleta = [_Data Referência Focus]
RETURN
    IF (
        NOT ISBLANK ( _Coleta ),
        CALCULATE (
            MAX ( fExpectativas[Mediana] ),
            REMOVEFILTERS ( dCalendario ),
            dCalendario[Data] = _Coleta,
            fExpectativas[AnoReferencia] = YEAR ( _Coleta ) + 1
        )
    )
```

### Focus Mediana Início do Ano

*O que o mercado esperava em janeiro para o IPCA do ano.* · formato: `0.00%`

```dax
Focus Mediana Início do Ano =
-- =============================================================
-- Focus Mediana Início do Ano
-- Objetivo : o que o mercado esperava em janeiro para o IPCA do ano.
-- =============================================================
VAR _Ano = YEAR ( [_Data Referência IPCA] )
RETURN
    CALCULATE (
        MAX ( fExpectativas[Mediana] ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = DATE ( _Ano, 1, 1 ),
        fExpectativas[AnoReferencia] = _Ano
    )
```

### Focus vs Realizado (p.p.)

*IPCA realizado no ano menos a expectativa Focus de janeiro (anos fechados).* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Focus vs Realizado (p.p.) =
-- =============================================================
-- Focus vs Realizado (p.p.)
-- Objetivo : erro de previsão do mercado (positivo = inflação surpreendeu para cima).
-- Regra    : IPCA de jan–dez menos a mediana Focus coletada em janeiro do ano.
--            Só para anos fechados (dezembro publicado), para não comparar YTD com ano cheio.
-- =============================================================
VAR _Data      = [_Data Referência IPCA]
VAR _AnoFechado = MONTH ( _Data ) = 12
VAR _Realizado = [IPCA Acum. Ano %]
VAR _Esperado  = [Focus Mediana Início do Ano]
RETURN
    IF (
        _AnoFechado && NOT ISBLANK ( _Esperado ),
        ( _Realizado - _Esperado ) * 100
    )
```

### Juro Real Ex-Post %

*(1 + Selic 12M) / (1 + IPCA 12M) - 1, no mês do IPCA.* · formato: `0.00%`

```dax
Juro Real Ex-Post % =
-- =============================================================
-- Juro Real Ex-Post %
-- Objetivo : juro real efetivamente obtido nos últimos 12 meses.
-- Regra    : equação de Fisher (1 + Selic 12M) / (1 + IPCA 12M) - 1.
--            Selic 12M = composição da Selic mensal (SGS 4390), alinhada no mês do IPCA.
-- =============================================================
VAR _Data  = [_Data Referência IPCA]
VAR _IPCA  = [IPCA 12M %]
VAR _Selic =
    CALCULATE (
        [Selic 12M %],
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] = _Data
    )
RETURN
    IF (
        NOT ISBLANK ( _IPCA ) && NOT ISBLANK ( _Selic ),
        DIVIDE ( 1 + _Selic, 1 + _IPCA ) - 1
    )
```


## 07 Textos e HTML

### Texto Dados Até

*'Dados até: mmm/aaaa' para o cabeçalho de todas as páginas.* · formato: `texto/HTML`

```dax
Texto Dados Até =
-- =============================================================
-- Texto Dados Até
-- Objetivo : 'Dados até: mmm/aaaa' para o cabeçalho de todas as páginas.
-- =============================================================
VAR _Data = [Último Mês Disponível]
RETURN
    "Dados até: " & FORMAT ( _Data, "mmm/yyyy" )
```

### Texto Mês de Referência

*Mês de referência por extenso (ex.: setembro de 2026).* · formato: `texto/HTML`

```dax
Texto Mês de Referência =
-- =============================================================
-- Texto Mês de Referência
-- Objetivo : mês de referência por extenso (ex.: setembro de 2026).
-- =============================================================
VAR _Data = [_Data Referência IPCA]
RETURN
    IF ( NOT ISBLANK ( _Data ), FORMAT ( _Data, "mmmm" ) & " de " & YEAR ( _Data ) )
```

### Título Visão Geral

*Título dinâmico da página Visão Geral.* · formato: `texto/HTML`

```dax
Título Visão Geral =
-- =============================================================
-- Título Visão Geral
-- Objetivo : título dinâmico da página Visão Geral.
-- =============================================================
VAR _Mes = [Texto Mês de Referência]
RETURN
    "Inflação no Brasil" & IF ( NOT ISBLANK ( _Mes ), " · " & _Mes )
```

### Título Composição

*Título dinâmico da página Composição.* · formato: `texto/HTML`

```dax
Título Composição =
-- =============================================================
-- Título Composição
-- Objetivo : título dinâmico da página Composição.
-- =============================================================
VAR _Mes = [Texto Mês de Referência]
RETURN
    "Composição do IPCA" & IF ( NOT ISBLANK ( _Mes ), " · " & _Mes )
```

### Título Comparativos

*Título dinâmico da página Comparativos.* · formato: `texto/HTML`

```dax
Título Comparativos =
-- =============================================================
-- Título Comparativos
-- Objetivo : título dinâmico da página Comparativos.
-- =============================================================
VAR _Mes = [Texto Mês de Referência]
RETURN
    "IPCA, INPC e IGP-M" & IF ( NOT ISBLANK ( _Mes ), " · " & _Mes )
```

### Título Expectativas

*Título dinâmico da página Expectativas.* · formato: `texto/HTML`

```dax
Título Expectativas =
-- =============================================================
-- Título Expectativas
-- Objetivo : título dinâmico da página Expectativas.
-- =============================================================
VAR _Mes = [Texto Mês de Referência]
RETURN
    "Expectativas e juros" & IF ( NOT ISBLANK ( _Mes ), " · " & _Mes )
```

### Título Metodologia

*Título dinâmico da página Metodologia.* · formato: `texto/HTML`

```dax
Título Metodologia =
-- =============================================================
-- Título Metodologia
-- Objetivo : título dinâmico da página Metodologia.
-- =============================================================
VAR _Mes = [Texto Mês de Referência]
RETURN
    "Metodologia e fontes" & IF ( NOT ISBLANK ( _Mes ), " · " & _Mes )
```

### Subtítulo Meta

*Frase narrativa da posição do IPCA 12M em relação à meta.* · formato: `texto/HTML`

```dax
Subtítulo Meta =
-- =============================================================
-- Subtítulo Meta
-- Objetivo : subtítulo narrativo (ex.: 'A inflação acumulada em 12 meses está
--            1,24 p.p. acima do teto da meta.').
-- Regra    : FORMAT respeita a cultura pt-BR do modelo (vírgula decimal).
-- =============================================================
VAR _IPCA = [IPCA 12M %]
VAR _Piso = [Limite Inferior %]
VAR _Teto = [Limite Superior %]
VAR _Txt  = "A inflação acumulada em 12 meses está "
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _IPCA ), "Sem 12 meses completos no período selecionado.",
        _IPCA > _Teto,
            _Txt & FORMAT ( ( _IPCA - _Teto ) * 100, "0.00" ) & " p.p. acima do teto da meta.",
        _IPCA < _Piso,
            _Txt & FORMAT ( ( _Piso - _IPCA ) * 100, "0.00" ) & " p.p. abaixo do piso da meta.",
        _Txt & "dentro do intervalo de tolerância, "
            & FORMAT ( ( _Teto - _IPCA ) * 100, "0.00" ) & " p.p. abaixo do teto."
    )
```

### Subtítulo Composição

*Frase sobre o grupo de maior pressão no mês.* · formato: `texto/HTML`

```dax
Subtítulo Composição =
-- =============================================================
-- Subtítulo Composição
-- Objetivo : frase sobre o grupo de maior pressão no mês.
-- =============================================================
VAR _Grupo   = [Grupo de Maior Pressão]
VAR _Contrib = [Contribuição do Grupo de Maior Pressão (p.p.)]
VAR _Difusao = [Difusão de Alta %]
RETURN
    IF (
        NOT ISBLANK ( _Grupo ),
        _Grupo & " foi o grupo de maior pressão, com "
            & FORMAT ( _Contrib, "0.00" ) & " p.p.; "
            & FORMAT ( _Difusao, "0%" ) & " dos grupos tiveram alta."
    )
```

### Subtítulo Juro Real

*Frase sobre o juro real ex-post.* · formato: `texto/HTML`

```dax
Subtítulo Juro Real =
-- =============================================================
-- Subtítulo Juro Real
-- Objetivo : frase sobre o juro real ex-post.
-- =============================================================
VAR _Juro = [Juro Real Ex-Post %]
RETURN
    IF (
        NOT ISBLANK ( _Juro ),
        "O juro real ex-post em 12 meses é de " & FORMAT ( _Juro, "0.00%" )
            & IF ( _Juro >= 0.05, " — política monetária contracionista.", "." )
    )
```

### Última Carga

*Data e hora da última execução do Python (_ControleCarga).* · formato: `texto/HTML`

```dax
Última Carga =
-- =============================================================
-- Última Carga
-- Objetivo : data e hora da última execução do Python (_ControleCarga).
-- =============================================================
VAR _Carga = MAX ( _ControleCarga[DataHoraCarga] )
RETURN
    "Última carga: " & FORMAT ( _Carga, "dd/mm/yyyy hh:nn" )
```

### HTML Card IPCA Mês

*Cartão KPI do IPCA mensal.* · formato: `texto/HTML`

```dax
HTML Card IPCA Mês =
-- =============================================================
-- HTML Card IPCA Mês
-- Objetivo : cartão KPI do IPCA mensal.
-- Badge    : variação em p.p. contra o mês anterior.
--            Semântica de inflação: ALTA = vermelho, QUEDA = verde.
-- Decimais : texto formatado é partido em inteiro/decimal (preserva sinal
--            negativo — TRUNC do exemplo original perdia o '-' em -0,30%).
-- Visual   : HTML Content (AppSource) → campo 'Values' = esta medida.
-- =============================================================
VAR _Valor    = [IPCA Mensal %]
VAR _Delta    = [Variação vs Mês Anterior (p.p.)]
VAR _Texto    = FORMAT ( _Valor * 100, "0.00" )                 -- ex.: "4,52" / "-0,30"
VAR _Inteiro  = LEFT ( _Texto, LEN ( _Texto ) - 3 )                -- "4"   (preserva o sinal)
VAR _Decimal  = RIGHT ( _Texto, 3 )                                -- ",52"
VAR _CorDec   = "#C9C9D3"                                          -- decimais "apagados"
VAR _CorTxt   = SWITCH ( TRUE (), _Delta > 0, "#E5484D", _Delta < 0, "#22A06B", "#8A8AA0" )
VAR _CorFundo = SWITCH ( TRUE (), _Delta > 0, "#FDECEC", _Delta < 0, "#E6F6EE", "#F0F0F5" )
VAR _Seta     = SWITCH ( TRUE (), _Delta > 0, "↑", _Delta < 0, "↓", "→" )
VAR _Badge    =
    IF (
        NOT ISBLANK ( _Delta ),
        "<span style='background:" & _CorFundo & ";color:" & _CorTxt
            & ";padding:3px 8px;border-radius:8px;font-size:12px;font-weight:600;white-space:nowrap;'>"
            & _Seta & " " & FORMAT ( ABS ( _Delta ), "0.00" ) & " p.p.</span>"
    )
VAR _Narrativa = "Mês anterior: <b style='color:#1A1A2E;'>" & FORMAT ( [IPCA Mensal Mês Anterior %], "0.00%" ) & "</b>"
RETURN
    IF (
        ISBLANK ( _Valor ),
        "<div style='font-family:Segoe UI;color:#8A8AA0;padding:16px;'>Sem dados no período</div>",
        "<div style='font-family:Segoe UI,sans-serif;padding:16px 18px;background:#FFFFFF;"
            & "border-radius:16px;display:flex;justify-content:space-between;gap:12px;height:100%;box-sizing:border-box;'>"
        -- coluna esquerda: título, valor, badge e narrativa
        & "<div style='min-width:0;'>"
        & "<div style='font-size:15px;color:#1A1A2E;font-weight:600;'>IPCA do mês</div>"
        & "<div style='font-size:34px;font-weight:700;color:#1A1A2E;margin:6px 0 8px 0;letter-spacing:-0.5px;'>"
            & _Inteiro & "<span style='color:" & _CorDec & ";'>" & _Decimal & "%</span></div>"
        & _Badge
        & "<div style='font-size:12px;color:#8A8AA0;margin-top:10px;line-height:1.35;'>" & _Narrativa & "</div>"
        & "</div>"
        -- coluna direita: mini-indicadores
        & "<div style='display:flex;flex-direction:column;justify-content:flex-end;min-width:118px;'>"
        & "<div style='display:flex;align-items:center;gap:8px;margin-top:10px;'>"
            & "<div style='width:30px;height:30px;border-radius:50%;background:#E9E4FF;color:#7B61FF;"
            & "display:flex;align-items:center;justify-content:center;font-size:14px;'>⇅</div>"
            & "<div style='font-size:12px;line-height:1.25;color:#1A1A2E;font-weight:600;'>"
            & FORMAT ( [IPCA Livres %], "0.00%" ) & "<br><span style='color:#8A8AA0;font-weight:400;'>Livres</span></div></div>"
        & "<div style='display:flex;align-items:center;gap:8px;margin-top:10px;'>"
            & "<div style='width:30px;height:30px;border-radius:50%;background:#E9E4FF;color:#7B61FF;"
            & "display:flex;align-items:center;justify-content:center;font-size:14px;'>⚙</div>"
            & "<div style='font-size:12px;line-height:1.25;color:#1A1A2E;font-weight:600;'>"
            & FORMAT ( [IPCA Monitorados %], "0.00%" ) & "<br><span style='color:#8A8AA0;font-weight:400;'>Monitorados</span></div></div>"
        & "</div></div>"
    )
```

### HTML Card IPCA Acum. Ano

*Cartão KPI do IPCA acumulado no ano.* · formato: `texto/HTML`

```dax
HTML Card IPCA Acum. Ano =
-- =============================================================
-- HTML Card IPCA Acum. Ano
-- Objetivo : cartão KPI do IPCA acumulado no ano.
-- Badge    : acumulado do ano vs o mesmo período do ano anterior.
--            Semântica de inflação: ALTA = vermelho, QUEDA = verde.
-- Decimais : texto formatado é partido em inteiro/decimal (preserva sinal
--            negativo — TRUNC do exemplo original perdia o '-' em -0,30%).
-- Visual   : HTML Content (AppSource) → campo 'Values' = esta medida.
-- =============================================================
VAR _Valor    = [IPCA Acum. Ano %]
VAR _Delta    = [Δ Acum. Ano vs Ano Anterior (p.p.)]
VAR _Texto    = FORMAT ( _Valor * 100, "0.00" )                 -- ex.: "4,52" / "-0,30"
VAR _Inteiro  = LEFT ( _Texto, LEN ( _Texto ) - 3 )                -- "4"   (preserva o sinal)
VAR _Decimal  = RIGHT ( _Texto, 3 )                                -- ",52"
VAR _CorDec   = "#C9C9D3"                                          -- decimais "apagados"
VAR _CorTxt   = SWITCH ( TRUE (), _Delta > 0, "#E5484D", _Delta < 0, "#22A06B", "#8A8AA0" )
VAR _CorFundo = SWITCH ( TRUE (), _Delta > 0, "#FDECEC", _Delta < 0, "#E6F6EE", "#F0F0F5" )
VAR _Seta     = SWITCH ( TRUE (), _Delta > 0, "↑", _Delta < 0, "↓", "→" )
VAR _Badge    =
    IF (
        NOT ISBLANK ( _Delta ),
        "<span style='background:" & _CorFundo & ";color:" & _CorTxt
            & ";padding:3px 8px;border-radius:8px;font-size:12px;font-weight:600;white-space:nowrap;'>"
            & _Seta & " " & FORMAT ( ABS ( _Delta ), "0.00" ) & " p.p.</span>"
    )
VAR _Narrativa = "Mesmo período de " & ( YEAR ( [_Data Referência IPCA] ) - 1 ) & ": <b style='color:#1A1A2E;'>" & FORMAT ( [IPCA Acum. Ano Mesmo Período Ano Anterior %], "0.00%" ) & "</b>"
RETURN
    IF (
        ISBLANK ( _Valor ),
        "<div style='font-family:Segoe UI;color:#8A8AA0;padding:16px;'>Sem dados no período</div>",
        "<div style='font-family:Segoe UI,sans-serif;padding:16px 18px;background:#FFFFFF;"
            & "border-radius:16px;display:flex;justify-content:space-between;gap:12px;height:100%;box-sizing:border-box;'>"
        -- coluna esquerda: título, valor, badge e narrativa
        & "<div style='min-width:0;'>"
        & "<div style='font-size:15px;color:#1A1A2E;font-weight:600;'>Acumulado no ano</div>"
        & "<div style='font-size:34px;font-weight:700;color:#1A1A2E;margin:6px 0 8px 0;letter-spacing:-0.5px;'>"
            & _Inteiro & "<span style='color:" & _CorDec & ";'>" & _Decimal & "%</span></div>"
        & _Badge
        & "<div style='font-size:12px;color:#8A8AA0;margin-top:10px;line-height:1.35;'>" & _Narrativa & "</div>"
        & "</div>"
        -- coluna direita: mini-indicadores
        & "<div style='display:flex;flex-direction:column;justify-content:flex-end;min-width:118px;'>"
        & "<div style='display:flex;align-items:center;gap:8px;margin-top:10px;'>"
            & "<div style='width:30px;height:30px;border-radius:50%;background:#E9E4FF;color:#7B61FF;"
            & "display:flex;align-items:center;justify-content:center;font-size:14px;'>◎</div>"
            & "<div style='font-size:12px;line-height:1.25;color:#1A1A2E;font-weight:600;'>"
            & FORMAT ( [Focus Mediana Ano Corrente], "0.00%" ) & "<br><span style='color:#8A8AA0;font-weight:400;'>Focus p/ o ano</span></div></div>"
        & "<div style='display:flex;align-items:center;gap:8px;margin-top:10px;'>"
            & "<div style='width:30px;height:30px;border-radius:50%;background:#E9E4FF;color:#7B61FF;"
            & "display:flex;align-items:center;justify-content:center;font-size:14px;'>⚑</div>"
            & "<div style='font-size:12px;line-height:1.25;color:#1A1A2E;font-weight:600;'>"
            & FORMAT ( [Meta Ano %], "0.0%" ) & "<br><span style='color:#8A8AA0;font-weight:400;'>Meta do ano</span></div></div>"
        & "</div></div>"
    )
```

### HTML Card IPCA 12M

*Cartão KPI do IPCA acumulado em 12 meses.* · formato: `texto/HTML`

```dax
HTML Card IPCA 12M =
-- =============================================================
-- HTML Card IPCA 12M
-- Objetivo : cartão KPI do IPCA acumulado em 12 meses.
-- Badge    : vermelho se o 12M subiu vs mês anterior, verde se caiu.
--            Semântica de inflação: ALTA = vermelho, QUEDA = verde.
-- Decimais : texto formatado é partido em inteiro/decimal (preserva sinal
--            negativo — TRUNC do exemplo original perdia o '-' em -0,30%).
-- Visual   : HTML Content (AppSource) → campo 'Values' = esta medida.
-- =============================================================
VAR _Valor    = [IPCA 12M %]
VAR _Delta    = [Δ 12M vs Mês Anterior (p.p.)]
VAR _Texto    = FORMAT ( _Valor * 100, "0.00" )                 -- ex.: "4,52" / "-0,30"
VAR _Inteiro  = LEFT ( _Texto, LEN ( _Texto ) - 3 )                -- "4"   (preserva o sinal)
VAR _Decimal  = RIGHT ( _Texto, 3 )                                -- ",52"
VAR _CorDec   = "#C9C9D3"                                          -- decimais "apagados"
VAR _CorTxt   = SWITCH ( TRUE (), _Delta > 0, "#E5484D", _Delta < 0, "#22A06B", "#8A8AA0" )
VAR _CorFundo = SWITCH ( TRUE (), _Delta > 0, "#FDECEC", _Delta < 0, "#E6F6EE", "#F0F0F5" )
VAR _Seta     = SWITCH ( TRUE (), _Delta > 0, "↑", _Delta < 0, "↓", "→" )
VAR _Badge    =
    IF (
        NOT ISBLANK ( _Delta ),
        "<span style='background:" & _CorFundo & ";color:" & _CorTxt
            & ";padding:3px 8px;border-radius:8px;font-size:12px;font-weight:600;white-space:nowrap;'>"
            & _Seta & " " & FORMAT ( ABS ( _Delta ), "0.00" ) & " p.p.</span>"
    )
VAR _Narrativa = "Meta: " & FORMAT ( [Meta Ano %], "0.0%" ) & " · Teto: " & FORMAT ( [Limite Superior %], "0.0%" )
RETURN
    IF (
        ISBLANK ( _Valor ),
        "<div style='font-family:Segoe UI;color:#8A8AA0;padding:16px;'>Sem dados no período</div>",
        "<div style='font-family:Segoe UI,sans-serif;padding:16px 18px;background:#FFFFFF;"
            & "border-radius:16px;display:flex;justify-content:space-between;gap:12px;height:100%;box-sizing:border-box;'>"
        -- coluna esquerda: título, valor, badge e narrativa
        & "<div style='min-width:0;'>"
        & "<div style='font-size:15px;color:#1A1A2E;font-weight:600;'>IPCA 12 meses</div>"
        & "<div style='font-size:34px;font-weight:700;color:#1A1A2E;margin:6px 0 8px 0;letter-spacing:-0.5px;'>"
            & _Inteiro & "<span style='color:" & _CorDec & ";'>" & _Decimal & "%</span></div>"
        & _Badge
        & "<div style='font-size:12px;color:#8A8AA0;margin-top:10px;line-height:1.35;'>" & _Narrativa & "</div>"
        & "</div>"
        -- coluna direita: mini-indicadores
        & "<div style='display:flex;flex-direction:column;justify-content:flex-end;min-width:118px;'>"
        & "<div style='display:flex;align-items:center;gap:8px;margin-top:10px;'>"
            & "<div style='width:30px;height:30px;border-radius:50%;background:#E9E4FF;color:#7B61FF;"
            & "display:flex;align-items:center;justify-content:center;font-size:14px;'>▲</div>"
            & "<div style='font-size:12px;line-height:1.25;color:#1A1A2E;font-weight:600;'>"
            & [Status Meta] & "<br><span style='color:#8A8AA0;font-weight:400;'>Status da meta</span></div></div>"
        & "<div style='display:flex;align-items:center;gap:8px;margin-top:10px;'>"
            & "<div style='width:30px;height:30px;border-radius:50%;background:#E9E4FF;color:#7B61FF;"
            & "display:flex;align-items:center;justify-content:center;font-size:14px;'>⧗</div>"
            & "<div style='font-size:12px;line-height:1.25;color:#1A1A2E;font-weight:600;'>"
            & FORMAT ( [Meses Consecutivos Acima do Teto], "0" ) & " meses" & "<br><span style='color:#8A8AA0;font-weight:400;'>Acima do teto</span></div></div>"
        & "</div></div>"
    )
```

### HTML Status Meta

*Faixa com barra de progresso do IPCA 12M até o teto da meta.* · formato: `texto/HTML`

```dax
HTML Status Meta =
-- =============================================================
-- HTML Status Meta
-- Objetivo : barra de progresso do IPCA 12M com a banda de tolerância em lavanda.
-- Regra    : posições em % da largura; FORMAT "0" gera inteiros (o CSS não aceita
--            vírgula decimal, que a cultura pt-BR produziria com "0.0").
-- =============================================================
VAR _IPCA    = [IPCA 12M %]
VAR _Piso    = [Limite Inferior %]
VAR _Meta    = [Meta Ano %]
VAR _Teto    = [Limite Superior %]
VAR _Escala  = MAX ( _Teto * 1.4, _IPCA * 1.1 )                    -- fim da barra
VAR _NumPiso = ROUND ( DIVIDE ( _Piso, _Escala ) * 100, 0 )     -- posições numéricas
VAR _NumTeto = ROUND ( DIVIDE ( _Teto, _Escala ) * 100, 0 )
VAR _PctIPCA = FORMAT ( MAX ( MIN ( DIVIDE ( _IPCA, _Escala ), 1 ), 0 ) * 100, "0" )
VAR _PctPiso = FORMAT ( _NumPiso, "0" )
VAR _PctMeta = FORMAT ( DIVIDE ( _Meta, _Escala ) * 100, "0" )
VAR _PctTeto = FORMAT ( _NumTeto, "0" )
VAR _PctBanda = FORMAT ( _NumTeto - _NumPiso, "0" )
VAR _Status  = [Status Meta]
VAR _Cor     = IF ( _Status = "Acima do teto", "#E5484D", "#7B61FF" )
VAR _Marcador =                                                    -- linha vertical fina
    "<div style='position:absolute;top:-4px;width:2px;height:18px;background:#1A1A2E;opacity:.35;left:"
RETURN
    IF (
        NOT ISBLANK ( _IPCA ),
        "<div style='font-family:Segoe UI,sans-serif;padding:12px 16px;'>"
        & "<div style='display:flex;justify-content:space-between;font-size:12px;color:#8A8AA0;margin-bottom:8px;'>"
            & "<span><b style='color:#1A1A2E;'>Status da meta:</b> "
            & "<span style='color:" & _Cor & ";font-weight:600;'>" & _Status & "</span></span>"
            & "<span>IPCA 12M " & FORMAT ( _IPCA, "0.00%" ) & "</span></div>"
        & "<div style='position:relative;height:10px;border-radius:6px;background:#F0F0F5;'>"
            -- banda de tolerância (piso → teto) em lavanda
            & "<div style='position:absolute;height:10px;background:#E9E4FF;left:" & _PctPiso
                & "%;width:" & _PctBanda & "%;'></div>"
            -- progresso do IPCA
            & "<div style='position:absolute;height:10px;border-radius:6px;background:" & _Cor
                & ";width:" & _PctIPCA & "%;opacity:.9;'></div>"
            & _Marcador & _PctMeta & "%;'></div>"
            & _Marcador & _PctTeto & "%;'></div>"
        & "</div>"
        & "<div style='position:relative;height:16px;font-size:10px;color:#8A8AA0;margin-top:4px;'>"
            & "<span style='position:absolute;left:" & _PctPiso & "%;transform:translateX(-50%);'>Piso "
                & FORMAT ( _Piso, "0.0%" ) & "</span>"
            & "<span style='position:absolute;left:" & _PctMeta & "%;transform:translateX(-50%);'>Meta "
                & FORMAT ( _Meta, "0.0%" ) & "</span>"
            & "<span style='position:absolute;left:" & _PctTeto & "%;transform:translateX(-50%);'>Teto "
                & FORMAT ( _Teto, "0.0%" ) & "</span>"
        & "</div></div>"
    )
```

### HTML Tabela Grupos

*Tabela-resumo dos grupos com mini barras de contribuição.* · formato: `texto/HTML`

```dax
HTML Tabela Grupos =
-- =============================================================
-- HTML Tabela Grupos
-- Objetivo : ranking dos 9 grupos com barra proporcional à contribuição.
-- Regra    : barra roxa = pressão de alta; verde = grupo que puxou o índice para baixo.
--            Ordenado pela contribuição (CONCATENATEX ... [@Contrib], DESC).
-- =============================================================
VAR _Tabela =
    ADDCOLUMNS (
        ALL ( dGrupoIPCA ),
        "@Contrib", [Contribuição Grupo (p.p.)],
        "@Var", [Variação Grupo Mensal %]
    )
VAR _MaxAbs = MAXX ( _Tabela, ABS ( [@Contrib] ) )
VAR _Linhas =
    CONCATENATEX (
        _Tabela,
        VAR _Larg = FORMAT ( DIVIDE ( ABS ( [@Contrib] ), _MaxAbs ) * 100, "0" )
        VAR _Cor  = IF ( [@Contrib] < 0, "#22A06B", "#7B61FF" )
        RETURN
            "<tr style='border-bottom:1px solid #F0F0F5;'>"
            & "<td style='padding:6px 4px;'><span style='display:inline-block;width:8px;height:8px;"
                & "border-radius:50%;margin-right:6px;background:" & dGrupoIPCA[CorHex] & ";'></span>"
                & dGrupoIPCA[Grupo] & "</td>"
            & "<td style='padding:6px 4px;text-align:right;color:#8A8AA0;'>"
                & FORMAT ( [@Var], "0.00%" ) & "</td>"
            & "<td style='padding:6px 4px;width:40%;'><div style='background:#F0F0F5;border-radius:4px;height:8px;'>"
                & "<div style='height:8px;border-radius:4px;background:" & _Cor & ";width:" & _Larg
                & "%;'></div></div></td>"
            & "<td style='padding:6px 4px;text-align:right;font-weight:600;'>"
                & FORMAT ( [@Contrib], "0.00" ) & "</td></tr>",
        "",
        [@Contrib], DESC
    )
RETURN
    IF (
        NOT ISBLANK ( _MaxAbs ),
        "<table style='font-family:Segoe UI,sans-serif;font-size:12px;color:#1A1A2E;width:100%;border-collapse:collapse;'>"
        & "<tr style='color:#8A8AA0;font-size:11px;text-align:left;'>"
            & "<th style='padding:4px;font-weight:400;'>Grupo</th>"
            & "<th style='padding:4px;font-weight:400;text-align:right;'>Var. mês</th>"
            & "<th style='padding:4px;font-weight:400;'>Contribuição</th>"
            & "<th style='padding:4px;font-weight:400;text-align:right;'>p.p.</th></tr>"
        & _Linhas
        & "</table>"
    )
```

### HTML Cabeçalho Narrativo

*Cabeçalho do relatório com título, frase da meta e 'Dados até'.* · formato: `texto/HTML`

```dax
HTML Cabeçalho Narrativo =
-- =============================================================
-- HTML Cabeçalho Narrativo
-- Objetivo : cabeçalho do relatório com título, frase da meta e 'Dados até'.
-- =============================================================
VAR _Titulo = [Título Visão Geral]
VAR _Frase  = [Subtítulo Meta]
VAR _Dados  = [Texto Dados Até]
VAR _Status = [Status Meta]
VAR _Cor    = IF ( _Status = "Acima do teto", "#E5484D", "#22A06B" )
RETURN
    "<div style='font-family:Segoe UI,sans-serif;display:flex;justify-content:space-between;align-items:center;padding:4px 8px;'>"
    & "<div><div style='font-size:20px;font-weight:600;color:#1A1A2E;'>" & _Titulo & "</div>"
    & "<div style='font-size:12px;color:#8A8AA0;margin-top:2px;'>"
        & "<span style='display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;background:"
        & _Cor & ";'></span>" & _Frase & "</div></div>"
    & "<div style='font-size:11px;color:#8A8AA0;background:#FFFFFF;border:1px solid #ECECF2;"
        & "border-radius:12px;padding:4px 10px;white-space:nowrap;'>" & _Dados & "</div>"
    & "</div>"
```

### SVG Sparkline 12M

*Sparkline SVG dos últimos 24 meses do indicador 12M (URL da imagem).* · formato: `texto/HTML` · categoria: ImageUrl

```dax
SVG Sparkline 12M =
-- =============================================================
-- SVG Sparkline 12M
-- Objetivo : minigráfico do 12M dentro de tabelas nativas (uma linha por indicador).
-- Regra    : últimos 24 meses; coordenadas inteiras numa escala ×10 (o CSS/SVG
--            não aceita vírgula decimal); '#' codificado como %23 no data URI.
-- Uso      : categoria de dados = URL da imagem; tabela com dIndicador[Indicador].
-- =============================================================
VAR _DataFim = [_Data Referência]
VAR _Pontos  =
    CALCULATETABLE (
        FILTER (
            ADDCOLUMNS ( VALUES ( dCalendario[Data] ), "@V", [Indicador 12M %] ),
            NOT ISBLANK ( [@V] )
        ),
        REMOVEFILTERS ( dCalendario ),
        dCalendario[Data] > EDATE ( _DataFim, -24 ),
        dCalendario[Data] <= _DataFim
    )
VAR _Min    = MINX ( _Pontos, [@V] )
VAR _Max    = MAXX ( _Pontos, [@V] )
VAR _Ini    = MINX ( _Pontos, dCalendario[Data] )
VAR _N      = COUNTROWS ( _Pontos )
VAR _PassoX = DIVIDE ( 2300, _N - 1 )                              -- largura 2300 (escala ×10)
VAR _Coord  =                                                      -- "x,y x,y ..." inteiros
    ADDCOLUMNS (
        _Pontos,
        "@X", DATEDIFF ( _Ini, dCalendario[Data], MONTH ) * _PassoX,
        "@Y", 360 - DIVIDE ( [@V] - _Min, _Max - _Min, 0.5 ) * 320
    )
VAR _Linha  =
    CONCATENATEX ( _Coord, FORMAT ( [@X], "0" ) & "," & FORMAT ( [@Y], "0" ), " ", dCalendario[Data], ASC )
VAR _Ult    = TOPN ( 1, _Coord, dCalendario[Data], DESC )
VAR _UltX   = FORMAT ( MAXX ( _Ult, [@X] ), "0" )
VAR _UltY   = FORMAT ( MAXX ( _Ult, [@Y] ), "0" )
RETURN
    IF (
        _N >= 2,
        "data:image/svg+xml;utf8,"
        & "<svg xmlns='http://www.w3.org/2000/svg' viewBox='-40 -40 2380 480'>"
        & "<polyline fill='none' stroke='%237B61FF' stroke-width='28' stroke-linejoin='round' "
        & "stroke-linecap='round' points='" & _Linha & "'/>"
        & "<circle cx='" & _UltX & "' cy='" & _UltY & "' r='40' fill='%237B61FF'/>"
        & "</svg>"
    )
```

### Rótulo Acima do Teto

*Rótulo 'Acima do teto em X p.p.' para as colunas dos anos que estouraram.* · formato: `texto/HTML`

```dax
Rótulo Acima do Teto =
-- =============================================================
-- Rótulo Acima do Teto
-- Objetivo : rótulo 'Acima do teto em X p.p.' para as colunas dos anos que estouraram.
-- =============================================================
VAR _Excesso = [Acima do Teto no Ano (p.p.)]
RETURN
    IF ( NOT ISBLANK ( _Excesso ), "Acima do teto em " & FORMAT ( _Excesso, "0.00" ) & " p.p." )
```


## 08 Auxiliares

### _Data Referência

*Mês-base dos cálculos do(s) indicador(es) SGS em contexto.* · formato: `dd/mm/yyyy` · oculta

```dax
_Data Referência =
-- =============================================================
-- _Data Referência
-- Objetivo : mês-base dos cálculos do(s) indicador(es) SGS em contexto.
-- Regra    : último mês do contexto, limitado ao último mês com dado publicado.
--            Se TODO o contexto for posterior ao último dado, retorna BLANK
--            (evita repetir o último valor em meses futuros do eixo).
--            Num contexto anual (ex.: 2026 incompleto) devolve o último mês com dado.
-- =============================================================
VAR _MinContexto = MIN ( dCalendario[Data] )
VAR _MaxContexto = MAX ( dCalendario[Data] )
VAR _UltimaKey =
    CALCULATE (
        MAX ( fIndicadores[DataKey] ),
        REMOVEFILTERS ( dCalendario )
    )
VAR _UltimaData =
    IF (
        NOT ISBLANK ( _UltimaKey ),
        DATE ( QUOTIENT ( _UltimaKey, 10000 ), MOD ( QUOTIENT ( _UltimaKey, 100 ), 100 ), 1 )
    )
RETURN
    IF (
        NOT ISBLANK ( _UltimaData ) && _MinContexto <= _UltimaData,
        MIN ( _MaxContexto, _UltimaData )
    )
```

### _Data Referência Grupos

*Mês-base dos cálculos por grupo do IPCA (SIDRA).* · formato: `dd/mm/yyyy` · oculta

```dax
_Data Referência Grupos =
-- =============================================================
-- _Data Referência Grupos
-- Objetivo : mês-base dos cálculos por grupo do IPCA (SIDRA).
-- Regra    : último mês do contexto, limitado ao último mês com dado publicado.
--            Se TODO o contexto for posterior ao último dado, retorna BLANK
--            (evita repetir o último valor em meses futuros do eixo).
--            Num contexto anual (ex.: 2026 incompleto) devolve o último mês com dado.
-- =============================================================
VAR _MinContexto = MIN ( dCalendario[Data] )
VAR _MaxContexto = MAX ( dCalendario[Data] )
VAR _UltimaKey =
    CALCULATE (
        MAX ( fIPCAGrupos[DataKey] ),
        REMOVEFILTERS ( dCalendario ),
        REMOVEFILTERS ( dGrupoIPCA )
    )
VAR _UltimaData =
    IF (
        NOT ISBLANK ( _UltimaKey ),
        DATE ( QUOTIENT ( _UltimaKey, 10000 ), MOD ( QUOTIENT ( _UltimaKey, 100 ), 100 ), 1 )
    )
RETURN
    IF (
        NOT ISBLANK ( _UltimaData ) && _MinContexto <= _UltimaData,
        MIN ( _MaxContexto, _UltimaData )
    )
```

### _Data Referência Focus

*Mês de coleta de referência das expectativas Focus.* · formato: `dd/mm/yyyy` · oculta

```dax
_Data Referência Focus =
-- =============================================================
-- _Data Referência Focus
-- Objetivo : mês de coleta de referência das expectativas Focus.
-- Regra    : último mês do contexto, limitado ao último mês com dado publicado.
--            Se TODO o contexto for posterior ao último dado, retorna BLANK
--            (evita repetir o último valor em meses futuros do eixo).
--            Num contexto anual (ex.: 2026 incompleto) devolve o último mês com dado.
-- =============================================================
VAR _MinContexto = MIN ( dCalendario[Data] )
VAR _MaxContexto = MAX ( dCalendario[Data] )
VAR _UltimaKey =
    CALCULATE (
        MAX ( fExpectativas[DataColetaKey] ),
        REMOVEFILTERS ( dCalendario )
    )
VAR _UltimaData =
    IF (
        NOT ISBLANK ( _UltimaKey ),
        DATE ( QUOTIENT ( _UltimaKey, 10000 ), MOD ( QUOTIENT ( _UltimaKey, 100 ), 100 ), 1 )
    )
RETURN
    IF (
        NOT ISBLANK ( _UltimaData ) && _MinContexto <= _UltimaData,
        MIN ( _MaxContexto, _UltimaData )
    )
```

### _Data Referência IPCA

*Mês-base do IPCA (SGS 433), usado por meta, comparativos e textos.* · formato: `dd/mm/yyyy` · oculta

```dax
_Data Referência IPCA =
-- =============================================================
-- _Data Referência IPCA
-- Objetivo : mês-base do IPCA (SGS 433), usado por meta, comparativos e textos.
-- =============================================================
CALCULATE (
    [_Data Referência],
    REMOVEFILTERS ( dIndicador ),
    dIndicador[CodigoSGS] = 433
)
```

### _Valor Bruto

*Valor mensal do indicador, sem deslocar datas (uso interno em iteradores).* · formato: `0.0000%` · oculta

```dax
_Valor Bruto =
-- =============================================================
-- _Valor Bruto
-- Objetivo : valor do indicador no(s) mês(es) do contexto, sem nenhum ajuste de data.
-- Uso      : APENAS dentro de iteradores mês a mês (PRODUCTX / FILTER), onde o contexto
--            já é um único mês. Exige um único indicador: somar taxas de séries
--            diferentes não tem significado econômico.
-- =============================================================
IF (
    HASONEVALUE ( dIndicador[CodigoSGS] ),
    SUM ( fIndicadores[Valor] )
)
```

### _Indicador Composto

*TRUE se o indicador em contexto é taxa mensal (pode ser composta).* · formato: `texto/HTML` · oculta

```dax
_Indicador Composto =
-- =============================================================
-- _Indicador Composto
-- Objetivo : proteger os acumulados de séries que NÃO podem ser compostas
--            (IPCA 12M oficial e Selic % a.a.).
-- =============================================================
SELECTEDVALUE ( dIndicador[TipoTaxa] ) = "Mensal"
```

### Cor Status Meta

*Hex do status da meta (vermelho acima do teto).* · formato: `texto/HTML`

```dax
Cor Status Meta =
-- =============================================================
-- Cor Status Meta
-- Objetivo : hex do status da meta (vermelho acima do teto).
-- =============================================================
SWITCH (
    [Status Meta],
    "Acima do teto", "#E5484D",
    "Abaixo do piso", "#5B45D6",
    "Dentro", "#22A06B",
    "#8A8AA0"
)
```

### Cor Coluna Realizado vs Teto

*Cor da coluna anual: negativa se estourou o teto.* · formato: `texto/HTML`

```dax
Cor Coluna Realizado vs Teto =
-- =============================================================
-- Cor Coluna Realizado vs Teto
-- Objetivo : cor da coluna anual: negativa se estourou o teto.
-- =============================================================
VAR _Realizado = [IPCA Acum. Ano %]
VAR _Teto      = [Limite Superior %]
RETURN
    IF ( _Realizado > _Teto, "#E5484D", "#7B61FF" )
```

### Cor Variação

*Vermelho se a inflação subiu vs mês anterior, verde se caiu.* · formato: `texto/HTML`

```dax
Cor Variação =
-- =============================================================
-- Cor Variação
-- Objetivo : vermelho se a inflação subiu vs mês anterior, verde se caiu.
-- =============================================================
VAR _Delta = [Variação vs Mês Anterior (p.p.)]
RETURN
    SWITCH ( TRUE (), _Delta > 0, "#E5484D", _Delta < 0, "#22A06B", "#8A8AA0" )
```

### Cor Heatmap Grupo

*Fundo do heatmap grupo × mês na paleta do projeto.* · formato: `texto/HTML`

```dax
Cor Heatmap Grupo =
-- =============================================================
-- Cor Heatmap Grupo
-- Objetivo : fundo do heatmap grupo × mês na paleta do projeto.
-- =============================================================
VAR _V = [Variação Grupo Mensal %]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _V ), BLANK (),
        _V < 0, "#E6F6EE",           -- deflação: verde suave
        _V < 0.003, "#F3F0FF",       -- até 0,30%
        _V < 0.006, "#E9E4FF",       -- até 0,60%
        _V < 0.01, "#B9A8FF",        -- até 1,00%
        "#7B61FF"                    -- acima de 1,00%
    )
```

### Cor Fonte Heatmap Grupo

*Texto branco sobre as células mais escuras do heatmap.* · formato: `texto/HTML`

```dax
Cor Fonte Heatmap Grupo =
-- =============================================================
-- Cor Fonte Heatmap Grupo
-- Objetivo : texto branco sobre as células mais escuras do heatmap.
-- =============================================================
VAR _V = [Variação Grupo Mensal %]
RETURN
    IF ( _V >= 0.01, "#FFFFFF", "#1A1A2E" )
```

### Cor Grupo

*Cor fixa do grupo (dGrupoIPCA[CorHex]).* · formato: `texto/HTML`

```dax
Cor Grupo =
-- =============================================================
-- Cor Grupo
-- Objetivo : cor fixa do grupo (dGrupoIPCA[CorHex]).
-- =============================================================
SELECTEDVALUE ( dGrupoIPCA[CorHex], "#C9C9D3" )
```

### Cor Juro Real

*Roxo para juro real positivo, vermelho para negativo.* · formato: `texto/HTML`

```dax
Cor Juro Real =
-- =============================================================
-- Cor Juro Real
-- Objetivo : roxo para juro real positivo, vermelho para negativo.
-- =============================================================
IF ( [Juro Real Ex-Post %] < 0, "#E5484D", "#7B61FF" )
```

### Checagem IPCA 12M (p.p.)

*IPCA 12M calculado (DAX) menos a série oficial SGS 13522.* · formato: `+0.00" p.p.";-0.00" p.p.";0.00" p.p."`

```dax
Checagem IPCA 12M (p.p.) =
-- =============================================================
-- Checagem IPCA 12M (p.p.)
-- Objetivo : validar a regra de composição do IPCA 12M contra o número oficial.
-- Regra    : diferença em p.p. com ambos arredondados a 2 casas (como publicados).
--            Esperado: 0,00 (até ±0,02 por arredondamento das taxas mensais).
-- =============================================================
VAR _Calc    = [IPCA 12M %]
VAR _Oficial = [IPCA 12M % (SGS 13522)]
RETURN
    IF (
        NOT ISBLANK ( _Calc ) && NOT ISBLANK ( _Oficial ),
        ROUND ( _Calc * 100, 2 ) - ROUND ( _Oficial * 100, 2 )
    )
```

### Checagem IPCA 12M Status

*OK / Arredondamento / Divergente.* · formato: `texto/HTML`

```dax
Checagem IPCA 12M Status =
-- =============================================================
-- Checagem IPCA 12M Status
-- Objetivo : OK / Arredondamento / Divergente.
-- =============================================================
VAR _Dif = ABS ( [Checagem IPCA 12M (p.p.)] )
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _Dif ), BLANK (),
        _Dif <= 0.01, "OK",
        _Dif <= 0.05, "Arredondamento",
        "Divergente"
    )
```

### Checagem Meses Divergentes

*Meses do período com |diferença| > 0,01 p.p.* · formato: `0`

```dax
Checagem Meses Divergentes =
-- =============================================================
-- Checagem Meses Divergentes
-- Objetivo : meses do período com |diferença| > 0,01 p.p.
-- =============================================================
VAR _Tabela =
    ADDCOLUMNS (
        VALUES ( dCalendario[Data] ),
        "@Dif", ABS ( [Checagem IPCA 12M (p.p.)] )
    )
RETURN
    COUNTROWS ( FILTER ( _Tabela, [@Dif] > 0.01 ) ) + 0
```

### Marcador Último Ponto IPCA 12M

*IPCA 12M apenas no último mês com dado (série-marcador do gráfico).* · formato: `0.00%`

```dax
Marcador Último Ponto IPCA 12M =
-- =============================================================
-- Marcador Último Ponto IPCA 12M
-- Objetivo : destacar o último ponto da linha IPCA 12M × Meta.
-- Uso      : 2ª série do gráfico de linhas, só com marcador e rótulo (linha oculta).
-- =============================================================
VAR _Mes    = MAX ( dCalendario[Data] )
VAR _Ultimo = [Último Mês Disponível]
RETURN
    IF ( _Mes = _Ultimo, [IPCA 12M %] )
```
