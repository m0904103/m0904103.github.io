import yfinance as yf
import pandas as pd
import ta
import numpy as np

def calculate_indicators(symbol, df):
    if df.empty or len(df) < 60: return "Too small"
    close = df['Close']
    if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
    
    sma60 = ta.trend.SMAIndicator(close, window=60).sma_indicator()
    rsi = ta.momentum.RSIIndicator(close).rsi()
    macd_obj = ta.trend.MACD(close)
    macd = macd_obj.macd()
    macd_sig = macd_obj.macd_signal()
    
    latest_close = float(close.iloc[-1])
    latest_sma60 = float(sma60.iloc[-1])
    latest_rsi = float(rsi.iloc[-1])
    latest_macd = float(macd.iloc[-1])
    latest_macd_sig = float(macd_sig.iloc[-1])
    
    # Check MA5 and MA10 for short term alignment
    ma5 = close.rolling(5).mean().iloc[-1]
    ma10 = close.rolling(10).mean().iloc[-1]
    
    is_regular = latest_close > latest_sma60 and ma5 > ma10 and latest_rsi > 50 and latest_macd > latest_macd_sig
    
    print(f"{symbol}: Close={latest_close:.2f}, MA60={latest_sma60:.2f}, MA5={ma5:.2f}, MA10={ma10:.2f}, RSI={latest_rsi:.2f}, MACD={latest_macd:.2f}, MACD_Sig={latest_macd_sig:.2f}")
    print(f"Is Regular: {is_regular}")

df = yf.download("NVDA", period="1y", progress=False)
# Flatten columns
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
calculate_indicators("NVDA", df)
