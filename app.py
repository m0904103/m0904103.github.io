import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
import yfinance as yf
import time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

cache = {"indices": None, "last_update": 0}

def fetch_realtime_indices():
    current_time = time.time()
    if cache["indices"] and (current_time - cache["last_update"] < 300):
        data = cache["indices"].copy()
        data["cloud_status"] = "cached"
        data["cloud_time"] = datetime.datetime.fromtimestamp(cache["last_update"]).strftime("%H:%M:%S")
        return data

    # ✅ 修正 1: ^VIXTAIEX 是無效代碼，正確的台指VIX是 ^VIXTWN
    symbols = {
        '台股加權': '^TWII', '美金/台幣': 'TWD=X', '費城半導體': '^SOX',
        '美股標普': '^GSPC', '那斯達克': '^IXIC', 'VIX (恐慌)': '^VIX',
        '台指VIX (波動率)': '^VIXTWN',
        'TSM_ADR': 'TSM', 'TSM_TW': '2330.TW'
    }
    results = {}
    try:
        for key, symbol in symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    close = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else close
                    chg = ((close / prev) - 1) * 100
                    if key in ['TSM_ADR', 'TSM_TW']:
                        results[key] = float(close)
                    else:
                        results[key] = {
                            "close": round(float(close), 2),
                            "change": round(float(chg), 2),
                            "signal": "Buy" if chg > 0 else "Sell"
                        }
            except Exception:
                pass  # 單一個股失敗不影響整體

        # ✅ 修正 2: TSM ADR 溢價計算
        # 公式: (TSM_ADR美元 × 匯率) / (台股2330 × 5股) - 1
        if 'TSM_ADR' in results and 'TSM_TW' in results:
            fx = results.get('美金/台幣', {}).get('close', 31.5)
            tsm_adr = results['TSM_ADR']
            tsm_tw = results['TSM_TW']
            if tsm_tw > 0 and fx > 0:
                adr_p = ((tsm_adr * fx) / (tsm_tw * 5) - 1) * 100
                results['adr_premium'] = {
                    "close": round(adr_p, 2),
                    "change": 0,
                    "signal": "Premium" if adr_p > 0 else "Discount"
                }

        results.pop('TSM_ADR', None)
        results.pop('TSM_TW', None)

        # ✅ 修正 3: 台指VIX抓取失敗時，不使用硬編碼的38.59
        # 讓前端知道數據不可用，顯示 --- 而非錯誤的固定值
        # (移除舊版 硬編碼 38.59 的 fallback)

        # ✅ 新增: 根據VIX自動計算建議現金水位，與前端邏輯同步
        us_vix = results.get('VIX (恐慌)', {}).get('close', 0)
        tw_vix = results.get('台指VIX (波動率)', {}).get('close', 0)
        max_vix = max(us_vix, tw_vix)

        suggested_cash = 30
        if max_vix > 25:
            suggested_cash = 50
        if max_vix > 35:
            suggested_cash = 70

        results['suggested_cash'] = suggested_cash

        # 寫入快取
        cache["indices"] = results
        cache["last_update"] = current_time

        results["cloud_status"] = "live"
        results["cloud_time"] = datetime.datetime.fromtimestamp(current_time).strftime("%H:%M:%S")
        return results

    except Exception as e:
        return {"error": str(e), "cloud_status": "offline"}


@app.get("/indices")
def get_indices():
    return fetch_realtime_indices()


@app.get("/scan")
def get_scan():
    return {
        "tw": [
            {"symbol": "2330", "name": "台積電", "market": "tw", "close": 2260.0, "ma60": 1952.15, "rsi": 66.9, "trend_score": 100, "signal": "Strong Buy", "sector": "台股權值"},
            {"symbol": "2317", "name": "鴻海", "market": "tw", "close": 230.0, "ma60": 215.9, "rsi": 71.5, "trend_score": 100, "signal": "Strong Buy", "sector": "AI 基建"}
        ],
        "us": [
            {"symbol": "NVDA", "name": "NVIDIA", "market": "us", "close": 1250.0, "ma60": 1180.5, "rsi": 68.2, "trend_score": 100, "signal": "Strong Buy", "sector": "AI 基建"}
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok", "cloud_time": datetime.datetime.now().strftime("%H:%M:%S")}
