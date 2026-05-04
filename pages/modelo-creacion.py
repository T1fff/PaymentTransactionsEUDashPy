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
            " No se encontró comparacion_modelos.csv en /data/ — verifica la ruta.",
            style={"color": "var(--txt2)", "fontSize": "13px"},
        )
    return dash_table.DataTable(
        data=df_models.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df_models.columns],
        style_table={"overflowX": "auto", "borderRadius": "var(--r-sm)", "overflow": "hidden"},
        style_header={
            "backgroundColor": "var(--bg)", "color": "var(--txt2)",
            "fontWeight": "700", "fontSize": "11px", "textTransform": "uppercase",
            "letterSpacing": "0.5px", "border": "none",
            "borderBottom": "2px solid var(--border)", "padding": "10px 14px",
        },
        style_cell={
            "fontFamily": "Plus Jakarta Sans, sans-serif", "fontSize": "13px",
            "color": "var(--txt)", "padding": "9px 14px",
            "border": "none", "borderBottom": "1px solid var(--border2)",
            "backgroundColor": "white",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "var(--surface2)"},
            {"if": {"state": "active"}, "backgroundColor": "var(--accent-lt)", "border": "none"},
        ],
        page_size=15,
        sort_action="native",
        filter_action="native",
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
    # 1 · VARIABLES
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Variables del Modelo", "Features seleccionados y definición del target"),

    html.Div(style={
        "display": "grid", "gridTemplateColumns": "1fr 1fr",
        "gap": "16px", "marginBottom": "28px",
    }, children=[

        # Features
        html.Div(className="card", children=[
            html.Div("Features (X)", className="card-title"),
            html.Div("8 variables: 7 categóricas + 1 numérica continua", className="card-sub"),

            html.Div(style={"marginBottom": "16px"}, children=[
                html.Div("Categóricas — FEATURES_CAT", style={
                    "fontSize": "11px", "fontWeight": "700", "color": "var(--txt2)",
                    "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "8px",
                }),
                html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "6px"}, children=[
                    _chip(f, "--purple", "--purple-lt")
                    for f in ["frecuencia", "pais_origen", "pais_destino",
                              "tipo_trx", "tipo_psp", "unidad", "tipo_monto"]
                ]),
            ]),

            html.Div(children=[
                html.Div("Numérica", style={
                    "fontSize": "11px", "fontWeight": "700", "color": "var(--txt2)",
                    "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "8px",
                }),
                _chip("monto_final", "--teal", "--teal-lt"),
            ]),
        ]),

        # Target
        html.Div(className="card", children=[
            html.Div("Target (y) es tipo_fraude", className="card-title"),
            html.Div("Esta variable se convirtió a binaria (tipo_fraude_bin)", className="card-sub"),

            html.Div(style={
                "background": "var(--surface2)", "borderRadius": "var(--r-xs)",
                "padding": "12px 14px", "marginBottom": "14px",
                "fontFamily": "monospace", "fontSize": "12px",
                "color": "var(--txt)", "lineHeight": "2",
                "border": "1px solid var(--border)",
            }, children=[
                html.Span('df["tipo_fraude_bin"] =', style={"color": "var(--txt2)"}),
                html.Br(),
                html.Span('  (df["tipo_fraude"].str.lower()', style={"color": "var(--txt2)"}),
                html.Br(),
                html.Span('    == ', style={"color": "var(--txt2)"}),
                html.Span('"con fraude")', style={"color": "var(--teal)", "fontWeight": "700"}),
                html.Br(),
                html.Span("  .astype(int)", style={"color": "var(--accent)", "fontWeight": "700"}),
            ]),

            html.Div(style={"display": "flex", "gap": "10px"}, children=[
                html.Div(style={
                    "flex": "1", "background": "var(--teal-lt)", "borderRadius": "var(--r-xs)",
                    "padding": "12px", "textAlign": "center",
                }, children=[
                    html.Div("0", style={"fontSize": "24px", "fontWeight": "800", "color": "var(--teal)", "fontFamily": "Sora, sans-serif"}),
                    html.Div("Sin fraude", style={"fontSize": "11px", "color": "var(--txt2)", "fontWeight": "600"}),
                ]),
                html.Div(style={
                    "flex": "1", "background": "var(--accent-lt)", "borderRadius": "var(--r-xs)",
                    "padding": "12px", "textAlign": "center",
                }, children=[
                    html.Div("1", style={"fontSize": "24px", "fontWeight": "800", "color": "var(--accent)", "fontFamily": "Sora, sans-serif"}),
                    html.Div("Con fraude", style={"fontSize": "11px", "color": "var(--txt2)", "fontWeight": "600"}),
                ]),
            ]),
        ]),
    ]),

    # ══════════════════════════════════════════════════════════════════════
    # 2 · PREPROCESAMIENTO
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Preprocesamiento",
                   "ColumnTransformer con pipelines independientes por tipo de variable"),

    html.Div(className="card", style={"marginBottom": "28px"}, children=[

        # Pills resumen
        html.Div(style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
            "gap": "10px", "marginBottom": "22px",
        }, children=[
            _pill("Split",            "80% train / 20% test",    "var(--purple)"),
            _pill("Estratificación",  "Sí, sobre y",            "var(--teal)"),
            _pill("Imputación num.",  "SimpleImputer (mediana)",  "var(--accent)"),
            _pill("Imputación cat.",  "SimpleImputer (moda)",     "var(--amber)"),
            _pill("Escalado",         "StandardScaler",           "var(--teal)"),
            _pill("Encoding",         "OneHotEncoder (drop=first)","var(--purple)"),
        ]),

        # Dos pipelines lado a lado
        html.Div(style={
            "display": "grid", "gridTemplateColumns": "1fr 1fr",
            "gap": "14px", "marginBottom": "16px",
        }, children=[

            html.Div(style={
                "background": "var(--teal-lt)", "borderRadius": "var(--r-sm)",
                "padding": "16px", "border": "1px solid rgba(0,201,167,0.2)",
            }, children=[
                html.Div("Pipeline Numérico", style={
                    "fontFamily": "Sora, sans-serif", "fontWeight": "700",
                    "fontSize": "13px", "color": "var(--teal)", "marginBottom": "10px",
                }),
                html.Div("Variable:", style={"fontSize": "11px", "color": "var(--txt2)", "marginBottom": "6px"}),
                _chip("monto_final", "--teal", "--teal-lt"),
                html.Div(style={"marginTop": "14px", "display": "flex", "flexDirection": "column", "gap": "8px"}, children=[
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                        html.Div("", style={"fontWeight": "800", "color": "var(--teal)", "fontSize": "15px", "width": "20px"}),
                        html.Code("SimpleImputer(strategy='median')",
                                  style={"fontSize": "12px", "fontFamily": "monospace", "color": "var(--txt)"}),
                    ]),
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                        html.Div("", style={"fontWeight": "800", "color": "var(--teal)", "fontSize": "15px", "width": "20px"}),
                        html.Code("StandardScaler()",
                                  style={"fontSize": "12px", "fontFamily": "monospace", "color": "var(--txt)"}),
                    ]),
                ]),
            ]),

            html.Div(style={
                "background": "var(--purple-lt)", "borderRadius": "var(--r-sm)",
                "padding": "16px", "border": "1px solid rgba(108,92,231,0.2)",
            }, children=[
                html.Div("Pipeline Categórico", style={
                    "fontFamily": "Sora, sans-serif", "fontWeight": "700",
                    "fontSize": "13px", "color": "var(--purple)", "marginBottom": "10px",
                }),
                html.Div("Variables (7):", style={"fontSize": "11px", "color": "var(--txt2)", "marginBottom": "6px"}),
                html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "4px", "marginBottom": "14px"}, children=[
                    _chip(f, "--purple", "--purple-lt")
                    for f in ["frecuencia", "pais_origen", "pais_destino",
                              "tipo_trx", "tipo_psp", "unidad", "tipo_monto"]
                ]),
                html.Div(style={"display": "flex", "flexDirection": "column", "gap": "8px"}, children=[
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                        html.Div("", style={"fontWeight": "800", "color": "var(--purple)", "fontSize": "15px", "width": "20px"}),
                        html.Code("SimpleImputer(strategy='most_frequent')",
                                  style={"fontSize": "12px", "fontFamily": "monospace", "color": "var(--txt)"}),
                    ]),
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                        html.Div("", style={"fontWeight": "800", "color": "var(--purple)", "fontSize": "15px", "width": "20px"}),
                        html.Code("OneHotEncoder(drop='first', handle_unknown='ignore')",
                                  style={"fontSize": "11px", "fontFamily": "monospace", "color": "var(--txt)"}),
                    ]),
                ]),
            ]),
        ]),

        _inline_note([
            html.Strong("drop='first': ", style={"color": "var(--accent)"}),
            "elimina una categoría por variable para evitar multicolinealidad perfecta. ",
            html.Strong("handle_unknown='ignore': ", style={"color": "var(--accent)"}),
            "garantiza que categorías no vistas en entrenamiento no rompan la inferencia en producción. ",
            "El ColumnTransformer usa remainder='drop', descartando cualquier columna no especificada.",
        ]),
    ]),

    # ══════════════════════════════════════════════════════════════════════
    # 3 · VALIDACIÓN Y BÚSQUEDA
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Validación y Búsqueda de Hiperparámetros",
                   "StratifiedKFold (k=5) · RandomizedSearchCV (n_iter=20) · balanced_accuracy"),

    html.Div(style={
        "display": "grid", "gridTemplateColumns": "1fr 1fr",
        "gap": "16px", "marginBottom": "28px",
    }, children=[

        html.Div(className="card", children=[
            html.Div("Configuración de RandomizedSearchCV", className="card-title"),
            html.Div("Aplicado a cada modelo y cada técnica de balanceo", className="card-sub"),
            html.Div(style={"display": "flex", "flexDirection": "column", "gap": "8px"}, children=[
                (lambda lbl, val, c: html.Div(style={
                    "display": "flex", "justifyContent": "space-between", "alignItems": "center",
                    "padding": "9px 14px", "background": "var(--surface2)",
                    "borderRadius": "var(--r-xs)", "border": "1px solid var(--border)",
                }, children=[
                    html.Span(lbl, style={"fontSize": "13px", "color": "var(--txt2)"}),
                    html.Span(val, style={"fontWeight": "800", "color": c,
                                          "fontFamily": "Sora, sans-serif", "fontSize": "13px"}),
                ]))(*row)
                for row in [
                    ("Iteraciones",              "n_iter = 20",          "var(--purple)"),
                    ("Folds CV",                 "k = 5",                "var(--purple)"),
                    ("Shuffle",                  "True",                 "var(--teal)"),
                    ("Métrica refit",            "balanced_accuracy",    "var(--accent)"),
                    ("n_jobs",                   "-1 (todos los cores)", "var(--txt)"),
                    ("Estratificación en folds", "StratifiedKFold",      "var(--teal)"),
                ]
            ]),
        ]),

        html.Div(className="card", children=[
            html.Div("Métricas registradas por fold (SCORING_MULTIPLE)", className="card-title"),
            html.Div("Todas almacenadas en cv_results_ para análisis posterior", className="card-sub"),
            html.Div(style={"display": "flex", "flexDirection": "column", "gap": "6px"}, children=[
                html.Div(style={
                    "display": "flex", "alignItems": "center", "gap": "10px",
                    "padding": "8px 12px", "background": f"var({bg})", "borderRadius": "var(--r-xs)",
                }, children=[
                    _chip(m, c, bg),
                    html.Span(desc, style={"fontSize": "12px", "color": "var(--txt2)"}),
                ])
                for m, c, bg, desc in [
                    ("pr_auc",            "--accent",  "--accent-lt",  "Área PR ← métrica principal de fraude"),
                    ("roc_auc",           "--teal",    "--teal-lt",    "Área ROC"),
                    ("f1",                "--purple",  "--purple-lt",  "F1-score"),
                    ("recall",            "--amber",   "--amber-lt",   "Sensibilidad (fraudes capturados)"),
                    ("precision",         "--coral",   "--amber-lt",   "Precisión positiva"),
                    ("balanced_accuracy", "--txt",     "--surface2",   "← refit (optimización)"),
                ]
            ]),
        ]),
    ]),

    # ══════════════════════════════════════════════════════════════════════
    # 4 · TÉCNICAS DE BALANCEO
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Técnicas de Balanceo",
                   "4 variantes evaluadas por modelo"),

    html.Div(style={
        "display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
        "gap": "14px", "marginBottom": "28px",
    }, children=[

        html.Div(className="card", style={"borderTop": "3px solid var(--txt3)"}, children=[
            html.Div(" sin_balanceo", className="card-title"),
            html.Div("Línea base sin corrección", className="card-sub"),
            html.Div("balancer = None", style={"fontFamily": "monospace", "fontSize": "12px", "color": "var(--txt2)", "marginBottom": "8px"}),
            _inline_note(
                "Referencia para medir el impacto real de cada técnica.",
                "--txt3", "--surface2"
            ),
        ]),

        html.Div(className="card", style={"borderTop": "3px solid var(--teal)"}, children=[
            html.Div(" smote", className="card-title"),
            html.Div("Synthetic Minority Over-sampling", className="card-sub"),
            html.Div("SMOTE(random_state=SEED)", style={"fontFamily": "monospace", "fontSize": "12px", "color": "var(--txt2)", "marginBottom": "8px"}),
            _inline_note(
                "Genera instancias sintéticas de fraude interpolando entre k vecinos más cercanos.",
                "--teal", "--teal-lt"
            ),
        ]),

        html.Div(className="card", style={"borderTop": "3px solid var(--purple)"}, children=[
            html.Div(" adasyn", className="card-title"),
            html.Div("Adaptive Synthetic Sampling", className="card-sub"),
            html.Div("ADASYN(random_state=SEED)", style={"fontFamily": "monospace", "fontSize": "12px", "color": "var(--txt2)", "marginBottom": "8px"}),
            _inline_note(
                "Como SMOTE pero focaliza la generación en zonas de mayor dificultad de clasificación.",
                "--purple", "--purple-lt"
            ),
        ]),

        html.Div(className="card", style={"borderTop": "3px solid var(--amber)"}, children=[
            html.Div(" weights", className="card-title"),
            html.Div("Penalización por peso en el clasificador", className="card-sub"),
            html.Div("balancer = 'weights'", style={"fontFamily": "monospace", "fontSize": "12px", "color": "var(--txt2)", "marginBottom": "8px"}),
            _inline_note([
                html.Strong("XGBoost: ", style={"color": "var(--amber)"}),
                html.Code("scale_pos_weight = n_sin_fraude / n_con_fraude", style={"fontSize": "11px", "fontFamily": "monospace"}),
                html.Br(),
                html.Strong("RF / LR / SVC: ", style={"color": "var(--amber)"}),
                html.Code("class_weight='balanced'", style={"fontSize": "11px", "fontFamily": "monospace"}),
            ], "--amber", "--amber-lt"),
        ]),
    ]),

    # ══════════════════════════════════════════════════════════════════════
    # 5 · MODELOS E HIPERPARÁMETROS
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Modelos e Hiperparámetros Optimizados",
                   "Pipeline: preprocessor → [balancer] → classifier"),

    html.Div(style={"display": "flex", "flexDirection": "column", "gap": "14px", "marginBottom": "28px"}, children=[

        # XGBoost
        html.Div(className="card", style={"borderLeft": "4px solid var(--accent)"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between",
                            "alignItems": "flex-start", "marginBottom": "14px"}, children=[
                html.Div(children=[
                    html.Div(" XGBoost — XGBClassifier", className="card-title", style={"fontSize": "15px"}),
                    html.Div("tree_method='hist', device='cuda', eval_metric='logloss'", className="card-sub"),
                ]),
                html.Span("PR-AUC 0.952", style={
                    "background": "var(--accent-lt)", "color": "var(--accent)",
                    "borderRadius": "20px", "padding": "4px 12px", "fontSize": "12px", "fontWeight": "700",
                }),
            ]),
            html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"}, children=[
                html.Div(children=[
                    html.Div("Rango de búsqueda (base):", style={"fontSize": "11px", "color": "var(--txt2)", "fontWeight": "700", "textTransform": "uppercase", "letterSpacing": "0.4px", "marginBottom": "7px"}),
                    html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "5px"}, children=[
                        _chip(p, "--accent", "--accent-lt")
                        for p in ["n_estimators ∈ [50,200]", "max_depth ∈ [3,6]",
                                  "learning_rate ∈ [0.05,0.15]", "subsample ∈ [0.7,0.9]"]
                    ]),
                ]),
                html.Div(children=[
                    html.Div("Extra en variante weights:", style={"fontSize": "11px", "color": "var(--txt2)", "fontWeight": "700", "textTransform": "uppercase", "letterSpacing": "0.4px", "marginBottom": "7px"}),
                    _chip("scale_pos_weight ∈ [4, n_neg/n_pos × 1.5]", "--amber", "--amber-lt"),
                    html.Div("Fijos: reg_alpha=0.1, reg_lambda=1.0, colsample_bytree=0.8",
                             style={"fontSize": "12px", "color": "var(--txt2)", "marginTop": "10px", "fontFamily": "monospace"}),
                ]),
            ]),
        ]),

        # Random Forest
        html.Div(className="card", style={"borderLeft": "4px solid var(--teal)"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between",
                            "alignItems": "flex-start", "marginBottom": "12px"}, children=[
                html.Div(children=[
                    html.Div(" Random Forest — RandomForestClassifier", className="card-title", style={"fontSize": "15px"}),
                    html.Div("class_weight='balanced' en variante weights", className="card-sub"),
                ]),
                html.Span("PR-AUC 0.966", style={
                    "background": "var(--teal-lt)", "color": "var(--teal)",
                    "borderRadius": "20px", "padding": "4px 12px", "fontSize": "12px", "fontWeight": "700",
                }),
            ]),
            html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "5px"}, children=[
                _chip(p, "--teal", "--teal-lt")
                for p in ["n_estimators ∈ [50,300]", "max_depth ∈ {None,5,10,20}",
                          "min_samples_split ∈ [2,20]", "min_samples_leaf ∈ [1,10]",
                          "max_features ∈ {sqrt, log2}"]
            ]),
        ]),

        # Regresión Logística
        html.Div(className="card", style={"borderLeft": "4px solid var(--purple)"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between",
                            "alignItems": "flex-start", "marginBottom": "12px"}, children=[
                html.Div(children=[
                    html.Div(" Regresión Logística — solver='saga'", className="card-title", style={"fontSize": "15px"}),
                    html.Div("Soporta L1 y L2 — class_weight='balanced' en variante weights", className="card-sub"),
                ]),
            ]),
            html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "5px"}, children=[
                _chip(p, "--purple", "--purple-lt")
                for p in ["C ∈ [0.001,10] (log-uniforme)", "penalty ∈ {l1, l2}", "max_iter ∈ [500,2000]"]
            ]),
        ]),

        # Naive Bayes
        html.Div(className="card", style={"borderLeft": "4px solid var(--amber)"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between",
                            "alignItems": "flex-start", "marginBottom": "12px"}, children=[
                html.Div(children=[
                    html.Div(" Naive Bayes — GaussianNB (NaiveBayesChunked)", className="card-title", style={"fontSize": "15px"}),
                    html.Div("Wrapper propio con partial_fit por bloques para eficiencia en memoria — no soporta class_weight", className="card-sub"),
                ]),
                html.Span("PR-AUC 0.175", style={
                    "background": "var(--amber-lt)", "color": "var(--amber)",
                    "borderRadius": "20px", "padding": "4px 12px", "fontSize": "12px", "fontWeight": "700",
                }),
            ]),
            html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "5px"}, children=[
                _chip(p, "--amber", "--amber-lt")
                for p in ["var_smoothing ∈ [1e-12, 1e-6] (log-uniforme)", "chunk_size ∈ {5000, 10000, 20000}"]
            ]),
        ]),

        # LinearSVC
        html.Div(className="card", style={"borderLeft": "4px solid var(--coral)"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between",
                            "alignItems": "flex-start", "marginBottom": "12px"}, children=[
                html.Div(children=[
                    html.Div(" LinearSVC + CalibratedClassifierCV (cv=3)", className="card-title", style={"fontSize": "15px"}),
                    html.Div("Calibrado para obtener predict_proba — class_weight='balanced' en variante weights", className="card-sub"),
                ]),
                html.Span("PR-AUC 0.684", style={
                    "background": "var(--amber-lt)", "color": "var(--coral)",
                    "borderRadius": "20px", "padding": "4px 12px", "fontSize": "12px", "fontWeight": "700",
                }),
            ]),
            html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "5px"}, children=[
                _chip(p, "--coral", "--amber-lt")
                for p in ["estimator__C ∈ [0.001,10] (log-uniforme)", "estimator__max_iter ∈ [1000,5000]"]
            ]),
        ]),
    ]),

    # ══════════════════════════════════════════════════════════════════════
    # 6 · TABLA RESULTADOS CSV
    # ══════════════════════════════════════════════════════════════════════
    _section_title("", "Tabla de Resultados", "Métricas y tiempo de cada modelo"),

    html.Div(className="card", style={"marginBottom": "28px"}, children=[
        html.Div("Métricas en test set por modelo y técnica de balanceo", className="card-title"),
        html.Div("Haz clic en los encabezados para ordenar · Escribe en los campos para filtrar", className="card-sub"),
        html.Div(style={"marginTop": "12px"}, children=[_build_csv_table()]),
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
                "Ambos superan a Naive Bayes y LinearSVC con p < 0.001.",
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
                                    "background": "var(--red)", "flexShrink": "0", "marginTop": "5px"}),
                    html.Span("Naive Bayes: PR-AUC 0.175 — el supuesto de independencia entre features no se cumple en datos de fraude.",
                              style={"fontSize": "12px", "color": "var(--txt2)", "lineHeight": "1.5"}),
                ]),
                html.Div(style={"display": "flex", "alignItems": "flex-start", "gap": "8px"}, children=[
                    html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%",
                                    "background": "var(--amber)", "flexShrink": "0", "marginTop": "5px"}),
                    html.Span("LinearSVC: PR-AUC 0.684 — rendimiento moderado, descartado frente a los ensambles.",
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
            "background": "linear-gradient(135deg, #ff6584 0%, #ff9aab 100%)",
            "borderRadius": "var(--r)", "padding": "28px 32px", "color": "#fff",
            "boxShadow": "0 8px 28px rgba(255,101,132,0.38)",
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
                    "Tras evaluar cinco algoritmos bajo diversas estrategias de balanceo sobre un dataset de 657,943 registros "
                    "con un desbalanceo extremo del 0.3%, se determinó que la estrategia sin balanceo artificial ofrece el mejor "
                    "rendimiento real. Aunque técnicas como SMOTE o pesos por clase incrementan el Recall, lo hacen a costa de "
                    "una pérdida masiva de precisión que invalidaría el sistema en un entorno de producción. El modelo XGBoost "
                    "fue seleccionado como la solución óptima para el despliegue debido a que la diferencia en el ROC-AUC frente "
                    "a Random Forest resultó estadísticamente no significativa (p=0.922), pero con una eficiencia computacional "
                    "diez veces superior. Además, se consideró este modelo por lo siguiente:",
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
                html.P("El uso de tree_method='hist' junto con device='cuda' permite aprovechar los nucleos de una tarjeta gráfica NVIDIA. Esto reduce el tiempo de ejecución a solo 55.8 segundos, logrando una velocidad casi diez veces superior a la de Random Forest (535.3s).",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
            html.Div(className="card", style={"borderTop": "3px solid var(--teal)"}, children=[
                html.Div("Regularización nativa", className="card-title"),
                html.P("reg_alpha (L1) y reg_lambda (L2) ya incorporados en el objetivo, sin necesidad de pasos adicionales en el pipeline.",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
            html.Div(className="card", style={"borderTop": "3px solid var(--purple)"}, children=[
                html.Div("Desbalanceo integrado", className="card-title"),
                html.P("Mediante el parámetro scale_pos_weight, el modelo ajusta internamente el peso de la clase minoritaria (0.3% de fraude). Esto penaliza con mayor rigor los errores en los casos positivos, optimizando el rendimiento sin sufrir la degradación de precisión observada con SMOTE o ADASYN.",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
            html.Div(className="card", style={"borderTop": "3px solid var(--amber)"}, children=[
                html.Div("Interpretabilidad", className="card-title"),
                html.P("El modelo ofrece soporte nativo para SHAP y LIME, permitiendo auditar cada alerta de fraude de forma individual. El análisis confirmó que el país de destino y el tipo de transacción son los principales predictores, otorgando transparencia total al proceso de decisión.",
                       style={"fontSize": "13px", "color": "var(--txt2)", "lineHeight": "1.6"}),
            ]),
        ]),
        
        html.Div(style={
            "marginTop": "40px",
            "marginBottom": "60px",
            "padding": "20px",
            "borderRadius": "12px",
            "background": "rgba(var(--accent-rgb), 0.05)",  # Fondo muy suave del color de acento
            "border": "1px dashed var(--accent)",           # Borde discontinuo para un toque técnico
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