import os
import threading
import urllib.request

import duckdb
import numpy as np
import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN — EDITA ESTO
# ══════════════════════════════════════════════════════════════════════════════

# Opción A: variable de entorno (recomendado en Render → Environment)
# Opción B: pega la URL directamente como fallback del os.environ.get
PARQUET_URL = os.environ.get(
    "PARQUET_URL",
    "https://github.com/T1fff/PaymentTransactionsEUDashPy/releases/download/listo/df_final.parquet"
)

_BASE          = os.path.dirname(os.path.abspath(__file__))
_REPO          = os.path.dirname(os.path.dirname(_BASE))   # sube 2 niveles desde utils/
LOCAL_PARQUET  = "/tmp/df_final.parquet"
LOCAL_FALLBACK = os.path.join(_REPO, "data", "df_final.parquet")
LOCAL_CSV      = os.path.join(_REPO, "data", "df_final.csv")

# ══════════════════════════════════════════════════════════════════════════════
# MAPEO DE COLUMNAS
# ══════════════════════════════════════════════════════════════════════════════
COLUMN_MAP = {
    "KEY": "clave", "FREQ": "frecuencia", "REF_AREA": "pais_origen",
    "COUNT_AREA": "pais_destino", "TYP_TRNSCTN": "tipo_trx", "RL_TRNSCTN": "tipo_psp",
    "FRD_TYP": "tipo_fraude", "UNIT_MEASURE": "unidad", "TIME_PERIOD": "anio",
    "OBS_VALUE": "monto", "OBS_STATUS": "tipo_monto", "DECIMALS": "decimales",
    "TITLE": "descripcion", "UNIT_MULT": "multiplicador_unidad",
}

# ══════════════════════════════════════════════════════════════════════════════
# ESTADO INTERNO
# ══════════════════════════════════════════════════════════════════════════════
_lock               = threading.Lock()
_con                = None   # DuckDB connection singleton
_parquet_path       = None   # ruta al parquet en disco
_df_cache           = None   # DataFrame cacheado (tipado optimizado)


# ══════════════════════════════════════════════════════════════════════════════
# PASO 1 — Garantizar parquet en disco
# ══════════════════════════════════════════════════════════════════════════════
def _ensure_parquet() -> str:
    global _parquet_path

    if _parquet_path and os.path.exists(_parquet_path):
        return _parquet_path

    # Buscar candidatos locales
    for candidate in [LOCAL_PARQUET, LOCAL_FALLBACK]:
        if os.path.exists(candidate):
            print(f"[data_loader] ✅ Parquet local encontrado: {candidate}")
            _parquet_path = candidate
            return _parquet_path

    # Convertir CSV local si existe
    if os.path.exists(LOCAL_CSV):
        print("[data_loader] 🔄 Convirtiendo CSV → Parquet...")
        try:
            df = pd.read_csv(LOCAL_CSV, low_memory=True)
            df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})
            if "tipo_fraude" in df.columns:
                df["tipo_fraude"] = df["tipo_fraude"].map(
                    {"F": "con fraude", "_Z": "sin fraude"}
                ).fillna(df["tipo_fraude"])
            if "monto_final" not in df.columns and "monto" in df.columns:
                mult = pd.to_numeric(df.get("multiplicador_unidad", 1), errors="coerce").replace(0, 1)
                dec  = pd.to_numeric(df.get("decimales", 0), errors="coerce").fillna(0)
                df["monto_final"] = (df["monto"] * (10.0 ** (mult - dec))).astype("float32")
            df["monto_real"] = df.get("monto_final", df.get("monto", 0))
            os.makedirs(os.path.dirname(LOCAL_FALLBACK), exist_ok=True)
            df.to_parquet(LOCAL_FALLBACK, index=False, engine="pyarrow", compression="snappy")
            print(f"[data_loader] ✅ Parquet guardado: {LOCAL_FALLBACK}")
            _parquet_path = LOCAL_FALLBACK
            return _parquet_path
        except Exception as e:
            print(f"[data_loader] ⚠️  Error convirtiendo CSV: {e}")

    # Descargar desde URL remota
    print(f"[data_loader] ⬇️  Descargando desde URL remota...")
    try:
        urllib.request.urlretrieve(PARQUET_URL, LOCAL_PARQUET)
        print(f"[data_loader] ✅ Descargado: {LOCAL_PARQUET}")
        _parquet_path = LOCAL_PARQUET
        return _parquet_path
    except Exception as e:
        print(f"[data_loader] ⚠️  Descarga fallida: {e}")

    # Fallback: muestra sintética
    print("[data_loader] ⚠️  Usando datos de muestra")
    sample_path = "/tmp/sample_data.parquet"
    _generate_sample_data().to_parquet(sample_path, index=False)
    _parquet_path = sample_path
    return _parquet_path


# ══════════════════════════════════════════════════════════════════════════════
# PASO 2 — Conexión DuckDB (para la vista 'payments' sin cargar RAM)
# ══════════════════════════════════════════════════════════════════════════════
def get_con() -> duckdb.DuckDBPyConnection:
    """
    Devuelve la conexión DuckDB con la vista 'payments'.
    Úsala en callbacks nuevos para evitar cargar el df completo:

        from utils.data_loader import get_con
        df_resultado = get_con().execute(
            "SELECT anio, SUM(monto_final) as total FROM payments GROUP BY anio"
        ).df()
    """
    global _con

    if _con is not None:
        return _con

    with _lock:
        if _con is not None:
            return _con

        path = _ensure_parquet()
        _con = duckdb.connect(database=":memory:")

        # Detectar columnas del parquet
        raw_cols = _con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{path}') LIMIT 0"
        ).df()["column_name"].tolist()

        # Construir SELECT con renombramiento
        renames  = {k: v for k, v in COLUMN_MAP.items() if k in raw_cols}
        parts    = [f'"{old}" AS "{new}"' for old, new in renames.items()]
        parts   += [f'"{c}"' for c in raw_cols if c not in renames]
        select   = ", ".join(parts) if parts else "*"

        _con.execute(
            f"CREATE VIEW payments AS SELECT {select} FROM read_parquet('{path}')"
        )

        # Asegurar columna monto_real
        view_cols = _con.execute("DESCRIBE payments").df()["column_name"].tolist()
        if "monto_real" not in view_cols:
            src = "monto_final" if "monto_final" in view_cols else "monto"
            _con.execute(
                f"CREATE OR REPLACE VIEW payments AS "
                f"SELECT {select}, {src} AS monto_real FROM read_parquet('{path}')"
            )

        print("[data_loader] ✅ DuckDB listo — vista 'payments' disponible")
        return _con


# ══════════════════════════════════════════════════════════════════════════════
# PASO 3 — load_data(): compatibilidad total con código existente
# ══════════════════════════════════════════════════════════════════════════════
def load_data(path=None) -> pd.DataFrame:
    """
    Carga el DataFrame completo UNA SOLA VEZ con tipos optimizados.

    Compatible con TODO el código existente:
      - multivariado.py → _render_barras: pd.crosstab(df[var], df["tipo_fraude"])
      - univariado.py   → _render_monto:  df[df["unidad"]=="PN"]["monto_real"]
      - univariado.py   → _render_indicativa: df[var].value_counts()
      - univariado.py   → _render_stats_monto: df["monto"].isna()

    RAM estimada con tipos optimizados: ~80–120 MB
    (el DataFrame sin optimizar sería ~400–600 MB)
    """
    global _df_cache

    if _df_cache is not None:
        return _df_cache

    with _lock:
        if _df_cache is not None:
            return _df_cache

        parquet_path = _ensure_parquet()

        print("[data_loader] 📂 Cargando DataFrame optimizado en RAM...")
        try:
            # Usar DuckDB para leer y castear en una sola pasada (más eficiente que pandas)
            tmp_con = duckdb.connect(":memory:")

            # Detectar columnas disponibles
            raw_cols = tmp_con.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{parquet_path}') LIMIT 0"
            ).df()["column_name"].tolist()

            # Construir proyección solo con columnas que existen
            def col(name):
                """Devuelve el nombre real de la columna (original o renombrada)."""
                # Buscar si existe en el parquet con nombre original o ya renombrado
                orig = {v: k for k, v in COLUMN_MAP.items()}.get(name, name)
                if name in raw_cols:
                    return f'"{name}"'
                elif orig in raw_cols:
                    return f'"{orig}"'
                return None

            def safe_cast(expr, dtype, alias):
                if expr is None:
                    return f"NULL AS {alias}"
                return f"CAST({expr} AS {dtype}) AS {alias}"

            # Mapear columnas con sus tipos destino
            cols_sql = [
                safe_cast(col("frecuencia"),           "VARCHAR", "frecuencia"),
                safe_cast(col("pais_origen"),           "VARCHAR", "pais_origen"),
                safe_cast(col("pais_destino"),          "VARCHAR", "pais_destino"),
                safe_cast(col("tipo_trx"),              "VARCHAR", "tipo_trx"),
                safe_cast(col("tipo_psp"),              "VARCHAR", "tipo_psp"),
                # tipo_fraude: normalizar F→con fraude, _Z→sin fraude
                (
                    "CASE "
                    "WHEN tipo_fraude='F'  THEN 'con fraude' "
                    "WHEN tipo_fraude='_Z' THEN 'sin fraude' "
                    "ELSE tipo_fraude END AS tipo_fraude"
                    if col("tipo_fraude") else "NULL AS tipo_fraude"
                ),
                safe_cast(col("unidad"),                "VARCHAR", "unidad"),
                safe_cast(col("tipo_monto"),            "VARCHAR", "tipo_monto"),
                safe_cast(col("decimales"),             "FLOAT",   "decimales"),
                safe_cast(col("descripcion"),           "VARCHAR", "descripcion"),
                safe_cast(col("monto"),                 "FLOAT",   "monto"),
                safe_cast(col("monto_final"),           "FLOAT",   "monto_final"),
                # monto_real = monto_final si existe, sino monto
                (
                    "CAST(monto_final AS FLOAT) AS monto_real"
                    if col("monto_final") else
                    "CAST(monto AS FLOAT) AS monto_real"
                ),
                safe_cast(col("multiplicador_unidad"), "FLOAT", "multiplicador_unidad"),
            ]

            sql = f"SELECT {', '.join(cols_sql)} FROM read_parquet('{parquet_path}')"
            _df_cache = tmp_con.execute(sql).df()
            tmp_con.close()

        except Exception as e:
            print(f"[data_loader] ⚠️  Error: {e} — usando muestra")
            _df_cache = _generate_sample_data()

        # Convertir a categorical para reducir RAM en columnas de baja cardinalidad
        for col_name in ["frecuencia", "pais_origen", "pais_destino", "tipo_trx",
                         "tipo_psp", "tipo_fraude", "unidad", "tipo_monto"]:
            if col_name in _df_cache.columns:
                _df_cache[col_name] = _df_cache[col_name].astype("category")

        ram_mb = _df_cache.memory_usage(deep=True).sum() / 1024 ** 2
        print(f"[data_loader] ✅ Listo: {len(_df_cache):,} filas | {ram_mb:.1f} MB RAM")
        return _df_cache


# ══════════════════════════════════════════════════════════════════════════════
# query() — función nueva para callbacks futuros sin tocar RAM
# ══════════════════════════════════════════════════════════════════════════════
def query(sql: str, params: list = None) -> pd.DataFrame:
    """
    Ejecuta SQL sobre el dataset completo SIN cargarlo en RAM.

    Tabla: 'payments' — columnas ya renombradas al español.

    Ejemplo:
        from utils.data_loader import query
        df = query(
            "SELECT anio, COUNT(*) as n FROM payments WHERE pais_origen=? GROUP BY anio",
            ["DE"]
        )
    """
    return get_con().execute(sql, params or []).df()


# ══════════════════════════════════════════════════════════════════════════════
# get_summary_stats() — misma firma que antes
# ══════════════════════════════════════════════════════════════════════════════
def get_summary_stats(df: pd.DataFrame = None) -> dict:
    """Compatible con el código existente. El parámetro df se ignora."""
    try:
        row = get_con().execute("""
            SELECT
                COUNT(*)                                                      AS total_registros,
                COUNT(DISTINCT pais_origen)                                   AS n_paises,
                AVG(CASE WHEN monto IS NULL THEN 1.0 ELSE 0.0 END) * 100     AS pct_nan_monto,
                AVG(CASE WHEN tipo_fraude IN ('con fraude','F')
                         THEN 1.0 ELSE 0.0 END) * 100                        AS fraude_pct
            FROM payments
        """).df().iloc[0]
        return {
            "total_registros": f"{int(row['total_registros']):,}",
            "columnas":        "14",
            "pct_nan_monto":   f"{row['pct_nan_monto']:.1f}%",
            "n_paises":        str(int(row['n_paises'])),
            "fraude_pct":      f"{row['fraude_pct']:.2f}%",
        }
    except Exception:
        return {
            "total_registros": "662,616",
            "columnas": "14",
            "pct_nan_monto": "21.7%",
            "n_paises": "29",
            "fraude_pct": "0.29%",
        }


# ══════════════════════════════════════════════════════════════════════════════
# Datos de muestra (fallback)
# ══════════════════════════════════════════════════════════════════════════════
def _generate_sample_data() -> pd.DataFrame:
    np.random.seed(42)
    n = 5_000
    monto = np.random.rand(n).astype("float32") * 1000
    df = pd.DataFrame({
        "frecuencia":           pd.Categorical(np.random.choice(["A", "H", "Q"], n, p=[0.415, 0.358, 0.227])),
        "pais_origen":          pd.Categorical(np.random.choice(["DE", "FR", "ES", "PL", "RO"], n)),
        "pais_destino":         pd.Categorical(np.random.choice(["W0", "W1", "W2", "G1", "DE"], n)),
        "tipo_trx":             pd.Categorical(np.random.choice(["CT0", "DD", "EMP0", "CHQ", "CP0"], n)),
        "tipo_psp":             pd.Categorical(np.random.choice(["1", "2", "_Z"], n, p=[0.585, 0.409, 0.006])),
        "tipo_fraude":          pd.Categorical(np.random.choice(["con fraude", "sin fraude"], n, p=[0.003, 0.997])),
        "unidad":               pd.Categorical(np.random.choice(["PN", "EUR", "XDF"], n, p=[0.447, 0.39, 0.163])),
        "tipo_monto":           pd.Categorical(np.random.choice(["A", "Q", "M", "P"], n, p=[0.729, 0.141, 0.074, 0.056])),
        "decimales":            np.random.choice([2.0, 3.0], n, p=[0.093, 0.907]).astype("float32"),
        "descripcion":          np.random.choice(["Card payments, sent", "Cheques, sent", "Credit transfers, sent"], n),
        "monto":                monto,
        "monto_final":          monto,
        "monto_real":           monto,
        "multiplicador_unidad": np.random.choice([1.0, 1_000_000.0], n, p=[0.093, 0.907]).astype("float32"),
    })
    return df