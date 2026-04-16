import dash
from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from utils.svg_icons import ico_bulb, ico_chi, ico_check, ico_exclude
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_loader import load_data

dash.register_page(__name__, path="/multivariado", name="EDA Multivariado", order=4)

# ── SVG icons ──────────────────────────────────────────────────────────────

# ── Styles ─────────────────────────────────────────────────────────────────
CARD  = {"backgroundColor":"#fff","border":"1px solid #E8E4F9","borderRadius":"16px","padding":"20px 24px","marginBottom":"16px"}
TH    = {"fontSize":"11px","color":"#6E6D7A","padding":"8px 12px","background":"#F2F0EB","borderBottom":"2px solid #E8E4F9","textAlign":"left","whiteSpace":"nowrap"}
TD    = {"fontSize":"12px","color":"#3D3D50","padding":"7px 12px","borderBottom":"1px solid #F0EDFE"}

def card_title(text):
    return html.Div(text, style={"fontSize":"14px","fontWeight":"600","color":"#1E1E2E","marginBottom":"4px"})
def card_sub(text):
    return html.Div(text, style={"fontSize":"12px","color":"#6E6D7A","marginBottom":"14px"})

# ── Variable groups (matching R code exactly) ──────────────────────────────
VARS_BARRAS     = ["frecuencia","tipo_trx","tipo_psp","unidad","tipo_monto"]
VARS_TABLA      = ["clave","pais_origen","pais_destino","anio"]
VARS_EXCLUIDAS  = ["decimales","descripcion","multiplicador_unidad"]

EXCLUDED_REASONS = {
    "decimales":            "Para este análisis la variable decimales se excluye frente al tipo de fraude (tipo_fraude) porque presenta baja frecuencia por categoría, haciendo que sea poco interpretable. Además, decimales corresponde a un atributo técnico de precisión numérica que no representa una característica explicativa independiente con significado analítico propio.",
    "descripcion":          "Para este análisis la variable descripcion se excluye frente al tipo de fraude (tipo_fraude) porque presenta baja frecuencia por categoría, haciendo que sea poco interpretable. Además, descripcion corresponde a una etiqueta textual derivada de las demás variables y no constituye una característica explicativa independiente.",
    "multiplicador_unidad": "Para este análisis la variable multiplicador_unidad se excluye frente al tipo de fraude (tipo_fraude) porque presenta baja frecuencia por categoría, haciendo que sea poco interpretable. Además, multiplicador_unidad corresponde a un atributo técnico de escala monetaria que no representa una característica explicativa independiente con significado analítico propio.",
    "clave":                "Para este análisis la variable clave (clave compuesta de la transacción) se excluye frente al tipo de fraude (tipo_fraude) porque presenta baja frecuencia por categoría, haciendo que sea poco interpretable. Además, clave corresponde a un código estructural compuesto que integra múltiples atributos técnicos, por lo que no representa una característica explicativa independiente con significado analítico propio.",
}

INTERPRETACIONES = {
    "frecuencia":  "El gráfico muestra que la gran mayoría de las transacciones corresponden a la clase sin fraude, distribuyéndose principalmente en las categorías A (41.7%) y H (35.6%), mientras que Q representa una proporción menor. En contraste, los casos de fraude son extremadamente pocos y se concentran completamente en una sola categoría de frecuencia (H), lo que evidencia el fuerte desbalance de la variable respuesta. Esta diferencia sugiere que las transacciones realizadas con frecuencia a mitad de año son más propensas a que sean fraude y en otro caso es casi nula esta posibilidad.",
    "tipo_trx":    "Los débitos directos (DD) y transferencias de crédito (CT0) concentran mayor número de casos de fraude en términos absolutos, aunque en términos relativos la proporción de fraude varía entre categorías. Los instrumentos TOTL y TOTL1 al ser agregados pueden distorsionar el análisis comparativo.",
    "tipo_psp":    "El PSP del pagador (1) concentra la mayor proporción de transacciones en ambos grupos. La categoría sin rol definido (_Z) presenta una distribución distinta respecto al fraude, con una proporción relativa mayor.",
    "unidad":      "Las transacciones en PN (número puro) y EUR tienen distribuciones diferentes respecto a la presencia de fraude. Las series XDF y las ratios derivadas presentan patrones particulares que las distinguen del resto.",
    "tipo_monto":  "Los montos clasificados como 'A' (normales y validados) concentran la mayoría de casos de fraude en términos absolutos. Las categorías Q (suprimido) y M (no puede existir) presentan proporciones distintas entre transacciones fraudulentas y legítimas.",
    "pais_origen": "Las entidades supranacionales 'Euro Area changing composition' (U2) y 'EU changing composition' (B0) concentran el mayor porcentaje de fraude con un 5.86% y 5.76% respectivamente, seguidas de ES y SK (3.81%). El gráfico muestra las 5 categorías con más casos de fraude absoluto.",
    "pais_destino": "La categoría 'World' (W0) domina ampliamente en ambos grupos. La distribución varía significativamente entre transacciones fraudulentas y legítimas en las categorías de destino específico.",
    "anio":        "Los casos de fraude aparecen principalmente en años recientes (2022–2024). Los últimos años concentran más transacciones y también más registros de fraude, reflejando tanto un aumento real del fenómeno como una mejora en los sistemas de detección y reporte.",
}

# ── Contingency table data (real EDA values) ───────────────────────────────
CONTINGENCY_DATA = {
    "pais_origen": {
        "con fraude":  [("U2",114,5.86),("B0",112,5.76),("ES",74,3.81),("SK",74,3.81),("GR",72,3.70),("MT",72,3.70),("PT",72,3.70),("AT",70,3.60),("BE",70,3.60),("CY",70,3.60)],
        "sin fraude":  [("RO",28746,4.35),("HU",28724,4.35),("PL",28203,4.27),("CZ",28063,4.25),("NL",27204,4.12),("PT",25600,3.87),("LT",25520,3.86),("DE",25149,3.81),("FI",25092,3.80),("LU",25086,3.80)],
    },
    "pais_destino": {
        "con fraude":  [("W0",1620,83.33),("W1",162,8.33),("W2",80,4.12),("G1",42,2.16),("SE",12,0.62)],
        "sin fraude":  [("W0",87113,13.19),("W1",21593,3.27),("W2",21427,3.24),("G1",17350,2.63),("SE",16045,2.43)],
    },
    "anio": {
        "con fraude":  [(2022,756,38.89),(2023,756,38.89),(2024,432,22.22)],
        "sin fraude":  [(2022,32455,4.91),(2023,32710,4.95),(2024,31129,4.71),(2021,17948,2.72),(2020,17948,2.72)],
    },
}


# ══════════════════════════════════════════════════════════════════════════
# Layout
# ══════════════════════════════════════════════════════════════════════════
layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Análisis Bivariado", className="page-title"),
            html.P("Análisis de la variable de respuesta (tipo_fraude) frente a las variables independientes", className="page-sub"),
        ], className="section-header"),

        html.Div([
            card_title("Tipo de análisis"),
            dcc.Tabs(id="multi-tab", value="cat", children=[
                dcc.Tab(label="Variables categóricas vs tipo_fraude", value="cat",
                        style={"fontSize":"13px"},
                        selected_style={"fontSize":"13px","color":"#FF6584","fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
                dcc.Tab(label="Variable numérica (monto) vs tipo_fraude", value="num",
                        style={"fontSize":"13px"},
                        selected_style={"fontSize":"13px","color":"#FF6584","fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
            ], style={"marginTop":"10px"}),
        ], style=CARD),

        html.Div(id="multi-tab-content"),
    ], className="page-content"),
])


# ══════════════════════════════════════════════════════════════════════════
# Tab render callback
# ══════════════════════════════════════════════════════════════════════════
@callback(Output("multi-tab-content","children"), Input("multi-tab","value"))
def render_tab(tab):
    if tab == "cat":
        return _tab_categorica()
    return _tab_numerica()


# ══════════════════════════════════════════════════════════════════════════
# TAB categórica — layout estático + outputs dinámicos
# ══════════════════════════════════════════════════════════════════════════
def _tab_categorica():
    opts = [
        {"label": "── Gráfico de barras ──",       "value": "_h1", "disabled": True},
        *[{"label": f"  {v}", "value": v} for v in VARS_BARRAS],
        {"label": "── Tabla de contingencia ──",   "value": "_h2", "disabled": True},
        *[{"label": f"  {v}", "value": v} for v in VARS_TABLA],
        {"label": "── Excluidas ──",               "value": "_h3", "disabled": True},
        *[{"label": f"  {v}", "value": v} for v in VARS_EXCLUIDAS],
    ]
    return html.Div([
        # Selector
        dbc.Row([
            dbc.Col(html.Div([
                card_title("Variable categórica"),
                dcc.Dropdown(id="multi-cat-var", options=opts, value="frecuencia",
                             clearable=False, style={"fontFamily":"Plus Jakarta Sans","fontSize":"13px"}),
            ], style=CARD), md=6),
        ], className="g-3 mb-2"),

        # Dynamic content area
        html.Div(id="bivariado-cat-contenido"),
        html.Div(id="interpretacion-bloque",style={"marginTop":"12px"}),
    ])


@callback(
    Output("bivariado-cat-contenido",  "children"),
    Output("interpretacion-bloque",    "children"),
    Input("multi-cat-var",             "value"),
)
def update_cat(var):
    if var is None or var.startswith("_"):
        raise PreventUpdate

    # ── Excluidas ──────────────────────────────────────────────────────
    if var in VARS_EXCLUIDAS or var == "clave":
        reason = EXCLUDED_REASONS.get(var, "Variable excluida del análisis.")
        excluded_card = html.Div([
            html.Div([
                ico_exclude(),
                html.Span("Variable excluida del análisis bivariado",
                          style={"fontSize":"13px","fontWeight":"700","color":"#D97706","verticalAlign":"middle"}),
            ], style={"display":"flex","alignItems":"center","marginBottom":"8px"}),
            html.P(reason, style={"fontSize":"13px","color":"#92400E","lineHeight":"1.6","margin":"0"}),
        ], style={"background":"#FEF9EC","borderRadius":"12px","padding":"16px 20px",
                  "borderLeft":"4px solid #F59E0B"})
        return excluded_card, html.Div(), html.Div()

    df = load_data()

    # ── Tabla de contingencia ──────────────────────────────────────────
    if var in VARS_TABLA:
        contenido = _render_contingency(var, df)
    else:
        # Gráfico de barras
        contenido = _render_barras(var, df)
    

    # Interpretación block
    interp = _render_interpretacion(var)

    return contenido, interp


# ── Barras múltiples ────────────────────────────────────────────────────────
def _render_barras(var, df):
    counts = pd.crosstab(df[var].astype(str), df["tipo_fraude"])
    fraud_col    = "con fraude"  if "con fraude"  in counts.columns else counts.columns[0]
    nofraude_col = "sin fraude" if "sin fraude" in counts.columns else counts.columns[-1]

    # Grouped bar — all categories
    cats = counts.index.tolist()
    f_vals  = [int(counts.loc[c, fraud_col])    if fraud_col    in counts.columns else 0 for c in cats]
    nf_vals = [int(counts.loc[c, nofraude_col]) if nofraude_col in counts.columns else 0 for c in cats]

    # Labels from pct within group
    pct    = counts.div(counts.sum(axis=1), axis=0) * 100
    f_pct  = [round(pct.loc[c, fraud_col],    1) if fraud_col    in pct.columns else 0 for c in cats]
    nf_pct = [round(pct.loc[c, nofraude_col], 1) if nofraude_col in pct.columns else 0 for c in cats]

    max_nf = max(nf_vals or [1])
    x_max  = max_nf * 1.18

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="sin fraude", x=cats, y=nf_vals,
        marker_color="#FF6584",
        text=[f"{v:,} ({p}%)" for v,p in zip(nf_vals, nf_pct)],
        textposition="outside", cliponaxis=False,
    ))
    fig.add_trace(go.Bar(
        name="con fraude", x=cats, y=f_vals,
        marker_color="#EF4444",
        text=[f"{v:,} ({p}%)" for v,p in zip(f_vals, f_pct)],
        textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(
        barmode="group", template="plotly_white", height=360,
        margin=dict(t=10,b=30,l=20,r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Cantidad de transacciones", gridcolor="#F0EDE8", range=[0, x_max]),
        xaxis=dict(title=var),
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        font=dict(family="Plus Jakarta Sans", color="#1E1E2E"),
    )

    return dbc.Row([
        dbc.Col(html.Div([
            card_title(f"Distribución de {var} por tipo de fraude"),
            card_sub("Gráfico de barras múltiple · frecuencias absolutas y porcentaje dentro de cada grupo"),
            dcc.Graph(figure=fig, config={"displayModeBar":False}),
        ], style=CARD), md=12),
    ], className="g-3")


# ── Tabla de contingencia ───────────────────────────────────────────────────
def _render_contingency(var, df):
    data = CONTINGENCY_DATA.get(var, {})
    fraud_rows    = data.get("con fraude",  [])
    nofraude_rows = data.get("sin fraude", [])

    def make_rows(rows, color):
        return [html.Tr([
            html.Td(str(r[0]), style={**TD,"fontFamily":"monospace","fontSize":"11px"}),
            html.Td(f"{r[1]:,}", style={**TD,"textAlign":"right","fontWeight":"600","color":color}),
            html.Td(f"{r[2]}%", style={**TD,"textAlign":"right","color":color}),
        ]) for r in rows]

    table_header = html.Thead(html.Tr([
        html.Th(var, style=TH), html.Th("n", style={**TH,"textAlign":"right"}),
        html.Th("%", style={**TH,"textAlign":"right"}),
    ]))

    return dbc.Row([
        dbc.Col(html.Div([
            card_title("con fraude"),
            card_sub(f"Distribución de {var} en transacciones fraudulentas"),
            html.Div(
                html.Table([table_header, html.Tbody(make_rows(fraud_rows, "#EF4444"))],
                           style={"width":"100%","borderCollapse":"collapse"}),
                style={"overflowY":"auto","maxHeight":"320px","borderRadius":"8px","border":"1px solid #E8E4F9"},
            ),
        ], style=CARD), md=6),
        dbc.Col(html.Div([
            card_title("sin fraude"),
            card_sub(f"Distribución de {var} en transacciones legítimas"),
            html.Div(
                html.Table([table_header, html.Tbody(make_rows(nofraude_rows, "#FF6584"))],
                           style={"width":"100%","borderCollapse":"collapse"}),
                style={"overflowY":"auto","maxHeight":"320px","borderRadius":"8px","border":"1px solid #E8E4F9"},
            ),
        ], style=CARD), md=6),
    ], className="g-3")





# ── Interpretación block ────────────────────────────────────────────────────
def _render_interpretacion(var):
    text = INTERPRETACIONES.get(var, "")
    if not text:
        return html.Div()
    return dbc.Row([
        dbc.Col(html.Div([
            html.Div([
                ico_bulb(),
                html.Span("Interpretación", style={"fontSize":"14px","fontWeight":"600","color":"#FF6584","verticalAlign":"middle"}),
            ], style={"display":"flex","alignItems":"center","marginBottom":"10px"}),
            html.P(text, style={"fontSize":"13px","color":"#3D3D50","lineHeight":"1.75","margin":"0"}),
        ], style=CARD), md=12),
    ], className="g-3")


# ══════════════════════════════════════════════════════════════════════════
# TAB numérica — estático
# ══════════════════════════════════════════════════════════════════════════
def _tab_numerica():
    df = load_data()
    fraud    = df[df["tipo_fraude"]=="con fraude"]["monto"].dropna()
    no_fraud = df[df["tipo_fraude"]=="sin fraude"]["monto"].dropna()

    # Boxplot con media como punto rojo
    fig_box = go.Figure()
    for grp, serie, col in [("sin fraude", no_fraud, "#FF6584"), ("con fraude", fraud, "#EF4444")]:
        fig_box.add_trace(go.Box(y=serie, name=grp, marker_color=col, boxpoints=False))
        fig_box.add_trace(go.Scatter(
            x=[grp], y=[serie.mean()], mode="markers",
            marker=dict(color="#EF4444", size=8, symbol="circle"),
            showlegend=False, hovertemplate=f"Media {grp}: {serie.mean():.2f}<extra></extra>",
        ))
    fig_box.update_layout(
        template="plotly_white", height=380,
        margin=dict(t=10,b=30,l=20,r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Valor de la transacción (monto)", gridcolor="#F0EDE8"),
        xaxis=dict(title="¿Hubo fraude? (tipo_fraude)"),
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        font=dict(family="Plus Jakarta Sans", color="#1E1E2E"),
    )

    # Stats table
    def stat_row(grp, s):
        return [grp, f"{len(s):,}", f"{s.mean():.2f}", f"{s.std():.2f}",
                f"{s.median():.2f}", f"{s.min():.2f}", f"{s.max():.2e}",
                f"{s.quantile(.25):.2f}", f"{s.quantile(.75):.2f}",
                f"{s.quantile(.75)-s.quantile(.25):.2f}"]

    total = pd.concat([fraud, no_fraud])
    tbl_rows = []
    for label, serie, color in [("con fraude",fraud,"#EF4444"),("sin fraude",no_fraud,"#FF6584"),("Total",total,"#1E1E2E")]:
        cells = stat_row(label, serie)
        tbl_rows.append(html.Tr([
            html.Td(cells[0], style={**TD,"fontWeight":"600","color":color}),
            *[html.Td(c, style={**TD,"textAlign":"right","fontSize":"11px"}) for c in cells[1:]],
        ], style={"background":"#F2F0EB" if label=="Total" else "transparent"}))

    stat_cols = ["Tipo","n","Media","DS","Mediana","Mínimo","Máximo","Q1","Q3","IQR"]

    # AD test result text
    ad_text = (
        "Anderson-Darling normality test\n\n"
        "con fraude:\n  A = 555.78,  p-value < 2.2e-16\n\n"
        "sin fraude:\n  A = 195608,  p-value < 2.2e-16"
    )
    wilcox_text = (
        "Wilcoxon rank sum test with continuity correction\n\n"
        "W = 396270632\np-value = 6.228e-16\n"
        "alternative hypothesis: true location shift is not equal to 0"
    )

    return html.Div([
        # Boxplot + stats
        dbc.Row([
            dbc.Col(html.Div([
                card_title("Distribución del monto por tipo de fraude"),
                card_sub("Los puntos rojos indican la media de cada grupo"),
                dcc.Graph(figure=fig_box, config={"displayModeBar":False}),
            ], style=CARD), md=8),

            dbc.Col(html.Div([
                card_title("Estadísticas descriptivas"),
                card_sub("monto por tipo de fraude"),
                html.Div(
                    html.Table([
                        html.Thead(html.Tr([html.Th(c, style={**TH,"fontSize":"10px"}) for c in stat_cols])),
                        html.Tbody(tbl_rows),
                    ], style={"width":"100%","borderCollapse":"collapse"}),
                    style={"overflowX":"auto","maxHeight":"380px","borderRadius":"8px","border":"1px solid #E8E4F9"},
                ),
                html.P("La media es considerablemente mayor en el grupo sin fraude. Sin embargo, las medianas en ambos casos son cercanas a cero, indicando una distribución fuertemente asimétrica. La mediana y el IQR resultan medidas más representativas que la media.",
                       style={"fontSize":"11px","color":"#6E6D7A","lineHeight":"1.6","marginTop":"12px",
                              "padding":"10px","background":"#F2F0EB","borderRadius":"8px"}),
            ], style=CARD), md=4),
        ], className="g-3"),

        # Pruebas estadísticas
        dbc.Row([
            dbc.Col(html.Div([
                card_title("Prueba de normalidad (Anderson-Darling)"),
                html.Pre(ad_text, style={"fontSize":"12px","color":"#FF6584","background":"#F2F0EB",
                                          "padding":"12px","borderRadius":"8px","fontFamily":"monospace",
                                          "marginBottom":"10px","whiteSpace":"pre-wrap"}),
                html.Div("Con un nivel de confianza del 95% y dado que en ambas pruebas el p-valor es menor a 0.05, se concluye que ambas poblaciones no siguen una distribución normal.",
                         style={"fontSize":"12px","color":"#3D3D50","lineHeight":"1.6","padding":"10px",
                                "background":"rgba(239,68,68,.05)","borderRadius":"8px","borderLeft":"3px solid #EF4444"}),
            ], style=CARD), md=6),

            dbc.Col(html.Div([
                card_title("Prueba de Wilcoxon (no paramétrica)"),
                html.Pre(wilcox_text, style={"fontSize":"12px","color":"#FF6584","background":"#F2F0EB",
                                              "padding":"12px","borderRadius":"8px","fontFamily":"monospace",
                                              "marginBottom":"10px","whiteSpace":"pre-wrap"}),
                html.Div("La prueba de Wilcoxon arrojó un p-valor extremadamente pequeño (< 0.05). Se rechaza H₀: el valor de la transacción no se comporta de la misma manera en operaciones fraudulentas y no fraudulentas, lo que constituye un indicio de dependencia entre ambas variables.",
                         style={"fontSize":"12px","color":"#3D3D50","lineHeight":"1.6","padding":"10px",
                                "background":"rgba(22,163,74,.05)","borderRadius":"8px","borderLeft":"3px solid #16A34A"}),
            ], style=CARD), md=6),
        ], className="g-3"),

        # Interpretación
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    ico_bulb(),
                    html.Span("Interpretación", style={"fontSize":"14px","fontWeight":"600","color":"#FF6584","verticalAlign":"middle"}),
                ], style={"display":"flex","alignItems":"center","marginBottom":"10px"}),
                html.P("El gráfico muestra la distribución del valor de las transacciones según si hubo o no fraude. Las operaciones no fraudulentas presentan alta dispersión con numerosos valores extremos, mientras que las transacciones fraudulentas se concentran en valores bajos con escasa variabilidad. Este patrón sugiere que el fraude se asocia principalmente a importes reducidos.",
                       style={"fontSize":"13px","color":"#3D3D50","lineHeight":"1.75","marginBottom":"10px"}),
                html.P("La prueba de Wilcoxon confirma que existe diferencia estadísticamente significativa (p-valor < 0.05) en los montos entre ambos grupos, lo que constituye un indicio de dependencia entre el valor de la transacción y el tipo de fraude.",
                       style={"fontSize":"13px","color":"#3D3D50","lineHeight":"1.75","margin":"0"}),
            ], style=CARD), md=12),
        ], className="g-3"),
    ])
