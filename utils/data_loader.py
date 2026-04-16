import pandas as pd
import numpy as np
import os
import threading

COLUMN_MAP = {
    "KEY": "clave", "FREQ": "frecuencia", "REF_AREA": "pais_origen",
    "COUNT_AREA": "pais_destino", "TYP_TRNSCTN": "tipo_trx", "RL_TRNSCTN": "tipo_psp",
    "FRD_TYP": "tipo_fraude", "UNIT_MEASURE": "unidad", "TIME_PERIOD": "anio",
    "OBS_VALUE": "monto", "OBS_STATUS": "tipo_monto", "DECIMALS": "decimales",
    "TITLE": "descripcion", "UNIT_MULT": "multiplicador_unidad",
}

_BASE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_BASE)

_CANDIDATES = [
    os.path.join(_REPO, "data", "df_final.parquet"),
    os.path.join(_REPO, "data", "df_final.csv"),
    os.path.join(_REPO, "data", "payments_eu.csv"),
    os.path.join(_REPO, "data", "data_payments.csv"),
]

_df_cache = None
_lock = threading.Lock()


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # ── Renombrar SIN eliminar columnas ────────────────────────────────
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})

    # ── TIPOS OPTIMIZADOS ──────────────────────────────────────────────
    if "anio" in df.columns:
        df["anio"] = df["anio"].astype(str).str[:4]
        df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int16")

    if "monto" in df.columns:
        df["monto"] = pd.to_numeric(df["monto"], errors="coerce").astype("float32")

    if "decimales" in df.columns:
        df["decimales"] = pd.to_numeric(df["decimales"], errors="coerce").astype("float32")

    if "multiplicador_unidad" in df.columns:
        df["multiplicador_unidad"] = (
            pd.to_numeric(df["multiplicador_unidad"], errors="coerce")
            .replace(0, 1)
            .astype("float32")
        )

    # ── CATEGÓRICAS SEGURAS (solo las útiles) ──────────────────────────
    categorical_cols = [
        "frecuencia", "pais_origen", "pais_destino",
        "tipo_trx", "tipo_psp", "tipo_fraude", "unidad", "tipo_monto"
    ]

    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # ❌ NO tocar: clave, descripcion (alta cardinalidad)

    # ── NORMALIZAR FRAUDE ──────────────────────────────────────────────
    if "tipo_fraude" in df.columns:
        df["tipo_fraude"] = (
            df["tipo_fraude"]
            .map({"F": "con fraude", "_Z": "sin fraude"})
            .fillna(df["tipo_fraude"])
        )

    # ── MONTO FINAL (si no existe) ─────────────────────────────────────
    if "monto_final" not in df.columns:
        if all(c in df.columns for c in ["monto", "multiplicador_unidad", "decimales"]):
            df["monto_final"] = (
                df["monto"] *
                (10.0 ** (df["multiplicador_unidad"] - df["decimales"]))
            ).astype("float32")
        elif "monto" in df.columns:
            df["monto_final"] = df["monto"]

    return df


def _save_parquet(df: pd.DataFrame, csv_path: str):
    try:
        pq = csv_path.replace(".csv", ".parquet")
        df.to_parquet(pq, engine="pyarrow", compression="snappy", index=False)
        print(f"[data_loader] 💾 Parquet guardado: {pq}")
    except Exception as e:
        print(f"[data_loader] Error guardando parquet: {e}")


def load_data(path=None):
    global _df_cache

    if _df_cache is not None:
        return _df_cache

    with _lock:
        if _df_cache is not None:
            return _df_cache

        for fpath in ([path] if path else []) + _CANDIDATES:
            if not fpath or not os.path.exists(fpath):
                continue

            try:
                if fpath.endswith(".parquet"):
                    print(f"[data_loader] ⚡ Parquet: {fpath}")
                    df = pd.read_parquet(fpath, engine="pyarrow")
                else:
                    print(f"[data_loader] 📂 CSV: {fpath}")
                    df = pd.read_csv(fpath, low_memory=True)

                df = _clean(df)

                print(f"[data_loader] ✅ {len(df):,} filas")
                print(f"[data_loader] 💾 RAM: {df.memory_usage(deep=True).sum()/1024**2:.2f} MB")

                if fpath.endswith(".csv"):
                    _save_parquet(df, fpath)

                _df_cache = df
                return _df_cache

            except Exception as e:
                print(f"[data_loader] ✗ {os.path.basename(fpath)}: {e}")
                continue

        print("[data_loader] ⚠ fallback sample")
        _df_cache = _generate_sample_data()
        return _df_cache


def _generate_sample_data():
    np.random.seed(42)
    n = 5000

    df = pd.DataFrame({
        "clave": [f"id_{i}" for i in range(n)],
        "frecuencia": np.random.choice(["A","Q","M"], n),
        "pais_origen": np.random.choice(["DE","FR","ES"], n),
        "pais_destino": np.random.choice(["DE","FR","IT"], n),
        "tipo_trx": np.random.choice(["CT0","DD"], n),
        "tipo_psp": np.random.choice(["1","2"], n),
        "tipo_fraude": np.random.choice(["con fraude","sin fraude"], n),
        "unidad": np.random.choice(["EUR","PN"], n),
        "anio": np.random.choice(range(2018,2025), n),
        "monto": np.random.rand(n).astype("float32") * 1000,
        "tipo_monto": np.random.choice(["A","Q"], n),
        "decimales": np.zeros(n),
        "descripcion": np.random.choice(["Card","Transfer"], n),
        "multiplicador_unidad": np.ones(n),
    })

    df["monto_final"] = df["monto"]
    return df


def get_summary_stats(df: pd.DataFrame):
    return {
        "total_registros": f"{len(df):,}",
        "columnas": str(len(df.columns)),
        "pct_nan_monto": f"{df['monto'].isna().mean()*100:.1f}%",
        "n_paises": str(df["pais_origen"].nunique()),
        "fraude_pct": f"{(df['tipo_fraude']=='con fraude').mean()*100:.2f}%",
    }