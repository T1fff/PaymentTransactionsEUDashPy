import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from utils.svg_icons import ico_target, ico_bar_chart, ico_grid, ico_network

dash.register_page(__name__, path="/objetivos", name="Objetivos", order=1)

A = "#FF6584"; P = "#6C5CE7"; T = "#00C9A7"; AM = "#FDB94B"

def stage_card(num_label, ico_fn, title, desc, bg_num, bg_card, border_c, title_c):
    return html.Div([
        html.Div([
            html.Div(num_label, style={"fontFamily": "'Sora',sans-serif", "fontSize": "22px",
                                        "fontWeight": "800", "color": bg_num, "lineHeight": "1"}),
            html.Div(ico_fn(), style={"marginLeft": "auto", "display": "flex", "alignItems": "center"}),
        ], style={"display": "flex", "alignItems": "flex-start"}),
        html.Div(title, style={"fontSize": "14px", "fontWeight": "700",
                                "color": title_c, "marginTop": "4px"}),
        html.Div(desc, style={"fontSize": "12px", "color": "#6E6D7A",
                               "lineHeight": "1.55", "marginTop": "5px"}),
    ], style={"padding": "12px", "background": bg_card, "borderRadius": "14px",
              "marginBottom": "10px", "borderLeft": f"4px solid {border_c}",
              "height": "calc(33.33% - 7px)"})



layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Objetivo del Análisis", className="page-title"),
            html.P("Metas generales y específicas del proyecto", className="page-sub"),
        ], className="section-header"),

        # ── ROW 1: Objetivo general (full width) ──────────────────────
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Objetivo General", className="card-title"),
                html.Hr(style={"borderColor": "#F0EDE8", "margin": "8px 0 14px"}),
                html.Div([
                    html.P("Desarrollar un dashboard analítico interactivo orientado a la visualización y exploración de los patrones de transacciones financieras en la Unión Europea, con énfasis en la identificación de variables asociadas a comportamientos fraudulentos.",
                           style={"fontSize": "15px", "color": "#1E1E2E",
                                  "lineHeight": "1.75", "fontWeight": "600"}),
                ]),
            ], className="card"), md=12),
        ], className="g-3 mb-3"),

        # ── ROW 2: OE + Etapas + Gauge (equal height) ─────────────────
        dbc.Row([
            # Objetivos específicos
            dbc.Col(html.Div([
                html.Div("Objetivos Específicos", className="card-title"),
                html.Hr(style={"borderColor": "#F0EDE8", "margin": "8px 0 12px"}),
                html.Div(className="obj-card", children=[
                    html.Div("OE 1 · Calidad del Dato", className="obj-card-title"),
                    html.Div("Evaluar la calidad, cobertura y estructura del conjunto de datos mediante técnicas de análisis descriptivo y detección de valores faltantes.", className="obj-card-text"),
                ]),
                html.Div(className="obj-card", children=[
                    html.Div("OE 2 · Variables Explicativas", className="obj-card-title"),
                    html.Div("Identificar y caracterizar las variables con mayor capacidad explicativa para la clasificación de transacciones fraudulentas.", className="obj-card-text"),
                ]),
                html.Div(className="obj-card", children=[
                    html.Div("OE 3 · Dashboard de Visualización", className="obj-card-title"),
                    html.Div("Diseñar e implementar un dashboard que permita explorar de manera dinámica el comportamiento de las transacciones según dimensiones temporales, geográficas y tipológicas.", className="obj-card-text"),
                ]),
            ], className="card", style={"height": "100%"}), md=7),

            # Etapas
            dbc.Col(html.Div([
                html.Div("Etapas del Proyecto", className="card-title"),
                html.Hr(style={"borderColor": "#F0EDE8", "margin": "8px 0 12px"}),
                stage_card("01", ico_bar_chart, "EDA",
                           "Análisis univariado y bivariado · distribuciones · valores faltantes",
                           "#FFE4E9", "#FFF7F8", A, A),
                stage_card("02", ico_grid, "Dashboard",
                           "Visualización interactiva · filtros dinámicos · mapas · gráficas",
                           "#EEF0FF", "#F8F8FF", P, P),
                stage_card("03", ico_network, "Modelo ML",
                           "Random Forest · Naive Bayes · clasificación de fraude · métricas",
                           "#E0FAF5", "#F5FFFE", T, T),
            ], className="card", style={"height": "100%"}), md=5),

          
        ], className="g-3", style={"alignItems": "stretch"}),

    ], className="page-content"),
])
