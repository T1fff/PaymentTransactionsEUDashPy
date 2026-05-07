import dash
from dash import html, dcc, dash_table, callback, Input, Output
import pandas as pd
import os

dash.register_page(
    __name__,
    path="/modelo-creacion",
    name="Creación del Modelo",
)

# ── Carga de datos ─────────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.dirname(__file__))
_CSV  = os.path.join(_BASE, "data", "comparacion_modelos.csv")
_CSV_PARAMS = os.path.join(_BASE, "data", "mejores_parametros.csv")

try:
    df_params = pd.read_csv(_CSV_PARAMS)
except Exception:
    df_params = pd.DataFrame()
try:
    df_models = pd.read_csv(_CSV)
except Exception:
    df_models = pd.DataFrame()

# ── Datos estadísticos Bootstrap PR-AUC ───────────────────────────────────
STAT_ROWS = [
    {"Modelo A": "Random Forest", "Modelo B": "XGBoost",     "Dif AUC": "-0.000", "IC 95%": "[-0.000, 0.000]", "p-valor": "0.922"},
    {"Modelo A": "Random Forest", "Modelo B": "Naive Bayes", "Dif AUC":  "0.007", "IC 95%": "[0.006, 0.007]",  "p-valor": "0.000"},
    {"Modelo A": "Random Forest", "Modelo B": "LinearSVC",   "Dif AUC":  "0.002", "IC 95%": "[0.001, 0.004]",  "p-valor": "0.000"},
    {"Modelo A": "XGBoost",       "Modelo B": "Naive Bayes", "Dif AUC":  "0.007", "IC 95%": "[0.006, 0.007]",  "p-valor": "0.000"},
    {"Modelo A": "XGBoost",       "Modelo B": "LinearSVC",   "Dif AUC":  "0.002", "IC 95%": "[0.001, 0.004]",  "p-valor": "0.000"},
]

PRAUC_ROWS = [
    {"Modelo": "Random Forest", "PR-AUC": "0.9659", "IC 95%": "[0.9537, 0.9761]"},
    {"Modelo": "XGBoost",       "PR-AUC": "0.9522", "IC 95%": "[0.9357, 0.9656]"},
    {"Modelo": "Naive Bayes",   "PR-AUC": "0.1753", "IC 95%": "[0.1607, 0.1902]"},
    {"Modelo": "LinearSVC",     "PR-AUC": "0.6844", "IC 95%": "[0.6319, 0.7411]"},
]

# ── Helpers ────────────────────────────────────────────────────────────────
def _section_title(icon, title, subtitle=""):
    children_row = []
    if icon:  # ← solo muestra el cuadrado si hay icono
        children_row.append(
            html.Div(icon, style={
                "width": "40px", "height": "40px", "borderRadius": "12px",
                "background": "var(--accent-lt)", "color": "var(--accent)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontSize": "20px", "flexShrink": "0",
            })
        )
    children_row.append(
        html.Div(children=[
            html.H2(title, className="page-title", style={"fontSize": "20px"}),
            html.P(subtitle, className="page-sub") if subtitle else None,
        ])
    )
    return html.Div(style={"marginBottom": "20px", "marginTop": "8px"}, children=[
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "12px"}, children=children_row),
    ])


def _chip(text, color="--accent", bg="--accent-lt"):
    return html.Code(text, style={
        "background": f"var({bg})", "color": f"var({color})",
        "padding": "3px 10px", "borderRadius": "6px",
        "fontSize": "12px", "fontWeight": "700", "fontFamily": "monospace",
        "whiteSpace": "nowrap",
    })


def _pill(label, value, color="var(--accent)"):
    return html.Div(style={
        "background": "var(--surface)", "border": "1px solid var(--border)",
        "borderRadius": "var(--r-sm)", "padding": "12px 16px",
        "display": "flex", "flexDirection": "column", "gap": "3px",
        "boxShadow": "var(--shadow-sm)",
    }, children=[
        html.Span(label, style={
            "fontSize": "10px", "color": "var(--txt2)", "fontWeight": "700",
            "textTransform": "uppercase", "letterSpacing": "0.6px",
        }),
        html.Span(value, style={
            "fontSize": "14px", "fontWeight": "800",
            "color": color, "fontFamily": "Sora, sans-serif",
        }),
    ])


def _simple_table(rows, highlight_col=None, highlight_color="var(--accent)"):
    if not rows:
        return html.Div()
    cols = list(rows[0].keys())
    return html.Table(className="stats-table", style={"width": "100%"}, children=[
        html.Thead(html.Tr([html.Th(c) for c in cols])),
        html.Tbody([
            html.Tr([
                html.Td(
                    row[c],
                    style={
                        "color": highlight_color if c == highlight_col else "var(--txt)",
                        "fontWeight": "700" if c == highlight_col else "400",
                    }
                )
                for c in cols
            ])
            for row in rows
        ]),
    ])


def _inline_note(text, color="--accent", bg="--accent-lt"):
    return html.Div(style={
        "background": f"var({bg})", "borderLeft": f"4px solid var({color})",
        "borderRadius": "0 var(--r-xs) var(--r-xs) 0",
        "padding": "11px 16px", "fontSize": "13px",
        "color": "var(--txt)", "lineHeight": "1.7",
    }, children=text)


def _build_csv_table():
    if df_models.empty:
        return html.P(
            "No se encontró comparacion_modelos.csv en /data/ — verifica la ruta.",
            style={"color": "var(--txt2)", "fontSize": "13px"},
        )

    # Renombrar columnas para display
    df_display = df_models.copy()
    df_display = df_display.drop(columns=["f1_cv_refit"], errors="ignore")
    df_display = df_display.rename(columns={
        "modelo"          : "Modelo",
        "balanceo"        : "Balanceo",
        "pr_auc_cv"       : "PR-AUC CV",
        "roc_auc_cv"      : "ROC-AUC CV",
        "recall_cv"       : "Recall CV",
        "precision_cv"    : "Precision CV",
        "f1_cv"           : "F1 CV",
        "pr_auc_test"     : "PR-AUC Test",
        "roc_auc_test"    : "ROC-AUC Test",
        "tiempo_s"        : "Tiempo (s)",
    })

    # 2. En numeric_cols
    numeric_cols = ["PR-AUC CV", "ROC-AUC CV",
                    "Recall CV", "Precision CV", "F1 CV",
                    "PR-AUC Test", "ROC-AUC Test"]

    columns = []
    for c in df_display.columns:
        col = {"name": c, "id": c}
        if c in numeric_cols:
            col["type"]   = "numeric"
            col["format"] = {"specifier": ".4f"}
        columns.append(col)

    # Colores por modelo
    modelo_colors = {
        "XGBoost_hist"       : "var(--accent)",
        "Random_Forest"      : "var(--teal)",
        "Logistic_Regression": "#8b5cf6",
        "LinearSVC"          : "var(--coral)",
        "Naive_Bayes"        : "var(--amber)",
    }

    style_data_conditional = [
        # Filas alternas
        {"if": {"row_index": "odd"},  "backgroundColor": "var(--surface2)"},
        {"if": {"state": "active"},   "backgroundColor": "var(--accent-lt)", "border": "none"},
        # Columna Modelo en negrita
        {"if": {"column_id": "Modelo"},  "fontWeight": "700"},
        # Columna Balanceo con color acento
        {"if": {"column_id": "Balanceo"}, "color": "var(--accent)", "fontWeight": "600"},
        # PR-AUC Test alto (>= 0.90) en verde
        *[
            {
                "if": {"filter_query": f'{{PR-AUC Test}} >= 0.90', "column_id": "PR-AUC Test"},
                "color": "#16a34a", "fontWeight": "700",
            }
        ],
        # PR-AUC Test medio (0.50 - 0.90) en amarillo
        *[
            {
                "if": {"filter_query": f'{{PR-AUC Test}} < 0.90 && {{PR-AUC Test}} >= 0.50', "column_id": "PR-AUC Test"},
                "color": "var(--amber)", "fontWeight": "600",
            }
        ],
        # PR-AUC Test bajo (< 0.50) en rojo
        *[
            {
                "if": {"filter_query": f'{{PR-AUC Test}} < 0.50', "column_id": "PR-AUC Test"},
                "color": "var(--coral)", "fontWeight": "600",
            }
        ],
    ]

    return dash_table.DataTable(
        data=df_display.to_dict("records"),
        columns=columns,
        style_table={
            "overflowX"    : "auto",
            "borderRadius" : "var(--r-sm)",
            "overflow"     : "hidden",
        },
        style_header={
            "backgroundColor" : "#1a1828",
            "color"           : "#ffffff",
            "fontWeight"      : "700",
            "fontSize"        : "11px",
            "textTransform"   : "uppercase",
            "letterSpacing"   : "0.5px",
            "border"          : "none",
            "borderBottom"    : "2px solid var(--border)",
            "padding"         : "10px 14px",
            "textAlign"       : "center",
        },
        style_cell={
            "fontFamily"      : "Plus Jakarta Sans, sans-serif",
            "fontSize"        : "13px",
            "color"           : "var(--txt)",
            "padding"         : "9px 14px",
            "border"          : "none",
            "borderBottom"    : "1px solid var(--border2)",
            "backgroundColor" : "white",
            "textAlign"       : "center",
            "minWidth"        : "100px",
        },
        style_cell_conditional=[
            {"if": {"column_id": "Modelo"},   "textAlign": "left", "minWidth": "140px"},
            {"if": {"column_id": "Balanceo"}, "textAlign": "left", "minWidth": "110px"},
            {"if": {"column_id": "Tiempo (s)"}, "minWidth": "90px"},
        ],
        style_data_conditional=style_data_conditional,
        page_size=10,
        sort_action="native",
        filter_action="native",
        tooltip_header={
            "PR-AUC Test"   : "Área bajo la curva Precision-Recall en el conjunto de test",
            "ROC-AUC Test"  : "Área bajo la curva ROC en el conjunto de test",
            "F1 CV (refit)" : "F1 usado como métrica de refit en RandomizedSearchCV",
            "Tiempo (s)"    : "Tiempo total de entrenamiento en segundos",
        },
        tooltip_delay=0,
        tooltip_duration=None,
    )
def _params_table(df, modelo, cols_rename):
    """Filtra el df por modelo y muestra solo las columnas relevantes."""
    if df.empty:
        return html.P("No se encontró mejores_parametros.csv", style={"color": "var(--txt2)", "fontSize": "13px"})
    
    subset = df[df["modelo"] == modelo][["balanceo"] + list(cols_rename.keys())].copy()
    subset = subset.rename(columns=cols_rename)
    
    return dash_table.DataTable(
        data=subset.to_dict("records"),
        columns=[{"name": c, "id": c} for c in subset.columns],
        style_table={"overflowX": "auto", "borderRadius": "var(--r-sm)", "overflow": "hidden"},
        style_header={
            "backgroundColor": "#1a1828", "color": "#ffffff",
            "fontWeight": "700", "fontSize": "11px", "textTransform": "uppercase",
            "letterSpacing": "0.5px", "border": "none",
            "borderBottom": "2px solid var(--border)", "padding": "10px 14px",
        },
        style_cell={
            "fontFamily": "Plus Jakarta Sans, sans-serif", "fontSize": "13px",
            "color": "var(--txt)", "padding": "9px 14px",
            "border": "none", "borderBottom": "1px solid var(--border2)",
            "backgroundColor": "white", "textAlign": "center",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "var(--surface2)"},
            {"if": {"column_id": "balanceo"}, "fontWeight": "700", "color": "var(--accent)"},
        ],
    )
    


# ══════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════
layout = html.Div(className="page-content", children=[

    # ── ENCABEZADO ──────────────────────────────────────────────────────────
    html.Div(className="section-header", style={"marginBottom": "36px"}, children=[
        html.H1("Creación del Modelo Predictivo", className="page-title"),
        html.P(
            "Pipeline completo de ML: variables seleccionadas, preprocesamiento, "
            "estrategia de validación, técnicas de balanceo y optimización de hiperparámetros.",
            className="page-sub",
        ),
    ]),


    # ══════════════════════════════════════════════════════════════════════
    # 6 · TABLA RESULTADOS CSV
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Tabla de Resultados", "Métricas y tiempo de cada modelo"),

    html.Div(className="card", style={"marginBottom": "28px"}, children=[
        html.Div("Métricas en validation y test set por modelo y técnica de balanceo", className="card-title"),
        html.Div("Haz clic en los encabezados para ordenar · Escribe en los campos para filtrar", className="card-sub"),
        html.Div(style={"marginTop": "12px"}, children=[_build_csv_table()]),
    ]),
    
# ══════════════════════════════════════════════════════════════════════
# 6.5 · MEJORES HIPERPARÁMETROS
# ══════════════════════════════════════════════════════════════════════
    _section_title("", "Mejores Hiperparámetros por Modelo",
                "Resultado de RandomizedSearchCV (n_iter=20) — un registro por estrategia de balanceo"),

    html.Div(style={"display": "flex", "flexDirection": "column", "gap": "14px", "marginBottom": "28px"}, children=[

        # XGBoost
        html.Div(className="card", style={"borderLeft": "4px solid var(--accent)"}, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "14px"}, children=[
                html.Div("XGBoost", className="card-title", style={"fontSize": "15px", "margin": "0"}),
                html.Span("PR-AUC 0.952", style={
                    "background": "var(--accent-lt)", "color": "var(--accent)",
                    "borderRadius": "20px", "padding": "3px 12px", "fontSize": "11px", "fontWeight": "700",
                }),
            ]),
            _params_table(df_params, "XGBoost_hist", {
                "classifier__learning_rate":    "learning_rate",
                "classifier__max_depth":        "max_depth",
                "classifier__n_estimators":     "n_estimators",
                "classifier__subsample":        "subsample",
                "classifier__scale_pos_weight": "scale_pos_weight",
            }),
        ]),

        # Random Forest
        html.Div(className="card", style={"borderLeft": "4px solid var(--teal)"}, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "14px"}, children=[
                html.Div("Random Forest", className="card-title", style={"fontSize": "15px", "margin": "0"}),
                html.Span("PR-AUC 0.966", style={
                    "background": "var(--teal-lt)", "color": "var(--teal)",
                    "borderRadius": "20px", "padding": "3px 12px", "fontSize": "11px", "fontWeight": "700",
                }),
            ]),
            _params_table(df_params, "Random_Forest", {
                "classifier__n_estimators":      "n_estimators",
                #"classifier__max_depth":         "max_depth",
                "classifier__max_features":      "max_features",
                "classifier__min_samples_leaf":  "min_samples_leaf",
                "classifier__min_samples_split": "min_samples_split",
            }),
        ]),

        # Logistic Regression
        html.Div(className="card", style={"borderLeft": "4px solid var(--purple, #8b5cf6)"}, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "14px"}, children=[
                html.Div("Logistic Regression", className="card-title", style={"fontSize": "15px", "margin": "0"}),
                html.Span("PR-AUC 0.679", style={
                    "background": "var(--accent-lt)", "color": "var(--purple, #8b5cf6)",
                    "borderRadius": "20px", "padding": "3px 12px", "fontSize": "11px", "fontWeight": "700",
                }),
            ]),
            _params_table(df_params, "Logistic_Regression", {
                "classifier__max_iter": "max_iter",
                "classifier__C":       "C",
                "classifier__penalty": "penalty",
            }),
        ]),

        # LinearSVC
        html.Div(className="card", style={"borderLeft": "4px solid var(--coral)"}, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "14px"}, children=[
                html.Div("LinearSVC", className="card-title", style={"fontSize": "15px", "margin": "0"}),
                html.Span("PR-AUC 0.684", style={
                    "background": "var(--amber-lt)", "color": "var(--coral)",
                    "borderRadius": "20px", "padding": "3px 12px", "fontSize": "11px", "fontWeight": "700",
                }),
            ]),
            _params_table(df_params, "LinearSVC", {
                
                "classifier__estimator__C":        "C",
                "classifier__estimator__max_iter": "max_iter",
            }),
        ]),

        # Naive Bayes
        html.Div(className="card", style={"borderLeft": "4px solid var(--amber)"}, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "14px"}, children=[
                html.Div("Naive Bayes", className="card-title", style={"fontSize": "15px", "margin": "0"}),
                html.Span("PR-AUC 0.175", style={
                    "background": "var(--amber-lt)", "color": "var(--amber)",
                    "borderRadius": "20px", "padding": "3px 12px", "fontSize": "11px", "fontWeight": "700",
                }),
            ]),
            _params_table(df_params, "Naive_Bayes", {
                'classifier__chunk_size': "chunk_size",
                "classifier__var_smoothing": "var_smoothing",
            }),
        ]),
    ]),

# ══════════════════════════════════════════════════════════════════════
    # 7 · COMPARACIÓN ESTADÍSTICA
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Comparación Estadística de Modelos",
                   "Test Bootstrap PR-AUC — IC 95%"),

    html.Div(style={
        "display": "grid", "gridTemplateColumns": "1fr 1fr",
        "gap": "16px", "marginBottom": "28px",
    }, children=[

        html.Div(className="card", children=[
            html.Div("Test de diferencia de PR-AUC entre pares de modelos", className="card-title"),
            html.Div("H₀: no hay diferencia significativa (α = 0.05)", className="card-sub"),
            html.Div(style={"overflowX": "auto", "marginBottom": "12px"}, children=[
                _simple_table(STAT_ROWS, highlight_col="p-valor", highlight_color="var(--accent)"),
            ]),
            _inline_note([
                html.Strong("Resultado clave: ", style={"color": "var(--accent)"}),
                "Random Forest y XGBoost no difieren significativamente (p = 0.922). "
                "Ambos superan a Naive Bayes, LinearSVC y Logistic Regression con p < 0.001.",
            ]),
        ]),

        html.Div(className="card", children=[
            html.Div("PR-AUC Bootstrap — Intervalos de Confianza 95%", className="card-title"),
            html.Div("Variabilidad del rendimiento estimada por remuestreo", className="card-sub"),
            html.Div(style={"overflowX": "auto", "marginBottom": "14px"}, children=[
                _simple_table(PRAUC_ROWS),
            ]),
            html.Div(style={"display": "flex", "flexDirection": "column", "gap": "8px"}, children=[
                html.Div(style={"display": "flex", "alignItems": "flex-start", "gap": "8px"}, children=[
                    html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%",
                                    "background": "var(--teal)", "flexShrink": "0", "marginTop": "5px"}),
                    html.Span("RF y XGBoost tienen IC que se solapan → rendimiento equivalente estadísticamente.",
                              style={"fontSize": "12px", "color": "var(--txt2)", "lineHeight": "1.5"}),
                ]),
                html.Div(style={"display": "flex", "alignItems": "flex-start", "gap": "8px"}, children=[
                    html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%",
                                    "background": "var(--amber)", "flexShrink": "0", "marginTop": "5px"}),
                    html.Span("Logistic Regression y LinearSVC: PR-AUC 0.679 y 0.684 — rendimiento moderado, "
                              "fronteras de decisión lineales insuficientes para capturar la complejidad del fraude.",
                              style={"fontSize": "12px", "color": "var(--txt2)", "lineHeight": "1.5"}),
                ]),
                html.Div(style={"display": "flex", "alignItems": "flex-start", "gap": "8px"}, children=[
                    html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%",
                                    "background": "var(--red)", "flexShrink": "0", "marginTop": "5px"}),
                    html.Span("Naive Bayes: PR-AUC 0.186 — el supuesto de independencia entre features "
                              "no se cumple en datos de fraude.",
                              style={"fontSize": "12px", "color": "var(--txt2)", "lineHeight": "1.5"}),
                ]),
            ]),
        ]),
    ]),

    # ══════════════════════════════════════════════════════════════════════
    # 8 · LIME
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Interpretabilidad con LIME",
                   "Buscar las variables más influyentes en la predicción"),

    html.Div(className="card", style={"marginBottom": "14px"}, children=[
        html.P(
            "LIME perturba el espacio de características alrededor de una predicción individual "
            "para ajustar un modelo lineal interpretable localmente. Permite identificar qué variables "
            ",y en qué dirección, empujaron al modelo a clasificar una transacción como fraude.",
            style={"fontSize": "13px", "color": "var(--txt)", "lineHeight": "1.8", "margin": "0"},
        ),
    ]),

    html.Div(style={
        "display": "grid", "gridTemplateColumns": " 1fr",
        "gap": "16px", "marginBottom": "28px",
    }, children=[

        html.Div(className="card", children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "4px"}, children=[
                html.Div(" LIME Random Forest", className="card-title"),
                html.Span("PR-AUC 0.966", style={
                    "background": "var(--teal-lt)", "color": "var(--teal)",
                    "borderRadius": "20px", "padding": "2px 10px", "fontSize": "11px", "fontWeight": "700",
                }),
            ]),
            html.Div("Explicación local instancia clasificada como fraude", className="card-sub"),
            html.Img(src="/assets/lime_Random_Forest.png", style={
                "width": "100%", "borderRadius": "var(--r-sm)",
                "border": "1px solid var(--border)", "marginTop": "8px",
            }),
        ]),

        html.Div(className="card", children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "4px"}, children=[
                html.Div(" LIME XGBoost", className="card-title"),
                html.Span("PR-AUC 0.952", style={
                    "background": "var(--accent-lt)", "color": "var(--accent)",
                    "borderRadius": "20px", "padding": "2px 10px", "fontSize": "11px", "fontWeight": "700",
                }),
            ]),
            html.Div("Explicación local instancia clasificada como fraude", className="card-sub"),
            html.Img(src="/assets/lime_XGBoost.png", style={
                "width": "100%", "borderRadius": "var(--r-sm)",
                "border": "1px solid var(--border)", "marginTop": "8px",
            }),
        ]),
    ]),

# ══════════════════════════════════════════════════════════════════════
    # 9 · CONCLUSIÓN Y ELECCIÓN
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Conclusión y Elección del Modelo",
                   "Justificación técnica de la selección final"),

    html.Div(style={"marginBottom": "48px"}, children=[

        # Hero card
        html.Div(style={
            "background": "linear-gradient(135deg, #2563eb 0%, #60a5fa 100%)",
            "borderRadius": "var(--r)", "padding": "28px 32px", "color": "#fff",
            "boxShadow": "0 8px 28px rgba(37,99,235,0.38)",
            "marginBottom": "16px", "position": "relative", "overflow": "hidden",
        }, children=[
            html.Div(style={
                "position": "absolute", "top": "-50px", "right": "-50px",
                "width": "200px", "height": "200px", "borderRadius": "50%",
                "background": "rgba(255,255,255,0.07)",
            }),
            html.Div(style={"position": "relative", "zIndex": "1"}, children=[
                html.Div("⚡ MODELO SELECCIONADO", style={
                    "fontSize": "11px", "fontWeight": "700", "opacity": "0.8",
                    "marginBottom": "6px", "letterSpacing": "1.5px",
                }),
                html.H2("XGBoost", style={
                    "fontFamily": "Sora, sans-serif", "fontSize": "34px",
                    "fontWeight": "800", "margin": "0 0 10px",
                }),
                html.Div(style={"display": "flex", "gap": "10px", "flexWrap": "wrap", "marginBottom": "18px"}, children=[
                    html.Span(t, style={
                        "fontSize": "13px", "fontWeight": "700",
                        "background": "rgba(255,255,255,0.2)",
                        "padding": "4px 14px", "borderRadius": "20px",
                    })
                    for t in ["PR-AUC 0.9522", "IC 95% [0.9357, 0.9656]",
                              "tree_method='hist' + CUDA", "p-valor vs RF = 0.922"]
                ]),
                html.P(
                    "Se evaluaron cinco algoritmos (XGBoost, Random Forest, Logistic Regression, LinearSVC y Naive Bayes) "
                    "bajo cuatro estrategias de balanceo sobre un dataset de 657,943 registros con un desbalanceo extremo "
                    "del 0.3%. La estrategia sin balanceo artificial dominó consistentemente en PR-AUC test en todos los "
                    "modelos: SMOTE, ADASYN y class weights incrementaron el Recall hacia valores cercanos a 1.0, pero a "
                    "costa de una pérdida masiva de precisión que haría inoperativo cualquier sistema de alertas en "
                    "producción. El ROC-AUC de 0.9998 fue validado y es técnicamente legítimo: la diferencia entre CV y "
                    "test es nula, el experimento sin las variables frecuencia y pais_destino lo redujo a 0.95 descartando "
                    "fuga de datos, y se mantiene estable bajo todos los esquemas de balanceo. XGBoost fue seleccionado "
                    "sobre Random Forest (PR-AUC 0.9659) porque la diferencia en ROC-AUC resultó estadísticamente no "
                    "significativa (p=0.922), pero con una eficiencia computacional casi diez veces superior. "
                    "Logistic Regression (0.6792), LinearSVC (0.6844) y Naive Bayes (0.1864) fueron descartados por "
                    "rendimiento significativamente inferior (p=0.000). Se considera este modelo por lo siguiente:",
                    style={"fontSize": "14px", "lineHeight": "1.8", "opacity": "0.93", "margin": "0"},
                ),
            ]),
        ]),

        # 4 razones
        html.Div(style={
            "display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(210px, 1fr))",
            "gap": "12px",
        }, children=[
            html.Div(className="card", style={"borderTop": "3px solid var(--accent)"}, children=[
                html.Div("Eficiencia GPU", className="card-title"),
                html.P("El uso de tree_method='hist' junto con device='cuda' permite aprovechar los núcleos de una "
                       "tarjeta gráfica NVIDIA. Esto reduce el tiempo de ejecución a solo 115.8 segundos, logrando "
                       "una velocidad casi diez veces superior a la de Random Forest (1361.9s) bajo la misma configuración.",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
            html.Div(className="card", style={"borderTop": "3px solid var(--teal)"}, children=[
                html.Div("Regularización nativa", className="card-title"),
                html.P("reg_alpha (L1) y reg_lambda (L2) ya incorporados en el objetivo de optimización, "
                       "sin necesidad de pasos adicionales en el pipeline. Esto reduce el riesgo de sobreajuste "
                       "de forma transparente durante el entrenamiento.",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
            html.Div(className="card", style={"borderTop": "3px solid var(--purple)"}, children=[
                html.Div("Desbalanceo integrado", className="card-title"),
                html.P("Mediante scale_pos_weight, el modelo ajusta internamente el peso de la clase minoritaria "
                       "(0.3% de fraude). A diferencia de SMOTE o ADASYN, que degradaron la precisión hasta valores "
                       "del 2-5%, la configuración sin balanceo con XGBoost mantuvo una precisión de 0.9357 con "
                       "un recall de 0.7923.",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
            html.Div(className="card", style={"borderTop": "3px solid var(--amber)"}, children=[
                html.Div("Interpretabilidad", className="card-title"),
                html.P("El modelo ofrece soporte nativo para SHAP y LIME, permitiendo auditar cada alerta de fraude "
                       "de forma individual. El análisis con LIME confirmó que pais_destino_W0 y tipo_trx son los "
                       "principales predictores, con la frecuencia como señal secundaria y el monto con menor peso "
                       "relativo, otorgando transparencia total al proceso de decisión.",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
        ]),

        html.Div(style={
            "marginTop": "40px",
            "marginBottom": "60px",
            "padding": "20px",
            "borderRadius": "12px",
            "background": "rgba(37,99,235,0.05)",
            "border": "1px dashed #2563eb",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "gap": "10px"
        }, children=[
            html.Span("", style={"fontSize": "18px"}),
            html.P([
                "Documentación técnica completa del modelado disponible en: ",
                html.A(
                    "Jupyter Book — PaymentTransactionsEU",
                    href="https://t1fff.github.io/PaymentTransactionsEUpy/modelo/",
                    target="_blank",
                    style={
                        "color": "var(--accent)",
                        "fontWeight": "800",
                        "textDecoration": "none",
                        "marginLeft": "5px",
                        "transition": "all 0.3s ease",
                    }
                ),
            ], style={
                "fontSize": "14px",
                "color": "var(--txt)",
                "margin": "0",
                "fontWeight": "500"
            }),
        ]),
    ]),
])