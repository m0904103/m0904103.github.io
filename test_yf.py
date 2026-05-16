import yfinance as yf

INDICES = {
    "台股加權": "^TWII",
    "費城半導體": "^SOX",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "VIX (恐慌)": "^VIX"
}

for name, sym in INDICES.items():
    try:
        df = yf.download(sym, period="5d", interval="1d", progress=False)
        if not df.empty:
            print(f"{name} ({sym}): Success. Latest Close: {df['Close'].iloc[-1].values[0] if hasattr(df['Close'].iloc[-1], 'values') else df['Close'].iloc[-1]}")
        else:
            print(f"{name} ({sym}): Empty DataFrame")
    except Exception as e:
        print(f"{name} ({sym}): Failed - {e}")
