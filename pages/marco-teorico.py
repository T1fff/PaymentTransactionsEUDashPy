import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/marco-teorico", name="Marco Teórico", order=3)

# ── Paleta del proyecto ────────────────────────────────────────────────────
A = "#FF6584"; P = "#6C5CE7"; T = "#00C9A7"; AM = "#FDB94B"


def ref(n: int) -> html.Sup:
    """Superíndice de referencia numérica."""
    return html.Sup(
        html.A(f"[{n}]", href="#",
               style={"color": P, "textDecoration": "none", "fontWeight": "700",
                      "fontSize": "10px", "marginLeft": "1px"}),
    )


def card_seccion(titulo: str, contenido: list) -> html.Div:
    return html.Div(
        className="card",
        style={"borderLeft": f"4px solid {P}", "marginBottom": "0"},
        children=[
            html.Div(titulo, className="card-title",
                     style={"fontSize": "15px", "marginBottom": "12px"}),
            html.Hr(style={"borderColor": "#F0EDE8", "margin": "0 0 14px"}),
            *contenido,
        ],
    )


def parrafo(*children) -> html.P:
    return html.P(list(children), className="intro-text",
                  style={"marginBottom": "12px", "lineHeight": "1.85",
                         "fontSize": "14px", "color": "#1E1E2E"})


def formula(texto: str) -> html.Div:
    """Bloque para fórmulas matemáticas."""
    return html.Div(
        texto,
        style={
            "background": "#F7F5FF",
            "border": f"1px solid {P}30",
            "borderRadius": "6px",
            "padding": "10px 18px",
            "fontFamily": "monospace",
            "fontSize": "13px",
            "color": P,
            "margin": "8px 0 14px",
            "textAlign": "center",
            "letterSpacing": "0.3px",
        }
    )


# ── Layout ─────────────────────────────────────────────────────────────────

def layout():
    return html.Div([
        html.Div([

            # ── Encabezado ────────────────────────────────────────────────
            html.Div([
                html.H1("Marco Teórico", className="page-title"),
                html.P(
                    "Contexto financiero, regulatorio e institucional del fraude "
                    "en pagos dentro del Espacio Económico Europeo.",
                    className="page-sub",
                ),
            ], className="section-header"),

            # ── Sección 1 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "1. El sistema de pagos en el Espacio Económico Europeo",
                    [
                        parrafo(
                            "El Espacio Económico Europeo (EEE) alberga uno de los sistemas de pagos "
                            "más integrados del mundo. Compuesto por los 27 estados miembros de la "
                            "Unión Europea más Islandia, Liechtenstein y Noruega, el EEE procesa "
                            "cientos de miles de millones de transacciones al año a través de "
                            "instrumentos como transferencias de crédito, débitos directos, pagos "
                            "con tarjeta y transacciones de dinero electrónico. Esta infraestructura "
                            "fue posible gracias al proyecto SEPA (Single Euro Payments Area), una "
                            "iniciativa de armonización impulsada por el sector bancario europeo que "
                            "unificó los estándares técnicos y jurídicos de los pagos en euros.", ref(7),
                        ),
                        parrafo(
                            "La digitalización acelerada de los pagos minoristas ha incrementado "
                            "exponencialmente el volumen de transacciones electrónicas, lo que a su "
                            "vez ha ampliado la superficie de exposición al fraude. Cada nuevo canal "
                            "de pago digital representa una oportunidad tanto para los consumidores "
                            "como para los actores fraudulentos, quienes adaptan continuamente sus "
                            "métodos de ataque a los mecanismos de seguridad vigentes.", ref(2),
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

            # ── Sección 2 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "2. El BCE y la EBA como autoridades supervisoras del fraude",
                    [
                        parrafo(
                            "El Banco Central Europeo (BCE) es la institución encargada de la "
                            "política monetaria de la zona euro y cumple además un rol fundamental "
                            "en la supervisión estadística del sistema de pagos. A través del "
                            "Reglamento (UE) N.º 1409/2013 sobre estadísticas de pagos "
                            "(ECB/2013/43), el BCE obliga a los proveedores de servicios de pago "
                            "(PSP) radicados en la zona euro a reportar semestralmente información "
                            "detallada sobre transacciones fraudulentas a sus bancos centrales "
                            "nacionales, quienes a su vez consolidan y transmiten los datos al BCE.", ref(10),
                        ),
                        parrafo(
                            "La Autoridad Bancaria Europea (EBA, por sus siglas en inglés) es un "
                            "organismo independiente de la UE cuya función principal es garantizar "
                            "la integridad y solidez del sistema bancario europeo. En materia de "
                            "fraude, la EBA emitió en 2018 las Directrices sobre reporte de fraude "
                            "bajo PSD2 (EBA/GL/2018/05), vigentes desde enero de 2019, que "
                            "especifican el contenido, formato y periodicidad de los reportes que "
                            "los PSP deben presentar. Desde 2024, el BCE y la EBA publican "
                            "conjuntamente un informe anual sobre fraude en pagos que consolida "
                            "los datos de todo el EEE.", ref(11), ref(2),
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

            # ── Sección 3 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "3. La Directiva PSD2 y su impacto en la seguridad de los pagos",
                    [
                        parrafo(
                            "La Directiva (UE) 2015/2366, conocida como PSD2, constituye el "
                            "principal instrumento regulatorio del mercado de pagos en la UE. "
                            "Aprobada el 25 de noviembre de 2015 y en vigor desde enero de 2018, "
                            "PSD2 introdujo requisitos de Autenticación Reforzada del Cliente "
                            "(SCA, por sus siglas en inglés) para las transacciones electrónicas, "
                            "obligando a los PSP a aplicar al menos dos factores de verificación "
                            "independientes en la mayoría de pagos en línea. El cumplimiento pleno "
                            "de la SCA entró en vigor el 31 de diciembre de 2020.", ref(8),
                        ),
                        parrafo(
                            "Los datos del informe conjunto EBA–BCE de 2025 confirman que la SCA "
                            "ha tenido un efecto positivo en la reducción de las tasas de fraude, "
                            "especialmente en pagos con tarjeta dentro del EEE. Las transacciones "
                            "autenticadas con SCA registraron tasas de fraude significativamente "
                            "menores que aquellas sin autenticación reforzada. No obstante, el "
                            "mismo informe advierte que han emergido nuevas tipologías de fraude "
                            "que explotan las exenciones de SCA o manipulan a los propios usuarios "
                            "para que autoricen transacciones fraudulentas, lo que demanda nuevos "
                            "enfoques de mitigación.", ref(2),
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

            # ── Sección 4 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "4. Magnitud y tendencia reciente del fraude en el EEE",
                    [
                        parrafo(
                            "Según el informe conjunto EBA–BCE de 2025, el valor total del fraude "
                            "en pagos dentro del EEE ascendió a €4.2 mil millones en 2024, lo que "
                            "representa un incremento del 17% frente a los €3.5 mil millones "
                            "registrados en 2023. Pese a este aumento en términos absolutos, la "
                            "tasa de fraude se mantuvo estable en aproximadamente el 0.002% del "
                            "valor total de las transacciones procesadas durante el año.", ref(2),
                        ),
                        parrafo(
                            "Desglosado por instrumento, las transferencias de crédito "
                            "concentraron €2.2 mil millones en pérdidas, con un incremento anual "
                            "del 16%, mientras que los pagos con tarjeta emitida en el EEE "
                            "acumularon €1.3 mil millones, un aumento del 29% respecto a 2023. "
                            "Un aspecto especialmente relevante es la distribución de las pérdidas "
                            "entre las partes involucradas: en las transferencias fraudulentas, "
                            "los propios usuarios soportaron aproximadamente el 85% del costo "
                            "total, principalmente como consecuencia de engaños que los llevaron "
                            "a iniciar las transacciones de forma voluntaria.", ref(2),
                        ),
                        parrafo(
                            "El fraude transfronterizo también representa un riesgo diferenciado. "
                            "Cuando la contraparte de la transacción se encuentra fuera del EEE, "
                            "donde la SCA no es legalmente obligatoria, las tasas de fraude son "
                            "sustancialmente más elevadas que en las operaciones domésticas o "
                            "intra-EEE. Esto evidencia cómo el marco regulatorio regional actúa "
                            "como un factor de contención efectivo del fraude.", ref(2),
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

            # ── Sección 5 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "5. El dataset oficial del BCE como fuente de este análisis",
                    [
                        parrafo(
                            "Los datos utilizados en este proyecto provienen del Portal de Datos "
                            "del BCE, específicamente del conjunto de datos PAY (Payment "
                            "Transactions – Key Indicators), que contiene estadísticas de "
                            "transacciones de pago totales y fraudulentas reportadas semestralmente "
                            "por los PSP de toda la zona euro. Estos datos incluyen transferencias "
                            "de crédito, débitos directos, pagos con tarjeta y transacciones de "
                            "dinero electrónico, con desgloses por país, tipo de instrumento y "
                            "carácter doméstico o transfronterizo de la operación.", ref(12),
                        ),
                        parrafo(
                            "La recopilación de estos datos está respaldada jurídicamente por el "
                            "Reglamento ECB/2020/59 y la Directriz ECB/2021/13, que actualizan "
                            "el alcance del Reglamento original ECB/2013/43. Con las revisiones "
                            "más recientes, el ámbito de recolección incorporó nuevos métodos de "
                            "pago, canales digitales y desgloses detallados por categoría de "
                            "comercio. Gracias a este marco, el dataset del BCE constituye la "
                            "fuente más completa y estandarizada disponible para el análisis del "
                            "fraude en pagos a escala europea.", ref(13), ref(10),
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

            # ── Sección 6 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "6. Random Forest: fundamentos y aplicación en detección de fraude",
                    [
                        parrafo(
                            "Random Forest es un algoritmo de aprendizaje supervisado basado en el "
                            "principio de bagging (Bootstrap Aggregating), propuesto por Breiman "
                            "en 2001. El algoritmo construye un conjunto de árboles de decisión "
                            "independientes, cada uno entrenado sobre una submuestra aleatoria con "
                            "reemplazo del conjunto de entrenamiento (bootstrap sample). En cada "
                            "nodo de división de un árbol, solo se evalúa un subconjunto aleatorio "
                            "de ", html.Code("max_features"), " variables candidatas como posibles "
                            "puntos de corte, lo que introduce diversidad entre los árboles y "
                            "reduce la correlación entre sus predicciones. La clasificación final "
                            "se obtiene por votación mayoritaria entre todos los árboles del "
                            "ensamble.", ref(5),
                        ),
                        parrafo(
                            "La combinación de submuestreo de observaciones y submuestreo de "
                            "variables produce modelos con baja varianza y alta robustez frente al "
                            "ruido, sin incrementar sustancialmente el sesgo. A diferencia de un "
                            "árbol de decisión individual, que tiende a sobreajustarse a los datos "
                            "de entrenamiento, Random Forest generaliza mejor al promedio de "
                            "múltiples árboles con alta varianza individual pero errores poco "
                            "correlacionados entre sí. Esta propiedad lo hace especialmente "
                            "adecuado para conjuntos de datos tabulares con interacciones no "
                            "lineales y variables categóricas de alta cardinalidad, como las "
                            "presentes en este análisis.", ref(5),
                        ),
                        parrafo(
                            "En el contexto de la detección de fraude financiero, Random Forest "
                            "ha demostrado consistentemente un alto poder discriminante. Una "
                            "revisión sistemática de la literatura publicada entre 2012 y 2023 "
                            "identificó a Random Forest como el algoritmo con mayor frecuencia de "
                            "uso y mejores resultados en conjuntos de datos de transacciones reales, "
                            "alcanzando tasas de precisión superiores al 95% en clasificación "
                            "binaria de fraude.", ref(5), " En este proyecto, el modelo se "
                            "entrenó con los hiperparámetros ", html.Code("n_estimators"),
                            ", ", html.Code("max_depth"), ", ", html.Code("min_samples_split"),
                            ", ", html.Code("min_samples_leaf"), " y ", html.Code("max_features"),
                            " optimizados mediante RandomizedSearchCV con 10 pliegues estratificados.",
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

            # ── Sección 7 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "7. Balanced Accuracy como métrica en clases desbalanceadas",
                    [
                        parrafo(
                            "En problemas de clasificación con clases desbalanceadas, la exactitud "
                            "global (accuracy) resulta una métrica engañosa. Un clasificador que "
                            "etiquete todas las observaciones como la clase mayoritaria —en este "
                            "caso, transacciones legítimas— alcanzaría una accuracy del 99.7% sin "
                            "detectar ningún fraude real. Para corregir este sesgo se utiliza la "
                            "Balanced Accuracy (BA), definida como el promedio aritmético de la "
                            "sensibilidad (recall de la clase positiva) y la especificidad (recall "
                            "de la clase negativa):", ref(4),
                        ),
                        formula("BA = (Sensibilidad + Especificidad) / 2  =  (TP/(TP+FN) + TN/(TN+FP)) / 2"),
                        parrafo(
                            "Esta formulación garantiza que ambas clases reciban igual peso en la "
                            "evaluación, independientemente de su frecuencia relativa. Un "
                            "clasificador aleatorio obtiene una BA de 0.5, mientras que un modelo "
                            "perfecto alcanza 1.0. Si el modelo clasifica todo como la clase "
                            "mayoritaria, la sensibilidad colapsa a 0 y la BA desciende a 0.5, "
                            "penalizando correctamente el comportamiento trivial que la accuracy "
                            "ordinaria premiaría.", ref(4),
                        ),
                        parrafo(
                            "En este proyecto, la Balanced Accuracy se registró como una de las "
                            "métricas de validación cruzada en todos los modelos evaluados, "
                            "permitiendo comparar el rendimiento real sobre ambas clases más allá "
                            "de la capacidad del modelo para identificar transacciones legítimas. "
                            "Su complemento con el PR-AUC y el F1-Score, ambos enfocados en la "
                            "clase positiva, constituye el conjunto de métricas que guía la "
                            "selección del modelo final.",
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

            # ── Sección 8 ─────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(card_seccion(
                    "8. Resumen metodológico del modelo predictivo",
                    [
                        parrafo(
                            "Para el modelado se seleccionaron ocho variables a partir del dataset "
                            "original de 29 columnas: siete categóricas —", html.Code("frecuencia"),
                            ", ", html.Code("pais_origen"), ", ", html.Code("pais_destino"),
                            ", ", html.Code("tipo_trx"), ", ", html.Code("tipo_psp"),
                            ", ", html.Code("unidad"), " y ", html.Code("tipo_monto"),
                            "— y la variable numérica ", html.Code("monto_final"),
                            ", transformada mediante ", html.Code("log1p"),
                            " para corregir la distribución sesgada. La variable objetivo ",
                            html.Code("tipo_fraude_bin"), " presenta un desbalanceo crítico del "
                            "0.3% de casos positivos, lo que condicionó todas las decisiones de "
                            "diseño del pipeline. El preprocesamiento se implementó con un ",
                            html.Code("ColumnTransformer"), " que aplica imputación y escalado "
                            "para la variable numérica, e imputación con OneHotEncoding para las "
                            "categóricas, clonado individualmente en cada experimento para "
                            "garantizar independencia entre modelos. Los datos se dividieron en "
                            "80% entrenamiento y 20% prueba con split estratificado.",
                        ),
                        parrafo(
                            "Se evaluaron seis algoritmos —Regresión Logística, Naive Bayes, "
                            "LinearSVC, XGBoost, LightGBM y Random Forest— bajo cuatro estrategias "
                            "de balanceo: sin balanceo, SMOTE, ADASYN y ajuste de pesos de clase. "
                            "La búsqueda de hiperparámetros se realizó con RandomizedSearchCV "
                            "usando StratifiedKFold de 10 pliegues, optimizando el F1-Score como "
                            "métrica de refit. El hallazgo principal fue que ninguna técnica de "
                            "balanceo mejoró el PR-AUC real sobre el conjunto de prueba: SMOTE, "
                            "ADASYN y class weights dispararon el recall a ~1.0 a costa de una "
                            "precisión inviable en producción. Random Forest sin balanceo obtuvo "
                            "el mejor PR-AUC test (0.9659), seguido de XGBoost (0.9522), "
                            "estadísticamente indistinguibles en ROC-AUC (p=0.922 por Bootstrap). "
                            "XGBoost fue seleccionado como modelo final por su eficiencia "
                            "computacional —55.8 s frente a 535.3 s de Random Forest—, sin "
                            "sacrificio significativo en capacidad predictiva. El análisis de "
                            "interpretabilidad con LIME reveló que el destino geográfico "
                            "(", html.Code("pais_destino_W0"), ") y el tipo de transacción "
                            "(", html.Code("tipo_trx_CP0"), ") son los predictores locales más "
                            "fuertes de fraude en ambos modelos finalistas.",
                        ),
                    ]
                ), md=12),
            ], className="g-3 mb-3"),

        ], className="page-content"),
    ])