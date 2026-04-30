import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import requests
import json
import logging

# Set up logging to track stability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI-Trader-Stability")

app = FastAPI(title="AI Stock Scanner Cloud v3.0 - STABLE")

class StableScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'}
        self.last_cache = {}

    def get_all_data(self, symbols):
        url = f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={','.join(symbols)}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = data['quoteResponse']['result']
                # Save to local cache file for emergency
                with open('last_data_cache.json', 'w') as f:
                    json.dump(results, f)
                return results
        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            # Load from emergency cache
            if os.path.exists('last_data_cache.json'):
                with open('last_data_cache.json', 'r') as f:
                    return json.load(f)
        return []

scraper = StableScraper()

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
VERSION = "3.0.0-STABLE"

async def update_data_loop():
    global cached_active_results, cached_indices_results, last_update
    while True:
        try:
            results = scraper.get_all_data(INDICES_SYMS + STOCKS_TW)
            res_map = {r['symbol']: r for r in results}
            
            # Indices
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

            # Active Market
            active_list = []
            for s in STOCKS_TW:
                if s in res_map:
                    r = res_map[s]
                    c, h, pc = r.get('regularMarketPrice', 0), r.get('regularMarketDayHigh', 0), r.get('regularMarketPreviousClose', 0)
                    active_list.append({
                        "symbol": s.replace(".TW",""), "name": STOCK_NAMES.get(s, s),
                        "price": c, "change": round(r.get('regularMarketChangePercent', 0), 2),
                        "signal": "🎯 買入突破" if c >= h and c > 0 else "監控中",
                        "advice": "多頭持股" if c >= h else "等待訊號",
                        "score": 100 if c >= h else 50,
                        "reasons": f"關鍵價: {h}",
                        "entry": c, "target": round(c*1.03, 2), "stop": round(c*0.97, 2)
                    })
            if active_list: cached_active_results = active_list
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
