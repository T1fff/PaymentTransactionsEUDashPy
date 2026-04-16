import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from utils.svg_icons import ico_info, ico_warn_small, ico_book, ico_loop, ico_find, ico_pin
import plotly.graph_objects as go

dash.register_page(__name__, path="/univariado", name="EDA Univariado", order=3)

# ── Tokens ─────────────────────────────────────────────────────────────────
BG_CARD  = "#ffffff"
TXT_MAIN = "#1E1E2E"
TXT_MUTE = "#6E6D7A"
TXT_DIM  = "#AEADB8"
C_GREEN  = "#00B894"
C_RED    = "#EF4444"
C_AMBER  = "#D97706"
C_PURP   = "#FF6584"
C_BLUE   = "#6C5CE7"
BORDER   = "#E8E5DE"
BORDER2  = "#F0EDE8"

def card(children, extra_style=None):
    s = {"backgroundColor":"#ffffff","border":"1px solid #E8E4F9","borderRadius":"16px",
         "padding":"24px","marginBottom":"20px"}
    if extra_style: s.update(extra_style)
    return html.Div(children, style=s)

def card_title(text, color=C_PURP):
    return html.H5(text, style={"color":color,"marginBottom":"16px","fontWeight":"600"})
def card_h4(text):
    return html.H4(text, style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"6px"})
def card_p(text):
    return html.P(text, style={"color":TXT_MUTE,"fontSize":"13px","margin":"0"})

def pill_green(text):
    return html.Span(f"✔ {text}", style={"background":"rgba(22,163,74,0.10)","color":"#15803D","padding":"2px 8px","borderRadius":"10px","fontSize":"11px"})
def pill_red(text):
    return html.Span(f"✖ {text}", style={"background":"rgba(239,68,68,0.10)","color":"#B91C1C","padding":"2px 8px","borderRadius":"10px","fontSize":"11px"})
def pill_amber(text):
    return html.Span(f"⚠ {text}", style={"background":"rgba(255,200,80,0.15)","color":"#B45309","padding":"2px 8px","borderRadius":"10px","fontSize":"11px"})

def code_green(text):
    return html.Code(text, style={"color":C_GREEN,"background":"rgba(80,200,140,0.1)","padding":"2px 6px","borderRadius":"4px"})
def code_red(text):
    return html.Code(text, style={"color":C_RED,"background":"rgba(255,100,100,0.1)","padding":"2px 6px","borderRadius":"4px"})
def code_amber(text):
    return html.Code(text, style={"color":"#B45309","background":"rgba(217,119,6,0.08)","padding":"2px 6px","borderRadius":"4px"})

TH  = {"color":C_PURP,"padding":"8px 12px","textAlign":"left","borderBottom":"1px solid #E8E4F9","fontSize":"13px"}
TD  = {"color":TXT_MUTE,"padding":"7px 12px","borderBottom":f"1px solid {BORDER2}","fontSize":"13px"}
TD_N= {"color":TXT_MUTE,"padding":"7px 12px","borderBottom":f"1px solid {BORDER2}","fontSize":"13px","textAlign":"center","width":"40px"}
TH_RIGHT  = {**TH,"textAlign":"right"}
TH_LEFT   = {**TH,"textAlign":"left"}

# ══════════════════════════════════════════════════════════════════════════
# DATOS REALES HARDCODEADOS
# ══════════════════════════════════════════════════════════════════════════

ALL_COLS = [
    ("KEY",              "Clave compuesta de transacción",                                              code_green, "clave",                "sel"),
    ("FREQ",             "Frecuencia del pago (Anual, trimestral, semestral, etc.)",                    code_green, "frecuencia",           "sel"),
    ("REF_AREA",         "País origen de la transacción",                                               code_green, "pais_origen",          "sel"),
    ("COUNT_AREA",       "Institución origen de la transacción",                                        code_green, "pais_destino",         "sel"),
    ("TYP_TRNSCTN",      "Clasificación de la transacción (Depósito, retiro, cheques, etc.)",           code_green, "tipo_trx",             "sel"),
    ("RL_TRNSCTN",       "Clasificación de la entidad que procesa la transacción",                      code_green, "tipo_psp",             "sel"),
    ("FRD_TYP",          "Clasificación del fraude",                                                    code_green, "tipo_fraude",          "sel"),
    ("TRANSFORMATION",   "Transformación realizada a la transacción",                                   code_red,   "descartada",           "disc"),
    ("UNIT_MEASURE",     "Unidad o divisa involucrada en la transacción",                               code_green, "unidad",               "sel"),
    ("TIME_PERIOD",      "Año en el que se procesó la transacción",                                     code_green, "anio",                 "sel"),
    ("OBS_VALUE",        "Monto de la transacción",                                                     code_green, "monto",                "sel"),
    ("OBS_STATUS",       "Clasificación del monto",                                                     code_green, "tipo_monto",           "sel"),
    ("CONF_STATUS",      "Clasificación de confidencialidad",                                           code_red,   "descartada",           "disc"),
    ("PRE_BREAK_VALUE",  "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("COMMENT_OBS",      "Observaciones",                                                               code_red,   "descartada",           "disc"),
    ("TIME_FORMAT",      "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("BREAKS",           "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("COMMENT_TS",       "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("COMPILING_ORG",    "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("DISS_ORG",         "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("TIME_PER_COLLECT", "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("COVERAGE",         "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("DATA_COMP",        "No especificada en la documentación",                                         code_red,   "descartada",           "disc"),
    ("DECIMALS",         "Cantidad de decimales presentes en el monto",                                 code_green, "decimales",            "sel"),
    ("METHOD_REF",       "Metodología utilizada para la recolección del dato",                          code_red,   "descartada",           "disc"),
    ("TITLE",            "Descripción de la transacción",                                               code_green, "descripcion",          "sel"),
    ("TITLE_COMPL",      "Columna copia de TITLE",                                                      code_amber, "duplicada",            "dup"),
    ("UNIT",             "Columna copia de UNIT_MEASURE",                                               code_amber, "duplicada",            "dup"),
    ("UNIT_MULT",        "Multiplicador del monto de la transacción",                                   code_green, "multiplicador_unidad", "sel"),
]

NAN_COUNTS = {
    "clave":0,"frecuencia":0,"pais_origen":0,"pais_destino":0,"tipo_trx":0,
    "tipo_psp":0,"tipo_fraude":0,"unidad":0,"anio":0,"monto":143875,
    "tipo_monto":0,"decimales":0,"descripcion":0,"multiplicador_unidad":0,
}

DESCRIPTIONS = {
    "tipo_fraude":        "La variable tipo_fraude representa la clasificación del fraude identificado en una transacción. Del total de observaciones, 660.672 no están relacionadas a un caso de fraude, mientras que 1.944 transacciones fueron marcadas como movimientos fraudulentos. Debido al alto desequilibrio entre las observaciones legales y las transacciones fraudulentas se debe tener mucha precaución a la hora de construir el modelo de predicción.",
    "frecuencia":         "Las transacciones anuales (A) representan un 41.53% del total, mientras que la frecuencia semestral (H) y trimestral (Q) agrupan un 35.75% y 22.72%, cada una. En números exactos esto es 275.179, 236.884 y 150.553 transacciones respectivamente.",
    "pais_origen":        "Los países tienen frecuencias muy similares. Romania, Hungría, Polonia, República Checa y Países Bajos son los 5 territorios con el porcentaje de origen más alto (>4%). Entidades como 'Euro Area changing composition' y 'EU changing composition' presentan baja frecuencia (<1%).",
    "pais_destino":       "El 22.54% de las transacciones no especifican el destino final sino que generalizan en entidades como World (13%), Rest of the World (3.28%), Domestic (3.25%) y Extra EEA (2.62%). Los países fuera de la EEA comprenden menos del 1% cada uno.",
    "tipo_trx":           "Los débitos directos (DD) y transferencias de crédito (CT0) son las categorías más grandes (14.59% c/u), seguidas por pagos electrónicos (14%), cheques (13.91%) y pagos con tarjeta (9.02%). TOTL y TOTL1 representan totales agregados.",
    "tipo_psp":           "El 58.51% de las transacciones se registraron desde el PSP del pagador (387.724), frente a 270.818 (40.87%) asociadas al PSP del beneficiario. Un 0.61% no tiene rol definido.",
    "unidad":             "Dominan PN (44.75%), EUR (39%) y XDF (9.22%). También se presentan ratios por habitantes, número de transacciones y GDP en menor proporción.",
    "tipo_monto":         "El 72.86% de las observaciones fueron clasificadas como A (monto validado). El 28% restante presenta un monto poco fiable: suprimido (Q=14.13%), no puede existir (M=7.39%), provisional (P=5.33%), no recolectado (L=0.19%) o estimado (E=0.10%).",
    "decimales":          "El 90.72% de los montos tienen 3 unidades decimales, frente al casi 10% restante que tiene 2. Útil para relacionar con multiplicador_unidad.",
    "descripcion":        "Mensaje corto asociado a cada transacción. Las más frecuentes: 'Card payments, sent', 'Cheques, sent', 'Credit transfers, sent', 'Direct debits, sent' (>3.000 apariciones cada una).",
    "multiplicador_unidad":"El 90.72% de los montos tienen un multiplicador de 6 (millones), frente al casi 10% con multiplicador 0 (unidades).",
    "clave":              "Clave compuesta por las principales características de la transacción. No es única. Ejemplo: PAY.A.AT.W0.CHQ.2._Z.G1.EUR con frecuencia máxima de 25.",
    "anio":               "El dataset cubre transacciones desde el año 2000. Se nota un incremento exponencial a partir de 2014. Los últimos 5 años (2022–2024) concentran los récords históricos de registros.",
    "monto":              "La distribución es altamente asimétrica en todas las categorías (PN, EUR, XDF), con fuerte concentración en valores bajos y valores extremos muy altos. Existen datos negativos, probablemente relacionados a saldos pendientes o deudas.",
}

VARS_TABLA      = ["clave","pais_origen","pais_destino","anio"]
VARS_GRAFICO    = ["frecuencia","tipo_trx","tipo_psp","unidad","tipo_monto","tipo_fraude","monto"]
VARS_INDICATIVA = ["decimales","descripcion","multiplicador_unidad"]

TABLA_DATA = {
    "clave": [
        ("PAY.A.AT.W0.CHQ.2._Z.G1.EUR",25),("PAY.A.AT.W0.CHQ.2._Z.G1.PN",25),
        ("PAY.A.AT.W0.CHQ.2._Z.N.EUR",25),("PAY.A.AT.W0.CHQ.2._Z.N.EUR_R_PNT",25),
        ("PAY.A.AT.W0.CHQ.2._Z.N.EUR_R_POP",25),("PAY.A.AT.W0.CHQ.2._Z.N.EUR_R_TT",25),
    ],
    "pais_origen": [
        ("RO",28816,4.35,"Romania"),("HU",28794,4.35,"Hungary"),("PL",28267,4.27,"Poland"),
        ("CZ",28133,4.25,"Czech Republic"),("NL",27274,4.12,"Netherlands"),
        ("PT",25672,3.87,"Portugal"),("LT",25590,3.86,"Lithuania"),
        ("DE",25219,3.81,"Germany"),("FI",25162,3.80,"Finland"),("LU",25156,3.80,"Luxembourg"),
    ],
    "pais_destino": [
        ("W0",88733,13.39,"World"),("W1",21755,3.28,"Rest of the World"),
        ("W2",21507,3.25,"Domestic"),("G1",17392,2.62,"Extra EEA"),
        ("SE",16057,2.42,"Sweden"),("DK",15769,2.38,"Denmark"),
        ("BG",15488,2.34,"Bulgaria"),("GR",15440,2.33,"Greece"),
        ("AT",15437,2.33,"Austria"),("BE",15437,2.33,"Belgium"),
    ],
    "anio": [
        (2000,2628,0.40),(2001,2772,0.42),(2002,2952,0.45),(2003,3060,0.46),
        (2004,3276,0.49),(2005,3348,0.51),(2006,3564,0.54),(2007,3996,0.60),
        (2008,4464,0.67),(2009,5040,0.76),(2010,5688,0.86),(2011,6444,0.97),
        (2012,7308,1.10),(2013,9324,1.41),(2014,17150,2.59),(2015,17836,2.69),
        (2016,17836,2.69),(2017,17916,2.70),(2018,17948,2.71),(2019,17948,2.71),
        (2020,17948,2.71),(2021,17948,2.71),(2022,33211,5.01),(2023,33466,5.05),(2024,31561,4.76),
    ],
}

FREQ_STATS = {
    "tipo_fraude": [("_Z","No Fraude",660672,99.7),("F","Fraude",1944,0.3)],
    "frecuencia":  [("A","Anual",275179,41.53),("H","Semestral",236884,35.75),("Q","Trimestral",150553,22.72)],
    "tipo_psp":    [("1","Payer's PSP",387724,58.51),("2","Payee's PSP",270818,40.87),("_Z","NA",4074,0.61)],
    "tipo_monto":  [("A","Valor normal",482780,72.86),("Q","Suprimido",93601,14.13),("M","No puede existir",48997,7.39),("P","Provisional",35316,5.33),("L","No recolectado",1277,0.19),("E","Estimado",645,0.10)],
    "tipo_trx":    [("DD","Direct debits",96675,14.59),("CT0","Credit transfers",96663,14.59),("EMP0","E-money",92772,14.00),("CHQ","Cheques",92173,13.91),("CP0","Card payments",59765,9.02),("SER","Other services",56997,8.60),("MREM","Remittances",52272,7.89),("TOTL","Total",48151,7.27),("TOTL1","Total excl. cash",44336,6.69),("CW1","Cash withdrawals",18738,2.83)],
    "unidad":      [("PN","Pure number",296348,44.72),("EUR","Euro",258391,39.00),("XDF","Domestic currency",61103,9.22),("PN_R_POP","PN per capita",7724,1.17),("EUR_R_POP","EUR per capita",7688,1.16),("EUR_R_TT","EUR ratio total",7555,1.14),("PN_R_TT","PN ratio total",7523,1.14),("EUR_R_PNT","EUR ratio n°",7061,1.07),("EUR_R_B1GQ","EUR ratio GDP",4487,0.68)],
}

INDICATIVA_FREQ = {
    "decimales":            [("3",601087,90.72),("2",61529,9.28)],
    "multiplicador_unidad": [("6 (millones)",601087,90.72),("1 (unidades)",61529,9.28)],
    "descripcion": [
        ("Card payments, sent",3672,0.55),("Cheques, sent",3672,0.55),
        ("Credit transfers, sent",3672,0.55),("Direct debits, sent",3672,0.55),
        ("Other payment services, sent",3672,0.55),
        ("Total payment transactions, sent",3672,0.55),
        ("E-money payments, sent",3672,0.55),
    ],
}

INDICATIVA_INFO = {
    "decimales":            ("decimales","El 90.72% de los registros tienen 3 decimales · 9.28% tienen 2 decimales · Variable técnica de precisión numérica."),
    "descripcion":          ("descripcion","Variable textual con alta cardinalidad. Las descripciones más frecuentes rondan los 3.500 registros cada una."),
    "multiplicador_unidad": ("multiplicador_unidad","El 90.72% de los montos tienen multiplicador 6 (millones) · 9.28% tienen multiplicador 1 (unidades). Variable técnica de escala monetaria."),
}

STATS_TABLA_HARDCODED = {
    "clave":        {"n":662616,"unique":51480},
    "pais_origen":  {"n":662616,"unique":29},
    "pais_destino": {"n":662616,"unique":52},
    "anio":         {"n":662616,"unique":25},
}

# Estadísticas reales de monto por unidad (del notebook)
MONTO_STATS_POR_UNIDAD = {
    "PN":  {"n":296348,"n_missing":66013,"pct_missing":22.27,"media":184654.0,"ds":2786927.0,"mediana":20.0,"minimo":-10.0,"maximo":207701558.0,"q1":0.0,"q3":1248.0,"iqr":1248.0},
    "EUR": {"n":258391,"n_missing":55972,"pct_missing":21.66,"media":353443535.0,"ds":5407405070.0,"mediana":27290.83,"minimo":-10.0,"maximo":263423125212.0,"q1":3.68,"q3":1656369.0,"iqr":1656365.32},
    "XDF": {"n":61103,"n_missing":17562,"pct_missing":28.74,"media":5685471097.0,"ds":75176776461.0,"mediana":38552.0,"minimo":-10.0,"maximo":2.950583e12,"q1":0.0,"q3":9495258.0,"iqr":9495258.0},
}

DICTS = {
    "tipo_fraude": {"title":"Clasificación del fraude","entries":[("F","Fraude"),("_Z","No Fraude")],"notes":[]},
    "frecuencia":  {"title":"Recurrencia del pago","entries":[("A","Transacciones anuales"),("H","Transacciones semestrales (mitad de año)"),("Q","Transacciones trimestrales")],"notes":[]},
    "tipo_psp":    {"title":"Rol del proveedor de servicios de pago","entries":[("1","Payer's PSP — Proveedor del pagador"),("2","Payee's PSP — Proveedor del beneficiario"),("_Z","NA — Sin rol definido")],"notes":[]},
    "tipo_monto":  {"title":"Clasificación del monto registrado","entries":[("A","Valor normal"),("Q","Valor faltante, suprimido"),("M","Valor faltante, dato no puede existir"),("P","Valor temporal / provisional"),("L","Valor faltante, dato existente pero no pudo ser recolectado"),("E","Valor estimado")],"notes":[]},
    "tipo_trx":    {"title":"Tipo de instrumento de pago","entries":[("CHQ","Cheques"),("CP0","Card payments"),("CT0","Credit transfers"),("CW1","Cash withdrawals using cards"),("DD","Direct debits"),("EMP0","E-money payments"),("MREM","Money remittances"),("SER","Other payment services"),("TOTL","Total payment transactions"),("TOTL1","Total excl. cash withdrawals")],"notes":["TOTL y TOTL1 son totales agregados, no instrumentos individuales."]},
    "unidad":      {"title":"Unidad o divisa de medida","entries":[("PN","Pure number"),("EUR","Euro"),("XDF","Domestic currency"),("PN_R_POP","Pure number per capita"),("EUR_R_POP","Euro per capita"),("EUR_R_TT","Euro; ratio to total value"),("PN_R_TT","Pure number; ratio to total number"),("EUR_R_PNT","Euro; ratio to number of transactions"),("EUR_R_B1GQ","Euro; ratio to GDP")],"notes":["No tiene sentido comparar series de distintas unidades sin transformación previa."]},
    "pais_origen": {"title":"País de origen (REF_AREA)","entries":[("AT","Austria"),("BE","Belgium"),("BG","Bulgaria"),("CY","Cyprus"),("CZ","Czech Republic"),("DE","Germany"),("DK","Denmark"),("EE","Estonia"),("ES","Spain"),("FI","Finland"),("FR","France"),("GR","Greece"),("HR","Croatia"),("HU","Hungary"),("IE","Ireland"),("IT","Italy"),("LT","Lithuania"),("LU","Luxembourg"),("LV","Latvia"),("MT","Malta"),("NL","Netherlands"),("PL","Poland"),("PT","Portugal"),("RO","Romania"),("SE","Sweden"),("SI","Slovenia"),("SK","Slovakia"),("U2","Euro Area changing composition"),("B0","EU changing composition")],"notes":["U2/B0: países incluidos/excluidos de la zona euro o la UE a lo largo del tiempo."]},
    "pais_destino":{"title":"País de destino (COUNT_AREA)","entries":[("W0","World"),("W1","Rest of the World"),("W2","Domestic"),("G1","Extra EEA"),("G3","Other EEA countries"),("NO","Norway"),("IS","Iceland"),("LI","Liechtenstein"),("AT","Austria"),("BE","Belgium"),("BG","Bulgaria"),("CY","Cyprus"),("CZ","Czech Republic"),("DE","Germany"),("DK","Denmark"),("EE","Estonia"),("ES","Spain"),("FI","Finland"),("FR","France"),("GR","Greece"),("HR","Croatia"),("HU","Hungary"),("IE","Ireland"),("IT","Italy"),("LT","Lithuania"),("LU","Luxembourg"),("LV","Latvia"),("MT","Malta"),("NL","Netherlands"),("PL","Poland"),("PT","Portugal"),("RO","Romania"),("SE","Sweden"),("SI","Slovenia"),("SK","Slovakia"),("AR","Argentina"),("AU","Australia"),("BR","Brazil"),("CA","Canada"),("CN","China"),("GB","United Kingdom"),("ID","Indonesia"),("IN","India"),("JP","Japan"),("KR","Korea"),("MX","Mexico"),("RU","Russian Federation"),("SA","Saudi Arabia"),("TR","Turkey"),("US","United States"),("ZA","South Africa")],"notes":["World: todo el conjunto de países e instituciones, incluyendo el país de referencia.","Rest of the world: igual que World pero excluyendo el país de origen.","Domestic: entidades dentro del territorio económico de un país.","Extra EEA: Noruega, Islandia y Liechtenstein."]},
    "decimales":           {"title":"Cantidad de decimales en monto","entries":[("3","3 decimales — 90.72% de los registros"),("2","2 decimales — 9.28% de los registros")],"notes":["Útil para relacionar con multiplicador_unidad."]},
    "multiplicador_unidad":{"title":"Multiplicador del monto (UNIT_MULT)","entries":[("6","Millones (×1,000,000) — 90.72% de los registros"),("0→1","Unidades (×1) — 9.28% de los registros")],"notes":["El valor 0 se trata como 1 (sin multiplicador)."]},
    "anio":                {"title":"Años cubiertos (TIME_PERIOD)","entries":[("2000–2013","Datos históricos — baja frecuencia, crecimiento gradual"),("2014–2021","Incremento exponencial — desde 17.150 hasta 17.948 registros/año"),("2022","33.211 registros — récord histórico"),("2023","33.466 registros — máximo absoluto"),("2024","31.561 registros")],"notes":["Los años pueden aparecer desglosados por trimestre o semestre según la variable frecuencia."]},
    "clave":               {"title":"Estructura de la clave compuesta (KEY)","entries":[("PAY","Prefijo fijo — Payment"),("[FREQ]","Frecuencia: A / H / Q"),("[REF_AREA]","País de origen: AT, DE, FR…"),("[COUNT_AREA]","País de destino: W0, BG, FR…"),("[TYP_TRNSCTN]","Tipo de transacción: TOTL, CHQ, DD…"),("[RL_TRNSCTN]","Tipo de PSP: 1, 2, _Z"),("[FRD_TYP]","Tipo de fraude: F, _Z"),("[UNIT_MEASURE]","Unidad: PN, EUR, XDF…")],"notes":["La clave no es única — la misma combinación de atributos aparece en varios años."]},
    "descripcion":         {"title":"Descripciones más frecuentes (TITLE)","entries":[("Card payments, sent","Pagos con tarjeta enviados"),("Cheques, sent","Cheques enviados"),("Credit transfers, sent","Transferencias de crédito enviadas"),("Direct debits, sent","Débitos directos enviados"),("Other payment services, sent","Otros servicios de pago enviados"),("Total payment transactions, sent","Total de transacciones enviadas"),("E-money payments, sent","Pagos con dinero electrónico enviados")],"notes":["Variable textual con alta cardinalidad. Se listan solo las 7 más frecuentes (>2.000 apariciones)."]},
    "monto":               {"title":"Variable numérica — estadísticas por unidad","entries":[("PN · Media","184.654 (Mediana: 20.0)"),("PN · Std","2.786.927"),("PN · Rango","-10 a 207.701.558"),("EUR · Media","353.443.535 € (Mediana: 27.290,83 €)"),("EUR · Std","5.407.405.070"),("EUR · Rango","-10 € a 263.423.125.212 €"),("XDF · Media","5.685.471.097 (Mediana: 38.552)"),("XDF · Std","75.176.776.461"),("XDF · Rango","-10 a 2,95 billones")],"notes":["Los valores negativos son probablemente saldos pendientes o deudas.","La distribución es altamente asimétrica en los tres grupos."]},
}

# ══════════════════════════════════════════════════════════════════════════
# TABS PREPARACIÓN / FALTANTES / TRATAMIENTO (sin cambios respecto al original)
# ══════════════════════════════════════════════════════════════════════════

def _tab_preparacion():
    rows = []
    for i, (col, desc, code_fn, alias, status) in enumerate(ALL_COLS, 1):
        bg = "rgba(91,79,207,0.03)" if i % 2 == 1 else "transparent"
        status_cell = pill_green(alias) if status=="sel" else (pill_red(alias) if status=="disc" else pill_amber(alias))
        rows.append(html.Tr([
            html.Td(str(i),            style={**TD_N,"background":bg}),
            html.Td(code_fn(col),      style={**TD,"background":bg}),
            html.Td(desc,              style={**TD,"background":bg,"fontSize":"12px"}),
            html.Td(status_cell,       style={**TD,"background":bg}),
        ]))
    return html.Div([
        card([card_h4("Diccionario de Columnas"),
              card_p("El dataset original cuenta con 29 columnas. Se describen todas las variables identificando columnas duplicadas y las conservadas para el análisis.")]),
        card([
            html.Div([ico_book(), html.Span("Columnas originales del dataset",style={"color":C_PURP,"fontWeight":"600","fontSize":"14px","verticalAlign":"middle","marginLeft":"5px"})],
                     style={"display":"flex","alignItems":"center","marginBottom":"16px"}),
            html.Div(html.Table([
                html.Thead(html.Tr([html.Th("#",style=TH),html.Th("Columna",style=TH),html.Th("Descripción",style=TH),html.Th("Estado",style=TH)])),
                html.Tbody(rows),
            ],style={"width":"100%","borderCollapse":"collapse"}),style={"overflowX":"auto"}),
        ]),
        dbc.Row([
            dbc.Col(card([
                html.H6("Leyenda",style={"color":TXT_MAIN,"marginBottom":"12px"}),
                html.Div([
                    html.Div([html.Span("✔",style={"color":C_GREEN,"marginRight":"8px"}),html.Span("Columna seleccionada",style={"color":TXT_MUTE,"fontSize":"12px"})],style={"display":"flex","alignItems":"center","marginBottom":"8px"}),
                    html.Div([html.Span("✖",style={"color":C_RED,"marginRight":"8px"}),html.Span("Columna descartada",style={"color":TXT_MUTE,"fontSize":"12px"})],style={"display":"flex","alignItems":"center","marginBottom":"8px"}),
                    html.Div([html.Span("⚠",style={"color":"#B45309","marginRight":"8px"}),html.Span("Columna duplicada (eliminada)",style={"color":TXT_MUTE,"fontSize":"12px"})],style={"display":"flex","alignItems":"center"}),
                ]),
            ],{"marginBottom":"0"}),md=4),
            dbc.Col(card([
                html.H6("Resumen de la selección",style={"color":TXT_MAIN,"marginBottom":"12px"}),
                html.Div([
                    html.Div([html.Div("14",style={"color":"#16A34A","fontSize":"1.4rem","fontWeight":"700"}),html.Div("Seleccionadas",style={"color":TXT_MUTE,"fontSize":"11px"})],
                             style={"background":"rgba(22,163,74,0.08)","border":"1px solid rgba(22,163,74,0.2)","borderRadius":"8px","padding":"12px","textAlign":"center","flex":"1"}),
                    html.Div([html.Div("13",style={"color":"#EF4444","fontSize":"1.4rem","fontWeight":"700"}),html.Div("Descartadas",style={"color":TXT_MUTE,"fontSize":"11px"})],
                             style={"background":"rgba(239,68,68,0.08)","border":"1px solid rgba(239,68,68,0.2)","borderRadius":"8px","padding":"12px","textAlign":"center","flex":"1","marginLeft":"10px"}),
                    html.Div([html.Div("2",style={"color":"#D97706","fontSize":"1.4rem","fontWeight":"700"}),html.Div("Duplicadas",style={"color":TXT_MUTE,"fontSize":"11px"})],
                             style={"background":"rgba(217,119,6,0.08)","border":"1px solid rgba(217,119,6,0.2)","borderRadius":"8px","padding":"12px","textAlign":"center","flex":"1","marginLeft":"10px"}),
                ],style={"display":"flex"}),
            ],{"marginBottom":"0"}),md=8),
        ],className="g-3"),
        card([
            html.Div([ico_loop(),html.Span("Comprobación de columnas duplicadas",style={"color":C_AMBER,"fontWeight":"600","fontSize":"14px","verticalAlign":"middle","marginLeft":"5px"})],
                     style={"display":"flex","alignItems":"center","marginBottom":"16px"}),
            dbc.Row([
                dbc.Col(html.Div([html.P(html.Code("UNIT_MEASURE == UNIT",style={"color":C_AMBER}),style={"marginBottom":"8px"}),html.P("¿Son idénticas?",style={"color":TXT_MUTE,"fontSize":"12px","marginBottom":"4px"}),html.Div("TRUE ✔",style={"color":C_GREEN,"fontWeight":"700","fontSize":"15px"})],style={"background":"rgba(217,119,6,0.06)","border":"1px solid rgba(217,119,6,0.2)","borderRadius":"8px","padding":"16px"}),md=6),
                dbc.Col(html.Div([html.P(html.Code("TITLE == TITLE_COMPL",style={"color":C_AMBER}),style={"marginBottom":"8px"}),html.P("¿Son idénticas?",style={"color":TXT_MUTE,"fontSize":"12px","marginBottom":"4px"}),html.Div("TRUE ✔",style={"color":C_GREEN,"fontWeight":"700","fontSize":"15px"})],style={"background":"rgba(217,119,6,0.06)","border":"1px solid rgba(217,119,6,0.2)","borderRadius":"8px","padding":"16px"}),md=6),
            ],className="g-3"),
        ]),
    ])


def _tab_faltantes():
    total = 662616
    cols_sorted = sorted(NAN_COUNTS.items(), key=lambda x: x[1])
    names  = [c for c,_ in cols_sorted]
    values = [v for _,v in cols_sorted]
    colors = ["#EF4444" if v>0 else "#16A34A" for v in values]
    fig_bar = go.Figure(go.Bar(x=values,y=names,orientation="h",marker_color=colors,textposition="outside",cliponaxis=False))
    fig_bar.update_layout(template="plotly_white",height=280,margin=dict(t=10,b=40,l=20,r=20),
                          paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                          yaxis=dict(gridcolor="#F0EDE8"),xaxis=dict(tickangle=-30),
                          font=dict(family="Plus Jakarta Sans",color="#6E6D7A",size=11),showlegend=False)
    rows = []
    for col, n_na in sorted(NAN_COUNTS.items(), key=lambda x: -x[1]):
        pct = round(n_na/total*100,2)
        bw  = max(2,min(100,pct*100)) if pct>0 else 0
        bc  = C_RED if n_na>0 else C_GREEN
        rows.append(html.Tr([
            html.Td(html.Code(col,style={"color":C_PURP,"background":"rgba(91,79,207,0.10)","padding":"2px 6px","borderRadius":"4px","fontSize":"11px"}),style=TD),
            html.Td(f"{total:,}",style={**TD,"textAlign":"right","color":TXT_DIM}),
            html.Td(f"{n_na:,}",style={**TD,"textAlign":"right","fontWeight":"600" if n_na>0 else "400","color":C_RED if n_na>0 else C_GREEN}),
            html.Td(f"{pct}%",style={**TD,"textAlign":"right","color":C_RED if n_na>0 else C_GREEN}),
            html.Td(html.Div(html.Div(style={"width":f"{bw}%","height":"6px","background":bc,"borderRadius":"3px"}),
                             style={"width":"100px","background":"rgba(255,255,255,.08)","height":"6px","borderRadius":"3px"}),style={**TD,"verticalAlign":"middle"}),
        ]))
    return html.Div([
        card([card_h4("Identificación de Valores Faltantes"),
              card_p("Se analiza la presencia de NAs en cada columna del dataset limpio. La mayoría de columnas no presentan valores faltantes. Sin embargo, la columna monto concentra la totalidad de los missing values.")]),
        dbc.Row([
            dbc.Col(html.Div([html.Div("143.875",style={"color":"#EF4444","fontSize":"2rem","fontWeight":"700","lineHeight":"1"}),html.Div("NAs en columna monto",style={"color":TXT_MUTE,"fontSize":"12px","marginTop":"6px"}),html.Div("Única columna con valores faltantes",style={"color":"rgba(185,28,28,0.5)","fontSize":"11px","marginTop":"4px"})],style={"background":"rgba(239,68,68,0.07)","border":"1px solid rgba(239,68,68,0.2)","borderRadius":"12px","padding":"20px","textAlign":"center"}),md=4),
            dbc.Col(html.Div([html.Div("13",style={"color":"#16A34A","fontSize":"2rem","fontWeight":"700","lineHeight":"1"}),html.Div("Columnas sin NAs",style={"color":TXT_MUTE,"fontSize":"12px","marginTop":"6px"}),html.Div("Completitud total en el resto de variables",style={"color":"rgba(21,128,61,0.5)","fontSize":"11px","marginTop":"4px"})],style={"background":"rgba(22,163,74,0.07)","border":"1px solid rgba(22,163,74,0.2)","borderRadius":"12px","padding":"20px","textAlign":"center"}),md=4),
            dbc.Col(html.Div([html.Div("21.71%",style={"color":"#0284C7","fontSize":"2rem","fontWeight":"700","lineHeight":"1","marginTop":"6px"}),html.Div("% de NAs sobre el total",style={"color":TXT_MUTE,"fontSize":"12px","marginTop":"6px"}),html.Div("Calculado sobre el total de filas del df",style={"color":"rgba(2,100,165,0.5)","fontSize":"11px","marginTop":"4px"})],style={"background":"rgba(2,132,199,0.07)","border":"1px solid rgba(2,132,199,0.2)","borderRadius":"12px","padding":"20px","textAlign":"center"}),md=4),
        ],className="g-3 mb-3"),
        card([
            html.Div([ico_find(),html.Span("NAs por columna",style={"color":C_PURP,"fontWeight":"600","fontSize":"14px","verticalAlign":"middle","marginLeft":"5px"})],style={"display":"flex","alignItems":"center","marginBottom":"4px"}),
            html.P("summarise(across(everything(), ~ sum(is.na(.))))",style={"color":TXT_DIM,"fontSize":"11px","fontFamily":"monospace","marginBottom":"16px"}),
            html.Div(html.Table([
                html.Thead(html.Tr([html.Th("Variable",style=TH),html.Th("Total obs.",style={**TH,"textAlign":"right"}),html.Th("NaN",style={**TH,"textAlign":"right"}),html.Th("% NaN",style={**TH,"textAlign":"right"}),html.Th("Proporción",style=TH)])),
                html.Tbody(rows),
            ],style={"width":"100%","borderCollapse":"collapse"}),style={"overflowX":"auto"}),
        ]),
        card([
            html.Div([ico_pin(),html.Span("Detalle — Columna monto",style={"color":C_RED,"fontWeight":"600","fontSize":"14px","verticalAlign":"middle","marginLeft":"5px"})],style={"display":"flex","alignItems":"center","marginBottom":"16px"}),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=fig_bar,config={"displayModeBar":False})],md=6),
                dbc.Col(html.Div([
                    html.P("Hallazgo clave",style={"color":C_RED,"fontWeight":"600","fontSize":"13px","marginBottom":"10px"}),
                    html.P("La columna monto es la única variable del dataset que presenta valores faltantes, concentrando el 100% de los NAs del conjunto de datos.",style={"color":TXT_MUTE,"fontSize":"13px","lineHeight":"1.6","marginBottom":"10px"}),
                    html.P("Dado que esta es la variable cuantitativa central del análisis, el tratamiento de estos valores faltantes tendrá un impacto directo en la calidad de los modelos y visualizaciones posteriores.",style={"color":TXT_MUTE,"fontSize":"13px","lineHeight":"1.6","marginBottom":"10px"}),
                    html.Div([html.P("⚠ Acción requerida",style={"color":"#B45309","fontWeight":"600","fontSize":"12px","marginBottom":"4px"}),html.P("Ver pestaña Tratamiento de Faltantes para la estrategia aplicada.",style={"color":"#B45309","fontSize":"12px","margin":"0"})],style={"background":"rgba(217,119,6,0.08)","border":"1px solid rgba(217,119,6,0.2)","borderRadius":"8px","padding":"12px","marginTop":"10px"}),
                ],style={"background":"rgba(239,68,68,0.05)","borderLeft":"3px solid #EF4444","borderRadius":"8px","padding":"16px"}),md=6),
            ],className="g-3"),
        ]),
    ])


def _tab_eda():
    opts = [
        {"label":"── Solo tabla resumen ──","value":"_header1","disabled":True},
        *[{"label":f"  {v}","value":v} for v in VARS_TABLA],
        {"label":"── Con gráficos ──","value":"_header2","disabled":True},
        *[{"label":f"  {v}","value":v} for v in VARS_GRAFICO],
        {"label":"── Solo indicativas ──","value":"_header3","disabled":True},
        *[{"label":f"  {v} (indicativa)","value":v} for v in VARS_INDICATIVA],
    ]
    return html.Div([
        card([card_h4("Análisis Univariado"),card_p("Se examina cada variable de forma individual con el objetivo de entender su distribución, medidas centrales y de dispersión.")]),
        card([
            html.P("Variable a analizar",style={"color":TXT_MAIN,"fontWeight":"600","fontSize":"15px","marginBottom":"4px"}),
            html.P("Selecciona una variable para visualizar su distribución e información estadística",style={"color":TXT_MUTE,"fontSize":"12px","marginBottom":"16px"}),
            dbc.Row([dbc.Col(dcc.Dropdown(id="uni-var-selector",options=opts,value="tipo_fraude",clearable=False,style={"fontFamily":"Plus Jakarta Sans","fontSize":"13px","background":"#fff"}),md=12)]),
        ]),
        dbc.Row([
            dbc.Col(card([html.Div(id="uni-graph-col")]),md=6),
            dbc.Col(card([html.Div(id="uni-stats-col")]),md=3),
            dbc.Col(html.Div(id="uni-dict-col"),md=3),
        ],className="g-3 align-items-start"),
    ])


def _tab_tratamiento():
    metricas = [
        ("CV_normalizado","RandomForest","148.4687","14.9892","5834.9932","0.8621","0.0383","20.0000"),
        ("CV_normalizado","XGBoost","206.9680","18.8973","5001.1419","0.8933","0.0430","7.6000"),
        ("CV_normalizado","LinearSVR","336.2136","31.8378","15951.5670","-0.0005","0.0001","165.3000"),
        ("CV_normalizado","KNN","408.1350","43.9160","12483.2473","0.3826","0.1112","13.9000"),
        ("CV_normalizado","BayesianRidge","994.7278","18.3951","15922.4942","0.0032","0.0006","1.3000"),
        ("CV_normalizado","Ridge","997.6360","18.4603","15922.4888","0.0032","0.0006","1.1000"),
        ("validacion_escala_real","RandomForest","299501.9098","","8887553.2063","0.8720","",""),
    ]
    TH_S={**TH,"fontSize":"11px","padding":"8px 10px"}
    TD_S={**TD,"fontSize":"11px","padding":"7px 10px"}
    headers=["tipo","modelo","MAE","MAE_std","RMSE","R2","R2_std","tiempo_s"]
    return html.Div([
        card([html.P("Tratamiento de Valores Faltantes",style={"color":TXT_MAIN,"fontWeight":"600","fontSize":"24px","marginBottom":"4px"}),html.P("En la variable monto, el 21.71% de las observaciones corresponden a valores faltantes. Se imputó con Random Forest tras una normalización previa. Se compararon: KNN, Ridge, BayesianRidge, Random Forest, XGBoost y LinearSVR.",style={"color":TXT_MUTE,"fontSize":"13px","lineHeight":"1.7","margin":"0"})]),
        card([card_title("Métricas de los Modelos entrenados"),html.Div(html.Table([html.Thead(html.Tr([html.Th(h,style=TH_S) for h in headers])),html.Tbody([html.Tr([html.Td(r[0],style=TD_S),html.Td(r[1],style={**TD_S,"fontWeight":"600","color":C_PURP}),html.Td(r[2],style=TD_S),html.Td(r[3],style=TD_S),html.Td(r[4],style=TD_S),html.Td(r[5],style={**TD_S,"fontWeight":"600","color":C_GREEN}),html.Td(r[6],style=TD_S),html.Td(r[7],style=TD_S)]) for r in metricas])],style={"width":"100%","borderCollapse":"collapse"}),style={"overflowX":"auto"})]),
        card([card_title("Predicciones vs Valores Reales"),html.Img(src="assets/fig_scatter.png",style={"width":"100%","borderRadius":"8px"})]),
        card([card_title("Distribución: Original vs Imputado"),html.Img(src="assets/fig_density.png",style={"width":"100%","borderRadius":"8px"})]),
        card([
            card_title("Prueba de Kolmogorov-Smirnov"),
            html.Code("Prueba KS (dos muestras)\n\nEstadístico D: 0.054155\np-valor:       0.000000\n\nSe rechaza H₀: las distribuciones difieren significativamente (p ≤ 0.05)\nLa imputación introdujo cambios menores en la distribución original.",style={"display":"block","color":"#B45309","fontSize":"13px","marginBottom":"12px","padding":"10px","background":"#F2F0EB","borderRadius":"6px","whiteSpace":"pre"}),
            html.P("La imputación con Random Forest está bien sustentada: R²=0.862 confirma poder predictivo real, D=0.054 en KS indica que la distribución acumulada no se desplaza más de 5.4 puntos porcentuales, y los estadísticos robustos (Q1, Q3, máximo) son prácticamente idénticos entre monto y monto_final.",style={"color":TXT_MUTE,"fontSize":"13px","lineHeight":"1.7","margin":"0"}),
        ]),
    ])


# ══════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════
layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Análisis Exploratorio Univariado",className="page-title"),
            html.P("Exploración detallada de variables individuales",className="page-sub"),
        ],className="section-header"),
        dbc.Row([dbc.Col(card([
            dcc.Tabs(id="uni-main-tab",value="prep",children=[
                dcc.Tab(label="Preparación de Columnas",value="prep",style={"fontSize":"13px","color":"#6E6D7A"},selected_style={"fontSize":"13px","color":C_PURP,"fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
                dcc.Tab(label="Identificación de Faltantes",value="nan",style={"fontSize":"13px","color":"#6E6D7A"},selected_style={"fontSize":"13px","color":C_PURP,"fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
                dcc.Tab(label="EDA Univariado",value="eda",style={"fontSize":"13px","color":"#6E6D7A"},selected_style={"fontSize":"13px","color":C_PURP,"fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
                dcc.Tab(label="Tratamiento de Faltantes",value="trat",style={"fontSize":"13px","color":"#6E6D7A"},selected_style={"fontSize":"13px","color":C_PURP,"fontWeight":"600","borderTop":"3px solid #5B4FCF"}),
            ]),
        ],{"marginBottom":"0"}),md=12)],className="g-3"),
        html.Div(id="uni-tab-content",style={"marginTop":"16px"}),
    ],className="page-content"),
],style={"minHeight":"100vh"})


# ══════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════

def _section_title(var):
    text = DESCRIPTIONS.get(var,"")
    if not text: return html.Div()
    return html.P(text,style={"fontSize":"12px","color":TXT_MUTE,"lineHeight":"1.6","marginTop":"12px","padding":"12px","background":"#F2F0EB","borderRadius":"8px","borderLeft":"3px solid #5B4FCF"})


def _build_dict(var):
    info = DICTS.get(var)
    if not info: return html.Div()
    entries    = info["entries"]
    notes      = info["notes"]
    scroll_h   = min(len(entries)*34+70,340)
    rows       = [html.Tr([
        html.Td(code,style={"fontFamily":"monospace","fontSize":"10px","fontWeight":"700","color":C_PURP,"padding":"5px 8px","borderBottom":f"1px solid {BORDER2}","whiteSpace":"nowrap","verticalAlign":"top","width":"1%"}),
        html.Td(label,style={"fontSize":"11px","color":TXT_MAIN,"padding":"5px 8px","borderBottom":f"1px solid {BORDER2}","lineHeight":"1.4"}),
    ]) for code,label in entries]
    note_els   = [html.Div([ico_info(),html.Span(f" {n}",style={"fontSize":"10px","color":TXT_MUTE,"lineHeight":"1.5","verticalAlign":"middle"})],style={"display":"flex","alignItems":"flex-start","gap":"4px","padding":"6px 8px","background":BORDER2,"borderRadius":"6px","marginTop":"4px"}) for n in notes]
    return card([
        html.Div(info["title"],style={"fontSize":"12px","fontWeight":"700","color":TXT_MAIN,"marginBottom":"10px"}),
        html.Div(html.Table([
            html.Thead(html.Tr([html.Th("Código",style={"fontSize":"9px","color":TXT_MUTE,"padding":"5px 8px","background":BORDER2,"borderBottom":f"2px solid {BORDER}","position":"sticky","top":"0","zIndex":"1"}),html.Th("Descripción",style={"fontSize":"9px","color":TXT_MUTE,"padding":"5px 8px","background":BORDER2,"borderBottom":f"2px solid {BORDER}","position":"sticky","top":"0","zIndex":"1"})])),
            html.Tbody(rows),
        ],style={"width":"100%","borderCollapse":"collapse"}),style={"maxHeight":f"{scroll_h}px","overflowY":"auto","borderRadius":"8px","border":f"1px solid {BORDER}"}),
        *note_els,
    ],{"padding":"16px","marginBottom":"0"})


def _render_tabla(var):
    data = TABLA_DATA.get(var,[])
    if var=="clave":
        hdr=["Categoría","Frecuencia"]; th_s=[TH_LEFT,TH_RIGHT]
        body=[html.Tr([html.Td(r[0],style={**TD,"fontFamily":"monospace","fontSize":"11px","textAlign":"left"}),html.Td(f"{r[1]:,}",style={**TD,"textAlign":"right"})]) for r in data]
    elif var in ("pais_origen","pais_destino"):
        hdr=["Código","Frecuencia","%","País/Descripción"]; th_s=[TH_LEFT,TH_RIGHT,TH_RIGHT,TH_LEFT]
        body=[html.Tr([html.Td(r[0],style={**TD,"fontFamily":"monospace","textAlign":"left"}),html.Td(f"{r[1]:,}",style={**TD,"textAlign":"right"}),html.Td(f"{r[2]}%",style={**TD,"textAlign":"right","color":C_PURP}),html.Td(r[3],style={**TD,"textAlign":"left"})]) for r in data]
    else:  # anio
        hdr=["Año","Frecuencia","%"]; th_s=[TH_LEFT,TH_RIGHT,TH_RIGHT]
        body=[html.Tr([html.Td(str(r[0]),style={**TD,"textAlign":"left"}),html.Td(f"{r[1]:,}",style={**TD,"textAlign":"right"}),html.Td(f"{r[2]}%",style={**TD,"textAlign":"right","color":C_PURP})]) for r in data]
    return [
        html.P(f"Distribución: {var}",style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"4px"}),
        html.P("Tabla de frecuencias",style={"color":TXT_MUTE,"fontSize":"12px","marginBottom":"12px"}),
        html.Div(html.Table([html.Thead(html.Tr([html.Th(h,style=th_s[i]) for i,h in enumerate(hdr)])),html.Tbody(body)],style={"width":"100%","borderCollapse":"collapse"}),style={"overflowX":"auto","borderRadius":"8px","border":"1px solid #E8E4F9"}),
        _section_title(var),
    ]


def _render_grafico(var):
    data = FREQ_STATS.get(var,[])
    if not data: return [html.Div("Sin datos",style={"color":TXT_MUTE})]
    cats   = [d[0] for d in data]
    labels = [d[1] for d in data]
    freqs  = [d[2] for d in data]
    pcts   = [d[3] for d in data]
    max_v  = max(freqs)
    lbl_len= max(len(f"{f:,} ({p}%)") for f,p in zip(freqs,pcts))
    r_pad  = int(lbl_len*6)+20
    x_max  = max_v*(1+r_pad/600)
    bar_color = C_RED if var=="tipo_fraude" else C_PURP
    fig = go.Figure(go.Bar(y=cats,x=freqs,orientation="h",marker_color=bar_color,
        text=[f"{f:,} ({p}%)" for f,p in zip(freqs,pcts)],textposition="outside",cliponaxis=False,
        customdata=labels,hovertemplate="<b>%{customdata}</b><br>n=%{x:,}<extra></extra>"))
    h = max(len(cats)*44+80,220)
    fig.update_layout(template="plotly_white",height=h,margin=dict(t=10,b=30,l=10,r=r_pad),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#F0EDE8",title="Núm. de transacciones",range=[0,x_max]),
        yaxis=dict(autorange="reversed"),
        font=dict(family="Plus Jakarta Sans",color=TXT_MUTE,size=11),showlegend=False)
    return [
        html.P(f"Distribución: {var}",style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"4px"}),
        html.P("Frecuencia por categoría",style={"color":TXT_MUTE,"fontSize":"12px","marginBottom":"12px"}),
        dcc.Graph(figure=fig,config={"displayModeBar":False}),
        _section_title(var),
    ]


def _render_monto():
    # Boxplot con estadísticas reales del notebook
    fig = go.Figure()
    palette = {"PN":C_PURP,"EUR":C_BLUE,"XDF":"#00C9A7"}
    for u, s in MONTO_STATS_POR_UNIDAD.items():
        r,g,b = int(palette[u][1:3],16),int(palette[u][3:5],16),int(palette[u][5:7],16)
        q1,q3 = s["q1"],s["q3"]
        wl    = max(s["minimo"],q1-1.5*s["iqr"])
        wu    = min(s["maximo"],q3+1.5*s["iqr"])
        fig.add_trace(go.Box(name=u,x=[u],
            q1=[q1],median=[s["mediana"]],q3=[q3],
            lowerfence=[wl],upperfence=[wu],mean=[s["media"]],
            marker_color=palette[u],line_color=palette[u],
            fillcolor=f"rgba({r},{g},{b},0.15)",boxmean=False,boxpoints=False))
        fig.add_trace(go.Scatter(x=[u],y=[s["media"]],mode="markers",
            marker=dict(color=palette[u],size=10,symbol="diamond",line=dict(color="#fff",width=1.5)),
            showlegend=False,hovertemplate=f"Media {u}: {s['media']:,.0f}<extra></extra>"))
    fig.update_layout(template="plotly_white",height=360,margin=dict(t=10,b=30,l=20,r=20),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="monto_real",gridcolor="#F0EDE8"),
        font=dict(family="Plus Jakarta Sans",color="#6E6D7A"),showlegend=True)
    return [
        html.P("Distribución: monto",style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"4px"}),
        html.P("Diagrama de cajas por tipo de unidad · PN / EUR / XDF",style={"color":TXT_MUTE,"fontSize":"12px","marginBottom":"12px"}),
        dcc.Graph(figure=fig,config={"displayModeBar":False}),
        _section_title("monto"),
    ]


def _render_indicativa(var):
    _,desc = INDICATIVA_INFO.get(var,(var,""))
    rows_data = INDICATIVA_FREQ.get(var,[])
    rows = [html.Tr([html.Td(str(r[0])[:30],style={**TD,"fontFamily":"monospace","fontSize":"11px"}),html.Td(f"{r[1]:,}",style={**TD,"textAlign":"right"}),html.Td(f"{r[2]}%",style={**TD,"textAlign":"right","color":C_PURP})]) for r in rows_data]
    return [
        html.P(f"Variable indicativa: {var}",style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"4px"}),
        html.Div(desc,style={"padding":"10px 12px","background":"#F2F0EB","borderRadius":"8px","borderLeft":"3px solid #5B4FCF","marginBottom":"12px","fontSize":"12px","color":TXT_MUTE}),
        html.Div(html.Table([
            html.Thead(html.Tr([html.Th("Categoría",style=TH),html.Th("Frecuencia",style={**TH,"textAlign":"right"}),html.Th("%",style={**TH,"textAlign":"right"})])),
            html.Tbody(rows),
        ],style={"width":"100%","borderCollapse":"collapse"}),style={"overflowX":"auto","borderRadius":"8px","border":"1px solid #E8E4F9"}),
    ]


def _render_stats_freq(var):
    data   = FREQ_STATS.get(var,[])
    n_total= sum(d[2] for d in data) if data else 662616
    n_unique=len(data)
    moda   = data[0][0] if data else "—"
    moda_n = data[0][2] if data else 0
    moda_p = data[0][3] if data else 0
    return [
        html.P("Estadísticas",style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"16px"}),
        *[html.Div([html.Div(lbl,style={"fontSize":"11px","color":TXT_MUTE}),html.Div(val,style={"fontSize":fs,"fontWeight":"700","color":col,"fontFamily":"'Sora',sans-serif","wordBreak":"break-all"})],style={"marginBottom":"14px"})
          for lbl,val,col,fs in [
              ("Total observaciones",f"{n_total:,}",TXT_MAIN,"18px"),
              ("Valores únicos",f"{n_unique:,}",C_PURP,"18px"),
              ("Valores nulos","0",C_GREEN,"18px"),
              ("Moda",str(moda),TXT_MAIN,"13px"),
              ("Frec. moda",f"{moda_n:,} ({moda_p}%)",TXT_MAIN,"13px"),
          ]],
        html.Hr(style={"borderColor":BORDER,"margin":"14px 0"}),
        html.P("Top 5",style={"fontSize":"12px","fontWeight":"600","color":C_PURP,"marginBottom":"8px"}),
        html.Table([
            html.Thead(html.Tr([html.Th("Categ.",style={**TH,"fontSize":"10px"}),html.Th("%",style={**TH,"fontSize":"10px","textAlign":"right"})])),
            html.Tbody([html.Tr([html.Td(str(d[0])[:18],style={**TD,"fontSize":"11px"}),html.Td(f"{d[3]}%",style={**TD,"fontSize":"11px","textAlign":"right","color":C_PURP,"fontWeight":"600"})]) for d in data[:5]]),
        ],style={"width":"100%","borderCollapse":"collapse"}),
    ]


def _render_stats_tabla(var):
    s = STATS_TABLA_HARDCODED.get(var,{"n":662616,"unique":"—"})
    return [
        html.P("Estadísticas",style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"16px"}),
        *[html.Div([html.Div(lbl,style={"fontSize":"11px","color":TXT_MUTE}),html.Div(val,style={"fontSize":"18px","fontWeight":"700","color":col,"fontFamily":"'Sora',sans-serif"})],style={"marginBottom":"14px"})
          for lbl,val,col in [("Total observaciones",f"{s['n']:,}",TXT_MAIN),("Valores únicos",f"{s['unique']:,}",C_PURP),("Valores nulos","0",C_GREEN)]],
    ]


def _render_stats_monto():
    return [
        html.P("Estadísticas",style={"color":TXT_MAIN,"fontWeight":"600","marginBottom":"16px"}),
        *[html.Div([html.Div(lbl,style={"fontSize":"11px","color":TXT_MUTE}),html.Div(val,style={"fontSize":"18px","fontWeight":"700","color":col,"fontFamily":"'Sora',sans-serif"})],style={"marginBottom":"14px"})
          for lbl,val,col in [("Obs. totales","662,616",TXT_MAIN),("NaN en monto","143,875",C_RED),("% NaN","21.71%",C_AMBER)]],
        html.Hr(style={"borderColor":BORDER,"margin":"14px 0"}),
        html.P("Por unidad",style={"fontSize":"12px","fontWeight":"600","color":C_PURP,"marginBottom":"8px"}),
        *[html.Div([
            html.Div(u,style={"fontSize":"12px","fontWeight":"700","color":C_PURP,"marginBottom":"3px"}),
            html.Div(f"n={s['n']:,} · NaN={s['n_missing']:,} ({s['pct_missing']}%)",style={"fontSize":"11px","color":TXT_MUTE}),
            html.Div(f"Mediana={s['mediana']:,.2f} · Media={s['media']:,.0f}",style={"fontSize":"11px","color":TXT_MUTE}),
          ],style={"padding":"8px","background":"#F2F0EB","borderRadius":"8px","marginBottom":"8px"})
          for u,s in MONTO_STATS_POR_UNIDAD.items()],
    ]


# ══════════════════════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════════════════════

@callback(Output("uni-tab-content","children"), Input("uni-main-tab","value"))
def render_main_tab(tab):
    if tab=="prep":  return _tab_preparacion()
    if tab=="nan":   return _tab_faltantes()
    if tab=="eda":   return _tab_eda()
    if tab=="trat":  return _tab_tratamiento()
    return html.Div()


@callback(
    Output("uni-graph-col","children"),
    Output("uni-stats-col","children"),
    Output("uni-dict-col","children"),
    Input("uni-var-selector","value"),
)
def update_eda(var):
    if var is None or var.startswith("_header"):
        return html.Div(), html.Div(), html.Div()
    try:
        d = _build_dict(var)
        if var in VARS_TABLA:
            return _render_tabla(var), _render_stats_tabla(var), d
        if var == "monto":
            return _render_monto(), _render_stats_monto(), d
        if var in VARS_INDICATIVA:
            return _render_indicativa(var), _render_stats_freq(var), d
        return _render_grafico(var), _render_stats_freq(var), d
    except Exception as e:
        err = html.Div(f"Error: {e}",style={"color":C_RED})
        return err, err, html.Div()