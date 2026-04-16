import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
from utils.svg_icons import ico_circle_x, ico_circle_ok, ico_alert
from utils.data_loader import load_data

dash.register_page(__name__, path="/problema", name="Problema", order=2)

A = "#FF6584"; P = "#6C5CE7"; T = "#00C9A7"; AM = "#FDB94B"

def layout():
    df = load_data()
    vc = df["tipo_fraude"].value_counts().reset_index()
    vc.columns = ["Tipo", "Conteo"]
    vc["Porcentaje"] = (vc["Conteo"] / vc["Conteo"].sum() * 100).round(2)

    fraude_n    = int(vc[vc["Tipo"] == "con fraude"]["Conteo"].values[0])   if "con fraude"  in vc["Tipo"].values else 1944
    no_fraude_n = int(vc[vc["Tipo"] == "sin fraude"]["Conteo"].values[0]) if "sin fraude" in vc["Tipo"].values else 660672

    # ── Main bar chart ─────────────────────────────────────────────────
    fig_bar = go.Figure()
    colors = {"sin fraude": P, "con fraude": A}
    for _, row in vc.iterrows():
        fig_bar.add_trace(go.Bar(
            name=row["Tipo"], x=[row["Tipo"]], y=[row["Conteo"]],
            marker_color=colors.get(row["Tipo"], "#ccc"),
            marker_line_width=0,
            text=[f'{row["Conteo"]:,}<br>({row["Porcentaje"]}%)'],
            textposition="outside",
            textfont=dict(size=12, family="Sora"),
        ))
    fig_bar.update_layout(
        template="plotly_white", showlegend=False,
        height=260, margin=dict(t=10, b=10, l=10, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="", gridcolor="#F0EDE8"),
        xaxis=dict(title=""),
        font=dict(family="Plus Jakarta Sans", color="#1E1E2E"),
        bargap=0.5,
    )

    # ── Fraud trend line ───────────────────────────────────────────────
    years = [2020, 2021, 2022, 2023, 2024]
    vals  = [2.1,  2.9,  3.4,  3.5,  4.2]
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=years, y=vals, mode="lines+markers+text",
        line=dict(color=A, width=3),
        marker=dict(color=A, size=8),
        text=[f"€{v}B" for v in vals],
        textposition="top center",
        textfont=dict(size=10, color=A, family="Sora"),
        fill="tozeroy", fillcolor="rgba(255,101,132,.08)",
        hovertemplate="<b>%{x}</b><br>€%{y}B<extra></extra>",
    ))
    fig_trend.update_layout(
        height=160, margin=dict(t=24, b=8, l=8, r=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(size=10, color="#AEADB8"), showgrid=False,
                   tickvals=years),
        yaxis=dict(visible=False), showlegend=False,
    )

    return html.Div([
        html.Div([
            html.Div([
                html.H1("El Problema", className="page-title"),
                html.P("Crecimiento del fraude financiero digital en la Unión Europea",
                       className="page-sub"),
            ], className="section-header"),
            
            # ── ROW 3: Trend (full width) ─────────────────────────────
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("Tendencia del fraude · 2020–2024", className="card-title"),
                    html.Div("Valor total de transacciones fraudulentas en el EEE · €Billones", className="card-sub"),
                    dcc.Graph(figure=fig_trend, config={"displayModeBar": False}),
                ], className="card"), md=12),
            ], className="g-3"),

            # ── ROW 1: KPI mini cards ──────────────────────────────────
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("€4.2B", style={"fontSize": "26px", "fontWeight": "800",
                                              "color": A, "fontFamily": "'Sora',sans-serif", "lineHeight": "1"}),
                    html.Div("Fraude total 2024", style={"fontSize": "11px", "color": "#AEADB8", "marginTop": "4px"}),
                    html.Div("↑ 20% vs 2023", style={"fontSize": "11px", "fontWeight": "700", "color": A, "marginTop": "3px"}),
                ], className="card", style={"textAlign": "center", "padding": "18px"}), md=3),

                dbc.Col(html.Div([
                    html.Div(f"{fraude_n:,}", style={"fontSize": "26px", "fontWeight": "800",
                                                      "color": A, "fontFamily": "'Sora',sans-serif", "lineHeight": "1"}),
                    html.Div("transacciones con fraude", style={"fontSize": "11px", "color": "#AEADB8", "marginTop": "4px"}),
                    html.Div("0.3% del total", style={"fontSize": "11px", "fontWeight": "700", "color": "#AEADB8", "marginTop": "3px"}),
                ], className="card", style={"textAlign": "center", "padding": "18px"}), md=3),

                dbc.Col(html.Div([
                    html.Div(f"{no_fraude_n:,}", style={"fontSize": "26px", "fontWeight": "800",
                                                         "color": P, "fontFamily": "'Sora',sans-serif", "lineHeight": "1"}),
                    html.Div("transacciones legítimas", style={"fontSize": "11px", "color": "#AEADB8", "marginTop": "4px"}),
                    html.Div("99.7% del total", style={"fontSize": "11px", "fontWeight": "700", "color": P, "marginTop": "3px"}),
                ], className="card", style={"textAlign": "center", "padding": "18px"}), md=3),

                dbc.Col(html.Div([
                    html.Div("27+", style={"fontSize": "26px", "fontWeight": "800",
                                            "color": T, "fontFamily": "'Sora',sans-serif", "lineHeight": "1", "color": A}),
                    html.Div("países analizados", style={"fontSize": "11px", "color": "#AEADB8", "marginTop": "4px"}),
                    html.Div("UE · 2000–2024", style={"fontSize": "11px", "fontWeight": "700", "color": "#AEADB8", "marginTop": "3px"}),
                ], className="card", style={"textAlign": "center", "padding": "18px"}), md=3),
            ], className="g-3 mb-3", style={"margin-top": "3px"}),

            # ── ROW 2: Descripción + Bar (equal height) ───────────────
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("Descripción del Problema", className="card-title"),
                    html.Hr(style={"borderColor": "#F0EDE8", "margin": "8px 0 14px"}),
                    html.Div([
                        html.P("La digitalización acelerada del sistema financiero europeo ha generado un incremento sostenido en las actividades fraudulentas. El valor total de transacciones fraudulentas en el EEE ascendió a €4,2 billones en 2024, frente a €3,5B en 2023 y €3,4B en 2022. Los nuevos tipos de fraude, especialmente aquellos que implican la manipulación de los pagadores, registran una tendencia creciente que exige enfoques de mitigación más sofisticados."),
                        
                        html.P("Uno de los principales desafíos radica en la naturaleza profundamente desbalanceada de los conjuntos de datos: las transacciones fraudulentas representan apenas el 0.3% del total."),
                    ], className="intro-text", style={"marginBottom": "12px"}),
                    html.Div([
                        html.Div([
                            ico_alert(size=14),
                            html.Span("Desbalance de clases",
                                      style={"fontSize": "12px", "fontWeight": "700",
                                             "color": AM, "marginLeft": "6px",
                                             "verticalAlign": "middle"}),
                        ]),
                        html.P("Se deberán aplicar técnicas de balanceo como SMOTE, "
                               "submuestreo o ajuste de pesos en el clasificador.",
                               style={"fontSize": "12px", "color": "#6E6D7A",
                                      "lineHeight": "1.5", "margin": "4px 0 0"}),
                    ], style={"background": "#FFF8EC", "borderRadius": "10px",
                              "padding": "12px", "borderLeft": f"3px solid {AM}"}),
                ], className="card", style={"height": "100%"}), md=8),

                dbc.Col(html.Div([
                    html.Div("Distribución tipo_fraude · Variable Objetivo", className="card-title"),
                    html.Div("Alto desbalance · 99.7% sin fraude vs 0.3% con fraude", className="card-sub"),
                    dcc.Graph(figure=fig_bar, config={"displayModeBar": False}),
                ], className="card", style={"height": "100%"}), md=4),

                
            ], className="g-3 mb-3", style={"alignItems": "stretch"}),

            

        ], className="page-content"),
    ])
