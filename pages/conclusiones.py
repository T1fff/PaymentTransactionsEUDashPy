import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from utils.svg_icons import ico_search, ico_bars_white, ico_dollar

dash.register_page(__name__, path="/conclusiones", name="Conclusiones", order=5)

# Iconos blancos — van sobre fondo morado del conc-card

layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Conclusión", className="page-title"),
            html.P("Hallazgos del análisis exploratorio y referencias bibliográficas", className="page-sub"),
        ], className="section-header"),

        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Hallazgos Principales", className="card-title"),
                html.Hr(style={"borderColor":"#E8E5DE","margin":"8px 0 16px"}),
                html.Div([
                    html.P("El anterior análisis permitió conocer a profundidad características generales del dataset escogido tales como número de observaciones y variables estudiadas. De la misma manera, permitió estudiar el posible impacto en este proyecto de cada una de las columnas listadas, pues, fuera por falta de documentación en la fuente original o duplicación de información, no todas eran aptas de ser incluidas.",
                           style={"fontSize":"14px","color":"#3D3D50","lineHeight":"1.75","marginBottom":"14px"}),
                    html.P("En un reconocimiento inicial se vio que la variable objetivo tipo_fraude, se encuentra desbalanceada a favor de observaciones que no presentaron fraude, de la misma forma, se pudo conocer a grandes rasgos, la distribución particular de las variables presentes en los datos como los países origen, destino, año de origen, monto o conteo, tipo de unidad, tipo de multiplicador, tipo de psp, descripción, por mencionar algunas.",
                           style={"fontSize":"14px","color":"#3D3D50","lineHeight":"1.75","marginBottom":"14px"}),
                    html.P("Al comparar los tipos de fraude con las diferentes variables se encontró que existe dependencia en la mayoría de casos. Aún así, es importante resaltar que los fraudes se concentran en categorías muy particulares, por ejemplo, en solo una de las categorías de la variable frecuencia se encontraron casos de fraude. Por otro lado, en la variable monto se encontró diferencias significativas entre el grupo en el que se identifica fraude y el grupo en el que no. Los montos suelen ser menores en las transacciones fraudulentas que en las que no lo son.",
                           style={"fontSize":"14px","color":"#3D3D50","lineHeight":"1.75"}),
                ]),
            ], className="card mb-3"), md=12),
        ]),

        dbc.Row([
            dbc.Col(html.Div([
                ico_search(),
                html.Div("Desbalance de clases", className="conc-card-title"),
                html.Div("El 99.7% de las transacciones son legítimas vs. 0.3% fraudulentas. Esto requiere técnicas de balanceo especiales como SMOTE o ajuste de pesos en el clasificador para construir un modelo robusto.", className="conc-card-text"),
            ], className="conc-card"), md=4),
            dbc.Col(html.Div([
                ico_bars_white(),
                html.Div("Dependencia estadística", className="conc-card-title"),
                html.Div("Existe dependencia entre tipo_fraude y la mayoría de variables categóricas analizadas. Los fraudes se concentran en categorías muy particulares, especialmente en transacciones anuales (frecuencia A).", className="conc-card-text"),
            ], className="conc-card"), md=4),
            dbc.Col(html.Div([
                ico_dollar(),
                html.Div("Monto como variable clave", className="conc-card-title"),
                html.Div("Se encontraron diferencias significativas en la variable monto entre transacciones fraudulentas y no fraudulentas. Los montos son menores en transacciones fraudulentas, lo cual es un patrón relevante para el modelo ML.", className="conc-card-text"),
            ], className="conc-card"), md=4),
        ], className="g-3 mb-4"),

        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Referencias", className="card-title"),
                html.Hr(style={"borderColor":"#E8E5DE","margin":"8px 0 16px"}),
                html.Div("[1] Banco Central Europeo. (2025). What is T2? https://www.ecb.europa.eu/ecb-and-you/explainers/tell-me/html/what-is-t2.en.html", className="ref-item"),
                html.Div("[2] European Banking Authority & European Central Bank. (2025). 2025 Report on Payment Fraud. https://www.ecb.europa.eu/press/pr/date/2025/html/ecb.pr251215~e133d9d683.en.html", className="ref-item"),
                html.Div("[3] Banco de España. (2023). TARGET. Sistema de liquidación bruta en tiempo real. https://www.bde.es/wbe/en/entidades-profesionales/operativa-gestiones/sistemas-pago-infraestructuras/target-banco-espana/", className="ref-item"),
                html.Div("[4] Sánchez-Aguayo, M., Urda, D., & Jerez, J. M. (2024). Financial fraud detection through the application of machine learning techniques: a literature review. Humanities and Social Sciences Communications, 11, 1130. https://doi.org/10.1057/s41599-024-03606-0", className="ref-item"),
                html.Div("[5] Albert, J. F., et al. (2025). Comparative analysis of machine learning models for the detection of fraudulent banking transactions. Cogent Business & Management, 12(1). https://doi.org/10.1080/23311975.2025.2474209", className="ref-item"),
                html.Div("[6] Chen, Y., et al. (2025). Deep learning in financial fraud detection: Innovations, challenges, and applications. Computers & Security. https://www.sciencedirect.com/science/article/pii/S2666764925000372", className="ref-item"),
            ], className="card"), md=12),
        ]),
    ], className="page-content"),
])
