import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import urllib.request
import json
import datetime
import gc

app = FastAPI(title="AI Stock Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCK_NAMES = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達", 
    "3231.TW": "緯創", "2376.TW": "技嘉", "2308.TW": "台達電", "1513.TW": "中興電",
    "1519.TW": "華城", "1503.TW": "士電", "2603.TW": "長榮", "2609.TW": "陽明",
    "2303.TW": "聯電", "2408.TW": "南亞科", "3443.TW": "創意", "3035.TW": "智原",
    "3661.TW": "世芯-KY", "2379.TW": "瑞昱", "3017.TW": "奇鋐", "2882.TW": "國泰金",
    "2881.TW": "富邦金", "2357.TW": "華碩", "6669.TW": "緯穎", "2353.TW": "宏碁",
    "2324.TW": "仁寶", "3037.TW": "欣興", "2409.TW": "友達", "3481.TW": "群創",
    "0050.TW": "元大台灣50", "0056.TW": "元大高股息", "00878.TW": "國泰永續高股息"
}

STOCKS_TW = list(STOCK_NAMES.keys())
STOCKS_US = [
    "AAPL","NVDA","MSFT","GOOGL","AMZN","META","TSLA","JPM","JNJ",
    "AMD","NFLX","ADBE","CRM","PYPL","V","UNH","XOM","ORCL","MA","XLE",
    "QQQ","SPY","SMH","SOXX","LLY","PLTR","TSM","AVGO","MU","DELL",
    "MARA","MSTR","IGV","MGV","DXYZ","XOVR","SARK","VTI","VGT","VOO","ASML",
    "FTNT", "SOFI", "HOOD", "COIN", "SMCI", "RIVN", "LCID", "GME", "AMC",
    "DJT", "RDDT", "ALAB", "ARM", "APP", "CVNA", "AFRM", "UPST"
]

INDICES = {
    "台股加權": "^TWII",
    "台指期 (領先指標)": "NQ=F",
    "費城半導體": "^SOX",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "VIX (恐慌)": "^VIX"
}

executor = ThreadPoolExecutor(max_workers=2)
cached_scan_results_tw = []
cached_scan_results_us = []
cached_indices_results = {}
cached_turtle_us = []
cached_fear_greed = {"value": 50, "sentiment": "Neutral"}
last_update = None

def flatten_yf_df(df):
    if df.empty: return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def fetch_fear_greed():
    try:
        url = "https://edition.cnn.com/markets/fear-and-greed"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }
        r = requests.get(url, headers=headers, timeout=10)
        import re
        match = re.search(r'score":([\d\.]+)', r.text)
        if not match:
            match = re.search(r'fear-greed-score="([\d\.]+)"', r.text)
        
        if match:
            val = int(float(match.group(1)))
            sent = "Neutral"
            if val < 25: sent = "Extreme Fear"
            elif val < 45: sent = "Fear"
            elif val > 75: sent = "Extreme Greed"
            elif val > 55: sent = "Greed"
            return {"value": val, "sentiment": sent}
    except: pass
    return {"value": 50, "sentiment": "Neutral"}

def clean_dict(data):
    if isinstance(data, list):
        return [clean_dict(v) for v in data]
    if isinstance(data, dict):
        return {k: clean_dict(v) for k, v in data.items()}
    if isinstance(data, float):
        if np.isnan(data) or np.isinf(data): return 0.0
    return data

def calculate_indicators(symbol: str, df: pd.DataFrame) -> Dict:
    try:
        if df.empty or len(df) < 60: return None
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        rsi = ta.momentum.RSIIndicator(close).rsi()
        macd_obj = ta.trend.MACD(close)
        macd_series = macd_obj.macd()
        macd_signal_series = macd_obj.macd_signal()
        sma60 = ta.trend.SMAIndicator(close, window=60).sma_indicator()
        stoch = ta.momentum.StochasticOscillator(high, low, close)
        k_series = stoch.stoch()
        d_series = stoch.stoch_signal()

        latest_close = float(close.iloc[-1])
        latest_sma60 = float(sma60.iloc[-1]) if not np.isnan(sma60.iloc[-1]) else latest_close
        latest_k = float(k_series.iloc[-1])
        latest_d = float(d_series.iloc[-1])
        latest_rsi = float(rsi.iloc[-1])
        latest_macd = float(macd_series.iloc[-1])
        latest_macd_sig = float(macd_signal_series.iloc[-1])
        
        is_regular = latest_close > latest_sma60
        strength = 0
        reasons = []
        
        if is_regular: 
            strength += 40
            reasons.append("正規軍(站穩季線)")
        else:
            reasons.append("非正規軍(季線之下)")
            
        if latest_k > latest_d: 
            strength += 20
            reasons.append("KD金叉")
        if latest_rsi > 50: 
            strength += 20
            reasons.append("RSI強勢")
        if latest_macd > latest_macd_sig: 
            strength += 20
            reasons.append("MACD多頭")
        
        try:
            prev_close = float(close.iloc[-2])
            change = ((latest_close - prev_close) / prev_close) * 100
        except: change = 0

        win_rate = 60
        if is_regular: win_rate += 10
        if latest_k > latest_d: win_rate += 10
        if latest_rsi > 50: win_rate += 10
        if latest_macd > latest_macd_sig: win_rate += 10

        return {
            "symbol": symbol,
            "name": STOCK_NAMES.get(symbol, symbol),
            "price": round(latest_close, 2),
            "change": round(change, 2),
            "rsi": round(latest_rsi, 1),
            "score": strength,
            "is_regular": is_regular,
            "reasons": " | ".join(reasons),
            "signal": "Buy" if strength >= 80 else ("Sell" if strength <= 40 else "Neutral"),
            "win_rate": win_rate
        }
    except: return None

def calculate_turtle_strategy(symbol, df):
    try:
        if df.empty or len(df) < 60: return None
        close = df['Close']
        high_20 = df['High'].rolling(window=20).max()
        low_10 = df['Low'].rolling(window=10).min()
        atr = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
        
        latest_close = float(close.iloc[-1])
        prev_high_20 = float(high_20.iloc[-2])
        prev_low_10 = float(low_10.iloc[-2])
        latest_atr = float(atr.iloc[-1])
        
        is_breakout = latest_close > prev_high_20
        signal = "觀察中"
        if is_breakout: signal = "🚀 突破進場"
        elif latest_close < prev_low_10: signal = "🛑 止損/出場"
        
        stop_loss = latest_close - (2 * latest_atr)
        target_price = latest_close + (3 * latest_atr)
        
        try:
            prev_close = float(close.iloc[-2])
            change = ((latest_close - prev_close) / prev_close) * 100
        except: change = 0

        return {
            "symbol": symbol,
            "name": STOCK_NAMES.get(symbol, symbol),
            "price": round(latest_close, 2),
            "change": round(change, 2),
            "score": 90 if is_breakout else 50,
            "advice": signal,
            "entry": round(latest_close, 2),
            "stop": round(stop_loss, 2),
            "target": round(target_price, 2),
            "win_rate": 85 if is_breakout else 60
        }
    except: return None

@app.on_event("startup")
async def startup_event():
    async def scan_tw():
        global cached_scan_results_tw
        executor_tw = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        while True:
            for s in STOCKS_TW:
                try:
                    df = await loop.run_in_executor(executor_tw, lambda: yf.download(s, period="7mo", interval="1d", progress=False, timeout=10))
                    df = flatten_yf_df(df)
                    if df.empty: continue
                    res = calculate_indicators(s, df)
                    if res:
                        cached_scan_results_tw = [r for r in cached_scan_results_tw if r['symbol'] != res['symbol']] + [res]
                except: continue
                await asyncio.sleep(3)
            await asyncio.sleep(300)

    async def scan_us():
        global cached_scan_results_us, cached_turtle_us, last_update
        executor_us = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        while True:
            for s in STOCKS_US:
                try:
                    df = await loop.run_in_executor(executor_us, lambda: yf.download(s, period="7mo", interval="1d", progress=False, timeout=10))
                    df = flatten_yf_df(df)
                    if df.empty: continue
                    res = calculate_indicators(s, df)
                    if res:
                        cached_scan_results_us = [r for r in cached_scan_results_us if r['symbol'] != res['symbol']] + [res]
                    res_turtle = calculate_turtle_strategy(s, df)
                    if res_turtle:
                        cached_turtle_us = [r for r in cached_turtle_us if r['symbol'] != res_turtle['symbol']] + [res_turtle]
                except: continue
                await asyncio.sleep(0.1)
            last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            gc.collect()
            await asyncio.sleep(300)

    async def update_indices():
        global cached_indices_results, cached_fear_greed
        executor_idx = ThreadPoolExecutor(max_workers=2)
        loop = asyncio.get_event_loop()
        while True:
            cached_fear_greed = fetch_fear_greed()
            for name, sym in INDICES.items():
                try:
                    ticker = yf.Ticker(sym)
                    hist = await loop.run_in_executor(executor_idx, lambda: ticker.history(period="2d"))
                    if not hist.empty:
                        c, p = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
                        cached_indices_results[name] = {"close": round(c, 2), "change": round(((c-p)/p)*100, 2), "signal": "Buy" if c>=p else "Sell"}
                except: continue
            await asyncio.sleep(60)

    asyncio.create_task(scan_tw())
    asyncio.create_task(scan_us())
    asyncio.create_task(update_indices())

@app.get("/")
def read_root():
    return {"status": "AI TRADER API ONLINE", "version": "v3.8.7", "update": last_update}

@app.get("/scan")
def get_scan():
    return clean_dict({"tw": cached_scan_results_tw, "us": cached_scan_results_us})

@app.get("/market/active")
def get_active():
    return clean_dict(cached_turtle_us)

@app.get("/indices")
def get_indices():
    return clean_dict(cached_indices_results)

@app.get("/sentiment")
def get_sentiment():
    return clean_dict(cached_fear_greed)

@app.get("/diagnose/{symbol}")
def diagnose(symbol: str):
    try:
        ticker_sym = symbol.upper()
        if not (ticker_sym.endswith(".TW") or any(char.isalpha() for char in ticker_sym)):
            if not ticker_sym.endswith(".TW"): ticker_sym += ".TW"
        df = yf.download(ticker_sym, period="7mo", progress=False)
        df = flatten_yf_df(df)
        if df.empty: raise HTTPException(status_code=404, detail="Symbol not found")
        res = calculate_indicators(ticker_sym, df)
        if not res: raise HTTPException(status_code=500, detail="Calculation failed")
        close = df['Close']
        sma60 = ta.trend.SMAIndicator(close, window=60).sma_indicator()
        res["ma60"] = round(float(sma60.iloc[-1]), 2) if not np.isnan(sma60.iloc[-1]) else res["price"]
        return clean_dict(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
