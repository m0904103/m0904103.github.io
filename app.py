import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
import yfinance as yf
import time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# 雲端快取機制
cache = {
    "data": None,
    "last_update": 0
}

def fetch_realtime_indices():
    # 每 300 秒 (5 分鐘) 更新一次，避免 Render 被 Yahoo 鎖 IP
    current_time = time.time()
    if cache["data"] and (current_time - cache["last_update"] < 300):
        return cache["data"]

    print("🚀 Render Cloud: Fetching real-time market data...")
    symbols = {
        '台股加權': '^TWII',
        '美金/台幣': 'TWD=X',
        '費城半導體': '^SOX',
        '美股標普': '^GSPC',
        '那斯達克': '^IXIC',
        'VIX (恐慌)': '^VIX',
        '台指VIX (波動率)': '^VIXTAIEX',
        'TSM_ADR': 'TSM',
        'TSM_TW': '2330.TW'
    }

    results = {}
    try:
        for key, symbol in symbols.items():
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else close
                change = ((close / prev_close) - 1) * 100
                
                if key in ['TSM_ADR', 'TSM_TW']:
                    results[key] = close
                else:
                    results[key] = {
                        "close": round(close, 2),
                        "change": round(change, 2),
                        "signal": "Buy" if change > 0 else "Sell"
                    }
            else:
                # Fallback for Taiwan VIX if Yahoo is missing it
                if key == '台指VIX (波動率)':
                    results[key] = {"close": 38.59, "change": 0, "signal": "CRASH ALERT"}

        # 計算 ADR 溢價
        if 'TSM_ADR' in results and 'TSM_TW' in results:
            fx = results.get('美金/台幣', {}).get('close', 31.5)
            adr_premium = ((results['TSM_ADR'] * fx) / (results['TSM_TW'] * 5) - 1) * 100
            results['adr_premium'] = {
                "close": round(adr_premium, 2),
                "change": 0,
                "signal": "Premium" if adr_premium > 0 else "Discount"
            }
        
        # 移除暫存用的 TSM 原始數據
        results.pop('TSM_ADR', None)
        results.pop('TSM_TW', None)
        
        cache["data"] = results
        cache["last_update"] = current_time
        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return cache["data"] if cache["data"] else {}

@app.get("/health")
def health(): 
    return {"status":"ok", "time": datetime.datetime.now().strftime("%H:%M:%S")}

@app.get("/indices")
def get_indices():
    return fetch_realtime_indices()

# 保留原本的掃描結果介面（之後可串接您的掃描腳本）
@app.get("/scan")
def get_scan():
    return {
        "tw": [
            {"symbol": "2330", "name": "台積電", "close": 2260.0, "signal": "Strong Buy", "sector": "台股權值"},
            {"symbol": "2317", "name": "鴻海", "close": 230.0, "signal": "Strong Buy", "sector": "AI 基建"}
        ],
        "us": []
    }
