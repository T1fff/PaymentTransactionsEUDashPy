import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from utils.svg_icons import ico_credit_card, ico_columns, ico_globe, ico_alert

dash.register_page(__name__, path="/", name="Introducción", order=0)

# ── palette ──────────────────────────────────────────────────────────
A = "#FF6584"; P = "#6C5CE7"; T = "#00C9A7"; AM = "#FDB94B"

def kpi_icon(ico_fn, bg):
    return html.Div(ico_fn(), className="kpi-icon",
                    style={"background": bg, "display": "flex",
                           "alignItems": "center", "justifyContent": "center"})

# ── Fraud trend sparkline ──────────────────────────────────────────────
years = list(range(2014, 2025))
fraud_bn = [1.1, 1.4, 1.7, 1.9, 2.3, 2.7, 2.1, 2.9, 3.4, 3.5, 4.2]

fig_spark = go.Figure()
fig_spark.add_trace(go.Scatter(
    x=years, y=fraud_bn,
    mode="lines", fill="tozeroy",
    line=dict(color="rgba(255,255,255,.9)", width=2.5),
    fillcolor="rgba(255,255,255,.15)",
    hovertemplate="<b>%{x}</b><br>€%{y}B<extra></extra>",
))
fig_spark.update_layout(
    height=90, margin=dict(t=0,b=0,l=0,r=0),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(visible=False), yaxis=dict(visible=False),
    showlegend=False,
)

# ── Donut: fraude vs no fraude ─────────────────────────────────────────
fig_donut = go.Figure(go.Pie(
    values=[1944, 660672], labels=["con fraude", "sin fraude"],
    hole=0.72,
    marker_colors=[A, P],
    textinfo="none",
    hovertemplate="<b>%{label}</b><br>%{value:,}<br>%{percent}<extra></extra>",
))
fig_donut.add_annotation(text="0.3%", x=0.5, y=0.55, showarrow=False,
                          font=dict(size=22, color=A, family="Sora"), xanchor="center")
fig_donut.add_annotation(text="fraude", x=0.5, y=0.4, showarrow=False,
                          font=dict(size=11, color="#6E6D7A"), xanchor="center")
fig_donut.update_layout(
    height=135, margin=dict(t=10,b=10,l=10,r=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
)

# ── Fraud by year bar ──────────────────────────────────────────────────
fig_bar = go.Figure(go.Bar(
    x=years, y=fraud_bn,
    marker_color=[A if y >= 2022 else "#E8E5DE" for y in years],
    marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>€%{y}B<extra></extra>",
))
fig_bar.update_layout(
    height=150, margin=dict(t=8,b=8,l=8,r=8),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(tickfont=dict(size=10, color="#AEADB8"), showgrid=False),
    yaxis=dict(visible=False), showlegend=False,
    bargap=0.3,
)

layout = html.Div([
    html.Div([
        # ── HEADER ────────────────────────────────────────────────────
        html.Div([
            html.P("Tiffany Mendoza S. y Sergio Rada · 2026-03-30",
                   style={"fontSize": "12px", "color": "#AEADB8", "marginBottom": "4px"}),
            html.H1("Detección de Fraude en Transacciones de Pago · UE",
                    className="page-title"),
            html.P("Análisis Exploratorio de Datos · Banco Central Europeo · 662,616 registros",
                   className="page-sub"),
        ], className="section-header"),

        # ── ROW 1: KPIs (equal height) ─────────────────────────────────
        dbc.Row([
            # Hero KPI – gradient coral
            dbc.Col(html.Div([
                html.Div("Fraude total 2024", className="kpi-lbl",
                         style={"color": "rgba(255,255,255,.8)", "marginBottom": "6px"}),
                html.Div("€4.2B", className="kpi-val",
                         style={"color": "#fff", "fontSize": "36px", "fontFamily": "'Sora',sans-serif"}),
                html.Div("↑ 20% vs 2023", className="kpi-trend",
                         style={"color": "rgba(255,255,255,.9)", "marginBottom": "8px"}),
                dcc.Graph(figure=fig_spark, config={"displayModeBar": False},
                          style={"marginTop": "auto"}),
            ], className="kpi-hero",
               style={"display": "flex", "flexDirection": "column", "minHeight": "160px"}), md=3),
            
            # Tendencia fraude anual
            dbc.Col(html.Div([
                html.Div("Fraude anual · €B", className="card-title"),
                html.Div("Valor total en el EEE · 2014–2024", className="card-sub"),
                dcc.Graph(figure=fig_bar, config={"displayModeBar": False}),
                dbc.Row([
                    dbc.Col(html.Div([
                        html.Div("€3.4B", style={"fontSize": "13px", "fontWeight": "800", "color": "#AEADB8", "fontFamily": "'Sora',sans-serif"}),
                        html.Div("2022", style={"fontSize": "10px", "color": "#AEADB8"}),
                    ], style={"textAlign": "center"}), md=4),
                    dbc.Col(html.Div([
                        html.Div("€3.5B", style={"fontSize": "13px", "fontWeight": "800", "color": "#AEADB8", "fontFamily": "'Sora',sans-serif"}),
                        html.Div("2023", style={"fontSize": "10px", "color": "#AEADB8"}),
                    ], style={"textAlign": "center"}), md=4),
                    dbc.Col(html.Div([
                        html.Div("€4.2B", style={"fontSize": "14px", "fontWeight": "800", "color": A, "fontFamily": "'Sora',sans-serif"}),
                        html.Div("2024 ↑", style={"fontSize": "10px", "color": A}),
                    ], style={"textAlign": "center"}), md=4),
                ], className="g-2"),
            ], className="card", style={"height": "100%"}), md=3),
            
            # Donut fraude
            dbc.Col(html.Div([
                html.Div("Variable objetivo · tipo_fraude", className="card-title"),
                html.Div("Distribución de clases · alto desbalance", className="card-sub"),
                dcc.Graph(figure=fig_donut, config={"displayModeBar": False}),
                dbc.Row([
                    dbc.Col(html.Div([
                        html.Div("■", style={"color": A, "fontSize": "15px", "lineHeight": "1"}),
                        html.Div("1,944", style={"fontSize": "14px", "fontWeight": "800", "color": A, "fontFamily": "'Sora',sans-serif"}),
                        html.Div("con fraude · 0.3%", style={"fontSize": "10px", "color": "#AEADB8"}),
                    ], style={"textAlign": "center"}), md=6),
                    dbc.Col(html.Div([
                        html.Div("■", style={"color": P, "fontSize": "15px", "lineHeight": "1"}),
                        html.Div("660,672", style={"fontSize": "14px", "fontWeight": "800", "color": P, "fontFamily": "'Sora',sans-serif"}),
                        html.Div("sin fraude · 99.7%", style={"fontSize": "10px", "color": "#AEADB8"}),
                    ], style={"textAlign": "center"}), md=6),
                ], className="g-2"),
            ], className="card", style={"height": "100%"}), md=3),
            
            # Regular KPIs
            dbc.Col(html.Div([
                kpi_icon(ico_credit_card, "#FFF0F3"),
                html.Div("662,616", className="kpi-val"),
                html.Div("Total registros", className="kpi-lbl"),
                html.Div("29 columnas totales", 
                         className="kpi-trend",
                         style={"color": "#AEADB8"}),
                html.Div("14 columnas tras limpieza y selección", 
                         className="kpi-trend",
                         style={"color": "#AEADB8"}),
                html.Div("21.7% del valores faltantes en columna monto", className="kpi-trend",
                         style={"color": "#FDB94B"}),
            ], className="kpi-card"), md=3),

            
            
        ], className="g-3 mb-3", style={"alignItems": "stretch"}),


        # ── ROW 3: Estructura + Origen (equal height) ──────────────────
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Contexto inicial", className="card-title"),
                html.Hr(style={"borderColor": "#F0EDE8", "margin": "8px 0 14px"}),
                html.Div([
                    html.P("El sistema financiero europeo constituye uno de los ecosistemas de pagos más integrados y regulados a nivel mundial. La creación de la Unión Europea impulsó el desarrollo de infraestructuras comunes que permiten el flujo de capital entre estados miembro casi de forma instantánea; en ese marco el sistema T2 desempeña un papel central al facilitar la circulación transfronteriza de dinero, apoyar la política monetaria única y ofrecer servicios de gestión de liquidez y liquidación en tiempo real."),
                    html.P("La creciente digitalización de las transacciones ha traído un aumento del fraude. Según datos del BCE, el valor de transacciones fraudulentas en el mostraron un incremento marcado en 2024, lo que exige defensas dinámicas y detección avanzada. El aprendizaje automático se perfila como una de las aproximaciones más prometedoras: modelos como Random Forest, redes neuronales y Naive Bayes han mostrado alta capacidad discriminante aunque enfrentan el reto del desbalance de clases."),
                ], className="intro-text", style={"margin": "0"}),
            ], className="card", style={"height": "100%"}), md=6),

            dbc.Col(html.Div([
                html.Div("Estructura del Proyecto", className="card-title"),
                html.Hr(style={"borderColor": "#F0EDE8", "margin": "8px 0 14px"}),
                *[html.Div([
                    html.Span(str(n), style={
                        "background": bg, "color": tc, "borderRadius": "50%",
                        "width": "24px", "height": "24px", "display": "inline-flex",
                        "alignItems": "center", "justifyContent": "center",
                        "fontSize": "11px", "fontWeight": "800", "marginRight": "12px",
                        "flexShrink": "0",
                    }),
                    html.Div([
                        html.Div(label, style={"fontSize": "13px", "fontWeight": "700", "color": "#1E1E2E"}),
                        html.Div(sub,   style={"fontSize": "11px", "color": "#AEADB8", "marginTop": "1px"}),
                    ]),
                ], style={"display": "flex", "alignItems": "center",
                          "padding": "11px 0", "borderBottom": "1px solid #F0EDE8"})
                for n, bg, tc, label, sub in [
                    (1, "#FF6584", "#fff", "Análisis Exploratorio de Datos", "Univariado y bivariado"),
                    (2, "#FF9AAB", "#fff", "Análisis Univariado",            "Distribuciones y estadísticas"),
                    (3, "#6C5CE7", "#fff", "Análisis Bivariado",             "Variable objetivo vs independientes"),
                    (4, "#00C9A7", "#fff", "Dashboard Interactivo",          "Visualización dinámica"),
                    (5, "#FDB94B", "#fff", "Modelo ML Predictivo",           "Random Forest · clasificación de fraude"),
                ]],
            ], className="card", style={"height": "100%"}), md=3),

            dbc.Col(html.Div([
                html.Div("Origen de los Datos", className="card-title"),
                html.Hr(style={"borderColor": "#F0EDE8", "margin": "8px 0 14px"}),
                html.Div([
                    html.Div("BCE", style={"fontSize": "32px", "fontWeight": "800",
                                            "fontFamily": "'Sora',sans-serif", "color": "#FF6584"}),
                    html.Div("Banco Central Europeo", style={"fontSize": "12px", "color": "#AEADB8"}),
                ], style={"marginBottom": "16px"}),
                html.P("Repositorio público de estadísticas de pagos de la Unión Europea. "
                       "Datos validados semestralmente por los Bancos Centrales Nacionales.",
                       style={"fontSize": "13px", "color": "#6E6D7A", "lineHeight": "1.7",
                              "marginBottom": "16px"}),
                dbc.Row([
                    dbc.Col(html.Div([
                        html.Div("2000", style={"fontSize": "18px", "fontWeight": "800",
                                                 "color": "#FF6584", "fontFamily": "'Sora',sans-serif"}),
                        html.Div("desde", style={"fontSize": "10px", "color": "#AEADB8"}),
                    ], style={"textAlign": "center", "padding": "3px",
                              "background": "#FFF0F3", "borderRadius": "10px"}), md=6),
                    dbc.Col(html.Div([
                        html.Div("27", style={"fontSize": "18px", "fontWeight": "800",
                                               "color": "#6C5CE7", "fontFamily": "'Sora',sans-serif"}),
                        html.Div("países", style={"fontSize": "10px", "color": "#AEADB8"}),
                    ], style={"textAlign": "center", "padding": "3px",
                              "background": "#EEF0FF", "borderRadius": "10px"}), md=6),
                ], className="g-2 mb-3", style={"margin-block": "15px"}),
                html.A("Ver fuente original →",
                       href="https://data.ecb.europa.eu/data/datasets/PAY/data-information?showDatasetModal=false",
                       target="_blank",
                       style={"fontSize": "12px", "color": "#FF6584", "fontWeight": "700",
                              "textDecoration": "none", "margin-top": "15px"}),
            ], className="card", style={"height": "100%" }), md=3),
        ], className="g-3", style={"alignItems": "stretch"}),

    ], className="page-content"),
])
