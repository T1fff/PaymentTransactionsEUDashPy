import duckdb
import pandas as pd
import os
import threading

_DB = None
_df_cache = None
_lock = threading.Lock()

def get_conn():
    global _DB
    if _DB is None:
        _DB = duckdb.connect(database=':memory:')
    return _DB


def load_data():
    global _df_cache

    if _df_cache is not None:
        return _df_cache

    with _lock:
        if _df_cache is not None:
            return _df_cache

        conn = get_conn()

        base = os.path.dirname(os.path.abspath(__file__))
        repo = os.path.dirname(base)

        path = os.path.join(repo, "data", "df_final.csv")

        print(f"[duckdb] leyendo: {path}")

        try:
            df = conn.execute(f"""
                SELECT 
                    *,
                    
                    -- FIX CRÍTICO: sobreescribir columnas correctamente
                    CAST(SUBSTR(CAST(anio AS VARCHAR), 1, 4) AS INTEGER) AS anio,
                    
                    CASE 
                        WHEN tipo_fraude = 'F' THEN 'con fraude'
                        WHEN tipo_fraude = '_Z' THEN 'sin fraude'
                        ELSE tipo_fraude
                    END AS tipo_fraude,

                    CAST(
                        monto * POWER(10, multiplicador_unidad - decimales)
                    AS FLOAT) AS monto_final

                FROM read_csv_auto('{path}', HEADER=TRUE)
            """).fetch_df()

            # 🔥 FIX PRINCIPAL: asegurar nombres correctos
            df.columns = [c.lower() for c in df.columns]

            # ── convertir categóricas ──
            categorical_cols = [
                "frecuencia","pais_origen","pais_destino",
                "tipo_trx","tipo_psp","tipo_fraude","unidad","tipo_monto"
            ]

            for col in categorical_cols:
                if col in df.columns:
                    df[col] = df[col].astype("category")

            print(f"[data_loader] columnas: {list(df.columns)}")
            print(f"[data_loader] ✅ {len(df):,} filas")
            print(f"[data_loader] 💾 RAM: {df.memory_usage(deep=True).sum()/1024**2:.2f} MB")

            _df_cache = df
            return _df_cache

        except Exception as e:
            print(f"[data_loader] error: {e}")
            return pd.DataFrame()