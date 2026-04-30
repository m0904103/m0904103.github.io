import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import requests
import json

app = FastAPI(title="AI Stock Scanner Cloud v2.1")

# The "Mobile App Gateway": Using Yahoo's v7 API (Most stable)
class MobileStockScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'}

    def get_quotes(self, symbols):
        sym_str = ",".join(symbols)
        url = f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={sym_str}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=5)
            data = resp.json()
            return data['quoteResponse']['result']
        except: return []

scraper = MobileStockScraper()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STOCK_NAMES = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達", 
    "3231.TW": "緯創", "2376.TW": "技嘉", "2308.TW": "台達電", "1513.TW": "中興電",
    "1519.TW": "華城", "2603.TW": "長榮", "2303.TW": "聯電", "3017.TW": "奇鋐"
}
STOCKS_TW = list(STOCK_NAMES.keys())
INDICES_SYMS = ["^TWII", "^SOX", "^GSPC", "^IXIC", "^VIX"]

cached_active_results = []
cached_indices_results = {}
last_update = None
VERSION = "2.1.0"

async def update_data_loop():
    global cached_active_results, cached_indices_results, last_update
    while True:
        try:
            # 1. Fetch All Data in one or two calls
            all_syms = INDICES_SYMS + STOCKS_TW
            results = scraper.get_quotes(all_syms)
            
            res_map = {r['symbol']: r for r in results}
            
            # 2. Process Indices
            new_indices = {}
            for name, sym in {"台股加權": "^TWII", "費城半導體": "^SOX", "美股標普": "^GSPC", "那斯達克": "^IXIC", "VIX (恐慌)": "^VIX"}.items():
                if sym in res_map:
                    r = res_map[sym]
                    new_indices[name] = {
                        "close": r.get('regularMarketPrice', 0),
                        "change": r.get('regularMarketChangePercent', 0),
                        "signal": "Buy" if r.get('regularMarketChangePercent', 0) >= 0 else "Sell"
                    }
            if new_indices: cached_indices_results = new_indices

            # 3. Process Stocks (Turtle Logic)
            active_list = []
            for s in STOCKS_TW:
                if s in res_map:
                    r = res_map[s]
                    c = r.get('regularMarketPrice', 0)
                    h = r.get('regularMarketDayHigh', 0)
                    pc = r.get('regularMarketPreviousClose', 0)
                    
                    signal = "🎯 買入突破" if c >= h else "觀望"
                    score = 100 if c >= h else 50
                    
                    active_list.append({
                        "symbol": s.replace(".TW",""), "name": STOCK_NAMES.get(s, s),
                        "price": c, "change": round(r.get('regularMarketChangePercent', 0), 2),
                        "signal": signal, "advice": "多頭持股" if c >= h else "等待突破",
                        "score": score, "reasons": f"今日高: {h}",
                        "entry": c, "target": round(c*1.03, 2), "stop": round(c*0.97, 2)
                    })
            
            if active_list: cached_active_results = sorted(active_list, key=lambda x: x['score'], reverse=True)
            last_update = datetime.datetime.now().strftime("%H:%M:%S")
        except: pass
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
