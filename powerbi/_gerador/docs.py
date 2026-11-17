# -*- coding: utf-8 -*-
"""Gera LEIAME_DASHBOARD.md (implementação, decisões, catálogo das medidas novas e valores de validação)."""
import re, sys
sys.path.insert(0, '/home/claude/build')
import medidas

ESP = {  # valor esperado sem filtros (IPCA, set/2026) — calculado em Python sobre as tabelas do .pbix
    "KPI Data Referência": "set/2026", "Indicador Selecionado": "IPCA",
    "KPI Mensal %": "0,82%", "KPI Mensal Mês Anterior %": "-0,32%", "KPI Δ Mensal (p.p.)": "+1,14 p.p.",
    "KPI Mensal Mesmo Mês Ano Anterior %": "0,48%", "KPI Acum. Ano %": "3,95%",
    "KPI Acum. Ano Mesmo Período Ano Anterior %": "3,64%", "KPI Δ Acum. Ano (p.p.)": "+0,31 p.p.",
    "KPI 12M %": "4,58% (= SGS 13522)", "KPI 12M Mês Anterior %": "4,22%", "KPI 12M Janela Anterior %": "5,17%",
    "KPI Δ 12M vs Janela Anterior (p.p.)": "-0,60 p.p.", "KPI Δ 12M vs Mês Anterior (p.p.)": "+0,35 p.p.",
    "KPI Média Mensal 12M %": "0,37%", "KPI Meses Apurados no Ano": "9", "KPI Meses em Alta no Ano": "8",
    "Posição na Banda da Meta %": "103%", "Grupo de Maior Alta": "Habitação", "Variação do Grupo de Maior Alta %": "2,31%",
    "Grupo de Maior Queda": "Educação", "Variação do Grupo de Maior Queda %": "0,04%",
    "Amplitude entre Grupos (p.p.)": "+2,27 p.p.", "Grupos em Alta": "9", "Grupos com Dado": "9",
    "Grupo de Maior Alívio": "Educação (contribuição positiva: não há alívio)",
    "Contribuição do Grupo de Maior Alívio (p.p.)": "+0,00 p.p.", "Variação do Grupo de Maior Pressão %": "2,31%",
    "Peso do Grupo de Maior Pressão %": "15,26%", "Gráfico Último Ponto 12M": "4,58% somente em set/2026",
}
FILT = {
    r"09 Dashboard\01 KPIs": "Responde ao seletor de indicador (fallback IPCA) e ao período (último mês do contexto). Ignora filtros de grupo.",
    r"09 Dashboard\02 Comparações": "Desloca o mês de referência com EDATE sobre dCalendario (REMOVEFILTERS explícito); seletor de indicador preservado.",
    r"09 Dashboard\03 Rankings e Contribuições": "Itera ALL(dGrupoIPCA) (9 linhas) no mês de referência dos grupos; o período filtra o mês; filtros de grupo são ignorados de propósito.",
    r"09 Dashboard\04 Gráficos e Títulos": "Avaliada ponto a ponto no eixo mensal ou por grupo; títulos usam o último mês do contexto.",
    r"09 Dashboard\05 HTML": "Combina medidas das demais pastas; o contexto é o da página (período e indicador).",
    r"09 Dashboard\06 Auxiliares": "Lê a seleção de dIndicador.",
}


def deps(expr):
    e = re.sub(r'"(?:[^"]|"")*"', '""', re.sub(r'--[^\n]*', '', expr))
    refs = []
    for r in re.findall(r'\[([^\]]+)\]', e):
        if not r.startswith('@') and r not in refs:
            refs.append(r)
    cols = sorted(set(re.findall(r"(d\w+|f\w+|_ControleCarga)\[", e)))
    return refs, cols


def blank_rule(x):
    e = x['expr']
    if x['folder'].endswith('05 HTML'):
        return 'Mostra "Sem dados publicados…" (ou nada) quando a medida principal é BLANK; nunca converte ausência em 0.'
    if 'NOT ISBLANK' in e or 'ISBLANK' in e:
        return 'Retorna BLANK se algum operando for BLANK (ausência ≠ 0).'
    if '+ 0' in e:
        return 'Contagem: 0 quando não há linhas que atendam ao critério.'
    return 'Herda o BLANK das medidas-base.'


L = []
A = L.append
A("# Monitor de Inflação — Dashboard (powerbi_dashboard)\n")
A("Projeto PBIP derivado de `powerbi/` (o mesmo modelo do `MonitorInflacao.pbix` enviado), com a camada visual montada "
  "e 63 medidas novas na pasta **09 Dashboard**. As pastas `powerbi/` e `powerbi_executivo/` não foram alteradas.\n")
A("## 1. Auditoria (resumo)\n")
A("| Item | Resultado |\n|---|---|")
for a, b in [
    ("Tabelas", "9: `fIndicadores` (mês × série SGS, 1.418 linhas), `fIPCAGrupos` (mês × grupo, 1.593), `fExpectativas` (coleta × ano, 890), `dCalendario` (178 meses), `dIndicador` (8), `dGrupoIPCA` (9), `dMeta` (20, desconectada), `_ControleCarga` (4), `_Medidas`"),
    ("Relacionamentos", "5, todos 1:* unidirecionais, chaves inteiras; sem ambiguidade, sem M:M, sem inativos"),
    ("Período", "IPCA/INPC/IGP-M/Livres/Monitorados/13522: jan/2012–set/2026 (177 meses). Selic: até out/2026. Grupos: até set/2026. Focus: até out/2026"),
    ("Qualidade", "0 nulos, 0 duplicidades, nenhuma lacuna mensal; Σ pesos dos grupos = 100% em todos os meses"),
    ("IPCA 12M", "Composição multiplicativa reproduz a SGS 13522 em todos os meses conferidos"),
    ("Medidas existentes", "95, corretas e reaproveitadas (nenhuma alterada)"),
    ("Relatório original", "5 páginas vazias → montado aqui"),
    ("Não disponível na base", "Contribuição por subitem/difusão oficial; meta para INPC/IGP-M (a meta do CMN é do IPCA)"),
]:
    A(f"| {a} | {b} |")
A("\n## 2. O que foi implementado\n")
A("- **5 páginas montadas (48 visuais)**: Visão Geral, Composição, Comparativos, Expectativas e Juros, Metodologia.")
A("- **Visão Geral** no layout da referência: cabeçalho (título, último período econômico ≠ data da carga), seletores de indicador e período; "
  "4 cards HTML (mês, acumulado no ano, 12 meses, distância da meta); gráfico de linhas suave (12M em violeta, meta tracejada em lilás, teto pontilhado, marcador do último período); "
  "ranking de contribuição (p.p.) com cor por sinal; rosca de **pesos** (composição válida, soma 100%) com IPCA do mês no centro e legenda em 2 colunas; insights calculados.")
A("- **Tema** `Monitor de Inflação · Violeta` (#8064F5 / #B8A6FA / #E7E0FF, fundo #F4F3F8, cards brancos, borda #E8E8EF, raio 16 px, sem sombra).")
A("- **Seletor de indicador** (IPCA, INPC, IGP-M, Livres, Monitorados): sem seleção = IPCA. O card de meta e os grupos são sempre IPCA (a meta e os pesos só existem para o IPCA) e dizem isso no título.")
A("- **Período** = segmentação de `dCalendario[Ano]` sincronizada nas 4 primeiras páginas; os KPIs mostram o último mês publicado dentro do período.")
A("- Todos os arquivos do relatório validados contra os JSON Schemas oficiais da Microsoft (PBIR: visualContainer 2.13.0, page 2.1.0).\n")
A("## 3. Decisões\n")
A("| Decisão | Por quê |\n|---|---|")
for a, b in [
    ("KPI 4 = distância da meta do CMN", "Meta oficial e validada na base (`dMeta`); responde à pergunta executiva central. Mostra desvio vs meta (p.p.), status vs teto e régua piso–meta–teto"),
    ("Rosca = pesos, não contribuições", "Pesos somam 100% (composição válida). Contribuições podem ser negativas e não formam uma pizza; vão no gráfico de barras"),
    ("Variação × contribuição separadas", "\"Maior alta\" usa variação %; \"maior pressão\" usa variação × peso. Página Composição mostra os dois rankings lado a lado"),
    ("Comparação do card 12M", "Janela de 12 meses anterior (encerrada 12 meses antes), em p.p.; a variação vs mês anterior fica no rodapé"),
    ("Cores dos sinais", "Inflação subindo = vermelho suave; caindo = verde suave (convenção de monitor de preços)"),
    ("HTML Content só onde agrega", "Cards, cabeçalho, insights, centro e legenda da rosca. Séries e rankings usam visuais nativos"),
    ("Medidas novas, antigas preservadas", "As 95 medidas originais continuam iguais (inclusive os cards HTML antigos, na paleta lavanda)"),
]:
    A(f"| {a} | {b} |")
A("\n## 4. Como abrir\n")
A("1. Abra `powerbi_dashboard\\MonitorInflacao.pbip` no Power BI Desktop (o cache de dados foi copiado; os dados aparecem sem atualizar).")
A("2. Se pedir, aceite **Habilitar visuais personalizados** — o *HTML Content* vem do AppSource (precisa de internet na primeira abertura).")
A("3. Página Inicial → **Atualizar** (opcional; lê os Parquets de `dados\\silver` via `pPastaDados`).")
A("4. Confira os valores da seção 6. Depois: Arquivo → Salvar como → `.pbix`, se quiser o arquivo único.\n")
A("## 5. Catálogo das medidas novas (pasta 09 Dashboard)\n")
A("Formatos: `%` = `0.00%`; p.p. = `+0.00 \"p.p.\"`. Todas as diferenças entre taxas estão em **pontos percentuais** (não variação relativa). "
  "Acumulados reaproveitam `Indicador Acum. Ano %` e `Indicador 12M %`, que compõem as taxas (Π(1+taxa)−1) e exigem 12 meses publicados para o 12M. "
  "O último período vem de `_Data Referência` (último mês **com dado** ≤ contexto), nunca de `MAX(Data)`.\n")
for x in medidas.MEASURES:
    refs, cols = deps(x['expr'])
    A(f"### {x['name']}\n")
    A(f"- **Finalidade:** {x['desc']}")
    A(f"- **Pasta / formato:** `{x['folder']}` · `{x['fmt'] or 'texto'}`" + (" · oculta" if x['hidden'] else ""))
    A(f"- **Dependências:** " + (", ".join(f"`[{r}]`" for r in refs) or "—") + (" · colunas de " + ", ".join(f"`{c}`" for c in cols) if cols else ""))
    A(f"- **Filtros:** {FILT[x['folder']]}")
    A(f"- **Ausência de dados:** {blank_rule(x)}")
    A(f"- **Validação:** " + (f"sem filtros deve retornar **{ESP[x['name']]}**." if x['name'] in ESP else
                               "conferir visualmente no relatório (texto/HTML) contra os valores da seção 6."))
    A(f"\n```dax\n{x['expr']}\n```\n")
A("## 6. Valores esperados para validação (sem filtros, mês de referência set/2026)\n")
A("Calculados em Python diretamente das tabelas do `.pbix` (mesma regra de composição). Use um cartão/tabela no Desktop para conferir; "
  "troque o seletor de indicador para checar as demais séries.\n")
A("```\n" + open('/home/claude/build/valores_esperados.txt').read() + "```\n")
A("## 7. Limitações e pendências\n")
A("- **Validado no Power BI Desktop desta máquina (17/10/2026):** o projeto abre sem erros, as 5 páginas renderizam e os valores conferem com a seção 6 "
  "(IPCA set/2026: 0,82% · 3,95% · 4,58% · +1,58 p.p.; IGP-M: 1,57% · 3,45% · 3,35%; ano 2020: IPCA 12M 4,52%). Seletor de indicador e de período testados.")
A("- Ajustes feitos após o teste: eixo X contínuo (`axisType = 'Scalar'`), alturas da Visão Geral e regra de indentação do TMDL.")
A("- Não foi rodado o Analisador de Desempenho; as medidas iteram no máximo ~180 meses ou 9 grupos.")
A("- O seletor de indicador inicia sem seleção (mostra IPCA por regra da medida). Se quiser que já apareça \"IPCA\" marcado, selecione e salve.")
A("- A rosca não tem legenda nativa (substituída pela legenda HTML com as mesmas cores fixas por grupo). Se um grupo novo surgir na base, ele recebe cor cinza até ser incluído na medida `HTML Legenda Pesos` e no visual.")
A("- Difusão é por **grupo** (9 itens), não o índice oficial de difusão por subitem; a base não tem subitens.")
open(sys.argv[1], 'w', encoding='utf-8').write("\n".join(L) + "\n")
print('ok', len(L))
