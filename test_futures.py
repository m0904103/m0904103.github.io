import yfinance as yf
symbols = ["WTX=F", "FITX.TW", "^TWII", "TX=F"]
for sym in symbols:
    try:
        t = yf.Ticker(sym)
        h = t.history(period="1d")
        if not h.empty:
            print(f"{sym}: {h['Close'].iloc[-1]}")
        else:
            print(f"{sym}: Empty")
    except Exception as e:
        print(f"{sym}: Error {e}")
