import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import urllib.request
import json
import datetime
import requests

app = FastAPI(title="AI Stock Scanner Cloud API")

# TWSE Real-time API Helper
def get_twse_realtime(symbol: str) -> Dict[str, Any]:
    clean_sym = symbol.replace(".TW", "").replace(".TWO", "")
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{clean_sym}.tw|otc_{clean_sym}.tw"
    try:
        resp = requests.get(url, timeout=5, verify=False)
        data = resp.json()
        if 'msgArray' in data and len(data['msgArray']) > 0:
            info = data['msgArray'][0]
            z = info.get('z', '-')
            tv = info.get('tv', '0')
            v = info.get('v', '0')
            latest = float(z) if z != '-' else None
            return {
                "price": latest,
                "volume": int(v) if v != '-' else 0,
                "tick_volume": int(tv) if tv != '-' else 0
            }
    except: pass
    return {"price": None, "volume": 0, "tick_volume": 0}

def get_twse_index() -> Dict[str, Any]:
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_t00.tw"
    try:
        resp = requests.get(url, timeout=5, verify=False)
        data = resp.json()
        if 'msgArray' in data and len(data['msgArray']) > 0:
            info = data['msgArray'][0]
            z = info.get('z', '-')
            p = info.get('y', '0')
            latest = float(z) if z != '-' else None
            prev = float(p) if p != '0' else latest
            change = ((latest - prev) / prev) * 100 if latest and prev else 0
            return {"close": round(latest, 2), "change": round(change, 2), "signal": "Buy" if change >= 0 else "Sell"}
    except: pass
    return None

# Enable CORS
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
    "2324.TW": "仁寶", "3037.TW": "欣興", "2409.TW": "友達", "3481.TW": "群創"
}

STOCKS_TW = list(STOCK_NAMES.keys())
STOCKS_US = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD", "NFLX", "SMH", "TSM", "AVGO"]

INDICES = {
    "台股加權": "^TWII",
    "費城半導體": "^SOX",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "VIX (恐慌)": "^VIX"
}

cached_scan_results_tw = []
cached_scan_results_us = []
cached_active_results = []
cached_indices_results = {}
last_update = None
last_error = "None"
VERSION = "1.1.8"

def clean_dict(data):
    if isinstance(data, list): return [clean_dict(v) for v in data]
    if isinstance(data, dict): return {k: clean_dict(v) for k, v in data.items()}
    if isinstance(data, float):
        if np.isnan(data) or np.isinf(data): return 0.0
    return data

def calculate_indicators(symbol: str, df: pd.DataFrame, market: str = "us") -> Dict:
    try:
        if df.empty or len(df) < 20: return None
        close = df['Close']
        sma50 = ta.trend.SMAIndicator(close, window=50).sma_indicator()
        latest_close = float(close.iloc[-1])
        latest_sma50 = float(sma50.iloc[-1]) if not np.isnan(sma50.iloc[-1]) else latest_close
        is_regular = latest_close > latest_sma50
        return {
            "symbol": symbol,
            "name": STOCK_NAMES.get(symbol, symbol),
            "close": round(latest_close, 2),
            "signal": "Buy" if is_regular else "Hold",
            "is_regular": is_regular
        }
    except: return None

def turtle_logic(symbol: str, df: pd.DataFrame) -> Dict:
    try:
        df = df.copy()
        c = df['Close'].iloc[-1]
        p = df['Close'].iloc[-2]
        h_1 = df['High'].iloc[-2]
        l_1 = df['Low'].iloc[-2]
        v = df['Volume'].iloc[-1]
        
        signal = "觀望"
        score = 20
        if c > h_1:
            signal = "🎯 買入突破"
            score = 100
        elif c < l_1:
            signal = "📉 賣出跌破"
            score = 90
        elif c > p: score = 50
        
        return {
            "symbol": symbol.replace(".TW",""),
            "name": STOCK_NAMES.get(symbol, symbol),
            "price": round(c, 2),
            "change": round(((c-p)/p)*100, 2),
            "signal": signal,
            "advice": signal,
            "reasons": f"突破 {round(h_1,2)}" if c > h_1 else f"跌破 {round(l_1,2)}" if c < l_1 else "區間震盪",
            "score": score
        }
    except: return None

async def update_data_loop():
    global cached_scan_results_tw, cached_scan_results_us, cached_active_results, cached_indices_results, last_update, last_error
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=5)

    while True:
        try:
            # Phase 1: High Priority - Active Market Scan
            hot_pool = STOCKS_TW[:15]
            try:
                data = await asyncio.wait_for(loop.run_in_executor(executor, lambda: yf.download(hot_pool, period="5d", interval="1d", progress=False)), timeout=30)
                is_multi = isinstance(data.columns, pd.MultiIndex)
                active_list = []
                for s in hot_pool:
                    try:
                        d_s = data.xs(s, axis=1, level=1).dropna() if is_multi else data.dropna()
                        rt = get_twse_realtime(s)
                        if rt['price']: d_s.iloc[-1, d_s.columns.get_loc('Close')] = rt['price']
                        res = turtle_logic(s, d_s)
                        if res: 
                            res["is_hot"] = rt['volume'] > 50000
                            active_list.append(res)
                    except: continue
                if active_list: cached_active_results = sorted(active_list, key=lambda x: x['score'], reverse=True)
            except: pass

            # Phase 2: Index Update (TWSE Fallback)
            new_indices = {}
            tw_idx = get_twse_index()
            if tw_idx: new_indices["台股加權"] = tw_idx
            for name, sym in INDICES.items():
                if name == "台股加權": continue
                try:
                    df_sym = await asyncio.wait_for(loop.run_in_executor(executor, lambda s=sym: yf.Ticker(s).history(period="5d", interval="1d")), timeout=10)
                    c = float(df_sym['Close'].iloc[-1])
                    p = float(df_sym['Close'].iloc[-2])
                    change = ((c - p) / p) * 100
                    new_indices[name] = {"close": round(c, 2), "change": round(change, 2), "signal": "Buy" if change >= 0 else "Sell"}
                except: continue
            if new_indices: cached_indices_results = new_indices

            last_update = datetime.datetime.now().strftime("%H:%M:%S")
        except Exception as e: last_error = str(e)
        await asyncio.sleep(60)

@app.get("/health")
def health(): return {"status":"ok", "version": VERSION, "last_update": last_update, "last_error": last_error}

@app.get("/market/active")
async def get_active_market(): return clean_dict(cached_active_results)

@app.get("/indices")
async def get_indices(): return clean_dict(cached_indices_results)

@app.get("/scan")
async def scan_stocks(): return clean_dict({"tw": cached_scan_results_tw, "us": cached_scan_results_us})

@app.on_event("startup")
async def startup(): asyncio.create_task(update_data_loop())
