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
from typing import List, Dict
import json
import datetime
import gc

app = FastAPI(title="AI Stock Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_FILE = "last_market_state.json"
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
full_data_cache = {} 
cached_indices_results = {}
cached_fear_greed = {"value": 50, "sentiment": "Neutral"}
last_update = None

def save_cache():
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                "data": full_data_cache,
                "update": last_update,
                "indices": cached_indices_results
            }, f)
    except: pass

def load_cache():
    global full_data_cache, last_update, cached_indices_results
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                content = json.load(f)
                full_data_cache = content.get("data", {})
                last_update = content.get("update", "")
                cached_indices_results = content.get("indices", {})
        except: pass

def flatten_yf_df(df):
    if df.empty: return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def fetch_fear_greed():
    try:
        url = "https://edition.cnn.com/markets/fear-and-greed"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        import re
        match = re.search(r'score":([\d\.]+)', r.text)
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
    if isinstance(data, list): return [clean_dict(v) for v in data]
    if isinstance(data, dict): return {k: clean_dict(v) for k, v in data.items()}
    if isinstance(data, float):
        if np.isnan(data) or np.isinf(data): return 0.0
    return data

def process_stock(symbol, df):
    try:
        if df.empty or len(df) < 60: return None
        df = flatten_yf_df(df)
        close, high, low = df['Close'], df['High'], df['Low']
        sma60 = ta.trend.SMAIndicator(close, window=60).sma_indicator()
        latest_close = float(close.iloc[-1])
        latest_sma60 = float(sma60.iloc[-1]) if not np.isnan(sma60.iloc[-1]) else latest_close
        atr = ta.volatility.AverageTrueRange(high, low, close).average_true_range()
        latest_atr = float(atr.iloc[-1])
        
        history = []
        for idx, row in df.tail(60).iterrows():
            history.append({
                "time": idx.strftime("%Y-%m-%d"),
                "date": idx.strftime("%Y-%m-%d"),
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
            "is_breakout": latest_close > float(high.rolling(window=20).max().iloc[-2]),
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
    load_cache()
    async def background_scanner():
        global last_update
        loop = asyncio.get_event_loop()
        while True:
            for s in STOCKS_TW + STOCKS_US:
                try:
                    df = await loop.run_in_executor(executor, lambda: yf.download(s, period="7mo", progress=False, timeout=10))
                    res = process_stock(s, df)
                    if res:
                        full_data_cache[s] = res
                        save_cache()
                except: continue
                await asyncio.sleep(0.5)
            last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_cache()
            gc.collect()
            await asyncio.sleep(300)

    async def update_indices():
        global cached_indices_results, cached_fear_greed
        loop = asyncio.get_event_loop()
        while True:
            cached_fear_greed = fetch_fear_greed()
            for name, sym in INDICES.items():
                try:
                    ticker = yf.Ticker(sym)
                    hist = await loop.run_in_executor(executor, lambda: ticker.history(period="2d"))
                    if not hist.empty:
                        c, p = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
                        cached_indices_results[name] = {"close": round(c, 2), "change": round(((c-p)/p)*100, 2)}
                except: continue
            save_cache()
            await asyncio.sleep(60)

    asyncio.create_task(background_scanner())
    asyncio.create_task(update_indices())

@app.get("/")
def read_root():
    return JSONResponse(content={"status": "AI TRADER v4.4.0 ONLINE", "update": last_update}, headers={"Access-Control-Allow-Origin": "*"})

@app.get("/scan")
def get_scan():
    tw = [v for k, v in full_data_cache.items() if k.endswith(".TW")]
    us = [v for k, v in full_data_cache.items() if not k.endswith(".TW")]
    return clean_dict({"tw": tw, "us": us})

@app.get("/market/active")
def get_active():
    active = [v for k, v in full_data_cache.items() if v.get("is_breakout")]
    return clean_dict(active)

@app.get("/sentiment")
def get_sentiment():
    bull_count = len([v for v in full_data_cache.values() if v.get("is_regular")])
    total = len(full_data_cache)
    sentiment_score = round((bull_count / total * 100), 1) if total > 0 else 50
    return clean_dict({
        "value": cached_fear_greed.get("value", 50),
        "sentiment": cached_fear_greed.get("sentiment", "Neutral"),
        "bull_ratio": sentiment_score,
        "bull_count": bull_count,
        "bear_count": total - bull_count,
        "total": total
    })

@app.get("/history/{symbol}")
def get_history(symbol: str):
    ticker_sym = symbol.upper()
    if ticker_sym.isdigit() and not ticker_sym.endswith(".TW"): ticker_sym += ".TW"
    if ticker_sym in full_data_cache:
        return clean_dict(full_data_cache[ticker_sym]["history"])
    raise HTTPException(status_code=404, detail="History not ready.")

@app.get("/diagnose/{symbol}")
def diagnose(symbol: str):
    ticker_sym = symbol.upper()
    if ticker_sym.isdigit() and not ticker_sym.endswith(".TW"): ticker_sym += ".TW"
    if ticker_sym in full_data_cache:
        return clean_dict(full_data_cache[ticker_sym])
    raise HTTPException(status_code=404, detail="Data not ready.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
