import yfinance as yf
import pandas as pd
import ta
import numpy as np

def test_stock(symbol):
    print(f"Testing {symbol}...")
    df = yf.download(symbol, period="7mo", progress=False)
    if df.empty:
        print(f"❌ {symbol} returned empty dataframe")
        return
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    close = df['Close']
    high = df['High']
    
    latest_close = float(close.iloc[-1])
    # 20-day high (excluding today)
    prev_20d_high = float(high.rolling(window=20).max().iloc[-2])
    
    is_breakout = latest_close > prev_20d_high
    
    print(f"Current Price: {latest_close}")
    print(f"20-Day High: {prev_20d_high}")
    print(f"Is Breakout? {'✅ YES' if is_breakout else '❌ NO'}")

# Test a few major TW stocks
test_stock("2330.TW")
test_stock("2454.TW")
test_stock("2603.TW")
