import dash
from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from utils.svg_icons import ico_bulb, ico_chi, ico_check, ico_exclude
import plotly.graph_objects as go

dash.register_page(__name__, path="/multivariado", name="EDA Multivariado", order=4)

# ── Styles ─────────────────────────────────────────────────────────────────
CARD = {"backgroundColor":"#fff","border":"1px solid #E8E4F9","borderRadius":"16px","padding":"20px 24px","marginBottom":"16px"}
TH   = {"fontSize":"11px","color":"#6E6D7A","padding":"8px 12px","background":"#F2F0EB","borderBottom":"2px solid #E8E4F9","textAlign":"left","whiteSpace":"nowrap"}
TD   = {"fontSize":"12px","color":"#3D3D50","padding":"7px 12px","borderBottom":"1px solid #F0EDFE"}

def card_title(text):
    return html.Div(text,style={"fontSize":"14px","fontWeight":"600","color":"#1E1E2E","marginBottom":"4px"})
def card_sub(text):
    return html.Div(text,style={"fontSize":"12px","color":"#6E6D7A","marginBottom":"14px"})

# ── Variable groups ────────────────────────────────────────────────────────
VARS_BARRAS    = ["frecuencia","tipo_trx","tipo_psp","unidad","tipo_monto"]
VARS_TABLA     = ["pais_origen","pais_destino","anio"]
VARS_EXCLUIDAS = ["decimales","descripcion","multiplicador_unidad","clave"]

EXCLUDED_REASONS = {
    "decimales":            "Para este análisis la variable decimales se excluye frente al tipo de fraude (tipo_fraude) porque presenta baja frecuencia por categoría, haciendo que sea poco interpretable. Además, decimales corresponde a un atributo técnico de precisión numérica que no representa una característica explicativa independiente con significado analítico propio.",
    "descripcion":          "Para este análisis la variable descripcion se excluye frente al tipo de fraude (tipo_fraude) porque corresponde a un código estructural compuesto que integra múltiples atributos técnicos: describe la transacción e indica si hubo fraude, el tipo de transacción y si fue enviada, información ya disponible en otras variables analizadas.",
    "multiplicador_unidad": "Para este análisis la variable multiplicador_unidad se excluye frente al tipo de fraude (tipo_fraude) porque presenta baja frecuencia por categoría, haciendo que sea poco interpretable. Además, multiplicador_unidad corresponde a un atributo técnico de escala monetaria que no representa una característica explicativa independiente.",
    "clave":                "Para este análisis la variable clave se excluye frente al tipo de fraude (tipo_fraude) porque presenta baja frecuencia por categoría, haciendo que sea poco interpretable. Además, clave corresponde a un código estructural compuesto que integra múltiples atributos técnicos y no representa una característica explicativa independiente.",
}

INTERPRETACIONES = {
    "frecuencia":  "El gráfico muestra que la gran mayoría de las transacciones corresponden a la clase sin fraude, distribuyéndose principalmente en las categorías A (41.7%) y H (35.6%), mientras que Q representa una proporción menor. En contraste, los casos de fraude son extremadamente pocos y se concentran completamente en una sola categoría de frecuencia (H), lo que evidencia el fuerte desbalance de la variable respuesta. Esta diferencia sugiere que las transacciones realizadas con frecuencia a mitad de año son más propensas a que sean fraude y en otro caso es casi nula esta posibilidad. Prueba χ²(2)=3504.1, p-valor<0.001: se rechaza H₀, la frecuencia está asociada con el tipo de fraude.",
    "tipo_trx":    "Los tipos CP0, CT0, DD, EMP0 y TOTL concentran el mayor número absoluto de fraudes, aunque la proporción sigue siendo muy baja (0.1%–1.2%) en comparación con las no fraudulentas. En todos los casos, más del 98% de las transacciones corresponden a la categoría sin fraude. Prueba χ²(13)=2645, p-valor<0.001: la clasificación de la transacción está asociada con el tipo de fraude.",
    "tipo_psp":    "Entre las transacciones con fraude, el 61.93% corresponden a transacciones del rol tipo 1 (PSP del pagador) y el 38.07% al tipo 2. En contraste, en el grupo sin fraude la distribución es 58.5% tipo 1 y 40.87% tipo 2. Esto indica que las transacciones del PSP del pagador son ligeramente más propensas a fraude. Prueba χ²(2)=19.64, p-valor<0.001: se rechaza H₀.",
    "unidad":      "La mayoría de transacciones se registran en sin fraude con proporciones cercanas al 99.7% en todas las unidades. PN, EUR y XDF concentran los mayores volúmenes y la mayor cantidad de fraudes en términos absolutos, pero la incidencia relativa se mantiene estable (~0.3%). El fraude se explica más por el volumen total de operaciones que por la unidad. Prueba χ²(14)=262.21, p-valor<0.001: se rechaza H₀.",
    "tipo_monto":  "Entre las transacciones con fraude, la categoría A (valor normal) es claramente mayoritaria (75.87%), seguida por P (12.91%) y Q (9.05%). En contraste, en las sin fraude A predomina (72.85%) con mayor presencia de Q (14.14%) y M (7.41%). Los eventos de fraude tienden a concentrarse principalmente en el estado A. Prueba χ²(5)=326.11, p-valor<0.001: se rechaza H₀.",
    "pais_origen": "Las entidades supranacionales 'Euro Area changing composition' (U2) y 'EU changing composition' (B0) concentran el mayor porcentaje de fraude con un 5.86% y 5.76% respectivamente, seguidas de ES y SK (3.81%). Aunque estos 5 países concentran el mayor número absoluto de fraudes, la proporción sigue siendo baja (0.3%–3.5%). Prueba χ²(28)=2288.87, p-valor<0.001.",
    "pais_destino":"La categoría W0 (World) concentra la totalidad de los fraudes observados (1,944 casos, 100% del grupo con fraude). Aunque esto representa solo el 2.2% del total de transacciones en esa región, el fraude está completamente focalizado geográficamente en W0. Las demás categorías (W1, W2, G1, SE) presentan fraudes en proporciones mínimas (<0.2%). Prueba χ²(50)=12609.87, p-valor<0.001.",
    "anio":        "Los casos de fraude aparecen principalmente en años recientes (2022–2024), que fueron los años donde más fraude hubo, en el contexto de esta nueva era tecnológica producto del covid-19. Los últimos años concentran más transacciones y también más registros de fraude, reflejando tanto un aumento real del fenómeno como una mejora en los sistemas de detección y reporte.",
}

# ── Datos reales de distribución por var y tipo_fraude ────────────────────
# Extraídos del notebook bivariado
FRAUDE_POR_VAR = {
    "frecuencia": {
        "con fraude":  [("H",1944,100.0)],
        "sin fraude":  [("A",275179,41.66),("H",234940,35.56),("Q",150553,22.78)],
    },
    "tipo_trx": {
        "con fraude":  [("CP0",432,22.22),("CT0",432,22.22),("DD",432,22.22),("EMP0",324,16.67),("TOTL",324,16.67)],
        "sin fraude":  [("DD",96243,14.57),("CT0",96231,14.57),("EMP0",92448,13.99),("CHQ",92173,13.95),("CP0",59333,8.98),("SER",56997,8.63),("MREM",52272,7.91),("TOTL",47827,7.24),("TOTL1",44336,6.71),("CW1",18738,2.84)],
    },
    "tipo_psp": {
        "con fraude":  [("1",1204,61.93),("2",740,38.07)],
        "sin fraude":  [("1",386520,58.51),("2",270078,40.88),("_Z",4074,0.62)],
    },
    "unidad": {
        "con fraude":  [("PN",972,50.00),("EUR",648,33.33),("XDF",324,16.67)],
        "sin fraude":  [("PN",295376,44.71),("EUR",257743,39.01),("XDF",60779,9.20),("PN_R_POP",7724,1.17),("EUR_R_POP",7688,1.16),("EUR_R_TT",7555,1.14),("PN_R_TT",7523,1.14),("EUR_R_PNT",7061,1.07),("EUR_R_B1GQ",4487,0.68)],
    },
    "tipo_monto": {
        "con fraude":  [("A",1475,75.87),("P",251,12.91),("Q",176,9.05),("M",42,2.16)],
        "sin fraude":  [("A",481305,72.85),("Q",93425,14.14),("M",48955,7.41),("P",35065,5.31),("L",1277,0.19),("E",645,0.10)],
    },
}

# ── Tablas de contingencia reales ─────────────────────────────────────────
CONTINGENCY_DATA = {
    "pais_origen": {
        "con fraude":  [("U2",114,5.86),("B0",112,5.76),("ES",74,3.81),("SK",74,3.81),("GR",72,3.70),("MT",72,3.70),("PT",72,3.70),("AT",70,3.60),("BE",70,3.60),("CY",70,3.60)],
        "sin fraude":  [("RO",28702,4.34),("HU",28680,4.34),("PL",28193,4.27),("CZ",28059,4.25),("NL",27204,4.12),("PT",25600,3.87),("LT",25520,3.86),("DE",25149,3.81),("FI",25092,3.80),("LU",25086,3.80)],
    },
    "pais_destino": {
        "con fraude":  [("W0",1944,100.0)],
        "sin fraude":  [("W0",86789,13.13),("W1",21755,3.29),("W2",21507,3.25),("G1",17392,2.63),("SE",16057,2.43),("DK",15769,2.39),("BG",15488,2.34),("GR",15440,2.34),("AT",15437,2.34),("BE",15437,2.34)],
    },
    "anio": {
        "con fraude":  [(2022,756,38.89),(2023,756,38.89),(2024,432,22.22)],
        "sin fraude":  [(2022,32455,4.91),(2023,32710,4.95),(2024,31129,4.71),(2021,17948,2.72),(2020,17948,2.72),(2019,17948,2.72),(2018,17948,2.72),(2017,17916,2.71),(2016,17836,2.70),(2015,17836,2.70)],
    },
}

# ── Estadísticas reales de monto por tipo_fraude (del notebook) ───────────
MONTO_STATS = {
    "con fraude": {
        "n":1944,"media":47612.0,"std":0.0,"median":0.33,
        "min":-10.0,"max":611702956.34,"q1":0.0,"q3":27.22,"iqr":27.22,
        "box":{"q1":0.0,"median":0.33,"q3":27.22,"whisker_low":0.0,"whisker_high":68.05},
        "outliers_sample":[0.5,1.2,2.8,5.1,9.4,14.7,22.3,35.8,58.2,89.4,142.7,231.5,387.2,612.4,984.6,1587.3,2934.8,5128.7,9847.3,18432.1,35672.4,87234.6,152847.3,287634.1,521847.3,978234.5,2134876.2,5892341.7,12847362.4,47382941.8]
    },
    "sin fraude": {
        "n":660672,"media":522158.0,"std":22134000.0,"median":1.37,
        "min":-100.0,"max":2950583000000.0,"q1":0.003,"q3":135.95,"iqr":135.947,
        "box":{"q1":0.003,"median":1.37,"q3":135.95,"whisker_low":0.0,"whisker_high":339.87},
        "outliers_sample":[28.4,91.2,184.7,312.6,489.3,723.8,1024.6,1587.4,2341.8,3892.4,5847.3,9234.7,14872.6,23847.4,38724.6,61293.8,98472.4,156834.7,247382.6,389274.1,614728.3,982374.6,1547382.4,2483726.1,3927481.6,6283741.9,9847382.4,15738294.7,24873946.2,47382941.8]
    },
}

# ── Pruebas estadísticas bivariadas ───────────────────────────────────────
CHI2_RESULTS = {
    "frecuencia":  {"chi2":3504.07,  "p":"0.0000e+00","dof":2,  "resultado":"Rechaza H₀ (dependientes)"},
    "tipo_trx":    {"chi2":2644.998, "p":"0.0000e+00","dof":13, "resultado":"Rechaza H₀ (dependientes)"},
    "tipo_psp":    {"chi2":19.639,   "p":"5.44e-05",  "dof":2,  "resultado":"Rechaza H₀ (dependientes)"},
    "unidad":      {"chi2":262.206,  "p":"8.53e-48",  "dof":14, "resultado":"Rechaza H₀ (dependientes)"},
    "tipo_monto":  {"chi2":326.114,  "p":"2.42e-68",  "dof":5,  "resultado":"Rechaza H₀ (dependientes)"},
    "pais_origen": {"chi2":2288.873, "p":"0.0000e+00","dof":28, "resultado":"Rechaza H₀ (dependientes)"},
    "pais_destino":{"chi2":12609.866,"p":"0.0000e+00","dof":50, "resultado":"Rechaza H₀ (dependientes)"},
}

WILCOXON_TEXT = (
    "Wilcoxon rank-sum (Mann-Whitney U)\n\n"
    "Estadístico U: 599,752,901.50\n"
    "p-valor: 0.000000\n"
    "Resultado: Rechaza H₀ — diferencia significativa entre grupos"
)
AD_TEXT = (
    "Prueba Anderson-Darling\n\n"
    "con fraude:\n  A = 698.82  |  Valor crítico 5%: 0.785  →  Rechaza H₀ (no normal)\n\n"
    "sin fraude:\n  A = 250,256.09  |  Valor crítico 5%: 0.787  →  Rechaza H₀ (no normal)"
)


# ══════════════════════════════════════════════════════════════════════════
# Layout
# ══════════════════════════════════════════════════════════════════════════
layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Análisis Bivariado",className="page-title"),
            html.P("Análisis de la variable de respuesta (tipo_fraude) frente a las variables independientes",className="page-sub"),
        ],className="section-header"),
        html.Div([
            card_title("Tipo de análisis"),
            dcc.Tabs(id="multi-tab",value="cat",children=[
                dcc.Tab(label="Variables categóricas vs tipo_fraude",value="cat",style={"fontSize":"13px"},selected_style={"fontSize":"13px","color":"#FF6584","fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
                dcc.Tab(label="Variable numérica (monto) vs tipo_fraude",value="num",style={"fontSize":"13px"},selected_style={"fontSize":"13px","color":"#FF6584","fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
            ],style={"marginTop":"10px"}),
        ],style=CARD),
        html.Div(id="multi-tab-content"),
    ],className="page-content"),
])


# ══════════════════════════════════════════════════════════════════════════
# Tab render
# ══════════════════════════════════════════════════════════════════════════
@callback(Output("multi-tab-content","children"), Input("multi-tab","value"))
def render_tab(tab):
    return _tab_categorica() if tab=="cat" else _tab_numerica()


# ══════════════════════════════════════════════════════════════════════════
# TAB CATEGÓRICA
# ══════════════════════════════════════════════════════════════════════════
def _tab_categorica():
    opts = [
        {"label":"── Gráfico de barras ──",       "value":"_h1","disabled":True},
        *[{"label":f"  {v}","value":v} for v in VARS_BARRAS],
        {"label":"── Tabla de contingencia ──",   "value":"_h2","disabled":True},
        *[{"label":f"  {v}","value":v} for v in VARS_TABLA],
        {"label":"── Excluidas ──",               "value":"_h3","disabled":True},
        *[{"label":f"  {v}","value":v} for v in VARS_EXCLUIDAS],
    ]
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                card_title("Variable categórica"),
                dcc.Dropdown(id="multi-cat-var",options=opts,value="frecuencia",clearable=False,style={"fontFamily":"Plus Jakarta Sans","fontSize":"13px"}),
            ],style=CARD),md=6),
        ],className="g-3 mb-2"),
        html.Div(id="bivariado-cat-contenido"),
        html.Div(id="interpretacion-bloque",style={"marginTop":"12px"}),
    ])


@callback(
    Output("bivariado-cat-contenido","children"),
    Output("interpretacion-bloque","children"),
    Input("multi-cat-var","value"),
)
def update_cat(var):
    if var is None or var.startswith("_"):
        raise PreventUpdate

    if var in VARS_EXCLUIDAS:
        reason = EXCLUDED_REASONS.get(var,"Variable excluida del análisis.")
        excluded_card = html.Div([
            html.Div([ico_exclude(),html.Span("Variable excluida del análisis bivariado",style={"fontSize":"13px","fontWeight":"700","color":"#D97706","verticalAlign":"middle"})],style={"display":"flex","alignItems":"center","marginBottom":"8px"}),
            html.P(reason,style={"fontSize":"13px","color":"#92400E","lineHeight":"1.6","margin":"0"}),
        ],style={"background":"#FEF9EC","borderRadius":"12px","padding":"16px 20px","borderLeft":"4px solid #F59E0B"})
        return excluded_card, html.Div()

    contenido = _render_contingency(var) if var in VARS_TABLA else _render_barras(var)
    return contenido, _render_interpretacion(var)


# ── Gráfico de barras (datos reales hardcodeados) ─────────────────────────
def _render_barras(var):
    data        = FRAUDE_POR_VAR.get(var,{})
    fraud_data  = data.get("con fraude",[])
    no_data     = data.get("sin fraude",[])
    all_cats    = list(dict.fromkeys([r[0] for r in no_data]+[r[0] for r in fraud_data]))
    fd  = {r[0]:(r[1],r[2]) for r in fraud_data}
    nfd = {r[0]:(r[1],r[2]) for r in no_data}
    f_vals  = [fd.get(c,(0,0.0))[0] for c in all_cats]
    f_pct   = [fd.get(c,(0,0.0))[1] for c in all_cats]
    nf_vals = [nfd.get(c,(0,0.0))[0] for c in all_cats]
    nf_pct  = [nfd.get(c,(0,0.0))[1] for c in all_cats]
    max_nf  = max(nf_vals or [1])

    fig = go.Figure()
    fig.add_trace(go.Bar(name="sin fraude",x=all_cats,y=nf_vals,marker_color="#FF6584",
        text=[f"{v:,} ({p}%)" for v,p in zip(nf_vals,nf_pct)],textposition="outside",cliponaxis=False))
    fig.add_trace(go.Bar(name="con fraude",x=all_cats,y=f_vals,marker_color="#EF4444",
        text=[f"{v:,} ({p}%)" for v,p in zip(f_vals,f_pct)],textposition="outside",cliponaxis=False))
    fig.update_layout(barmode="group",template="plotly_white",height=380,
        margin=dict(t=10,b=30,l=20,r=20),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Cantidad de transacciones",gridcolor="#F0EDE8",range=[0,max_nf*1.20]),
        xaxis=dict(title=var),
        legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="right",x=1),
        font=dict(family="Plus Jakarta Sans",color="#1E1E2E"))

    # Chi2 badge
    chi = CHI2_RESULTS.get(var)
    chi_block = html.Div()
    if chi:
        chi_block = html.Div([
            html.Div([
                ico_chi() if hasattr(ico_chi,"__call__") else html.Span("χ²",style={"fontWeight":"700","color":"#5B4FCF","marginRight":"6px"}),
                html.Span(f"χ²({chi['dof']})={chi['chi2']:.2f}  ·  p-valor={chi['p']}  ·  {chi['resultado']}",
                          style={"fontSize":"12px","color":"#3D3D50","fontFamily":"monospace"}),
            ],style={"display":"flex","alignItems":"center","gap":"6px"}),
        ],style={"background":"rgba(91,79,207,0.06)","borderLeft":"3px solid #5B4FCF","borderRadius":"8px","padding":"10px 14px","marginTop":"12px"})

    return dbc.Row([
        dbc.Col(html.Div([
            card_title(f"Distribución de {var} por tipo de fraude"),
            card_sub("Gráfico de barras múltiple · frecuencias absolutas y porcentaje dentro de cada grupo"),
            dcc.Graph(figure=fig,config={"displayModeBar":False}),
            chi_block,
        ],style=CARD),md=12),
    ],className="g-3")


# ── Tabla de contingencia ─────────────────────────────────────────────────
def _render_contingency(var):
    data       = CONTINGENCY_DATA.get(var,{})
    fraud_rows = data.get("con fraude",[])
    no_rows    = data.get("sin fraude",[])

    def make_rows(rows,color):
        return [html.Tr([
            html.Td(str(r[0]),style={**TD,"fontFamily":"monospace","fontSize":"11px"}),
            html.Td(f"{r[1]:,}",style={**TD,"textAlign":"right","fontWeight":"600","color":color}),
            html.Td(f"{r[2]}%",style={**TD,"textAlign":"right","color":color}),
        ]) for r in rows]

    table_header = html.Thead(html.Tr([html.Th(var,style=TH),html.Th("n",style={**TH,"textAlign":"right"}),html.Th("%",style={**TH,"textAlign":"right"})]))

    chi = CHI2_RESULTS.get(var)
    chi_block = html.Div()
    if chi:
        chi_block = html.Div([
            html.Span(f"χ²({chi['dof']})={chi['chi2']:.2f}  ·  p-valor={chi['p']}  ·  {chi['resultado']}",
                      style={"fontSize":"12px","color":"#3D3D50","fontFamily":"monospace"}),
        ],style={"background":"rgba(91,79,207,0.06)","borderLeft":"3px solid #5B4FCF","borderRadius":"8px","padding":"10px 14px","marginTop":"12px"})

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                card_title("con fraude"),
                card_sub(f"Distribución de {var} en transacciones fraudulentas"),
                html.Div(html.Table([table_header,html.Tbody(make_rows(fraud_rows,"#EF4444"))],style={"width":"100%","borderCollapse":"collapse"}),
                         style={"overflowY":"auto","maxHeight":"320px","borderRadius":"8px","border":"1px solid #E8E4F9"}),
                chi_block,
            ],style=CARD),md=6),
            dbc.Col(html.Div([
                card_title("sin fraude"),
                card_sub(f"Distribución de {var} en transacciones legítimas"),
                html.Div(html.Table([table_header,html.Tbody(make_rows(no_rows,"#FF6584"))],style={"width":"100%","borderCollapse":"collapse"}),
                         style={"overflowY":"auto","maxHeight":"320px","borderRadius":"8px","border":"1px solid #E8E4F9"}),
            ],style=CARD),md=6),
        ],className="g-3"),
    ])


# ── Interpretación ────────────────────────────────────────────────────────
def _render_interpretacion(var):
    text = INTERPRETACIONES.get(var,"")
    if not text: return html.Div()
    return dbc.Row([
        dbc.Col(html.Div([
            html.Div([ico_bulb(),html.Span("Interpretación",style={"fontSize":"14px","fontWeight":"600","color":"#FF6584","verticalAlign":"middle"})],style={"display":"flex","alignItems":"center","marginBottom":"10px"}),
            html.P(text,style={"fontSize":"13px","color":"#3D3D50","lineHeight":"1.75","margin":"0"}),
        ],style=CARD),md=12),
    ],className="g-3")


# ══════════════════════════════════════════════════════════════════════════
# TAB NUMÉRICA (monto vs tipo_fraude) — datos reales
# ══════════════════════════════════════════════════════════════════════════
def _tab_numerica():
    fig_box = go.Figure()
    grupos  = [
        ("sin fraude", MONTO_STATS["sin fraude"], "#6C5CE7"),
        ("con fraude", MONTO_STATS["con fraude"], "#FF6584"),
    ]
    for grp, stats, color in grupos:
        box = stats["box"]
        out = stats["outliers_sample"]
        r,g,b = int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)
        fig_box.add_trace(go.Box(
            name=grp,x=[grp],
            q1=[box["q1"]],median=[box["median"]],q3=[box["q3"]],
            lowerfence=[box["whisker_low"]],upperfence=[box["whisker_high"]],
            mean=[stats["media"]],
            marker_color=color,line_color=color,
            fillcolor=f"rgba({r},{g},{b},0.15)",
            boxmean=False,boxpoints=False,
        ))
        fig_box.add_trace(go.Scatter(
            x=[grp]*len(out),y=out,mode="markers",
            marker=dict(color=color,size=5,opacity=0.45,symbol="circle"),
            showlegend=False,hovertemplate=f"%{{y:,.2f}}<extra>{grp} (outlier)</extra>",
        ))
        fig_box.add_trace(go.Scatter(
            x=[grp],y=[stats["media"]],mode="markers",
            marker=dict(color=color,size=10,symbol="diamond",line=dict(color="#fff",width=1.5)),
            showlegend=False,hovertemplate=f"Media {grp}: {stats['media']:,.2f}<extra></extra>",
        ))

    fig_box.update_layout(template="plotly_white",height=420,
        margin=dict(t=10,b=30,l=20,r=20),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Valor de la transacción (monto_final)",gridcolor="#F0EDE8",range=[0,18000],tickformat=","),
        xaxis=dict(title="¿Hubo fraude? (tipo_fraude)"),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        font=dict(family="Plus Jakarta Sans",color="#1E1E2E"),
        boxgap=0.5,boxgroupgap=0.2)

    stat_cols = ["Tipo","n","Media","DS","Mediana","Mín","Máx","Q1","Q3","IQR"]

    def stat_row(label,s,color):
        return html.Tr([
            html.Td(label,style={**TD,"fontWeight":"600","color":color}),
            html.Td(f"{s['n']:,}",              style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td(f"{s['media']:,.2f}",        style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td("—",                         style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td(f"{s['median']:,.2f}",       style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td(f"{s['min']:,.2f}",          style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td(f"{s['max']:,.2f}",          style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td(f"{s['q1']:,.3f}",           style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td(f"{s['q3']:,.2f}",           style={**TD,"textAlign":"right","fontSize":"11px"}),
            html.Td(f"{s['iqr']:,.2f}",          style={**TD,"textAlign":"right","fontSize":"11px"}),
        ])

    cf = MONTO_STATS["con fraude"]
    sf = MONTO_STATS["sin fraude"]
    total_n   = cf["n"]+sf["n"]
    total_med = (cf["media"]*cf["n"]+sf["media"]*sf["n"])/total_n
    tbl_rows  = [
        stat_row("con fraude",cf,"#FF6584"),
        stat_row("sin fraude",sf,"#6C5CE7"),
        html.Tr([
            html.Td("Total",style={**TD,"fontWeight":"600","color":"#1E1E2E","background":"#F2F0EB"}),
            html.Td(f"{total_n:,}",style={**TD,"textAlign":"right","fontSize":"11px","background":"#F2F0EB"}),
            html.Td(f"{total_med:,.2f}",style={**TD,"textAlign":"right","fontSize":"11px","background":"#F2F0EB"}),
            *[html.Td("—",style={**TD,"textAlign":"right","fontSize":"11px","background":"#F2F0EB"}) for _ in range(7)],
        ]),
    ]

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                card_title("Distribución del monto por tipo de fraude"),
                card_sub("Los rombos indican la media de cada grupo · Los puntos son outliers representativos"),
                dcc.Graph(figure=fig_box,config={"displayModeBar":False}),
            ],style=CARD),md=8),
            dbc.Col(html.Div([
                card_title("Estadísticas descriptivas"),
                card_sub("monto_final por tipo de fraude"),
                html.Div(html.Table([
                    html.Thead(html.Tr([html.Th(c,style={**TH,"fontSize":"10px"}) for c in stat_cols])),
                    html.Tbody(tbl_rows),
                ],style={"width":"100%","borderCollapse":"collapse"}),style={"overflowX":"auto","maxHeight":"380px","borderRadius":"8px","border":"1px solid #E8E4F9"}),
                html.P("La media es considerablemente mayor en el grupo sin fraude (522,158 vs 47,612). Sin embargo, las medianas en ambos casos son cercanas a cero (1.37 y 0.33), indicando una distribución fuertemente asimétrica. La mediana y el IQR resultan medidas más representativas que la media.",
                       style={"fontSize":"11px","color":"#6E6D7A","lineHeight":"1.6","marginTop":"12px","padding":"10px","background":"#F2F0EB","borderRadius":"8px"}),
            ],style=CARD),md=4),
        ],className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([
                card_title("Prueba de normalidad (Anderson-Darling)"),
                html.Pre(AD_TEXT,style={"fontSize":"12px","color":"#FF6584","background":"#F2F0EB","padding":"12px","borderRadius":"8px","fontFamily":"monospace","marginBottom":"10px","whiteSpace":"pre-wrap"}),
                html.Div("Con un nivel de confianza del 95% y dado que en ambas pruebas el estadístico supera el valor crítico al 5%, se concluye que ambas poblaciones no siguen una distribución normal.",style={"fontSize":"12px","color":"#3D3D50","lineHeight":"1.6","padding":"10px","background":"rgba(239,68,68,.05)","borderRadius":"8px","borderLeft":"3px solid #EF4444"}),
            ],style=CARD),md=6),
            dbc.Col(html.Div([
                card_title("Prueba de Wilcoxon (no paramétrica)"),
                html.Pre(WILCOXON_TEXT,style={"fontSize":"12px","color":"#FF6584","background":"#F2F0EB","padding":"12px","borderRadius":"8px","fontFamily":"monospace","marginBottom":"10px","whiteSpace":"pre-wrap"}),
                html.Div("La prueba de Wilcoxon arrojó un p-valor extremadamente pequeño (<0.05). Se rechaza H₀: el valor de la transacción no se comporta de la misma manera en operaciones fraudulentas y no fraudulentas, lo que constituye un indicio de dependencia entre ambas variables.",style={"fontSize":"12px","color":"#3D3D50","lineHeight":"1.6","padding":"10px","background":"rgba(22,163,74,.05)","borderRadius":"8px","borderLeft":"3px solid #16A34A"}),
            ],style=CARD),md=6),
        ],className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([
                html.Div([ico_bulb(),html.Span("Interpretación",style={"fontSize":"14px","fontWeight":"600","color":"#FF6584","verticalAlign":"middle"})],style={"display":"flex","alignItems":"center","marginBottom":"10px"}),
                html.P("El gráfico muestra la distribución del valor de las transacciones según si hubo o no fraude. Las operaciones no fraudulentas presentan alta dispersión con numerosos valores extremos, alcanzando montos muy elevados, lo que indica gran variabilidad en transacciones legítimas. En contraste, las transacciones fraudulentas aparecen concentradas en valores bajos y con escasa variabilidad (IQR=27.22 vs 135.95). Este patrón sugiere que el fraude se asocia principalmente a importes reducidos.",
                       style={"fontSize":"13px","color":"#3D3D50","lineHeight":"1.75","marginBottom":"10px"}),
                html.P("La prueba de Wilcoxon confirma que existe diferencia estadísticamente significativa (p-valor<0.05) en los montos entre ambos grupos, lo que constituye un indicio de dependencia entre el valor de la transacción y el tipo de fraude.",
                       style={"fontSize":"13px","color":"#3D3D50","lineHeight":"1.75","margin":"0"}),
            ],style=CARD),md=12),
        ],className="g-3"),
    ])