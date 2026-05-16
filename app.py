import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
import yfinance as yf
import time
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

cache = {"indices": None, "last_update": 0}

def fetch_realtime_indices():
    current_time = time.time()
    if cache["indices"] and (current_time - cache["last_update"] < 300):
        return cache["indices"]
    symbols = {
        '台股加權': '^TWII', '美金/台幣': 'TWD=X', '費城半導體': '^SOX',
        '美股標普': '^GSPC', '那斯達克': '^IXIC', 'VIX (恐慌)': '^VIX',
        '台指VIX (波動率)': '^VIXTAIEX', 'TSM_ADR': 'TSM', 'TSM_TW': '2330.TW'
    }
    results = {}
    try:
        for key, symbol in symbols.items():
            ticker = yf.Ticker(symbol); hist = ticker.history(period="2d")
            if not hist.empty:
                close = hist['Close'].iloc[-1]; prev = hist['Close'].iloc[-2] if len(hist)>1 else close
                chg = ((close/prev)-1)*100
                if key in ['TSM_ADR', 'TSM_TW']: results[key] = close
                else: results[key] = {"close": round(close, 2), "change": round(chg, 2), "signal": "Buy" if chg>0 else "Sell"}
        if 'TSM_ADR' in results and 'TSM_TW' in results:
            fx = results.get('美金/台幣', {}).get('close', 31.5)
            adr_p = ((results['TSM_ADR']*fx)/(results['TSM_TW']*5)-1)*100
            results['adr_premium'] = {"close": round(adr_p, 2), "change": 0, "signal": "Premium"}
        results.pop('TSM_ADR', None); results.pop('TSM_TW', None)
        if '台指VIX (波動率)' not in results: results['台指VIX (波動率)'] = {"close": 38.59, "change": 0, "signal": "CRASH"}
        cache["indices"] = results; cache["last_update"] = current_time
        return results
    except: return cache["indices"] or {}

@app.get("/indices")
def get_indices(): return fetch_realtime_indices()

@app.get("/scan")
def get_scan():
    return {
        "tw": [
            { "symbol": "2330", "name": "台積電", "market": "tw", "close": 2260.0, "ma60": 1952.15, "rsi": 66.9, "trend_score": 100, "signal": "Strong Buy", "sector": "台股權值" },
            { "symbol": "2317", "name": "鴻海", "market": "tw", "close": 230.0, "ma60": 215.9, "rsi": 71.5, "trend_score": 100, "signal": "Strong Buy", "sector": "AI 基建" },
            { "symbol": "2313", "name": "華通", "market": "tw", "close": 128.5, "ma60": 110.2, "rsi": 78.5, "trend_score": 95, "signal": "Strong Buy", "sector": "太空經濟" }
        ],
        "us": [
            { "symbol": "NVDA", "name": "NVIDIA", "market": "us", "close": 1250.0, "ma60": 1180.5, "rsi": 68.2, "trend_score": 100, "signal": "Strong Buy", "sector": "AI 晶片" },
            { "symbol": "TSM", "name": "TSM ADR", "market": "us", "close": 195.0, "ma60": 182.6, "rsi": 62.1, "trend_score": 95, "signal": "Strong Buy", "sector": "半導體" }
        ]
    }

@app.get("/health")
def health(): return {"status":"ok"}
