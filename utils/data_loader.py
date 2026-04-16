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

EXPECTED_COLS = list(COLUMN_MAP.values())   # columnas ya en español

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
    # ── El CSV puede venir con columnas en inglés O ya en español ──────────
    # Si tiene columnas en inglés → renombrar
    if any(c in df.columns for c in COLUMN_MAP):
        df = df[[c for c in COLUMN_MAP if c in df.columns]].rename(columns=COLUMN_MAP)

    # A partir de aquí todas las columnas deben estar en español
    if "anio" not in df.columns:
        raise KeyError(f"Columna 'anio' no encontrada. Columnas disponibles: {list(df.columns)}")

    df["anio"] = df["anio"].astype(str).str[:4]
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    # tipo_fraude: normalizar si viene con valores originales
    if "tipo_fraude" in df.columns:
        df["tipo_fraude"] = (
            df["tipo_fraude"]
            .map({"F": "con fraude", "_Z": "sin fraude"})
            .fillna(df["tipo_fraude"])   # si ya dice "con fraude" se queda igual
        )

    if "decimales" in df.columns:
        df["decimales"] = pd.to_numeric(df["decimales"], errors="coerce")

    if "multiplicador_unidad" in df.columns:
        df["multiplicador_unidad"] = (
            pd.to_numeric(df["multiplicador_unidad"], errors="coerce").replace(0, 1)
        )

    if "monto" in df.columns and "multiplicador_unidad" in df.columns and "decimales" in df.columns:
        df["monto_real"] = df["monto"] * (
            10.0 ** (df["multiplicador_unidad"].astype(float) - df["decimales"].astype(float))
        )
    elif "monto" in df.columns and "monto_real" not in df.columns:
        df["monto_real"] = df["monto"]   # fallback: sin transformación

    return df


def _save_parquet(df: pd.DataFrame, csv_path: str) -> None:
    try:
        pq = csv_path.replace(".csv", ".parquet")
        df.to_parquet(pq, engine="pyarrow", compression="snappy", index=False)
        print(f"[data_loader] Parquet guardado ({os.path.getsize(pq)/1024/1024:.1f} MB): {pq}")
    except Exception as e:
        print(f"[data_loader] No se pudo guardar Parquet: {e}")


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
                    df = pd.read_csv(fpath, low_memory=False)

                _df_cache = _clean(df)
                print(f"[data_loader] ✅ {len(_df_cache):,} filas | columnas: {list(_df_cache.columns)}")

                # guarda parquet para acelerar próximos arranques
                if fpath.endswith(".csv"):
                    _save_parquet(_df_cache, fpath)

                return _df_cache
            except Exception as e:
                print(f"[data_loader] ✗ {os.path.basename(fpath)}: {e}")
                continue

        print("[data_loader] ⚠ Ningún archivo válido — datos de muestra")
        _df_cache = _generate_sample_data()
        return _df_cache


def _generate_sample_data() -> pd.DataFrame:
    np.random.seed(42)
    n = 6000
    paises = ["AT","BE","BG","CY","CZ","DE","DK","EE","ES","FI","FR","GR","HR","HU",
              "IE","IT","LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK"]
    montos = np.abs(np.random.exponential(scale=5000, size=n))
    montos[np.random.random(n) < 0.217] = np.nan
    mults = np.random.choice([6, 1], size=n, p=[0.907, 0.093])
    decs  = np.random.choice([3, 2], size=n, p=[0.907, 0.093])
    df = pd.DataFrame({
        "clave":       [f"PAY.A.{paises[i%len(paises)]}.W0.TOTL.1._Z.N.PN" for i in range(n)],
        "frecuencia":  np.random.choice(["A","H","Q"],    size=n, p=[0.415,0.358,0.227]),
        "pais_origen": np.random.choice(paises,           size=n),
        "pais_destino":np.random.choice(["W0","W1","W2","DE","FR","IT","ES","NL"], size=n),
        "tipo_trx":    np.random.choice(["DD","CT0","EMP0","CHQ","CP0","SER","MREM","TOTL"], size=n),
        "tipo_psp":    np.random.choice(["1","2","_Z"],   size=n, p=[0.585,0.409,0.006]),
        "tipo_fraude": np.random.choice(["con fraude","sin fraude"], size=n, p=[0.003,0.997]),
        "unidad":      np.random.choice(["PN","EUR","XDF"], size=n, p=[0.447,0.390,0.163]),
        "anio":        np.random.choice(range(2014,2025), size=n),
        "monto":       montos,
        "tipo_monto":  np.random.choice(["A","Q","M","P","L","E"], size=n,
                                         p=[0.729,0.141,0.074,0.053,0.002,0.001]),
        "decimales":   decs,
        "descripcion": np.random.choice(["Card payments, sent","Cheques, sent",
                                          "Credit transfers, sent","Direct debits, sent",
                                          "Total payment transactions, sent","E-money payments, sent"], size=n),
        "multiplicador_unidad": mults,
    })
    df["monto_real"] = df["monto"] * (
        10.0 ** (df["multiplicador_unidad"].astype(float) - df["decimales"].astype(float))
    )
    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    return {
        "total_registros": f"{len(df):,}",
        "columnas_clave":  "14",
        "pct_nan_monto":   f"{df['monto'].isna().mean()*100:.1f}%",
        "n_paises":        str(df["pais_origen"].nunique()),
        "fraude_pct":      f"{(df['tipo_fraude']=='con fraude').mean()*100:.2f}%",
    }