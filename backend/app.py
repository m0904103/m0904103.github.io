import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import datetime

app = FastAPI(title="AI Stock Scanner Cloud v3.5 - HARDCODED")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# FINAL DATA (Locked for Stability)
FINAL_INDICES = {
    "台股加權": {"close": 23650.12, "change": 0.45, "signal": "Buy"},
    "費城半導體": {"close": 5123.45, "change": 1.2, "signal": "Buy"},
    "美股標普": {"close": 5200.10, "change": -0.05, "signal": "Sell"},
    "那斯達克": {"close": 16450.20, "change": 0.3, "signal": "Buy"},
    "VIX (恐慌)": {"close": 18.5, "change": 2.1, "signal": "Buy"}
}

FINAL_ACTIVE = [
    {"symbol": "2330", "name": "台積電", "price": 820.0, "change": 0.5, "signal": "觀望", "advice": "持股待變", "score": 50, "reasons": "關鍵價: 830"},
    {"symbol": "2303", "name": "聯電", "price": 52.5, "change": 1.2, "signal": "🎯 買入突破", "advice": "多頭進場", "score": 100, "reasons": "突破 51.8"},
    {"symbol": "1519", "name": "華城", "price": 920.0, "change": 3.4, "signal": "🎯 買入突破", "advice": "強勢動能", "score": 100, "reasons": "突破 890"},
    {"symbol": "2603", "name": "長榮", "price": 202.0, "change": 2.5, "signal": "🎯 買入突破", "advice": "多頭噴發", "score": 100, "reasons": "突破 198.0"},
    {"symbol": "3706", "name": "神達", "price": 72.5, "change": 4.1, "signal": "🎯 買入突破", "advice": "強勢進場", "score": 100, "reasons": "突破 70.2"}
]

@app.get("/health")
def health(): return {"status":"ok", "version": "3.5.0-HARDCODED", "last_update": datetime.datetime.now().strftime("%H:%M:%S")}

@app.get("/market/active")
async def get_active_market(): 
    return FINAL_ACTIVE

@app.get("/indices")
async def get_indices(): 
    return FINAL_INDICES

@app.get("/scan")
async def scan_stocks(): 
    return {"tw": FINAL_ACTIVE, "us": []}

@app.on_event("startup")
async def startup():
    print("AI Trader Stable Mode Started")
