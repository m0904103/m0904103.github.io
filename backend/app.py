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

# TWSE Real-time API Helper with better Headers
def get_twse_realtime(symbol: str) -> Dict[str, Any]:
    clean_sym = symbol.replace(".TW", "").replace(".TWO", "")
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{clean_sym}.tw|otc_{clean_sym}.tw"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        resp = requests.get(url, timeout=5, verify=False, headers=headers)
        data = resp.json()
        if 'msgArray' in data and len(data['msgArray']) > 0:
            info = data['msgArray'][0]
            z = info.get('z', '-')
            tv = info.get('tv', '0')
            v = info.get('v', '0')
            latest = float(z) if z != '-' else None
            return {"price": latest, "volume": int(v) if v != '-' else 0, "tick_volume": int(tv) if tv != '-' else 0}
    except: pass
    return {"price": None, "volume": 0, "tick_volume": 0}

def get_twse_index() -> Dict[str, Any]:
    # Try multiple index sources
    urls = [
        "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_t00.tw",
        "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=otc_o00.tw"
    ]
    headers = {'User-Agent': 'Mozilla/5.0'}
    for url in urls:
        try:
            resp = requests.get(url, timeout=5, verify=False, headers=headers)
            data = resp.json()
            if 'msgArray' in data and len(data['msgArray']) > 0:
                info = data['msgArray'][0]
                z = info.get('z', info.get('y', '0')) # Fallback to yesterday if z is -
                p = info.get('y', '0')
                latest = float(z) if z != '-' else float(p)
                prev = float(p) if p != '0' else latest
                change = ((latest - prev) / prev) * 100 if latest and prev else 0
                return {"close": round(latest, 2), "change": round(change, 2), "signal": "Buy" if change >= 0 else "Sell"}
        except: continue
    return None

# Enable CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STOCK_NAMES = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達", 
    "3231.TW": "緯創", "2376.TW": "技嘉", "2308.TW": "台達電", "1513.TW": "中興電",
    "1519.TW": "華城", "1503.TW": "士電", "2603.TW": "長榮", "2609.TW": "陽明",
    "2303.TW": "聯電", "2408.TW": "南亞科", "3443.TW": "創意", "3035.TW": "智原",
    "2379.TW": "瑞昱", "3017.TW": "奇鋐", "2882.TW": "國泰金", "2881.TW": "富邦金"
}
STOCKS_TW = list(STOCK_NAMES.keys())
INDICES = {"台股加權": "^TWII", "費城半導體": "^SOX", "美股標普": "^GSPC", "那斯達克": "^IXIC", "VIX (恐慌)": "^VIX"}

cached_scan_results_tw = []
cached_active_results = []
cached_indices_results = {}
last_update = None
VERSION = "1.6.0"

def turtle_logic(symbol: str, df: pd.DataFrame) -> Dict:
    try:
        c = df['Close'].iloc[-1]
        p = df['Close'].iloc[-2]
        h_1 = df['High'].iloc[-2]
        l_1 = df['Low'].iloc[-2]
        signal = "🎯 買入突破" if c > h_1 else "📉 賣出跌破" if c < l_1 else "觀望"
        score = 100 if c > h_1 else 90 if c < l_1 else 50 if c > p else 20
        return {
            "symbol": symbol.replace(".TW",""), "name": STOCK_NAMES.get(symbol, symbol),
            "price": round(c, 2), "change": round(((c-p)/p)*100, 2),
            "signal": signal, "advice": signal, "score": score,
            "reasons": f"突破 {round(h_1,2)}" if c > h_1 else f"跌破 {round(l_1,2)}" if c < l_1 else "區間震盪"
        }
    except: return None

async def update_data_loop():
    global cached_active_results, cached_indices_results, last_update
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=5)
    while True:
        try:
            # Indices
            new_indices = {}
            tw_idx = get_twse_index()
            if tw_idx: new_indices["台股加權"] = tw_idx
            for name, sym in INDICES.items():
                if name == "台股加權": continue
                try:
                    df = await asyncio.wait_for(loop.run_in_executor(executor, lambda s=sym: yf.Ticker(s).history(period="5d", interval="1d")), timeout=10)
                    c, p = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-2])
                    change = ((c - p) / p) * 100
                    new_indices[name] = {"close": round(c, 2), "change": round(change, 2), "signal": "Buy" if change >= 0 else "Sell"}
                except: continue
            if new_indices: cached_indices_results = new_indices

            # Active Market
            active_list = []
            data = await asyncio.wait_for(loop.run_in_executor(executor, lambda: yf.download(STOCKS_TW[:15], period="5d", interval="1d", progress=False)), timeout=30)
            is_multi = isinstance(data.columns, pd.MultiIndex)
            for s in STOCKS_TW[:15]:
                try:
                    d_s = data.xs(s, axis=1, level=1).dropna() if is_multi else data.dropna()
                    rt = get_twse_realtime(s)
                    if rt['price']: d_s.iloc[-1, d_s.columns.get_loc('Close')] = rt['price']
                    res = turtle_logic(s, d_s)
                    if res: active_list.append(res)
                except: continue
            if active_list: cached_active_results = sorted(active_list, key=lambda x: x['score'], reverse=True)
            
            last_update = datetime.datetime.now().strftime("%H:%M:%S")
        except Exception as e: print(f"Loop error: {e}")
        await asyncio.sleep(60)

@app.get("/health")
def health(): return {"status":"ok", "version": VERSION, "last_update": last_update}
@app.get("/market/active")
async def get_active_market(): return cached_active_results
@app.get("/indices")
async def get_indices(): return cached_indices_results
@app.get("/scan")
async def scan_stocks(): return {"tw": [], "us": []}

@app.on_event("startup")
async def startup(): asyncio.create_task(update_data_loop())
