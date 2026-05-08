# pages/modelo.py
import dash
import requests
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, State, callback, no_update

dash.register_page(
    __name__,
    path="/modelo",
    name="Modelo Predictivo",
    title="Modelo ML · Fraude EU",
)

API_URL  = "https://modeloapi-production.up.railway.app/predict"
CORAL    = "#F25E7A"
PURPLE   = "#7C6AF7"
DARK     = "#1a1d2e"
LIGHT_BG = "#f4f5fb"
WHITE    = "#ffffff"
TEXT_SEC = "#6b7280"
BORDER   = "#eeeef5"
GREEN    = "#10b981"
FONT_D   = "Sora, Plus Jakarta Sans, sans-serif"
FONT_B   = "Plus Jakarta Sans, Inter, sans-serif"
CARD_H   = 700   # altura fija compartida

# ── SVGs como data URIs ───────────────────────────────────────────────────────
def svg_img(svg_content, w="20px", h="20px", style_extra=None):
    import base64
    encoded = base64.b64encode(svg_content.encode()).decode()
    style = {"width": w, "height": h, "display": "inline-block", "flexShrink": "0"}
    if style_extra:
        style.update(style_extra)
    return html.Img(src=f"data:image/svg+xml;base64,{encoded}", style=style)


SVG_SCAN_SRC = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="7" y="7" width="10" height="10" rx="1.5" stroke="white" stroke-width="2"/>
  <line x1="3" y1="12" x2="6" y2="12" stroke="white" stroke-width="2" stroke-linecap="round"/>
  <line x1="18" y1="12" x2="21" y2="12" stroke="white" stroke-width="2" stroke-linecap="round"/>
  <line x1="12" y1="3" x2="12" y2="6" stroke="white" stroke-width="2" stroke-linecap="round"/>
  <line x1="12" y1="18" x2="12" y2="21" stroke="white" stroke-width="2" stroke-linecap="round"/>
</svg>'''

SVG_ALERT_SRC = f'''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
        stroke="{CORAL}" stroke-width="2" stroke-linejoin="round"/>
  <line x1="12" y1="9" x2="12" y2="13" stroke="{CORAL}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="17" r="0.5" fill="{CORAL}" stroke="{CORAL}" stroke-width="1.5"/>
</svg>'''

SVG_CHECK_SRC = f'''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="{GREEN}" stroke-width="2"/>
  <polyline points="8 12 11 15 16 9" stroke="{GREEN}" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_DOT_SRC = f'''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
  <circle cx="5" cy="5" r="4" fill="{GREEN}"/>
</svg>'''

SVG_ERROR_SRC = f'''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="{CORAL}" stroke-width="2"/>
  <line x1="12" y1="8" x2="12" y2="12" stroke="{CORAL}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="16" r="0.5" fill="{CORAL}" stroke="{CORAL}" stroke-width="1.5"/>
</svg>'''

# ── Opciones ──────────────────────────────────────────────────────────────────
# frecuencia: A = Anual, H = Semestral, Q = Trimestral
FRECUENCIA_OPTS = [
    {"label": "A — Anual",       "value": "A"},
    {"label": "H — Semestral",   "value": "H"},
    {"label": "Q — Trimestral",  "value": "Q"},
]

# pais_origen: 29 países europeos + entidades de área
PAIS_ORIGEN_OPTS = [
    {"label": "AT — Austria",                        "value": "AT"},
    {"label": "BE — Bélgica",                        "value": "BE"},
    {"label": "B0 — EU (composición cambiante)",      "value": "B0"},
    {"label": "BG — Bulgaria",                       "value": "BG"},
    {"label": "CY — Chipre",                         "value": "CY"},
    {"label": "CZ — República Checa",                "value": "CZ"},
    {"label": "DE — Alemania",                       "value": "DE"},
    {"label": "DK — Dinamarca",                      "value": "DK"},
    {"label": "EE — Estonia",                        "value": "EE"},
    {"label": "ES — España",                         "value": "ES"},
    {"label": "FI — Finlandia",                      "value": "FI"},
    {"label": "FR — Francia",                        "value": "FR"},
    {"label": "GR — Grecia",                         "value": "GR"},
    {"label": "HR — Croacia",                        "value": "HR"},
    {"label": "HU — Hungría",                        "value": "HU"},
    {"label": "IE — Irlanda",                        "value": "IE"},
    {"label": "IT — Italia",                         "value": "IT"},
    {"label": "LT — Lituania",                       "value": "LT"},
    {"label": "LU — Luxemburgo",                     "value": "LU"},
    {"label": "LV — Letonia",                        "value": "LV"},
    {"label": "MT — Malta",                          "value": "MT"},
    {"label": "NL — Países Bajos",                   "value": "NL"},
    {"label": "PL — Polonia",                        "value": "PL"},
    {"label": "PT — Portugal",                       "value": "PT"},
    {"label": "RO — Rumanía",                        "value": "RO"},
    {"label": "SE — Suecia",                         "value": "SE"},
    {"label": "SI — Eslovenia",                      "value": "SI"},
    {"label": "SK — Eslovaquia",                     "value": "SK"},
    {"label": "U2 — Zona Euro (composición cambiante)", "value": "U2"},
]

# pais_destino: destinos mundiales, EEA y extra-EEA
PAIS_DESTINO_OPTS = [
    {"label": "W0 — World",                          "value": "W0"},
    {"label": "W1 — Rest of the World",              "value": "W1"},
    {"label": "W2 — Domestic",                       "value": "W2"},
    {"label": "G1 — Extra EEA",                      "value": "G1"},
    {"label": "G3 — Other EEA countries",            "value": "G3"},
    {"label": "AT — Austria",                        "value": "AT"},
    {"label": "BE — Bélgica",                        "value": "BE"},
    {"label": "BG — Bulgaria",                       "value": "BG"},
    {"label": "CY — Chipre",                         "value": "CY"},
    {"label": "CZ — República Checa",                "value": "CZ"},
    {"label": "DE — Alemania",                       "value": "DE"},
    {"label": "DK — Dinamarca",                      "value": "DK"},
    {"label": "EE — Estonia",                        "value": "EE"},
    {"label": "ES — España",                         "value": "ES"},
    {"label": "FI — Finlandia",                      "value": "FI"},
    {"label": "FR — Francia",                        "value": "FR"},
    {"label": "GB — Reino Unido",                    "value": "GB"},
    {"label": "GR — Grecia",                         "value": "GR"},
    {"label": "HR — Croacia",                        "value": "HR"},
    {"label": "HU — Hungría",                        "value": "HU"},
    {"label": "IE — Irlanda",                        "value": "IE"},
    {"label": "IS — Islandia",                       "value": "IS"},
    {"label": "IT — Italia",                         "value": "IT"},
    {"label": "LI — Liechtenstein",                  "value": "LI"},
    {"label": "LT — Lituania",                       "value": "LT"},
    {"label": "LU — Luxemburgo",                     "value": "LU"},
    {"label": "LV — Letonia",                        "value": "LV"},
    {"label": "MT — Malta",                          "value": "MT"},
    {"label": "NL — Países Bajos",                   "value": "NL"},
    {"label": "NO — Noruega",                        "value": "NO"},
    {"label": "PL — Polonia",                        "value": "PL"},
    {"label": "PT — Portugal",                       "value": "PT"},
    {"label": "RO — Rumanía",                        "value": "RO"},
    {"label": "SE — Suecia",                         "value": "SE"},
    {"label": "SI — Eslovenia",                      "value": "SI"},
    {"label": "SK — Eslovaquia",                     "value": "SK"},
    {"label": "AR — Argentina",                      "value": "AR"},
    {"label": "AU — Australia",                      "value": "AU"},
    {"label": "BR — Brasil",                         "value": "BR"},
    {"label": "CA — Canadá",                         "value": "CA"},
    {"label": "CN — China",                          "value": "CN"},
    {"label": "ID — Indonesia",                      "value": "ID"},
    {"label": "IN — India",                          "value": "IN"},
    {"label": "JP — Japón",                          "value": "JP"},
    {"label": "KR — Corea del Sur",                  "value": "KR"},
    {"label": "MX — México",                         "value": "MX"},
    {"label": "RU — Federación Rusa",                "value": "RU"},
    {"label": "SA — Arabia Saudita",                 "value": "SA"},
    {"label": "TR — Turquía",                        "value": "TR"},
    {"label": "US — Estados Unidos",                 "value": "US"},
    {"label": "ZA — Sudáfrica",                      "value": "ZA"},
]

# tipo_trx: instrumentos de transacción reales del dataset
TIPO_TRX_OPTS = [
    {"label": "CHQ — Cheques",                                      "value": "CHQ"},
    {"label": "CP0 — Card payments",                                "value": "CP0"},
    {"label": "CT0 — Credit transfers",                             "value": "CT0"},
    {"label": "CW1 — Cash withdrawals using cards",                 "value": "CW1"},
    {"label": "DD — Direct debits",                                 "value": "DD"},
    {"label": "EMP0 — E-money payments",                            "value": "EMP0"},
    {"label": "MREM — Money remittances",                           "value": "MREM"},
    {"label": "ND0 — Other services (not in Directive 2013/2466)",  "value": "ND0"},
    {"label": "ND1 — Credits by simple book entry",                 "value": "ND1"},
    {"label": "ND2 — Debits by simple book entry",                  "value": "ND2"},
    {"label": "ND3 — Other services (non-credit/debit book entry)", "value": "ND3"},
    {"label": "SER — Other payment services",                       "value": "SER"},
    {"label": "TOTL — Total payment transactions",                  "value": "TOTL"},
    {"label": "TOTL1 — Total excl. cash withdrawals",               "value": "TOTL1"},
]

# tipo_psp: rol del proveedor de servicios de pago
TIPO_PSP_OPTS = [
    {"label": "1 — Payer's PSP (pagador)",       "value": "1"},
    {"label": "2 — Payee's PSP (beneficiario)",  "value": "2"},
    {"label": "_Z — No aplica / Interno",        "value": "_Z"},
]

# unidad: tipo de medida/divisa del monto
UNIDAD_OPTS = [
    {"label": "PN — Número puro (conteo)",                              "value": "PN"},
    {"label": "EUR — Euro",                                             "value": "EUR"},
    {"label": "XDF — Divisa doméstica",                                 "value": "XDF"},
    {"label": "PN_R_POP — Núm. puro per cápita",                       "value": "PN_R_POP"},
    {"label": "EUR_R_POP — Euro per cápita",                           "value": "EUR_R_POP"},
    {"label": "EUR_R_TT — Euro / total valor transacciones",           "value": "EUR_R_TT"},
    {"label": "PN_R_TT — Núm. puro / total número transacciones",      "value": "PN_R_TT"},
    {"label": "EUR_R_PNT — Euro / número de transacciones",            "value": "EUR_R_PNT"},
    {"label": "EUR_R_B1GQ — Euro / PIB",                               "value": "EUR_R_B1GQ"},
    {"label": "XDF_R_TT — Divisa doméstica / total valor trx",         "value": "XDF_R_TT"},
    {"label": "XDF_R_PNT — Divisa doméstica / número de trx",          "value": "XDF_R_PNT"},
    {"label": "XDF_R_POP — Divisa doméstica per cápita",               "value": "XDF_R_POP"},
    {"label": "PN_R_POP6 — Núm. puro / millón habitantes",             "value": "PN_R_POP6"},
    {"label": "EUR_R_POP6 — Euro / millón habitantes",                 "value": "EUR_R_POP6"},
    {"label": "XDF_R_POP6 — Divisa doméstica / millón habitantes",     "value": "XDF_R_POP6"},
]

# tipo_monto: clasificación de la validez del monto
TIPO_MONTO_OPTS = [
    {"label": "A — Valor normal",                            "value": "A"},
    {"label": "Q — Valor faltante, suprimido",               "value": "Q"},
    {"label": "M — Valor faltante, dato no puede existir",   "value": "M"},
    {"label": "P — Valor provisional / temporal",            "value": "P"},
    {"label": "L — Valor faltante, no pudo recolectarse",    "value": "L"},
    {"label": "E — Valor estimado",                          "value": "E"},
]

# ── Charts ────────────────────────────────────────────────────────────────────
# Gauge height = CARD_H minus: header (~60px) + veredicto (~70px) + padding (48px)
GAUGE_H = CARD_H - 60 - 70 - 48   # ≈ 522px para CARD_H=700

def make_gauge(prob_fraud):
    color = CORAL if prob_fraud >= 0.3 else GREEN
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob_fraud * 100, 1),
        number={"suffix": "%", "font": {"size": 56, "family": FONT_D, "color": color}},
        gauge={
            "axis": {
                "range": [0, 100], "tickwidth": 1,
                "tickcolor": TEXT_SEC, "tickfont": {"size": 12, "color": TEXT_SEC},
            },
            "bar": {"color": color, "thickness": 0.2},
            "bgcolor": LIGHT_BG,
            "borderwidth": 0,
            "steps": [
                {"range": [0,  30], "color": "#e8fdf4"},
                {"range": [30, 60], "color": "#fff3e0"},
                {"range": [60,100], "color": "#fff0f3"},
            ],
            "threshold": {
                "line": {"color": CORAL, "width": 3},
                "thickness": 0.75, "value": 30,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": FONT_B, "color": DARK, "size": 13},
        height=GAUGE_H,
        margin={"l": 30, "r": 30, "t": 40, "b": 20},
        showlegend=False,
    )
    return fig


def make_proba_bar(p_fraud, p_legit):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[p_legit * 100], y=[""],
        orientation="h", marker_color=GREEN, name="Legítima",
        hovertemplate="%{x:.1f}%<extra>Legítima</extra>",
    ))
    fig.add_trace(go.Bar(
        x=[p_fraud * 100], y=[""],
        orientation="h", marker_color=CORAL, name="Fraude",
        hovertemplate="%{x:.1f}%<extra>Fraude</extra>",
        base=[p_legit * 100],
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": FONT_B, "color": DARK, "size": 12},
        height=120,
        barmode="stack",
        showlegend=True,
        legend={
            "orientation": "h",
            "y": -0.9,
            "x": 0,
            "xanchor": "left",
            "font": {"size": 11},
            "bgcolor": "rgba(0,0,0,0)",
        },
        xaxis={"range": [0, 100], "showgrid": False, "zeroline": False,
               "ticksuffix": "%", "tickfont": {"size": 10}},
        yaxis={"showgrid": False, "showticklabels": False},
        margin={"l": 0, "r": 0, "t": 8, "b": 52},
    )
    return fig


# ── UI helpers ────────────────────────────────────────────────────────────────
def card(children, extra_style=None):
    style = {
        "background": WHITE,
        "borderRadius": "16px",
        "padding": "24px",
        "boxShadow": "0 2px 16px rgba(124,106,247,0.09)",
        "border": f"1px solid {BORDER}",
        "boxSizing": "border-box",
    }
    if extra_style:
        style.update(extra_style)
    return html.Div(children, style=style)


def lbl(text):
    return html.P(text, style={
        "fontSize": "11px", "fontWeight": "600", "color": TEXT_SEC,
        "textTransform": "uppercase", "letterSpacing": "0.5px",
        "marginBottom": "5px", "marginTop": "0",
    })


def ddrop(id_, options, value):
    return dcc.Dropdown(
        id=id_, options=options, value=value, clearable=False,
        style={
            "borderRadius": "8px", "border": f"1.5px solid {BORDER}",
            "fontFamily": FONT_B, "fontSize": "13px",
        },
    )


def stat_row(label_text, value_text, color=None, last=False):
    return html.Div([
        html.Span(label_text, style={"fontSize": "12px", "color": TEXT_SEC}),
        html.Span(value_text, style={
            "fontSize": "12px", "fontWeight": "700",
            "color": color or DARK,
            "fontFamily": "JetBrains Mono, monospace",
        }),
    ], style={
        "display": "flex", "justifyContent": "space-between",
        "padding": "7px 0",
        "borderBottom": "none" if last else f"1px solid {BORDER}",
    })


# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div([

    # Header
    html.Div([
        html.Div([
            html.P("Modelo Predictivo", style={
                "fontSize": "11px", "fontWeight": "700", "color": CORAL,
                "textTransform": "uppercase", "letterSpacing": "1.5px",
                "marginBottom": "5px",
            }),
            html.H1("Detección de Fraude en Tiempo Real", style={
                "fontFamily": FONT_D, "fontSize": "clamp(20px, 2.5vw, 28px)",
                "fontWeight": "800", "color": DARK, "letterSpacing": "-0.8px",
                "margin": "0 0 6px 0",
            }),
            html.P(
                "XGBoost pipeline · API Railway · Umbral de clasificación 30%",
                style={"fontSize": "13px", "color": TEXT_SEC, "margin": "0"},
            ),
        ], style={"flex": "1"}),
        html.Div([
            svg_img(SVG_DOT_SRC, "10px", "10px", {"marginRight": "6px"}),
            html.Span("API activa · Railway",
                      style={"fontSize": "12px", "fontWeight": "600", "color": GREEN}),
        ], style={
            "background": "#e8fdf4", "borderRadius": "20px",
            "padding": "8px 14px", "display": "flex",
            "alignItems": "center", "alignSelf": "flex-start",
        }),
    ], style={
        "display": "flex", "alignItems": "flex-start",
        "justifyContent": "space-between", "marginBottom": "24px",
        "flexWrap": "wrap", "gap": "16px",
    }),

    # ── 3 columnas ────────────────────────────────────────────────────────────
    html.Div([

        # COL 1: Formulario
        card([
            html.H3("Datos de la Transacción", style={
                "fontFamily": FONT_D, "fontSize": "14px",
                "fontWeight": "700", "color": DARK, "marginBottom": "16px",
            }),
            html.Div([lbl("Frecuencia"),      ddrop("fr-frec",  FRECUENCIA_OPTS,   "H")],   style={"marginBottom": "10px"}),
            html.Div([lbl("País Origen"),      ddrop("fr-orig",  PAIS_ORIGEN_OPTS,  "LU")],  style={"marginBottom": "10px"}),
            html.Div([lbl("País Destino"),     ddrop("fr-dest",  PAIS_DESTINO_OPTS, "W0")],  style={"marginBottom": "10px"}),
            html.Div([lbl("Tipo Transacción"), ddrop("fr-tipo",  TIPO_TRX_OPTS,     "EMP0")], style={"marginBottom": "10px"}),
            html.Div([lbl("PSP"),              ddrop("fr-psp",   TIPO_PSP_OPTS,     "1")],   style={"marginBottom": "10px"}),
            html.Div([lbl("Unidad"),           ddrop("fr-unit",  UNIDAD_OPTS,       "EUR")], style={"marginBottom": "10px"}),
            html.Div([lbl("Tipo Monto"),       ddrop("fr-tmonto",TIPO_MONTO_OPTS,   "A")],   style={"marginBottom": "10px"}),
            html.Div([
                lbl("Cantidad"),
                dcc.Input(
                    id="fr-monto", type="number", value=0.3, min=0,
                    style={
                        "width": "100%", "padding": "7px 10px",
                        "borderRadius": "8px", "border": f"1.5px solid {BORDER}",
                        "fontFamily": FONT_B, "fontSize": "13px",
                        "color": DARK, "outline": "none", "boxSizing": "border-box",
                    },
                ),
            ], style={"marginBottom": "18px"}),
            html.Button(
                [svg_img(SVG_SCAN_SRC, "15px", "15px", {"marginRight": "7px", "verticalAlign": "middle"}),
                 html.Span("Analizar", style={"verticalAlign": "middle"})],
                id="btn-predict", n_clicks=0,
                style={
                    "width": "100%", "padding": "11px",
                    "background": f"linear-gradient(135deg, {CORAL} 0%, #f07090 100%)",
                    "color": WHITE, "border": "none", "borderRadius": "10px",
                    "fontSize": "14px", "fontWeight": "700", "fontFamily": FONT_D,
                    "cursor": "pointer", "display": "flex", "alignItems": "center",
                    "justifyContent": "center", "boxShadow": f"0 4px 14px {CORAL}44",
                },
            ),
            html.Div(id="pred-error", style={"marginTop": "10px"}),
        ], extra_style={
            "flex": "0 0 21%", "minWidth": "190px",
            "height": f"{CARD_H}px", "overflowY": "auto",
        }),

        # COL 2: Gauge — el graph ocupa todo el flex restante del card
        card([
            html.H3("Probabilidad de Fraude", style={
                "fontFamily": FONT_D, "fontSize": "15px",
                "fontWeight": "700", "color": DARK, "marginBottom": "2px",
            }),
            html.P("XGBoost · Pipeline completo",
                   style={"fontSize": "12px", "color": TEXT_SEC, "marginBottom": "0"}),
            # wrapper flex que crece — el graph recibe toda la altura disponible
            html.Div(
                dcc.Graph(
                    id="gauge-chart",
                    figure=make_gauge(0.0),
                    config={"displayModeBar": False},
                    style={"width": "100%", "height": "100%"},
                ),
                style={"flex": "1", "minHeight": "0"},   # minHeight:0 es clave para flex
            ),
            html.Div(id="veredicto"),
        ], extra_style={
            "flex": "1",
            "height": f"{CARD_H}px",
            "display": "flex",
            "flexDirection": "column",
        }),

        # COL 3: Distribución + Detalle
        html.Div([
            card([
                html.H4("Distribución de probabilidades", style={
                    "fontSize": "13px", "fontWeight": "700",
                    "color": DARK, "marginBottom": "2px",
                }),
                html.P("Por clase · legítima vs fraude",
                       style={"fontSize": "11px", "color": TEXT_SEC, "marginBottom": "0"}),
                dcc.Graph(
                    id="proba-bar",
                    figure=make_proba_bar(0.0, 1.0),
                    config={"displayModeBar": False},
                ),
            ], extra_style={"marginBottom": "14px", "flex": "0 0 auto"}),
            card([
                html.H4("Detalle de la predicción", style={
                    "fontSize": "13px", "fontWeight": "700",
                    "color": DARK, "marginBottom": "10px",
                }),
                html.Div(
                    id="pred-detail-inner",
                    children=html.Div([
                        html.Div("🔍", style={"fontSize": "28px", "marginBottom": "8px"}),
                        html.P("Haz clic en Analizar", style={
                            "fontSize": "13px", "fontWeight": "600",
                            "color": DARK, "margin": "0 0 4px 0",
                        }),
                        html.P("para ver el resultado de la predicción aquí.",
                               style={"fontSize": "12px", "color": TEXT_SEC, "margin": "0"}),
                    ], style={
                        "display": "flex", "flexDirection": "column",
                        "alignItems": "center", "justifyContent": "center",
                        "textAlign": "center",
                        "padding": "24px 12px",
                        "background": LIGHT_BG,
                        "borderRadius": "10px",
                        "border": f"1.5px dashed {BORDER}",
                    }),
                ),
            ], extra_style={"flex": "1"}),
        ], style={
            "flex": "0 0 27%", "minWidth": "200px",
            "height": f"{CARD_H}px",
            "display": "flex", "flexDirection": "column",
        }),

    ], style={"display": "flex", "gap": "16px", "alignItems": "stretch"}),

], style={
    "padding": "28px 32px", "fontFamily": FONT_B,
    "background": LIGHT_BG, "minHeight": "100vh",
})


# ── Callback ──────────────────────────────────────────────────────────────────
@callback(
    Output("gauge-chart",       "figure"),
    Output("proba-bar",         "figure"),
    Output("veredicto",         "children"),
    Output("pred-detail-inner", "children"),
    Output("pred-error",        "children"),
    Input("btn-predict",   "n_clicks"),
    State("fr-frec",   "value"),
    State("fr-orig",   "value"),
    State("fr-dest",   "value"),
    State("fr-tipo",   "value"),
    State("fr-psp",    "value"),
    State("fr-unit",   "value"),
    State("fr-tmonto", "value"),
    State("fr-monto",  "value"),
    prevent_initial_call=True,
)
def predict(n, frecuencia, pais_origen, pais_destino,
            tipo_trx, tipo_psp, unidad, tipo_monto, monto_final):

    payload = {
        "frecuencia":   frecuencia,
        "pais_origen":  pais_origen,
        "pais_destino": pais_destino,
        "tipo_trx":     tipo_trx,
        "tipo_psp":     tipo_psp,
        "unidad":       unidad,
        "tipo_monto":   tipo_monto,
        "monto_final":  float(monto_final or 0),
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        return no_update, no_update, no_update, no_update, _error_box("Timeout: la API tardó demasiado.")
    except Exception as e:
        return no_update, no_update, no_update, no_update, _error_box(f"Error: {str(e)[:90]}")

    p_fraud   = data["probability_fraud"]
    p_legit   = data["probability_legit"]
    pred      = data["prediction"]
    threshold = data.get("threshold_used", 0.3)
    version   = data.get("model_version", "xgb_fraude_v1")
    is_fraud  = pred == 1

    veredicto = html.Div([
        html.Div([
            svg_img(SVG_ALERT_SRC if is_fraud else SVG_CHECK_SRC, "20px", "20px"),
            html.Div([
                html.P(
                    "FRAUDE DETECTADO" if is_fraud else "TRANSACCIÓN LEGÍTIMA",
                    style={"fontSize": "13px", "fontWeight": "800", "margin": "0",
                           "color": CORAL if is_fraud else GREEN,
                           "fontFamily": FONT_D, "letterSpacing": "0.8px"},
                ),
                html.P(
                    f"Supera el umbral del {threshold*100:.0f}%" if is_fraud
                    else f"Por debajo del umbral del {threshold*100:.0f}%",
                    style={"fontSize": "11px", "color": TEXT_SEC, "margin": "2px 0 0 0"},
                ),
            ]),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px"}),
    ], style={
        "background": f"{CORAL}10" if is_fraud else f"{GREEN}10",
        "border": f"1.5px solid {CORAL}40" if is_fraud else f"1.5px solid {GREEN}40",
        "borderRadius": "10px", "padding": "12px 16px", "marginTop": "12px",
    })

    detail_rows = html.Div([
        stat_row("Modelo",      version),
        stat_row("Umbral",      f"{threshold*100:.0f}%"),
        stat_row("P(fraude)",   f"{p_fraud*100:.2f}%",  color=CORAL if is_fraud else GREEN),
        stat_row("P(legítima)", f"{p_legit*100:.2f}%",  color=GREEN if not is_fraud else TEXT_SEC),
        stat_row("Resultado",   "FRAUDE" if is_fraud else "LEGÍTIMA",
                 color=CORAL if is_fraud else GREEN, last=True),
    ])

    return make_gauge(p_fraud), make_proba_bar(p_fraud, p_legit), veredicto, detail_rows, None


def _error_box(msg):
    return html.Div([
        svg_img(SVG_ERROR_SRC, "14px", "14px", {"marginRight": "8px", "flexShrink": "0"}),
        html.Span(msg, style={"fontSize": "12px"}),
    ], style={
        "background": "#fff0f3", "border": f"1.5px solid {CORAL}44",
        "borderRadius": "8px", "padding": "10px 14px",
        "color": CORAL, "fontWeight": "500",
        "display": "flex", "alignItems": "center",
    })