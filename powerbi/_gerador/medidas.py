# -*- coding: utf-8 -*-
"""Gera as medidas novas do dashboard (pasta 09 Dashboard) em TMDL.
Todas reaproveitam as medidas-base existentes (Indicador Mensal %, Indicador Acum. Ano %,
Indicador 12M %, _Data Referência*, Contribuição Grupo (p.p.), Meta...)."""
import uuid, textwrap

NS = uuid.UUID("6f1c6c1e-7d3a-4b1f-9a51-0b5a9d1e2c33")
PCT = "0.00%"
PP = '+0.00" p.p.";-0.00" p.p.";0.00" p.p."'
MEASURES = []

# paleta
C = dict(fg="#25242B", fg2="#85838F", dec="#C9C7D1", vio="#8064F5", vio2="#B8A6FA", lil="#E7E0FF",
         bord="#E8E8EF", bg2="#FAFAFC", gbg="#DDF5E5", gfg="#1F8F4E", rbg="#FCE6E6", rfg="#D14343",
         nbg="#F0EFF5", nfg="#85838F")
FONT = "Segoe UI,Inter,sans-serif"


def m(name, expr, folder, desc, fmt=None, hidden=False):
    MEASURES.append(dict(name=name, expr=textwrap.dedent(expr).strip("\n"), folder=folder,
                         desc=desc, fmt=fmt, hidden=hidden))


F_AUX = r"09 Dashboard\06 Auxiliares"
F_KPI = r"09 Dashboard\01 KPIs"
F_CMP = r"09 Dashboard\02 Comparações"
F_RNK = r"09 Dashboard\03 Rankings e Contribuições"
F_GRA = r"09 Dashboard\04 Gráficos e Títulos"
F_HTM = r"09 Dashboard\05 HTML"

SEL = "VAR _Cod = [_Sel Código Indicador]\n"

# ---------------------------------------------------------------- Auxiliares
m("_Sel Código Indicador", """
    -- Indicador escolhido no seletor (somente séries de inflação com taxa mensal).
    -- Sem seleção única (ou seleção inválida) => IPCA (433), o indicador oficial da meta.
    VAR _Cod  = SELECTEDVALUE ( dIndicador[CodigoSGS] )
    VAR _Tipo = SELECTEDVALUE ( dIndicador[TipoTaxa] )
    VAR _Cat  = SELECTEDVALUE ( dIndicador[Categoria] )
    RETURN
        IF ( NOT ISBLANK ( _Cod ) && _Tipo = "Mensal" && _Cat = "Inflação", _Cod, 433 )
""", F_AUX, "Código SGS do indicador ativo no seletor; IPCA (433) quando não há seleção única válida.", "0", True)

m("Indicador Selecionado", SEL + """
    RETURN
        CALCULATE ( MAX ( dIndicador[Indicador] ), REMOVEFILTERS ( dIndicador ), dIndicador[CodigoSGS] = _Cod )
""", F_KPI, "Nome do indicador ativo no seletor (IPCA por padrão).")

m("KPI Data Referência", SEL + """
    RETURN
        CALCULATE ( [_Data Referência], REMOVEFILTERS ( dIndicador ), dIndicador[CodigoSGS] = _Cod )
""", F_KPI, "Último mês com dado publicado do indicador ativo, dentro do período filtrado.", "mmm/yyyy")

# ---------------------------------------------------------------- KPIs
m("KPI Mensal %", SEL + """
    RETURN
        CALCULATE ( [Indicador Mensal %], REMOVEFILTERS ( dIndicador ), dIndicador[CodigoSGS] = _Cod )
""", F_KPI, "Taxa do último mês do indicador ativo (BLANK = sem dado, diferente de 0%).", PCT)

m("KPI Acum. Ano %", SEL + """
    RETURN
        CALCULATE ( [Indicador Acum. Ano %], REMOVEFILTERS ( dIndicador ), dIndicador[CodigoSGS] = _Cod )
""", F_KPI, "Acumulado no ano (composição multiplicativa) até o mês de referência do indicador ativo.", PCT)

m("KPI 12M %", SEL + """
    RETURN
        CALCULATE ( [Indicador 12M %], REMOVEFILTERS ( dIndicador ), dIndicador[CodigoSGS] = _Cod )
""", F_KPI, "Acumulado em 12 meses (exige 12 meses publicados) do indicador ativo.", PCT)

m("KPI Média Mensal 12M %", """
    -- Média geométrica mensal equivalente à janela de 12 meses: (1 + 12M)^(1/12) - 1
    VAR _12M = [KPI 12M %]
    RETURN
        IF ( NOT ISBLANK ( _12M ), POWER ( 1 + _12M, 1 / 12 ) - 1 )
""", F_KPI, "Taxa mensal média equivalente (geométrica) dos últimos 12 meses.", PCT)

m("KPI Meses Apurados no Ano", SEL + """
    VAR _Data = [KPI Data Referência]
    RETURN
        IF (
            NOT ISBLANK ( _Data ),
            CALCULATE (
                COUNTROWS ( fIndicadores ),
                REMOVEFILTERS ( dCalendario ),
                REMOVEFILTERS ( dIndicador ),
                dIndicador[CodigoSGS] = _Cod,
                dCalendario[Data] >= DATE ( YEAR ( _Data ), 1, 1 ),
                dCalendario[Data] <= _Data
            )
        )
""", F_KPI, "Meses com dado publicado no ano do mês de referência.", "0")

m("KPI Meses em Alta no Ano", SEL + """
    VAR _Data = [KPI Data Referência]
    RETURN
        IF (
            NOT ISBLANK ( _Data ),
            CALCULATE (
                COUNTROWS ( fIndicadores ),
                REMOVEFILTERS ( dCalendario ),
                REMOVEFILTERS ( dIndicador ),
                dIndicador[CodigoSGS] = _Cod,
                dCalendario[Data] >= DATE ( YEAR ( _Data ), 1, 1 ),
                dCalendario[Data] <= _Data,
                fIndicadores[Valor] > 0
            ) + 0
        )
""", F_KPI, "Meses do ano com taxa positiva (0 quando todos ≤ 0).", "0")

# ---------------------------------------------------------------- Comparações
def deslocado(nome, base, meses, desc):
    m(nome, f"""
        VAR _Data = [KPI Data Referência]
        RETURN
            IF (
                NOT ISBLANK ( _Data ),
                CALCULATE ( [{base}], REMOVEFILTERS ( dCalendario ), dCalendario[Data] = EDATE ( _Data, {meses} ) )
            )
    """, F_CMP, desc, PCT)


def delta(nome, a, b, desc):
    m(nome, f"""
        -- Diferença em pontos percentuais (não é variação relativa).
        VAR _A = [{a}]
        VAR _B = [{b}]
        RETURN
            IF ( NOT ISBLANK ( _A ) && NOT ISBLANK ( _B ), ( _A - _B ) * 100 )
    """, F_CMP, desc, PP)


deslocado("KPI Mensal Mês Anterior %", "KPI Mensal %", -1, "Taxa do mês anterior ao de referência.")
deslocado("KPI Mensal Mesmo Mês Ano Anterior %", "KPI Mensal %", -12, "Taxa do mesmo mês do ano anterior.")
deslocado("KPI Acum. Ano Mesmo Período Ano Anterior %", "KPI Acum. Ano %", -12,
          "Acumulado de janeiro até o mesmo mês do ano anterior.")
deslocado("KPI 12M Mês Anterior %", "KPI 12M %", -1, "Acumulado 12M encerrado no mês anterior.")
deslocado("KPI 12M Janela Anterior %", "KPI 12M %", -12,
          "Acumulado da janela de 12 meses imediatamente anterior (encerrada 12 meses antes).")
delta("KPI Δ Mensal (p.p.)", "KPI Mensal %", "KPI Mensal Mês Anterior %",
      "Aceleração (+) ou desaceleração (−) da taxa mensal vs mês anterior.")
delta("KPI Δ Acum. Ano (p.p.)", "KPI Acum. Ano %", "KPI Acum. Ano Mesmo Período Ano Anterior %",
      "Acumulado no ano menos o mesmo período do ano anterior.")
delta("KPI Δ 12M vs Janela Anterior (p.p.)", "KPI 12M %", "KPI 12M Janela Anterior %",
      "Acumulado 12M menos a janela de 12 meses anterior.")
delta("KPI Δ 12M vs Mês Anterior (p.p.)", "KPI 12M %", "KPI 12M Mês Anterior %",
      "Variação do acumulado 12M em relação ao mês anterior.")

m("Posição na Banda da Meta %", """
    -- 0% = piso, 100% = teto. Pode passar de 0–100% (fora do intervalo).
    VAR _IPCA = [IPCA 12M %]
    VAR _Piso = [Limite Inferior %]
    VAR _Teto = [Limite Superior %]
    RETURN
        IF ( NOT ISBLANK ( _IPCA ) && _Teto > _Piso, DIVIDE ( _IPCA - _Piso, _Teto - _Piso ) )
""", F_CMP, "Posição do IPCA 12M dentro do intervalo de tolerância da meta (0% = piso, 100% = teto).", "0%")

# ---------------------------------------------------------------- Rankings e contribuições
TAB_VAR = """VAR _T =
        FILTER (
            ADDCOLUMNS ( ALL ( dGrupoIPCA ), "@v", [Variação Grupo Mensal %] ),
            NOT ISBLANK ( [@v] )
        )
"""
TAB_CON = """VAR _T =
        FILTER (
            ADDCOLUMNS ( ALL ( dGrupoIPCA ), "@c", [Contribuição Grupo (p.p.)] ),
            NOT ISBLANK ( [@c] )
        )
"""
m("Grupo de Maior Alta", "    " + TAB_VAR + """    VAR _Top = TOPN ( 1, _T, [@v], DESC, dGrupoIPCA[Ordem], ASC )
    RETURN
        MAXX ( _Top, dGrupoIPCA[Grupo] )
""", F_RNK, "Grupo com a maior VARIAÇÃO percentual no mês (não confundir com maior contribuição).")
m("Variação do Grupo de Maior Alta %", "    " + TAB_VAR + """    RETURN
        MAXX ( _T, [@v] )
""", F_RNK, "Maior variação mensal entre os grupos.", PCT)
m("Grupo de Maior Queda", "    " + TAB_VAR + """    VAR _Top = TOPN ( 1, _T, [@v], ASC, dGrupoIPCA[Ordem], ASC )
    RETURN
        MAXX ( _Top, dGrupoIPCA[Grupo] )
""", F_RNK, "Grupo com a menor variação percentual no mês (maior queda, se negativa).")
m("Variação do Grupo de Maior Queda %", "    " + TAB_VAR + """    RETURN
        MINX ( _T, [@v] )
""", F_RNK, "Menor variação mensal entre os grupos.", PCT)
m("Amplitude entre Grupos (p.p.)", """
    -- Dispersão simples: maior menos menor variação mensal entre os grupos.
    VAR _Max = [Variação do Grupo de Maior Alta %]
    VAR _Min = [Variação do Grupo de Maior Queda %]
    RETURN
        IF ( NOT ISBLANK ( _Max ) && NOT ISBLANK ( _Min ), ( _Max - _Min ) * 100 )
""", F_RNK, "Amplitude (máx − mín) das variações mensais dos grupos, em p.p.", PP)
m("Grupos em Alta", "    " + TAB_VAR + """    RETURN
        COUNTROWS ( FILTER ( _T, [@v] > 0 ) ) + 0
""", F_RNK, "Quantidade de grupos com variação positiva no mês.", "0")
m("Grupos com Dado", "    " + TAB_VAR + """    RETURN
        COUNTROWS ( _T ) + 0
""", F_RNK, "Quantidade de grupos com variação publicada no mês.", "0")
m("Grupo de Maior Alívio", "    " + TAB_CON + """    VAR _Top = TOPN ( 1, _T, [@c], ASC, dGrupoIPCA[Ordem], ASC )
    RETURN
        MAXX ( _Top, dGrupoIPCA[Grupo] )
""", F_RNK, "Grupo com a menor contribuição ponderada (variação × peso) no mês.")
m("Contribuição do Grupo de Maior Alívio (p.p.)", "    " + TAB_CON + """    RETURN
        MINX ( _T, [@c] )
""", F_RNK, "Menor contribuição ponderada entre os grupos, em p.p.", PP)
m("Variação do Grupo de Maior Pressão %", """
    VAR _Grupo = [Grupo de Maior Pressão]
    RETURN
        IF ( NOT ISBLANK ( _Grupo ),
            CALCULATE ( [Variação Grupo Mensal %], REMOVEFILTERS ( dGrupoIPCA ), dGrupoIPCA[Grupo] = _Grupo ) )
""", F_RNK, "Variação mensal do grupo de maior contribuição.", PCT)
m("Peso do Grupo de Maior Pressão %", """
    VAR _Grupo = [Grupo de Maior Pressão]
    RETURN
        IF ( NOT ISBLANK ( _Grupo ),
            CALCULATE ( [Peso Grupo %], REMOVEFILTERS ( dGrupoIPCA ), dGrupoIPCA[Grupo] = _Grupo ) )
""", F_RNK, "Peso (IBGE) do grupo de maior contribuição.", PCT)
m("Contribuição Grupo Janela 24M (p.p.)", """
    -- Contribuição por grupo limitada aos 24 meses que terminam no último mês do período filtrado.
    VAR _Mes = MAX ( dCalendario[Data] )
    VAR _Fim = CALCULATE ( [_Data Referência Grupos], ALLSELECTED ( dCalendario ), REMOVEFILTERS ( dGrupoIPCA ) )
    RETURN
        IF ( _Mes <= _Fim && _Mes > EDATE ( _Fim, -24 ), [Contribuição Grupo (p.p.)] )
""", F_RNK, "Contribuição (p.p.) somente nos últimos 24 meses do período — para o gráfico empilhado.", PP)

# ---------------------------------------------------------------- Gráficos, cores e títulos
m("Gráfico Último Ponto 12M", """
    -- Destaca apenas o último mês com dado dentro do período selecionado.
    VAR _Mes = MAX ( dCalendario[Data] )
    VAR _Ult = CALCULATE ( [KPI Data Referência], ALLSELECTED ( dCalendario ) )
    RETURN
        IF ( HASONEVALUE ( dCalendario[Data] ) && _Mes = _Ult, [KPI 12M %] )
""", F_GRA, "Valor do acumulado 12M só no último mês observado (marcador do gráfico).", PCT)
m("Cor Contribuição", """
    VAR _C = [Contribuição Grupo (p.p.)]
    RETURN
        IF ( _C < 0, "#B8A6FA", "#8064F5" )
""", F_GRA, "Violeta para contribuição positiva, lilás para negativa.")
m("Cor Variação Grupo", """
    VAR _V = [Variação Grupo Mensal %]
    RETURN
        IF ( _V < 0, "#B8A6FA", "#8064F5" )
""", F_GRA, "Violeta para variação positiva, lilás para negativa.")
m("Título Evolução", """
    "Evolução da inflação · " & [Indicador Selecionado] & " acumulado em 12 meses"
""", F_GRA, "Título dinâmico do gráfico principal.")
m("Título Contribuição", """
    VAR _D = CALCULATE ( [_Data Referência Grupos], REMOVEFILTERS ( dGrupoIPCA ) )
    RETURN
        "Contribuição por grupo · IPCA " & FORMAT ( _D, "mmm/yy" ) & " (p.p.)"
""", F_GRA, "Título dinâmico do ranking de contribuições.")
m("Título Variação Grupos", """
    VAR _D = CALCULATE ( [_Data Referência Grupos], REMOVEFILTERS ( dGrupoIPCA ) )
    RETURN
        "Variação do mês por grupo · " & FORMAT ( _D, "mmm/yy" )
""", F_GRA, "Título dinâmico do ranking de variações.")
m("Título Rosca Pesos", """
    VAR _D = CALCULATE ( [_Data Referência Grupos], REMOVEFILTERS ( dGrupoIPCA ) )
    RETURN
        "Peso dos grupos no IPCA · " & FORMAT ( _D, "mmm/yy" )
""", F_GRA, "Título dinâmico da rosca de pesos.")

# ---------------------------------------------------------------- HTML helpers (geram DAX)
def q(s):
    """literal DAX: escapa aspas duplas"""
    return '"' + s.replace('"', '""') + '"'


def split_value(var, fmt_dax):
    """divide o número formatado em parte inteira + decimais 'apagados' (como na referência)."""
    return f"""VAR _Txt = {fmt_dax}
    VAR _Int = LEFT ( _Txt, LEN ( _Txt ) - 3 )
    VAR _Dec = RIGHT ( _Txt, 3 )"""


def badge_dax(delta_var, suffix_dax, up_is_bad=True):
    up_bg, up_fg = (C['rbg'], C['rfg']) if up_is_bad else (C['gbg'], C['gfg'])
    dn_bg, dn_fg = (C['gbg'], C['gfg']) if up_is_bad else (C['rbg'], C['rfg'])
    return f"""VAR _BBg = SWITCH ( TRUE (), {delta_var} > 0, "{up_bg}", {delta_var} < 0, "{dn_bg}", "{C['nbg']}" )
    VAR _BFg = SWITCH ( TRUE (), {delta_var} > 0, "{up_fg}", {delta_var} < 0, "{dn_fg}", "{C['nfg']}" )
    VAR _Seta = SWITCH ( TRUE (), {delta_var} > 0, "↑", {delta_var} < 0, "↓", "→" )
    VAR _Badge =
        IF (
            NOT ISBLANK ( {delta_var} ),
            "<span style='display:inline-block;background:" & _BBg & ";color:" & _BFg
                & ";padding:3px 9px;border-radius:8px;font-size:12px;font-weight:600;white-space:nowrap;'>"
                & _Seta & " " & FORMAT ( ABS ( {delta_var} ), "0.00" ) & " p.p.</span>"
                & "<span style='font-size:11.5px;color:{C['fg2']};margin-left:8px;'>" & {suffix_dax} & "</span>"
        )"""


def icon_row(icon, value_dax, label_dax):
    """estatística de rodapé (ícone + valor + rótulo), dispostas lado a lado."""
    return (f"\"<div style='display:flex;align-items:center;gap:7px;min-width:0;'>"
            f"<div style='width:24px;height:24px;min-width:24px;border-radius:50%;background:{C['lil']};color:{C['vio']};"
            f"display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;'>{icon}</div>"
            f"<div style='font-size:11.5px;line-height:1.2;color:{C['fg']};font-weight:600;white-space:nowrap;'>\" & {value_dax} & "
            f"\"<br><span style='font-size:10.5px;color:{C['fg2']};font-weight:400;'>\" & {label_dax} & \"</span></div></div>\"")


def card_shell(title_dax, pill_dax, value_html_dax, badge_var, note_dax, rows):
    """título + período | valor (decimais apagados) | etiqueta de comparação | rodapé com 2 estatísticas."""
    rows_html = " & ".join(rows) if rows else '""'
    return f"""
        "<div style='font-family:{FONT};height:100%;box-sizing:border-box;padding:14px 18px 12px 18px;display:flex;flex-direction:column;'>"
        & "<div style='display:flex;justify-content:space-between;align-items:center;gap:8px;'>"
            & "<div style='font-size:14.5px;font-weight:600;color:{C['fg']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>" & {title_dax} & "</div>"
            & "<div style='font-size:11px;color:{C['fg']};border:1px solid {C['bord']};border-radius:14px;padding:3px 10px;white-space:nowrap;'>" & {pill_dax} & "</div>"
        & "</div>"
        & "<div style='font-size:32px;font-weight:700;color:{C['fg']};letter-spacing:-0.6px;margin:6px 0 5px 0;line-height:1.1;'>" & {value_html_dax} & "</div>"
        & "<div style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>" & {badge_var} & "</div>"
        & "<div style='display:flex;justify-content:space-between;gap:10px;border-top:1px solid #F0EFF5;padding-top:8px;margin-top:auto;'>" & {rows_html} & "</div>"
        & "</div>"
"""


NODATA = f"\"<div style='font-family:{FONT};color:{C['fg2']};padding:18px;font-size:13px;'>Sem dados publicados para o período selecionado.</div>\""


def pct(x):
    return f'FORMAT ( {x}, "0.00%" )'


def mmmyy(x):
    return f'FORMAT ( {x}, "mmm/yy" )'


# ---- Card 1: inflação do mês
m("HTML KPI Mês", f"""
    VAR _Nome  = [Indicador Selecionado]
    VAR _Data  = [KPI Data Referência]
    VAR _Valor = [KPI Mensal %]
    VAR _Ant   = [KPI Mensal Mês Anterior %]
    VAR _Delta = [KPI Δ Mensal (p.p.)]
    VAR _AA    = [KPI Mensal Mesmo Mês Ano Anterior %]
    VAR _Alta  = [KPI Meses em Alta no Ano]
    VAR _Qtd   = [KPI Meses Apurados no Ano]
    {split_value('_Valor', 'FORMAT ( _Valor * 100, "0.00" )')}
    VAR _ValorHtml = _Int & "<span style='color:{C['dec']};'>" & _Dec & "%</span>"
    {badge_dax('_Delta', '"vs " & ' + mmmyy('EDATE ( _Data, -1 )') + ' & " (" & ' + pct('_Ant') + ' & ")"')}
    VAR _Nota =
        SWITCH ( TRUE (),
            ISBLANK ( _Delta ), "Sem mês anterior para comparar",
            _Delta > 0, "Acelerou frente a " & {pct('_Ant')} & " no mês anterior",
            _Delta < 0, "Desacelerou frente a " & {pct('_Ant')} & " no mês anterior",
            "Estável frente ao mês anterior" )
    RETURN
        IF ( ISBLANK ( _Valor ), {NODATA},
        {card_shell('"Inflação do mês · " & _Nome', 'FORMAT ( _Data, "mmm/yyyy" )', '_ValorHtml', '_Badge', '_Nota',
                    [icon_row('↺', 'IF ( ISBLANK ( _AA ), "–", ' + pct('_AA') + ')', 'FORMAT ( EDATE ( _Data, -12 ), "mmm/yy" )'),
                     icon_row('▲', '_Alta & " de " & _Qtd', '"meses em alta"')])}
        )
""", F_HTM, "Card executivo: taxa do último mês, aceleração vs mês anterior e contexto.")

# ---- Card 2: acumulado no ano
m("HTML KPI Acum. Ano", f"""
    VAR _Nome  = [Indicador Selecionado]
    VAR _Data  = [KPI Data Referência]
    VAR _Valor = [KPI Acum. Ano %]
    VAR _AA    = [KPI Acum. Ano Mesmo Período Ano Anterior %]
    VAR _Delta = [KPI Δ Acum. Ano (p.p.)]
    VAR _Qtd   = [KPI Meses Apurados no Ano]
    VAR _Media = IF ( _Qtd > 0, POWER ( 1 + _Valor, 1 / _Qtd ) - 1 )
    {split_value('_Valor', 'FORMAT ( _Valor * 100, "0.00" )')}
    VAR _ValorHtml = _Int & "<span style='color:{C['dec']};'>" & _Dec & "%</span>"
    {badge_dax('_Delta', '"vs jan–" & ' + mmmyy('EDATE ( _Data, -12 )') + ' & " (" & ' + pct('_AA') + ' & ")"')}
    VAR _Nota =
        IF ( ISBLANK ( _AA ), "Sem ano anterior para comparar",
            "Mesmo período de " & YEAR ( _Data ) - 1 & ": " & {pct('_AA')} )
    RETURN
        IF ( ISBLANK ( _Valor ), {NODATA},
        {card_shell('"Acumulado no ano"', '"jan–" & FORMAT ( _Data, "mmm/yyyy" )', '_ValorHtml', '_Badge', '_Nota',
                    [icon_row('Σ', '_Qtd & IF ( _Qtd = 1, " mês", " meses" )', '"apurados no ano"'),
                     icon_row('≈', pct('_Media'), '"média mensal"')])}
        )
""", F_HTM, "Card executivo: acumulado no ano vs mesmo período do ano anterior.")

# ---- Card 3: 12 meses
m("HTML KPI 12M", f"""
    VAR _Data  = [KPI Data Referência]
    VAR _Valor = [KPI 12M %]
    VAR _Jan   = [KPI 12M Janela Anterior %]
    VAR _Delta = [KPI Δ 12M vs Janela Anterior (p.p.)]
    VAR _MesAnt = [KPI 12M Mês Anterior %]
    VAR _DMes  = [KPI Δ 12M vs Mês Anterior (p.p.)]
    VAR _Media = [KPI Média Mensal 12M %]
    {split_value('_Valor', 'FORMAT ( _Valor * 100, "0.00" )')}
    VAR _ValorHtml = _Int & "<span style='color:{C['dec']};'>" & _Dec & "%</span>"
    {badge_dax('_Delta', '"vs 12M anteriores (" & ' + pct('_Jan') + ' & ")"')}
    VAR _Nota =
        IF ( ISBLANK ( _Jan ), "Sem janela anterior completa",
            {mmmyy('EDATE ( _Data, -23 )')} & "–" & {mmmyy('EDATE ( _Data, -12 )')} & ": " & {pct('_Jan')} )
    RETURN
        IF ( ISBLANK ( _Valor ), {NODATA},
        {card_shell('"Acumulado 12 meses"', mmmyy('EDATE ( _Data, -11 )') + ' & "–" & ' + mmmyy('_Data'), '_ValorHtml', '_Badge', '_Nota',
                    [icon_row('⇅', 'IF ( ISBLANK ( _DMes ), "–", FORMAT ( _DMes, "+0.00;-0.00;0.00" ) & " p.p." )', '"vs mês anterior"'),
                     icon_row('≈', pct('_Media'), '"média mensal"')])}
        )
""", F_HTM, "Card executivo: acumulado 12M vs janela de 12 meses anterior.")

# ---- Card 4: meta (IPCA)
m("HTML KPI Meta", f"""
    VAR _Data   = [_Data Referência IPCA]
    VAR _IPCA   = [IPCA 12M %]
    VAR _Meta   = [Meta Ano %]
    VAR _Piso   = [Limite Inferior %]
    VAR _Teto   = [Limite Superior %]
    VAR _DMeta  = [Desvio vs Meta (p.p.)]
    VAR _DTeto  = [Desvio vs Teto (p.p.)]
    VAR _Status = [Status Meta]
    VAR _Cons   = [Meses Consecutivos Acima do Teto]
    VAR _Tipo   = CALCULATE ( MAX ( dMeta[TipoMeta] ), dMeta[Ano] = YEAR ( _Data ) )
    {split_value('_DMeta', 'FORMAT ( _DMeta, "+0.00;-0.00;0.00" )')}
    VAR _ValorHtml = _Int & "<span style='color:{C['dec']};'>" & _Dec & "</span><span style='font-size:15px;color:{C['fg2']};font-weight:600;'> p.p.</span>"
    VAR _SBg = SWITCH ( _Status, "Acima do teto", "{C['rbg']}", "Abaixo do piso", "{C['rbg']}", "{C['gbg']}" )
    VAR _SFg = SWITCH ( _Status, "Acima do teto", "{C['rfg']}", "Abaixo do piso", "{C['rfg']}", "{C['gfg']}" )
    VAR _STxt =
        SWITCH ( _Status,
            "Acima do teto", "↑ " & FORMAT ( _DTeto, "0.00" ) & " p.p. acima do teto",
            "Abaixo do piso", "↓ abaixo do piso",
            "Dentro do intervalo" )
    VAR _Suf =
        IF ( _Status = "Acima do teto",
            "há " & _Cons & IF ( _Cons = 1, " mês", " meses" ),
            "piso–teto " & FORMAT ( _Piso, "0.0%" ) & "–" & FORMAT ( _Teto, "0.0%" ) )
    VAR _Badge =
        "<span style='display:inline-block;background:" & _SBg & ";color:" & _SFg & ";padding:3px 9px;border-radius:8px;font-size:12px;font-weight:600;white-space:nowrap;'>" & _STxt & "</span>"
        & "<span style='font-size:11.5px;color:{C['fg2']};margin-left:8px;'>" & _Suf & "</span>"
    -- régua 0% → teto + 2 p.p.: faixa lilás = intervalo de tolerância; traço = meta; ponto = IPCA 12M
    VAR _Max   = _Teto + 0.02
    VAR _PosP  = DIVIDE ( _Piso, _Max ) * 100
    VAR _PosT  = DIVIDE ( _Teto, _Max ) * 100
    VAR _PosM  = DIVIDE ( _Meta, _Max ) * 100
    VAR _PosI  = MIN ( MAX ( DIVIDE ( _IPCA, _Max ) * 100, 0 ), 100 )
    VAR _Regua =
        "<div style='position:relative;height:8px;border-radius:4px;background:{C['nbg']};margin:12px 0 2px 0;'>"
        & "<div style='position:absolute;left:" & FORMAT ( _PosP, "0.0", "en-US" ) & "%;width:" & FORMAT ( _PosT - _PosP, "0.0", "en-US" ) & "%;top:0;bottom:0;background:{C['lil']};border-radius:4px;'></div>"
        & "<div style='position:absolute;left:" & FORMAT ( _PosM, "0.0", "en-US" ) & "%;top:-2px;width:2px;height:12px;background:{C['vio2']};'></div>"
        & "<div style='position:absolute;left:calc(" & FORMAT ( _PosI, "0.0", "en-US" ) & "% - 7px);top:-3px;width:14px;height:14px;border-radius:50%;background:{C['vio']};border:2px solid #FFFFFF;box-sizing:border-box;'></div>"
        & "</div>"
    VAR _Nota =
        "IPCA 12M <b style='color:{C['fg']};'>" & {pct('_IPCA')} & "</b> · meta " & {pct('_Meta')} & " (" & LOWER ( _Tipo ) & ")"
    RETURN
        IF ( ISBLANK ( _IPCA ) || ISBLANK ( _Meta ), {NODATA},
            "<div style='font-family:{FONT};height:100%;box-sizing:border-box;padding:14px 18px 12px 18px;display:flex;flex-direction:column;'>"
            & "<div style='display:flex;justify-content:space-between;align-items:center;'>"
                & "<div style='font-size:14.5px;font-weight:600;color:{C['fg']};white-space:nowrap;'>Distância da meta</div>"
                & "<div style='font-size:11px;color:{C['fg']};border:1px solid {C['bord']};border-radius:14px;padding:3px 10px;white-space:nowrap;'>CMN " & YEAR ( _Data ) & "</div>"
            & "</div>"
            & "<div style='font-size:32px;font-weight:700;color:{C['fg']};letter-spacing:-0.6px;margin:6px 0 5px 0;line-height:1.1;'>" & _ValorHtml & "</div>"
            & "<div>" & _Badge & "</div>"
            & _Regua
            & "<div style='font-size:11.5px;color:{C['fg2']};margin-top:auto;padding-top:6px;border-top:1px solid #F0EFF5;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>" & _Nota & "</div>"
            & "</div>"
        )
""", F_HTM, "Card executivo: IPCA 12M vs meta do CMN (desvio em p.p., status e régua piso–meta–teto).")

# ---- Cabeçalhos (um por página)
def header(nome, titulo, subtitulo):
    m(f"HTML Cabeçalho {nome}", f"""
        VAR _UltIPCA = CALCULATE ( [_Data Referência IPCA], REMOVEFILTERS ( dCalendario ) )
        VAR _Carga   = MAX ( _ControleCarga[DataHoraCarga] )
        VAR _Chip = "<span style='display:inline-flex;align-items:center;gap:6px;font-size:11.5px;color:{C['fg']};background:#FFFFFF;border:1px solid {C['bord']};border-radius:14px;padding:3px 10px;margin-right:8px;white-space:nowrap;'>"
        RETURN
            "<div style='font-family:{FONT};height:100%;box-sizing:border-box;overflow:hidden;display:flex;flex-direction:column;justify-content:center;'>"
            & "<div style='display:flex;align-items:center;gap:10px;'>"
                & "<div style='width:28px;height:28px;border-radius:9px;background:{C['vio']};color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;'>%</div>"
                & "<div style='font-size:21px;font-weight:700;color:{C['fg']};letter-spacing:-0.3px;'>{titulo}</div>"
                & "<div style='font-size:13px;color:{C['fg2']};margin-left:4px;'>{subtitulo}</div>"
            & "</div>"
            & "<div style='margin-top:5px;white-space:nowrap;overflow:hidden;'>"
                & _Chip & "<span style='width:7px;height:7px;border-radius:50%;background:{C['vio']};display:inline-block;'></span>Último período econômico: <b>" & FORMAT ( _UltIPCA, "mmm/yyyy" ) & "</b></span>"
                & _Chip & "<span style='width:7px;height:7px;border-radius:50%;background:{C['vio2']};display:inline-block;'></span>Base atualizada em " & FORMAT ( _Carga, "dd/mm/yyyy hh:nn" ) & "</span>"
                & "<span style='font-size:11px;color:{C['fg2']};'>Fontes: BCB/SGS · IBGE/SIDRA · Focus · CMN</span>"
            & "</div>"
            & "</div>"
    """, F_HTM, f"Cabeçalho da página {titulo}: título, último período econômico e data da carga (distintos).")


header("Visão Geral", "Monitor de Inflação", "Brasil · séries mensais oficiais")
header("Composição", "Composição do IPCA", "9 grupos · variação, peso e contribuição")
header("Comparativos", "Comparativos", "IPCA × INPC × IGP-M · livres × monitorados")
header("Expectativas", "Expectativas e Juros", "Focus · Selic · juro real ex-post")
header("Metodologia", "Metodologia e Qualidade", "Cargas, conferências e regras de cálculo")

# ---- Centro da rosca
m("HTML Centro Rosca", f"""
    VAR _Tot = [Contribuição Total (p.p.)] / 100
    VAR _N   = [Grupos com Dado]
    {split_value('_Tot', 'FORMAT ( _Tot * 100, "0.00" )')}
    RETURN
        IF ( NOT ISBLANK ( _Tot ),
            "<div style='font-family:{FONT};text-align:center;line-height:1.15;'>"
            & "<div style='font-size:11.5px;color:{C['fg2']};'>IPCA do mês</div>"
            & "<div style='font-size:26px;font-weight:700;color:{C['fg']};letter-spacing:-0.5px;'>" & _Int & "<span style='color:{C['dec']};'>" & _Dec & "%</span></div>"
            & "<div style='font-size:10.5px;color:{C['fg2']};'>Σ variação × peso</div>"
            & "</div>" )
""", F_HTM, "Texto central da rosca: IPCA do mês reconstruído pela soma das contribuições.")

# ---- Insights
m("HTML Insights", f"""
    VAR _Nome  = [Indicador Selecionado]
    VAR _Data  = [KPI Data Referência]
    VAR _Mes   = [KPI Mensal %]
    VAR _Ant   = [KPI Mensal Mês Anterior %]
    VAR _DMes  = [KPI Δ Mensal (p.p.)]
    VAR _DataI = [_Data Referência IPCA]
    VAR _IPCA12 = [IPCA 12M %]
    VAR _Meta  = [Meta Ano %]
    VAR _Piso  = [Limite Inferior %]
    VAR _Teto  = [Limite Superior %]
    VAR _DTeto = [Desvio vs Teto (p.p.)]
    VAR _DMeta = [Desvio vs Meta (p.p.)]
    VAR _Cons  = [Meses Consecutivos Acima do Teto]
    VAR _DataG = CALCULATE ( [_Data Referência Grupos], REMOVEFILTERS ( dGrupoIPCA ) )
    VAR _GP    = [Grupo de Maior Pressão]
    VAR _GPc   = [Contribuição do Grupo de Maior Pressão (p.p.)]
    VAR _GPv   = [Variação do Grupo de Maior Pressão %]
    VAR _GPp   = [Peso do Grupo de Maior Pressão %]
    VAR _Tot   = [Contribuição Total (p.p.)]
    VAR _GA    = [Grupo de Maior Alívio]
    VAR _GAc   = [Contribuição do Grupo de Maior Alívio (p.p.)]
    VAR _Alta  = [Grupos em Alta]
    VAR _NG    = [Grupos com Dado]
    VAR _Amp   = [Amplitude entre Grupos (p.p.)]
    VAR _GMax  = [Grupo de Maior Alta]
    VAR _VMax  = [Variação do Grupo de Maior Alta %]
    VAR _GMin  = [Grupo de Maior Queda]
    VAR _VMin  = [Variação do Grupo de Maior Queda %]
    VAR _PP = "+0.00;-0.00;0.00"
    VAR _Tag = "<span style='font-size:10.5px;color:{C['vio']};background:{C['lil']};border-radius:6px;padding:1px 6px;margin-left:6px;white-space:nowrap;'>"
    VAR _Li  = "<div style='display:flex;gap:9px;margin-bottom:6px;'><div style='width:6px;height:6px;min-width:6px;border-radius:50%;background:{C['vio']};margin-top:6px;'></div><div>"
    VAR _I1 =
        IF ( NOT ISBLANK ( _DMes ),
            _Li & "<b>" & _Nome & "</b> "
            & SWITCH ( TRUE (), _DMes > 0, "acelerou", _DMes < 0, "desacelerou", "ficou estável" )
            & " de " & {pct('_Ant')} & " para <b>" & {pct('_Mes')} & "</b> ("
            & FORMAT ( _DMes, _PP ) & " p.p.)" & _Tag & {mmmyy('EDATE ( _Data, -1 )')} & " → " & {mmmyy('_Data')} & "</span></div></div>" )
    VAR _I2 =
        IF ( NOT ISBLANK ( _IPCA12 ) && NOT ISBLANK ( _Teto ),
            _Li & "IPCA em 12 meses: <b>" & {pct('_IPCA12')} & "</b>, "
            & SWITCH ( TRUE (),
                _IPCA12 > _Teto, "<b style='color:{C['rfg']};'>" & FORMAT ( _DTeto, "0.00" ) & " p.p. acima do teto</b> de " & {pct('_Teto')}
                    & IF ( _Cons > 1, " há " & _Cons & " meses seguidos", "" ),
                _IPCA12 < _Piso, "<b style='color:{C['rfg']};'>abaixo do piso</b> de " & {pct('_Piso')},
                "<b style='color:{C['gfg']};'>dentro do intervalo</b>, " & FORMAT ( _DMeta, _PP ) & " p.p. vs meta de " & {pct('_Meta')} )
            & _Tag & {mmmyy('_DataI')} & "</span></div></div>" )
    VAR _I3 =
        IF ( NOT ISBLANK ( _GP ),
            _Li & "<b>" & _GP & "</b> foi a maior pressão: " & FORMAT ( _GPc, _PP ) & " p.p. dos "
            & FORMAT ( _Tot, "0.00" ) & " p.p. do IPCA (variação " & {pct('_GPv')} & ", peso " & FORMAT ( _GPp, "0.0%" ) & ")"
            & IF ( _GAc < 0, "; maior alívio: " & _GA & " (" & FORMAT ( _GAc, _PP ) & " p.p.)", "" )
            & _Tag & {mmmyy('_DataG')} & "</span></div></div>" )
    VAR _I4 =
        IF ( _NG > 0,
            _Li & "<b>" & _Alta & " de " & _NG & "</b> grupos subiram no mês; amplitude de " & FORMAT ( _Amp, "0.00" )
            & " p.p. entre " & _GMax & " (" & {pct('_VMax')} & ") e " & _GMin & " (" & {pct('_VMin')} & ")"
            & _Tag & {mmmyy('_DataG')} & "</span></div></div>" )
    RETURN
        "<div style='font-family:{FONT};height:100%;box-sizing:border-box;padding:12px 18px;color:{C['fg']};font-size:11.5px;line-height:1.38;'>"
        & "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
            & "<div style='font-size:15px;font-weight:600;'>Insights do período</div>"
            & "<div style='font-size:10.5px;color:{C['fg2']};'>calculados a partir dos dados · sem inferência causal</div>"
        & "</div>"
        & _I1 & _I2 & _I3 & _I4
        & "</div>"
""", F_HTM, "Observações calculadas (aceleração, meta, maior pressão, difusão/amplitude) com número e período.")


# ---- mini cards (páginas 2–4)
def mini(nome, titulo, valor_dax, tipo, sub_dax, desc):
    if tipo == "pct":
        vh = f"""{split_value('_V', 'FORMAT ( _V * 100, "0.00" )')}
    VAR _VH = _Int & "<span style='color:{C['dec']};'>" & _Dec & "%</span>\""""
    elif tipo == "pp":
        vh = f"""{split_value('_V', 'FORMAT ( _V, "+0.00;-0.00;0.00" )')}
    VAR _VH = _Int & "<span style='color:{C['dec']};'>" & _Dec & "</span><span style='font-size:13px;color:{C['fg2']};'> p.p.</span>\""""
    else:
        vh = 'VAR _VH = _V'
    m(f"HTML Mini {nome}", f"""
        VAR _V = {valor_dax}
        {vh}
        RETURN
            IF ( ISBLANK ( _V ), {NODATA},
                "<div style='font-family:{FONT};height:100%;box-sizing:border-box;padding:12px 16px;display:flex;flex-direction:column;justify-content:space-between;'>"
                & "<div style='font-size:12.5px;font-weight:600;color:{C['fg2']};'>{titulo}</div>"
                & "<div style='font-size:{'24' if tipo != 'text' else '19'}px;font-weight:700;color:{C['fg']};letter-spacing:-0.4px;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>" & _VH & "</div>"
                & "<div style='font-size:11px;color:{C['fg2']};line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>" & {sub_dax} & "</div>"
                & "</div>" )
    """, F_HTM, desc)


DG = 'FORMAT ( CALCULATE ( [_Data Referência Grupos], REMOVEFILTERS ( dGrupoIPCA ) ), "mmm/yyyy" )'
mini("Contribuição Total", "IPCA do mês (Σ grupos)", "[Contribuição Total (p.p.)] / 100", "pct",
     f'"Soma de variação × peso · " & {DG}', "Mini card: IPCA reconstruído pelos grupos.")
mini("Maior Pressão", "Maior pressão (contribuição)", "[Grupo de Maior Pressão]", "text",
     'FORMAT ( [Contribuição do Grupo de Maior Pressão (p.p.)], "+0.00;-0.00" ) & " p.p. · variação " & FORMAT ( [Variação do Grupo de Maior Pressão %], "0.00%" )',
     "Mini card: grupo de maior contribuição ponderada.")
mini("Maior Alta", "Maior variação no mês", "[Grupo de Maior Alta]", "text",
     'FORMAT ( [Variação do Grupo de Maior Alta %], "0.00%" ) & " · maior queda: " & [Grupo de Maior Queda] & " " & FORMAT ( [Variação do Grupo de Maior Queda %], "0.00%" )',
     "Mini card: grupo de maior variação percentual (≠ maior contribuição).")
mini("Difusão", "Difusão entre grupos", "[Difusão de Alta %]", "pct",
     '[Grupos em Alta] & " de " & [Grupos com Dado] & " grupos em alta · amplitude " & FORMAT ( [Amplitude entre Grupos (p.p.)], "0.00" ) & " p.p."',
     "Mini card: % de grupos com variação positiva.")
DI = 'FORMAT ( [_Data Referência IPCA], "mmm/yyyy" )'
mini("IPCA 12M", "IPCA · 12 meses", "[IPCA 12M %]", "pct",
     f'"Acum. ano " & FORMAT ( [IPCA Acum. Ano %], "0.00%" ) & " · " & {DI}', "Mini card IPCA 12M.")
mini("INPC 12M", "INPC · 12 meses", "[INPC 12M %]", "pct",
     '"Acum. ano " & FORMAT ( [INPC Acum. Ano %], "0.00%" ) & " · spread IPCA " & FORMAT ( [Spread IPCA − INPC (p.p.)], "+0.00;-0.00;0.00" ) & " p.p."', "Mini card INPC 12M.")
mini("IGP-M 12M", "IGP-M · 12 meses", "[IGP-M 12M %]", "pct",
     '"Acum. ano " & FORMAT ( [IGP-M Acum. Ano %], "0.00%" ) & " · spread IPCA " & FORMAT ( [Spread IPCA − IGP-M (p.p.)], "+0.00;-0.00;0.00" ) & " p.p."', "Mini card IGP-M 12M.")
mini("Livres x Monitorados", "Livres − Monitorados (12M)", "( [IPCA Livres 12M %] - [IPCA Monitorados 12M %] ) * 100", "pp",
     '"Livres " & FORMAT ( [IPCA Livres 12M %], "0.00%" ) & " · Monitorados " & FORMAT ( [IPCA Monitorados 12M %], "0.00%" )', "Mini card: diferença livres × monitorados em 12M.")
DF = 'FORMAT ( [_Data Referência Focus], "mmm/yyyy" )'
mini("Focus Ano", "Focus · IPCA ano corrente", "[Focus Mediana Ano Corrente]", "pct",
     f'"Coleta " & {DF} & " · no início do ano " & FORMAT ( [Focus Mediana Início do Ano], "0.00%" )', "Mini card Focus ano corrente.")
mini("Focus Próximo", "Focus · IPCA próximo ano", "[Focus Mediana Próximo Ano]", "pct",
     f'"Mediana · coleta " & {DF}', "Mini card Focus próximo ano.")
mini("Selic", "Selic (% a.a.)", "[Selic % a.a.]", "pct",
     '"Série 4189 · Selic 12M " & FORMAT ( [Selic 12M %], "0.00%" )', "Mini card Selic.")
mini("Juro Real", "Juro real ex-post (12M)", "[Juro Real Ex-Post %]", "pct",
     f'"(1+Selic 12M)/(1+IPCA 12M)−1 · " & {DI}', "Mini card juro real ex-post.")
mini("Checagem", "Conferência IPCA 12M × SGS 13522", "IF ( NOT ISBLANK ( [IPCA 12M %] ), [Checagem Meses Divergentes] & \" mês(es) divergente(s)\" )", "text",
     '"Tolerância 0,01 p.p. · último mês " & FORMAT ( [Checagem IPCA 12M (p.p.)], "+0.00;-0.00;0.00" ) & " p.p."', "Mini card: resultado da conferência do 12M.")


# ---------------------------------------------------------------- render TMDL
def render():
    out = []
    for x in MEASURES:
        lt = uuid.uuid5(NS, x["name"])
        out.append(f"\t/// {x['desc']}")
        out.append(f"\tmeasure '{x['name'].replace(chr(39), chr(39)*2)}' =")
        lines = [l for l in x["expr"].splitlines() if l.strip()]
        base = len(lines[0]) - len(lines[0].lstrip())
        for line in lines:
            ind = len(line) - len(line.lstrip())
            # TMDL: nenhuma linha pode ficar menos indentada que a primeira da expressão
            out.append("\t\t\t" + " " * max(0, ind - base) + line.lstrip())
        if x["fmt"]:
            out.append(f"\t\tformatString: {x['fmt']}")
        if x["hidden"]:
            out.append("\t\tisHidden")
        out.append(f"\t\tdisplayFolder: {x['folder']}")
        out.append(f"\t\tlineageTag: {lt}")
        out.append("")
    return "\n".join(out) + "\n"




# ---------------------------------------------------------------- cores fixas por grupo (rosca + legenda)
GRP = [  # (grupo, cor, nome curto)
    ("Alimentação e bebidas", "#8064F5", "Alimentação"),
    ("Habitação", "#5B45D6", "Habitação"),
    ("Transportes", "#B8A6FA", "Transportes"),
    ("Saúde e cuidados pessoais", "#3A3946", "Saúde"),
    ("Despesas pessoais", "#9D8CF7", "Desp. pessoais"),
    ("Educação", "#D9D0FD", "Educação"),
    ("Vestuário", "#85838F", "Vestuário"),
    ("Comunicação", "#C9C7D1", "Comunicação"),
    ("Artigos de residência", "#6E6C78", "Art. residência"),
]
_sw_cor = "SWITCH ( dGrupoIPCA[Grupo], " + ", ".join(f'"{g}", "{c}"' for g, c, _ in GRP) + ', "#C9C7D1" )'
_sw_nom = "SWITCH ( dGrupoIPCA[Grupo], " + ", ".join(f'"{g}", "{s}"' for g, _, s in GRP) + ", dGrupoIPCA[Grupo] )"
m("HTML Legenda Pesos", f"""
    VAR _T =
        FILTER (
            ADDCOLUMNS (
                ALL ( dGrupoIPCA ),
                "@p", [Peso Grupo %],
                "@cor", {_sw_cor},
                "@nome", {_sw_nom}
            ),
            NOT ISBLANK ( [@p] )
        )
    RETURN
        IF ( NOT ISEMPTY ( _T ),
            "<div style='font-family:{FONT};display:grid;grid-template-columns:1fr 1fr;gap:7px 14px;padding:2px 16px;font-size:11px;color:{C['fg']};'>"
            & CONCATENATEX (
                _T,
                "<div style='display:flex;align-items:center;gap:6px;min-width:0;' title='" & dGrupoIPCA[Grupo] & "'>"
                    & "<span style='width:9px;height:9px;min-width:9px;border-radius:50%;background:" & [@cor] & ";'></span>"
                    & "<span style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>" & [@nome] & "</span>"
                    & "<span style='margin-left:auto;color:{C['fg2']};'>" & FORMAT ( [@p], "0.0%" ) & "</span></div>",
                "",
                [@p], DESC
            )
            & "</div>" )
""", F_HTM, "Legenda da rosca (2 colunas, ordenada por peso) com as mesmas cores fixas por grupo.")


if __name__ == "__main__":
    import sys
    open(sys.argv[1], "w", encoding="utf-8").write(render())
    print(len(MEASURES), "medidas")
