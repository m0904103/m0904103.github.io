import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import datetime
import gc

app = FastAPI(title="AI Global Trading Terminal v4.6.8")

# ABSOLUTE CORS PERMISSION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCK_NAMES = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達", 
    "3231.TW": "緯創", "2376.TW": "技嘉", "2308.TW": "台達電", "1513.TW": "中興電",
    "2603.TW": "長榮", "2609.TW": "陽明", "2881.TW": "富邦金", "6669.TW": "緯穎"
}

STOCKS_TW = list(STOCK_NAMES.keys())
STOCKS_US = ["AAPL","NVDA","MSFT","GOOGL","AMZN","META","TSLA","AMD","NFLX","TSM","AVGO","MU","SMCI"]

INDICES = {"台股加權": "^TWII", "費城半導體": "^SOX", "美股標普": "^GSPC", "那斯達克": "^IXIC"}

executor = ThreadPoolExecutor(max_workers=1)
full_data_cache = {} 
cached_indices_results = {}
last_update = None

def clean_dict(data):
    if isinstance(data, list): return [clean_dict(v) for v in data]
    if isinstance(data, dict): return {k: clean_dict(v) for k, v in data.items()}
    if isinstance(data, float):
        if np.isnan(data) or np.isinf(data): return 0.0
    return data

def process_stock(symbol, df):
    try:
        if df.empty or len(df) < 20: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        close, high, low = df['Close'], df['High'], df['Low']
        sma60 = ta.trend.SMAIndicator(close, window=60).sma_indicator()
        
        latest_close = float(close.iloc[-1])
        latest_sma60 = float(sma60.iloc[-1]) if not np.isnan(sma60.iloc[-1]) else latest_close
        
        atr = ta.volatility.AverageTrueRange(high, low, close).average_true_range()
        latest_atr = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else 1.0
        
        history = []
        for idx, row in df.tail(40).iterrows():
            history.append({
                "time": idx.strftime("%Y-%m-%d"),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2)
            })

        return {
            "symbol": symbol,
            "name": STOCK_NAMES.get(symbol, symbol),
            "price": round(latest_close, 2),
            "currentPrice": round(latest_close, 2),
            "change": round(((latest_close - float(close.iloc[-2])) / float(close.iloc[-2])) * 100, 2),
            "is_regular": latest_close > latest_sma60,
            "is_breakout": latest_close > float(high.rolling(window=20).max().iloc[-2]) if len(high) > 20 else False,
            "ma60": round(latest_sma60, 2),
            "entry": round(latest_close, 2),
            "stop": round(latest_close - (2 * latest_atr), 2),
            "target": round(latest_close + (3 * latest_atr), 2),
            "history": history,
            "score": 90 if latest_close > latest_sma60 else 40,
            "win_rate": 85 if latest_close > latest_sma60 else 60
        }
    except: return None

@app.on_event("startup")
async def startup_event():
    async def scanner_loop():
        global last_update
        loop = asyncio.get_event_loop()
        while True:
            for s in STOCKS_TW + STOCKS_US:
                try:
                    df = await loop.run_in_executor(executor, lambda: yf.download(s, period="7mo", progress=False, timeout=15))
                    res = process_stock(s, df)
                    if res: full_data_cache[s] = res
                    gc.collect()
                except: continue
                await asyncio.sleep(2)
            last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await asyncio.sleep(600)

    async def indices_loop():
        global cached_indices_results
        loop = asyncio.get_event_loop()
        while True:
            for name, sym in INDICES.items():
                try:
                    ticker = yf.Ticker(sym)
                    hist = await loop.run_in_executor(executor, lambda: ticker.history(period="2d"))
                    if not hist.empty:
                        c, p = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
                        cached_indices_results[name] = {"close": round(c, 2), "change": round(((c-p)/p)*100, 2)}
                except: continue
            await asyncio.sleep(60)

    asyncio.create_task(scanner_loop())
    asyncio.create_task(indices_loop())

@app.get("/")
def read_root():
    return JSONResponse(content={"status": "AI TRADER v4.6.8 ULTIMATE", "update": last_update})

@app.get("/scan")
def get_scan():
    tw = [v for k, v in full_data_cache.items() if k.endswith(".TW")]
    us = [v for k, v in full_data_cache.items() if not k.endswith(".TW")]
    return JSONResponse(content=clean_dict({"tw": tw, "us": us}))

@app.get("/market/active")
def get_active():
    active = [v for k, v in full_data_cache.items() if v.get("is_breakout")]
    return JSONResponse(content=clean_dict(active))

@app.get("/sentiment")
def get_sentiment():
    total = len(full_data_cache)
    bulls = len([v for v in full_data_cache.values() if v.get("is_regular")])
    ratio = round((bulls / total * 100), 1) if total > 0 else 50
    return JSONResponse(content=clean_dict({
        "value": ratio, 
        "sentiment": "Greed" if ratio > 60 else ("Fear" if ratio < 40 else "Neutral"),
        "bull_count": bulls, "bear_count": total - bulls, "total": total
    }))

@app.get("/indices")
def get_indices():
    return JSONResponse(content=clean_dict(cached_indices_results))

@app.get("/history/{symbol}")
def get_history(symbol: str):
    sym = symbol.upper()
    if sym.isdigit() and not sym.endswith(".TW"): sym += ".TW"
    if sym in full_data_cache:
        return JSONResponse(content=clean_dict(full_data_cache[sym].get("history", [])))
    raise HTTPException(status_code=404, detail="Not in cache")

@app.get("/diagnose/{symbol}")
def diagnose(symbol: str):
    sym = symbol.upper()
    if sym.isdigit() and not sym.endswith(".TW"): sym += ".TW"
    if sym in full_data_cache:
        return JSONResponse(content=clean_dict(full_data_cache[sym]))
    raise HTTPException(status_code=404, detail="Not in cache")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
