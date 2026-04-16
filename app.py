import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
from flask_caching import Cache

# ── App ────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "FraudLens EU · Analytics"

# ── Flask-Caching (SimpleCache = RAM, sin dependencias externas) ───────────
cache = Cache(app.server, config={
    "CACHE_TYPE":            "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 600,      # 10 min antes de invalidar
})

# Exportamos cache para que data_loader pueda usarlo si se quiere
app.cache = cache

# ── Navbar ─────────────────────────────────────────────────────────────────
NAV_PAGES = [
    {"path": "/",             "name": "Introducción"},
    {"path": "/objetivos",    "name": "Objetivos"},
    {"path": "/problema",     "name": "Problema"},
    {"path": "/univariado",   "name": "EDA Univariado"},
    {"path": "/multivariado", "name": "EDA Multivariado"},
    {"path": "/conclusiones", "name": "Conclusiones"},
]

def build_navbar(current_path: str = "/") -> html.Nav:
    links = []
    for i, page in enumerate(NAV_PAGES):
        active = current_path.rstrip("/") == page["path"].rstrip("/")
        links.append(
            html.A(page["name"], href=page["path"],
                   className=f"nav-link {'active' if active else ''}")
        )
        if i == 2:
            links.append(html.Div(className="nav-divider"))

    return html.Nav(className="navbar", children=[
        html.A(className="nav-logo", href="/", children=[
            html.Div("🛡", className="nav-logo-icon"),
            html.Div("FraudLens EU", className="nav-logo-name"),
        ]),
        *links,
        html.Div("BCE · Datos de Pago", className="nav-badge"),
    ])

# ── Layout (sin sleep, sin carga de datos aquí) ────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="navbar-container"),
    dash.page_container,
])

@callback(Output("navbar-container", "children"), Input("url", "pathname"))
def update_navbar(pathname: str) -> html.Nav:
    return build_navbar(pathname or "/")

# ── WSGI server export ─────────────────────────────────────────────────────
server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8051)