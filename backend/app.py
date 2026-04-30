import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import datetime
import requests
import json

app = FastAPI(title="AI Stock Scanner Cloud API")

# Heavy-Duty Direct API Scraper (Bypassing yfinance)
class TurtleEngine:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    def get_history_direct(self, symbol):
        # Using Yahoo's web chart API directly
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
        try:
            resp = requests.get(url, headers=self.headers, timeout=5)
            data = resp.json()
            result = data['chart']['result'][0]
            quotes = result['indicators']['quote'][0]
            times = result['timestamp']
            df = pd.DataFrame({
                'Close': quotes['close'],
                'High': quotes['high'],
                'Low': quotes['low'],
                'Volume': quotes['volume']
            })
            return df.dropna()
        except: return pd.DataFrame()

    def get_realtime_twse(self, symbol):
        clean_sym = symbol.replace(".TW", "").replace(".TWO", "")
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{clean_sym}.tw|otc_{clean_sym}.tw"
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3, verify=False)
            data = resp.json()
            if 'msgArray' in data and len(data['msgArray']) > 0:
                info = data['msgArray'][0]
                z = info.get('z', info.get('y', '0'))
                v = info.get('v', '0')
                return {"price": float(z) if z != '-' else None, "volume": int(v) if v != '-' else 0}
        except: pass
        return {"price": None, "volume": 0}

engine = TurtleEngine()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STOCK_NAMES = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達", 
    "3231.TW": "緯創", "2376.TW": "技嘉", "2308.TW": "台達電", "1513.TW": "中興電",
    "1519.TW": "華城", "1503.TW": "士電", "2603.TW": "長榮", "2609.TW": "陽明",
    "2303.TW": "聯電", "2408.TW": "南亞科", "3443.TW": "創意", "3035.TW": "智原",
    "3661.TW": "世芯-KY", "2379.TW": "瑞昱", "3017.TW": "奇鋐", "2882.TW": "國泰金"
}
STOCKS_TW = list(STOCK_NAMES.keys())

cached_active_results = []
cached_indices_results = {}
last_update = None
VERSION = "1.9.0"

async def update_data_loop():
    global cached_active_results, cached_indices_results, last_update
    executor = ThreadPoolExecutor(max_workers=5)
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            # 1. Indices (Simplified for Speed)
            new_indices = {}
            for name, sym in {"台股加權": "^TWII", "費城半導體": "^SOX", "那斯達克": "^IXIC"}.items():
                df = engine.get_history_direct(sym)
                if not df.empty:
                    c, p = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    change = ((c - p) / p) * 100
                    new_indices[name] = {"close": round(c, 2), "change": round(change, 2), "signal": "Buy" if change >= 0 else "Sell"}
            if new_indices: cached_indices_results = new_indices

            # 2. Active Turtle Scan
            active_list = []
            for s in STOCKS_TW:
                try:
                    df = engine.get_history_direct(s)
                    if df.empty or len(df) < 2: continue
                    
                    rt = engine.get_realtime_twse(s)
                    c = rt['price'] if rt['price'] else df['Close'].iloc[-1]
                    p = df['Close'].iloc[-2]
                    h_1 = df['High'].iloc[-2]
                    l_1 = df['Low'].iloc[-2]
                    
                    signal = "觀望"
                    advice = "監控中"
                    score = 20
                    
                    if c > h_1:
                        signal = "🎯 買入突破"
                        advice = "多頭進場"
                        score = 100
                    elif c < l_1:
                        signal = "📉 賣出跌破"
                        advice = "空頭進場"
                        score = 90
                    elif c > h_1 * 0.99:
                        signal = "⚡ 即將突破"
                        advice = "準備做多"
                        score = 70
                    
                    active_list.append({
                        "symbol": s.replace(".TW",""), "name": STOCK_NAMES.get(s, s),
                        "price": round(c, 2), "change": round(((c-p)/p)*100, 2),
                        "signal": signal, "advice": advice, "score": score,
                        "reasons": f"關鍵價: {round(h_1,2)}",
                        "entry": round(c, 2), "target": round(c * 1.02, 2), "stop": round(c * 0.985, 2)
                    })
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
