# -*- coding: utf-8 -*-
"""Gera MonitorInflacao.Report/definition (PBIR) + tema 'Violeta' para o Monitor de Inflação."""
import json, os, hashlib, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from medidas import C, GRP

OUT = sys.argv[1]  # pasta MonitorInflacao.Report
VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
HTML = "htmlContent443BE3AD55E043BF878BED274D3A6855"
M = "_Medidas"
PAGE_BG = "#F4F3F8"
THEME_NAME = "Monitor_de_Inflacao_Violeta.json"


# ------------------------------------------------------------------ helpers de expressão
def lit(v):
    if isinstance(v, bool):
        s = "true" if v else "false"
    elif isinstance(v, (int, float)):
        s = f"{v}D"
    else:
        s = "'" + str(v).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": s}}}


def color(hexv):
    return {"solid": {"color": lit(hexv)}}


def col(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def meas(prop, entity=M):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def proj(field, display=None):
    k = "Column" if "Column" in field else "Measure"
    ent = field[k]["Expression"]["SourceRef"]["Entity"]
    prop = field[k]["Property"]
    p = {"field": field, "queryRef": f"{ent}.{prop}", "nativeQueryRef": prop}
    if display:
        p["displayName"] = display
    return p


def qref(field):
    k = "Column" if "Column" in field else "Measure"
    return f"{field[k]['Expression']['SourceRef']['Entity']}.{field[k]['Property']}"


def props(**kw):
    return [{"properties": kw}]


def container(title=None, title_measure=None, bg=True, border=True, radius=16, padding=None, header=False):
    o = {
        "background": props(show=lit(bg), color=color("#FFFFFF"), transparency=lit(0)),
        "border": props(show=lit(border), color=color(C["bord"]), radius=lit(radius), width=lit(1)),
        "dropShadow": props(show=lit(False)),
        "visualHeader": props(show=lit(header)),
    }
    if title or title_measure:
        t = dict(show=lit(True), fontColor=color(C["fg"]), fontSize=lit(12), bold=lit(True),
                 fontFamily=lit("Segoe UI Semibold"), alignment=lit("left"))
        if title_measure:
            t["text"] = {"expr": meas(title_measure)}
        else:
            t["text"] = lit(title)
        o["title"] = [{"properties": t}]
    else:
        o["title"] = props(show=lit(False))
    if padding is not None:
        o["padding"] = props(top=lit(padding[0]), bottom=lit(padding[1]), left=lit(padding[2]), right=lit(padding[3]))
    return o


class Page:
    def __init__(self, name, display, ptype=None):
        self.name, self.display, self.visuals, self.z = name, display, [], 0
        self.ptype = ptype

    def add(self, vtype, x, y, w, h, query=None, objects=None, vco=None, sort=None, filters=None,
            sync=None, alt=None):
        self.z += 1000
        seed = f"{self.name}-{len(self.visuals)}-{vtype}"
        vid = hashlib.sha1(seed.encode()).hexdigest()[:20]
        v = {"visualType": vtype}
        if query:
            v["query"] = {"queryState": query}
            if sort:
                v["query"]["sortDefinition"] = {"sort": sort, "isDefaultSort": False}
        if objects:
            v["objects"] = objects
        vco = vco or container()
        if alt:
            vco["general"] = props(altText=lit(alt))
        v["visualContainerObjects"] = vco
        if sync:
            v["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
        vis = {"$schema": VC_SCHEMA, "name": vid,
               "position": {"x": x, "y": y, "z": self.z, "height": h, "width": w, "tabOrder": self.z},
               "visual": v}
        if filters:
            vis["filterConfig"] = {"filters": filters}
        self.visuals.append(vis)
        return vis


def qs(**roles):
    return {r: {"projections": ps} for r, ps in roles.items()}


# ------------------------------------------------------------------ fábricas de visuais
def html(page, measure, x, y, w, h, vco=None, alt=None):
    objs = {"contentFormatting": props(showRawHtml=lit(False), fontFamily=lit("Segoe UI"), fontSize=lit(12),
                                        fontColour=color(C["fg"]), noDataMessage=lit(" "))}
    return page.add(HTML, x, y, w, h, qs(content=[proj(meas(measure))]), objs,
                    vco or container(padding=(0, 0, 0, 0)), alt=alt)


def textbox(page, x, y, w, h, paragraphs, vco=None):
    return page.add("textbox", x, y, w, h, None, {"general": props(paragraphs=paragraphs)},
                    vco or container(bg=False, border=False))


def run(text, size=10, bold=False, col_=None):
    st = {"fontSize": f"{size}pt", "fontFamily": "Segoe UI", "color": col_ or C["fg"]}
    if bold:
        st["fontWeight"] = "bold"
    return {"value": text, "textStyle": st}


def slicer(page, field, x, y, w, h, title, single=False, sync=None, filters=None):
    objs = {
        "data": props(mode=lit("Dropdown")),
        "header": props(show=lit(True), text=lit(title), fontColor=color(C["fg2"]), textSize=lit(9),
                        fontFamily=lit("Segoe UI")),
        "items": props(fontColor=color(C["fg"]), textSize=lit(10), fontFamily=lit("Segoe UI"),
                       background=color("#FFFFFF")),
        "selection": props(singleSelect=lit(single), selectAllCheckboxEnabled=lit(not single)),
    }
    return page.add("slicer", x, y, w, h, qs(Values=[proj(field)]), objs,
                    container(radius=12, padding=(4, 4, 10, 10)), filters=filters, sync=sync,
                    alt=f"Filtro de {title.lower()}")


def axis_objs(value_axis=True, cat_axis=True, legend=True, legend_pos="TopRight"):
    o = {
        "categoryAxis": props(show=lit(cat_axis), showAxisTitle=lit(False), gridlineShow=lit(False),
                              labelColor=color(C["fg2"]), fontSize=lit(9), fontFamily=lit("Segoe UI")),
        "valueAxis": props(show=lit(value_axis), showAxisTitle=lit(False), gridlineShow=lit(True),
                           gridlineColor=color("#ECEBF2"), gridlineStyle=lit("dotted"),
                           labelColor=color(C["fg2"]), fontSize=lit(9), fontFamily=lit("Segoe UI")),
        "legend": props(show=lit(legend), position=lit(legend_pos), showTitle=lit(False),
                        labelColor=color(C["fg2"]), fontSize=lit(9), fontFamily=lit("Segoe UI")),
    }
    return o


def line_chart(page, x, y, w, h, series, title=None, title_measure=None, tooltips=None, smooth=True, alt=None):
    """series: lista de (medida, nome, cor, estilo['solid'|'dashed'|'dotted'], espessura, marcador)"""
    o = axis_objs()
    o["categoryAxis"][0]["properties"]["axisType"] = lit("Scalar")
    o["lineStyles"] = props(strokeWidth=lit(2), lineChartType=lit("smooth" if smooth else "linear"), showMarker=lit(False))
    o["dataPoint"] = []
    for mname, nome, cor, estilo, esp, marc in series:
        sel = {"metadata": f"{M}.{mname}"}
        o["dataPoint"].append({"properties": {"fill": color(cor)}, "selector": sel})
        lp = {"strokeWidth": lit(esp), "lineStyle": lit(estilo), "showMarker": lit(marc)}
        if marc:
            lp.update(markerShape=lit("circle"), markerSize=lit(5), markerColor=color(cor))
        o["lineStyles"].append({"properties": lp, "selector": sel})
    o["labels"] = props(show=lit(False))
    roles = {"Category": [proj(col("dCalendario", "Data"), "Mês")],
             "Y": [proj(meas(s[0]), s[1]) for s in series]}
    if tooltips:
        roles["Tooltips"] = [proj(meas(t[0]), t[1]) for t in tooltips]
    return page.add("lineChart", x, y, w, h, qs(**roles), o,
                    container(title=title, title_measure=title_measure, padding=(6, 6, 10, 12)),
                    sort=[{"field": col("dCalendario", "Data"), "direction": "Ascending"}], alt=alt)


def bar_chart(page, vtype, x, y, w, h, cat_field, measure, title=None, title_measure=None, color_measure=None,
              fixed=None, tooltips=None, sort_desc=True, labels=True, alt=None):
    o = axis_objs(value_axis=False, legend=False)
    o["categoryAxis"][0]["properties"].update(maxMarginFactor=lit(40), innerPadding=lit(10), fontSize=lit(8))
    if color_measure:
        o["dataPoint"] = [{"properties": {"fill": {"solid": {"color": {"expr": meas(color_measure)}}}},
                           "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}]
    else:
        o["dataPoint"] = props(defaultColor=color(fixed or C["vio"]))
    o["labels"] = props(show=lit(labels), color=color(C["fg"]), fontSize=lit(8), fontFamily=lit("Segoe UI"))
    roles = {"Category": [proj(cat_field)], "Y": [proj(meas(measure))]}
    if tooltips:
        roles["Tooltips"] = [proj(meas(t)) for t in tooltips]
    return page.add(vtype, x, y, w, h, qs(**roles), o,
                    container(title=title, title_measure=title_measure, padding=(6, 6, 10, 12)),
                    sort=[{"field": meas(measure), "direction": "Descending" if sort_desc else "Ascending"}],
                    alt=alt)


def column_multi(page, vtype, x, y, w, h, cat_field, series, title, legend=True, sort_cat=True, alt=None,
                 series_field=None, labels=False):
    o = axis_objs(legend=legend)
    o["dataPoint"] = [{"properties": {"fill": color(cor)}, "selector": {"metadata": f"{M}.{mn}"}} for mn, _, cor in series]
    o["labels"] = props(show=lit(labels), color=color(C["fg"]), fontSize=lit(8))
    roles = {"Category": [proj(cat_field)], "Y": [proj(meas(mn), nome) for mn, nome, _ in series]}
    if series_field:
        roles["Series"] = [proj(series_field)]
        o["dataPoint"] = [{"properties": {"fill": color(c)},
                           "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": series_field,
                                                                             "Right": {"Literal": {"Value": "'" + g + "'"}}}}}]}}
                          for g, c, _ in GRP]
    return page.add(vtype, x, y, w, h, qs(**roles), o, container(title=title, padding=(6, 6, 10, 12)),
                    sort=[{"field": cat_field, "direction": "Ascending"}] if sort_cat else None, alt=alt)


def table(page, x, y, w, h, fields, title, sort=None, alt=None):
    o = {
        "columnHeaders": props(fontColor=color(C["fg2"]), backColor=color("#FFFFFF"), fontSize=lit(9),
                               fontFamily=lit("Segoe UI Semibold"), outline=lit("BottomOnly")),
        "values": props(fontColor=color(C["fg"]), backColor=color("#FFFFFF"), backColorSecondary=color(C["bg2"]),
                        fontSize=lit(9), fontFamily=lit("Segoe UI")),
        "grid": props(gridHorizontal=lit(True), gridHorizontalColor=color("#F0EFF5"), gridVertical=lit(False),
                      outlineColor=color(C["bord"]), rowPadding=lit(4)),
        "total": props(totals=lit(False)),
    }
    return page.add("tableEx", x, y, w, h, qs(Values=[proj(f, d) for f, d in fields]), o,
                    container(title=title, padding=(6, 6, 10, 10)), sort=sort, alt=alt)


def cat_filter(name, entity, prop, values):
    return {"name": name, "field": col(entity, prop), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "d", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {
                           "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}}],
                           "Values": [[{"Literal": {"Value": "'" + v + "'"}}] for v in values]}}}]},
            "howCreated": "User", "isHiddenInViewMode": True}


# ------------------------------------------------------------------ grid
W, H = 1280, 720
MX, GAP = 24, 16
KW = (W - 2 * MX - 3 * GAP) // 4  # 296
KX = [MX + i * (KW + GAP) for i in range(4)]  # 24, 336, 648, 960
PAGES = []


def header(p, measure, period=True):
    html(p, f"HTML Cabeçalho {measure}", MX, 8, 740, 72, vco=container(bg=False, border=False, padding=(0, 0, 0, 0)),
         alt="Cabeçalho da página")
    if period:
        slicer(p, col("dCalendario", "Ano"), 1026, 18, 230, 52, "Período (ano)", sync="Periodo")


# ================================================================== Página 1 — Visão Geral
p = Page("VisaoGeral", "Visão Geral"); PAGES.append(p)
header(p, "Visão Geral")
slicer(p, col("dIndicador", "Indicador"), 784, 18, 230, 52, "Indicador", single=True,
       filters=[cat_filter("fltIndCategoria", "dIndicador", "Categoria", ["Inflação"]),
                cat_filter("fltIndTipo", "dIndicador", "TipoTaxa", ["Mensal"])])
KY, KH = 86, 168
html(p, "HTML KPI Mês", KX[0], KY, KW, KH, alt="Inflação do último mês e aceleração")
html(p, "HTML KPI Acum. Ano", KX[1], KY, KW, KH, alt="Inflação acumulada no ano")
html(p, "HTML KPI 12M", KX[2], KY, KW, KH, alt="Inflação acumulada em 12 meses")
html(p, "HTML KPI Meta", KX[3], KY, KW, KH, alt="Distância do IPCA 12M para a meta do CMN")
RY = KY + KH + GAP  # 250
line_chart(p, MX, RY, 3 * KW + 2 * GAP, 166,
           [("KPI 12M %", "Acumulado 12M", C["vio"], "solid", 3, False),
            ("Meta Ano %", "Meta CMN (IPCA)", C["vio2"], "dashed", 2, False),
            ("Limite Superior %", "Teto da meta", "#D9D0FD", "dotted", 2, False),
            ("Gráfico Último Ponto 12M", "Último período", C["vio"], "solid", 1, True)],
           title_measure="Título Evolução",
           tooltips=[("KPI Mensal %", "Taxa do mês"), ("KPI Acum. Ano %", "Acumulado no ano")],
           alt="Evolução do acumulado em 12 meses do indicador selecionado com meta e teto do CMN")
BY = RY + 166 + GAP
BH = H - 20 - BY     # 202
bar_chart(p, "clusteredBarChart", MX, BY, 420, BH, col("dGrupoIPCA", "Grupo"), "Contribuição Grupo (p.p.)",
          title_measure="Título Contribuição", color_measure="Cor Contribuição",
          tooltips=["Variação Grupo Mensal %", "Peso Grupo %", "Participação na Inflação %"],
          alt="Contribuição ponderada de cada grupo para o IPCA do mês")
html(p, "HTML Insights", MX + 420 + GAP, BY, 3 * KW + 2 * GAP - 420 - GAP, BH, alt="Insights calculados")
# card direito (rosca + legenda) — fundo único
RX = KX[3]
textbox(p, RX, RY, KW, H - 20 - RY, [{"textRuns": [run(" ")]}], vco=container())
donut = p.add("donutChart", RX + 6, RY + 4, KW - 12, 270,
              qs(Category=[proj(col("dGrupoIPCA", "Grupo"))], Y=[proj(meas("Peso Grupo %"), "Peso")],
                 Tooltips=[proj(meas("Variação Grupo Mensal %"), "Variação no mês"),
                           proj(meas("Contribuição Grupo (p.p.)"), "Contribuição")]),
              {"legend": props(show=lit(False)),
               "labels": props(show=lit(False)),
               "dataPoint": [{"properties": {"fill": color(c)},
                              "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0,
                                  "Left": col("dGrupoIPCA", "Grupo"), "Right": {"Literal": {"Value": "'" + g + "'"}}}}}]}}
                             for g, c, _ in GRP]},
              container(title_measure="Título Rosca Pesos", bg=False, border=False, padding=(8, 0, 10, 10)),
              sort=[{"field": meas("Peso Grupo %"), "direction": "Descending"}],
              alt="Rosca com o peso de cada grupo na cesta do IPCA")
html(p, "HTML Centro Rosca", RX + KW // 2 - 75, RY + 4 + 136, 150, 66,
     vco=container(bg=False, border=False, padding=(0, 0, 0, 0)), alt="IPCA do mês")
html(p, "HTML Legenda Pesos", RX + 6, RY + 282, KW - 12, H - 20 - RY - 290,
     vco=container(bg=False, border=False, padding=(0, 0, 0, 0)), alt="Legenda dos grupos com peso")

# ================================================================== Página 2 — Composição
p = Page("Composicao", "Composição"); PAGES.append(p)
header(p, "Composição")
MY, MH = 86, 92
for i, n in enumerate(["Contribuição Total", "Maior Pressão", "Maior Alta", "Difusão"]):
    html(p, f"HTML Mini {n}", KX[i], MY, KW, MH, alt=n)
R2 = MY + MH + GAP  # 194
half = (W - 2 * MX - GAP) // 2  # 608
bar_chart(p, "clusteredBarChart", MX, R2, half, 250, col("dGrupoIPCA", "Grupo"), "Contribuição Grupo (p.p.)",
          title_measure="Título Contribuição", color_measure="Cor Contribuição",
          tooltips=["Variação Grupo Mensal %", "Peso Grupo %", "Participação na Inflação %"],
          alt="Contribuição ponderada por grupo (variação × peso)")
bar_chart(p, "clusteredBarChart", MX + half + GAP, R2, half, 250, col("dGrupoIPCA", "Grupo"), "Variação Grupo Mensal %",
          title_measure="Título Variação Grupos", color_measure="Cor Variação Grupo",
          tooltips=["Peso Grupo %", "Contribuição Grupo (p.p.)"],
          alt="Variação percentual do mês por grupo")
R3 = R2 + 250 + GAP  # 460
column_multi(p, "columnChart", MX, R3, 700, H - 20 - R3, col("dCalendario", "Data"),
             [("Contribuição Grupo Janela 24M (p.p.)", "Contribuição", C["vio"])],
             "Contribuição mensal por grupo · últimos 24 meses (p.p.)", series_field=col("dGrupoIPCA", "Grupo"),
             alt="Colunas empilhadas da contribuição de cada grupo nos últimos 24 meses")
table(p, MX + 700 + GAP, R3, W - 2 * MX - 700 - GAP, H - 20 - R3,
      [(col("dGrupoIPCA", "Grupo"), "Grupo"), (meas("Peso Grupo %"), "Peso"),
       (meas("Variação Grupo Mensal %"), "Variação"), (meas("Contribuição Grupo (p.p.)"), "Contribuição"),
       (meas("Participação na Inflação %"), "Participação"), (meas("Ranking Grupo por Contribuição"), "Rank")],
      "Quadro dos grupos · mês de referência",
      sort=[{"field": meas("Contribuição Grupo (p.p.)"), "direction": "Descending"}],
      alt="Tabela com peso, variação, contribuição e ranking dos grupos")

# ================================================================== Página 3 — Comparativos
p = Page("Comparativos", "Comparativos"); PAGES.append(p)
header(p, "Comparativos")
for i, n in enumerate(["IPCA 12M", "INPC 12M", "IGP-M 12M", "Livres x Monitorados"]):
    html(p, f"HTML Mini {n}", KX[i], MY, KW, MH, alt=n)
line_chart(p, MX, R2, W - 2 * MX, 250,
           [("IPCA 12M %", "IPCA", C["vio"], "solid", 3, False),
            ("INPC 12M %", "INPC", C["vio2"], "solid", 2, False),
            ("IGP-M 12M %", "IGP-M", "#3A3946", "solid", 2, False),
            ("Limite Superior %", "Teto da meta (IPCA)", "#D9D0FD", "dotted", 2, False)],
           title="Acumulado em 12 meses · IPCA × INPC × IGP-M",
           alt="Comparação do acumulado 12M entre IPCA, INPC e IGP-M")
line_chart(p, MX, R3, half, H - 20 - R3,
           [("IPCA Livres 12M %", "Livres", C["vio"], "solid", 3, False),
            ("IPCA Monitorados 12M %", "Monitorados", C["vio2"], "solid", 3, False)],
           title="Preços livres × monitorados · acumulado 12M", alt="Livres versus monitorados em 12 meses")
column_multi(p, "clusteredColumnChart", MX + half + GAP, R3, half, H - 20 - R3, col("dCalendario", "Ano"),
             [("IPCA Acum. Ano %", "IPCA", C["vio"]), ("INPC Acum. Ano %", "INPC", C["vio2"]),
              ("IGP-M Acum. Ano %", "IGP-M", "#3A3946")],
             "Acumulado no ano por indicador (ano corrente até o último mês)",
             alt="Acumulado anual de IPCA, INPC e IGP-M")

# ================================================================== Página 4 — Expectativas e Juros
p = Page("Expectativas", "Expectativas e Juros"); PAGES.append(p)
header(p, "Expectativas")
for i, n in enumerate(["Focus Ano", "Focus Próximo", "Selic", "Juro Real"]):
    html(p, f"HTML Mini {n}", KX[i], MY, KW, MH, alt=n)
line_chart(p, MX, R2, half, 250,
           [("IPCA 12M %", "IPCA 12M (realizado)", C["vio"], "solid", 3, False),
            ("Focus Mediana Ano Corrente", "Focus · ano corrente", C["vio2"], "dashed", 2, False),
            ("Meta Ano %", "Meta CMN", "#D9D0FD", "dotted", 2, False)],
           title="Realizado × expectativa Focus para o ano", alt="IPCA 12M versus mediana Focus")
line_chart(p, MX + half + GAP, R2, half, 250,
           [("Juro Real Ex-Post %", "Juro real ex-post", C["vio"], "solid", 3, False),
            ("Selic 12M %", "Selic 12M", C["vio2"], "solid", 2, False)],
           title="Juro real ex-post × Selic acumulada 12M", alt="Juro real ex-post e Selic 12M")
column_multi(p, "clusteredColumnChart", MX, R3, half, H - 20 - R3, col("dCalendario", "Ano"),
             [("IPCA Acum. Ano %", "IPCA realizado no ano", C["vio"]),
              ("Focus Mediana Início do Ano", "Focus no início do ano", C["vio2"])],
             "IPCA do ano × expectativa Focus no início do ano", alt="Realizado anual versus Focus de início do ano")
column_multi(p, "clusteredColumnChart", MX + half + GAP, R3, half, H - 20 - R3, col("dCalendario", "Ano"),
             [("Focus vs Realizado (p.p.)", "Erro do Focus (p.p.)", C["vio"])],
             "Realizado − Focus de início do ano (anos fechados, p.p.)", legend=False, labels=True,
             alt="Erro de previsão do Focus por ano")

# ================================================================== Página 5 — Metodologia
p = Page("Metodologia", "Metodologia"); PAGES.append(p)
header(p, "Metodologia", period=False)
html(p, "HTML Mini Checagem", KX[0], MY, 2 * KW + GAP, MH, alt="Conferência do IPCA 12M")
table(p, MX, R2, 2 * KW + GAP, 200,
      [(col("_ControleCarga", "Fonte"), "Fonte"), (col("_ControleCarga", "DataHoraCarga"), "Carga"),
       (col("_ControleCarga", "PrimeiroMes"), "Primeiro mês"), (col("_ControleCarga", "UltimoMes"), "Último mês"),
       (col("_ControleCarga", "Linhas"), "Linhas"), (col("_ControleCarga", "Observacao"), "Obs.")],
      "Controle de carga (camada silver)", alt="Tabela de controle de carga por fonte")
NOTAS = [
    ("Regras de cálculo", True),
    ("• Acumulados sempre compostos: Π(1 + taxa mensal) − 1. Taxas mensais nunca são somadas.", False),
    ("• 12 meses só é exibido com 12 meses publicados; conferido com a série oficial SGS 13522.", False),
    ("• Diferenças entre taxas são mostradas em pontos percentuais (p.p.), não em variação relativa.", False),
    ("• Contribuição do grupo = variação do grupo × peso IBGE do mês; a soma reconstrói o IPCA.", False),
    ("• Maior variação (%) ≠ maior contribuição (p.p.): um grupo pequeno pode subir muito e pesar pouco.", False),
    ("• Meta: CMN — ano-calendário até 2024; contínua (12 meses) a partir de 2025.", False),
    ("• Último período econômico (mês da taxa) ≠ data de atualização da base (carga).", False),
    ("• Seletor de indicador: IPCA, INPC, IGP-M, Livres, Monitorados; sem seleção = IPCA.", False),
]
textbox(p, MX, R2 + 200 + GAP, 2 * KW + GAP, H - 20 - (R2 + 200 + GAP),
        [{"textRuns": [run(t, 12 if b else 9.5, b, C["fg"] if b else C["fg2"])]} for t, b in NOTAS],
        vco=container(padding=(14, 14, 18, 18)))
table(p, KX[2], MY, 2 * KW + GAP, H - 20 - MY,
      [(col("dCalendario", "AnoMes"), "Mês"), (meas("IPCA Mensal %"), "IPCA mês"),
       (meas("IPCA 12M %"), "12M calculado"), (meas("IPCA 12M % (SGS 13522)"), "12M oficial"),
       (meas("Checagem IPCA 12M (p.p.)"), "Dif."), (meas("Checagem IPCA 12M Status"), "Status")],
      "Conferência mensal · IPCA 12M calculado × SGS 13522",
      sort=[{"field": col("dCalendario", "AnoMes"), "direction": "Descending"}],
      alt="Conferência mês a mês do IPCA 12M")


# ------------------------------------------------------------------ escrita
def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


d = os.path.join(OUT, "definition")
if os.path.exists(os.path.join(d, "pages")):
    shutil.rmtree(os.path.join(d, "pages"))
for pg in PAGES:
    pj = {"$schema": PAGE_SCHEMA, "name": pg.name, "displayName": pg.display, "displayOption": "FitToPage",
          "height": H, "width": W,
          "objects": {"background": props(color=color(PAGE_BG), transparency=lit(0)),
                      "outspace": props(color=color(PAGE_BG), transparency=lit(0))}}
    wjson(os.path.join(d, "pages", pg.name, "page.json"), pj)
    for v in pg.visuals:
        wjson(os.path.join(d, "pages", pg.name, "visuals", v["name"], "visual.json"), v)
wjson(os.path.join(d, "pages", "pages.json"),
      {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
       "pageOrder": [pg.name for pg in PAGES], "activePageName": PAGES[0].name})

# report.json: troca o tema (mantém o antigo registrado, sem uso)
rp = os.path.join(d, "report.json")
r = json.load(open(rp, encoding="utf-8"))
r["themeCollection"]["customTheme"]["name"] = THEME_NAME
items = r["resourcePackages"][0]["items"]
if not any(i["name"] == THEME_NAME for i in items):
    items.append({"name": THEME_NAME, "path": THEME_NAME, "type": "CustomTheme"})
wjson(rp, r)

THEME = {
    "name": "Monitor de Inflação · Violeta",
    "dataColors": ["#8064F5", "#B8A6FA", "#3A3946", "#5B45D6", "#D9D0FD", "#85838F", "#9D8CF7", "#C9C7D1",
                   "#6E6C78", "#E7E0FF", "#1F8F4E", "#D14343"],
    "background": "#FFFFFF", "foreground": C["fg"], "tableAccent": C["vio"],
    "good": C["gfg"], "neutral": C["fg2"], "bad": C["rfg"],
    "maximum": C["vio"], "center": C["vio2"], "minimum": C["lil"],
    "textClasses": {
        "callout": {"fontSize": 28, "fontFace": "Segoe UI Semibold", "color": C["fg"]},
        "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": C["fg"]},
        "header": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": C["fg"]},
        "label": {"fontSize": 9, "fontFace": "Segoe UI", "color": C["fg2"]},
    },
    "visualStyles": {
        "*": {"*": {
            "background": [{"show": True, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}],
            "border": [{"show": True, "color": {"solid": {"color": C["bord"]}}, "radius": 16}],
            "dropShadow": [{"show": False}],
            "title": [{"fontColor": {"solid": {"color": C["fg"]}}, "fontSize": 12, "fontFamily": "Segoe UI Semibold"}],
            "visualHeader": [{"show": False}],
        }},
        "page": {"*": {"background": [{"color": {"solid": {"color": PAGE_BG}}, "transparency": 0}],
                       "outspace": [{"color": {"solid": {"color": PAGE_BG}}, "transparency": 0}]}},
    },
}
wjson(os.path.join(OUT, "StaticResources", "RegisteredResources", THEME_NAME), THEME)
print("páginas:", [(pg.display, len(pg.visuals)) for pg in PAGES], "total", sum(len(pg.visuals) for pg in PAGES))
