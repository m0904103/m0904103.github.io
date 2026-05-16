import yfinance as yf
import pandas as pd
import numpy as np

INDICES = {
    "台股加權": "^TWII",
    "費城半導體": "^SOX",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "VIX (恐慌)": "^VIX"
}

index_syms = list(INDICES.values())
df_indices = yf.download(index_syms, period="5d", interval="1d", group_by='ticker', progress=False)

print(df_indices.columns)
for name, sym in INDICES.items():
    if sym in df_indices:
        df_sym = df_indices[sym].dropna(subset=['Close'])
        print(f"{sym}: length={len(df_sym)}")
    else:
        print(f"{sym} not in df_indices")
