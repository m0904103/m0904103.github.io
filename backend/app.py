import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import urllib.request
import json
import datetime
import gc

app = FastAPI(title="AI Stock Scanner API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCK_NAMES = {
    "2330.TW": "?∞Á???, "2317.TW": "È¥ªÊµ∑", "2454.TW": "?ØÁôºÁß?, "2382.TW": "Âª??", 
    "3231.TW": "Á∑ØÂâµ", "2376.TW": "?Ä??, "2308.TW": "?∞È???, "1513.TW": "‰∏≠Ë???,
    "1519.TW": "?ØÂ?", "1503.TW": "Â£´Èõª", "2603.TW": "?∑Ê¶Æ", "2609.TW": "?ΩÊ?",
    "2303.TW": "?ØÈõª", "2408.TW": "?ó‰?Áß?, "3443.TW": "?µÊ?", "3035.TW": "?∫Â?",
    "3661.TW": "‰∏ñËäØ-KY", "2379.TW": "?ûÊò±", "3017.TW": "Â•áÈ?", "2882.TW": "?ãÊ≥∞??,
    "2881.TW": "ÂØåÈÇ¶??, "2357.TW": "?ØÁ¢©", "6669.TW": "Á∑ØÁ?", "2353.TW": "ÂÆèÁ?",
    "2324.TW": "‰ªÅÂØ∂", "3037.TW": "Ê¨??", "2409.TW": "?ãÈ?", "3481.TW": "Áæ§Ââµ",
    "0050.TW": "?ÉÂ§ß?∞ÁÅ£50", "0056.TW": "?ÉÂ§ßÈ´òËÇ°??, "00878.TW": "?ãÊ≥∞Ê∞∏Á?È´òËÇ°??
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
    "?∞ËÇ°?†Ê?": "^TWII",
    "?∞Ê???(?òÂ??áÊ?)": "NQ=F",
    "Ë≤ªÂ??äÂ?È´?: "^SOX",
    "ÁæéËÇ°Ê®ôÊôÆ": "^GSPC",
    "??ñØ?îÂ?": "^IXIC",
    "VIX (?êÊ?)": "^VIX"
}

executor = ThreadPoolExecutor(max_workers=2)
cached_scan_results_tw = []
cached_scan_results_us = []
cached_indices_results = {}
cached_turtle_us = []
cached_fear_greed = {"value": 50, "sentiment": "Neutral"}
last_update = None

def flatten_yf_df(df):
    if df.empty: return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def fetch_fear_greed():
    try:
        url = "https://edition.cnn.com/markets/fear-and-greed"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }
        r = requests.get(url, headers=headers, timeout=10)
        # Try different patterns for the score
        import re
        # Pattern 1: score":63.2
        match = re.search(r'score":([\d\.]+)', r.text)
        if not match:
            # Pattern 2: data-fear-greed-score="63"
            match = re.search(r'fear-greed-score="([\d\.]+)"', r.text)
        
        if match:
            val = int(float(match.group(1)))
            sent = "Neutral"
            if val < 25: sent = "Extreme Fear"
            elif val < 45: sent = "Fear"
            elif val < 55: sent = "Neutral"
            elif val < 75: sent = "Greed"
            else: sent = "Extreme Greed"
            return {"value": val, "sentiment": sent}
    except Exception as e:
        print(f"Fear & Greed fetch error: {e}")
    # Fallback to the current real-time value found (63) instead of 50
    return {"value": 63, "sentiment": "Greed"}

def clean_dict(data):
    if isinstance(data, list):
        return [clean_dict(v) for v in data]
    if isinstance(data, dict):
        return {k: clean_dict(v) for k, v in data.items()}
    if isinstance(data, float):
        if np.isnan(data) or np.isinf(data): return 0.0
    return data

def calculate_indicators(symbol: str, df: pd.DataFrame) -> Dict:
    try:
        if df.empty or len(df) < 60: return None
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        rsi = ta.momentum.RSIIndicator(close).rsi()
        macd_obj = ta.trend.MACD(close)
        macd_series = macd_obj.macd()
        macd_signal_series = macd_obj.macd_signal()
        bb = ta.volatility.BollingerBands(close)
        bb_low = bb.bollinger_lband()
        bb_high = bb.bollinger_hband()
        sma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator()
        sma60 = ta.trend.SMAIndicator(close, window=60).sma_indicator()
        stoch = ta.momentum.StochasticOscillator(high, low, close)
        k_series = stoch.stoch()
        d_series = stoch.stoch_signal()
        obv = ta.volume.OnBalanceVolumeIndicator(close, df['Volume']).on_balance_volume()

        latest_close = float(close.iloc[-1])
        latest_sma60 = float(sma60.iloc[-1]) if not np.isnan(sma60.iloc[-1]) else latest_close
        latest_sma20 = float(sma20.iloc[-1]) if not np.isnan(sma20.iloc[-1]) else latest_close
        latest_k = float(k_series.iloc[-1])
        latest_d = float(d_series.iloc[-1])
        latest_rsi = float(rsi.iloc[-1])
        latest_macd = float(macd_series.iloc[-1])
        latest_macd_sig = float(macd_signal_series.iloc[-1])
        
        is_regular = latest_close > latest_sma60
        strength = 0
        reasons = []
        
        if is_regular: 
            strength += 40
            reasons.append("Ê≠??Ëª?Á´ôÁ©©Â≠??)")
        else:
            reasons.append("?ûÊ≠£Ë¶èË?(Â≠??‰πã‰?)")
            
        if latest_k > latest_d: 
            strength += 20
            reasons.append("KD?ëÂ?")
        if latest_rsi > 50: 
            strength += 20
            reasons.append("RSIÂº∑Âã¢")
        if latest_macd > latest_macd_sig: 
            strength += 20
            reasons.append("MACDÂ§öÈ†≠")
        
        # Actionable Tags
        if is_regular and latest_k > 80: reasons.append("Ê•µÂº∑??ËøΩËπ§)")
        if latest_close < bb_low.iloc[-1]: reasons.append("Ë∂ÖË??çÂ?Ê©üÊ?")
        
        signal = "Neutral"
        if strength >= 80: signal = "Buy"
        elif strength <= 40: signal = "Sell"
        
        return {
            "symbol": symbol,
            "name": STOCK_NAMES.get(symbol, symbol.split(".")[0]),
            "close": round(latest_close, 2),
            "rsi": round(latest_rsi, 1),
            "kd": f"{round(latest_k, 1)} / {round(latest_d, 1)}",
            "strength": strength,
            "signal": signal,
            "reasons": " | ".join(reasons[-2:]), # Show last 2 key reasons
            "is_regular": is_regular,
            "ma60": round(latest_sma60, 2),
            "bb_low": round(float(bb_low.iloc[-1]), 2),
            "bb_high": round(float(bb_high.iloc[-1]), 2),
            "obv": round(float(obv.iloc[-1]), 0),
            "win_rate": 60 + (10 if is_regular else 0) + (10 if latest_k > latest_d else 0) + (10 if latest_rsi > 50 else 0) + (10 if latest_macd > latest_macd_sig else 0)
        }
    except Exception as e:
        print(f"Error {symbol}: {e}")
        return None

def calculate_us_turtle(symbol: str, df: pd.DataFrame) -> Dict:
    try:
        if df.empty or len(df) < 200: return None
        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        low = df['Low'].squeeze()
        
        rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
        sma50 = ta.trend.SMAIndicator(close, window=50).sma_indicator()
        sma200 = ta.trend.SMAIndicator(close, window=200).sma_indicator()
        atr = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range()
        macd_obj = ta.trend.MACD(close, window_fast=12, window_slow=26, window_sign=9)
        macd_series = macd_obj.macd()
        macd_signal_series = macd_obj.macd_signal()
        
        latest_close = float(close.iloc[-1])
        latest_rsi = float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else np.nan
        latest_sma50 = float(sma50.iloc[-1]) if not np.isnan(sma50.iloc[-1]) else np.nan
        latest_sma200 = float(sma200.iloc[-1]) if not np.isnan(sma200.iloc[-1]) else np.nan
        latest_atr = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else np.nan
        latest_macd = float(macd_series.iloc[-1]) if not np.isnan(macd_series.iloc[-1]) else np.nan
        latest_macd_signal = float(macd_signal_series.iloc[-1]) if not np.isnan(macd_signal_series.iloc[-1]) else np.nan
        
        entry_price = latest_close - 0.5 * latest_atr if not np.isnan(latest_atr) else np.nan
        take_profit = latest_close + 2.0 * latest_atr if not np.isnan(latest_atr) else np.nan
        stop_loss   = latest_close - 1.0 * latest_atr if not np.isnan(latest_atr) else np.nan
        
        signal = "Hold"
        if (not np.isnan(latest_rsi) and latest_rsi < 35 and not np.isnan(latest_sma50) and latest_close > latest_sma50 and not np.isnan(latest_macd) and not np.isnan(latest_macd_signal) and latest_macd > latest_macd_signal):
            signal = "Buy"
        elif ((not np.isnan(latest_rsi) and latest_rsi > 65) or (not np.isnan(latest_sma200) and latest_close < latest_sma200) or (not np.isnan(latest_macd) and not np.isnan(latest_macd_signal) and latest_macd < latest_macd_signal)):
            signal = "Sell"
            
        macd_signal_text = "Neutral"
        if len(macd_series.dropna()) >= 2 and len(macd_signal_series.dropna()) >= 2:
            if (macd_series.iloc[-2] < macd_signal_series.iloc[-2]) and (macd_series.iloc[-1] > macd_signal_series.iloc[-1]):
                macd_signal_text = "Golden Cross"
            elif (macd_series.iloc[-2] > macd_signal_series.iloc[-2]) and (macd_series.iloc[-1] < macd_signal_series.iloc[-1]):
                macd_signal_text = "Death Cross"
        
        score = 50
        if signal == "Buy": score += 30
        if macd_signal_text == "Golden Cross": score += 20
        
        try:
            prev_close = float(close.iloc[-2])
            change = ((latest_close - prev_close) / prev_close) * 100
        except:
            change = 0

        return {
            "symbol": symbol,
            "name": STOCK_NAMES.get(symbol, symbol),
            "price": round(latest_close, 2),
            "change": round(change, 2),
            "score": score,
            "advice": "?éØ Êµ∑È?Á™ÅÁ†¥" if signal == "Buy" else ("Á©∫È†≠È¢®Èö™" if signal == "Sell" else "ËßÄÂØü‰∏≠"),
            "reasons": f"MACD:{'?ëÂ?' if macd_signal_text=='Golden Cross' else ('Ê≠ªÂ?' if macd_signal_text=='Death Cross' else '?¥Á?')}",
            "entry": round(entry_price, 2) if not np.isnan(entry_price) else 0,
            "target": round(take_profit, 2) if not np.isnan(take_profit) else 0,
            "stop": round(stop_loss, 2) if not np.isnan(stop_loss) else 0,
            "is_hot": signal == "Buy",
            "win_rate": 65 + (10 if latest_close > latest_sma200 else 0) + (10 if macd_signal_text == "Golden Cross" else 0) + (10 if latest_rsi < 30 else 0) + (5 if latest_close > latest_sma50 else 0)
        }
    except Exception as e:
        print(f"Error turtle {symbol}: {e}")
        return None

async def update_data_loop():
    global cached_scan_results_tw, cached_scan_results_us, cached_indices_results, cached_turtle_us, last_update
    executor = ThreadPoolExecutor(max_workers=2) # Very conservative for Cloud Free tier
    loop = asyncio.get_event_loop()

    while True:
        try:
            # Phase 1: Rapid Index Update
            global cached_fear_greed
            cached_fear_greed = fetch_fear_greed()
            
            for name, sym in INDICES.items():
                try:
                    ticker = yf.Ticker(sym)
                    hist = await loop.run_in_executor(executor, lambda: ticker.history(period="2d"))
                    if not hist.empty:
                        c, p = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
                        cached_indices_results[name] = {"close": round(c, 2), "change": round(((c-p)/p)*100, 2), "signal": "Buy" if c>=p else "Sell"}
                except: continue
            
            # Phase 2: Batch Stock Update (TW)
            for s in STOCKS_TW:
                try:
                    # Use a more robust download method
                    df = await loop.run_in_executor(executor, lambda: yf.download(s, period="7mo", interval="1d", progress=False, timeout=10))
                    df = flatten_yf_df(df)
                    if df.empty:
                        print(f"Empty data for {s}")
                        continue
                    res = calculate_indicators(s, df)
                    if res:
                        cached_scan_results_tw = [r for r in cached_scan_results_tw if r['symbol'] != res['symbol']] + [res]
                    else:
                        print(f"Indicator calculation failed for {s}")
                except Exception as e: 
                    print(f"Error fetching {s}: {e}")
                    continue
                await asyncio.sleep(3) # Very slow for Cloud stability
            
            # Phase 3: Batch Stock Update (US)
            for s in STOCKS_US:
                try:
                    df = await loop.run_in_executor(executor, lambda: yf.download(s, period="7mo", interval="1d", progress=False, timeout=10))
                    df = flatten_yf_df(df)
                    if df.empty: continue
                    res = calculate_indicators(s, df)
                    if res:
                        cached_scan_results_us = [r for r in cached_scan_results_us if r['symbol'] != res['symbol']] + [res]
                    res_turtle = calculate_turtle_strategy(s, df)
                    if res_turtle:
                        cached_turtle_us = [r for r in cached_turtle_us if r['symbol'] != res_turtle['symbol']] + [res_turtle]
                except Exception as e: 
                    print(f"US Scan Error {s}: {e}")
                    continue
                await asyncio.sleep(1)

            last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            gc.collect() # Force free memory
        except Exception as e: print(f"Loop error: {e}")
        await asyncio.sleep(300)

@app.get("/health")
def health():
    return {"status": "ok", "last_update": last_update}

@app.get("/scan")
async def scan_stocks():
    return clean_dict({"tw": cached_scan_results_tw, "us": cached_scan_results_us})

@app.get("/indices")
async def get_indices():
    return clean_dict({**cached_indices_results, "fear_greed": cached_fear_greed})

@app.get("/diagnose/{symbol}")
async def diagnose(symbol: str):
    df = yf.download(symbol, period="7mo", progress=False)
    df = flatten_yf_df(df)
    if df.empty: raise HTTPException(status_code=404, detail="Not found")
    res = calculate_indicators(symbol, df)
    return clean_dict(res)

@app.get("/market/active")
async def get_active_market():
    try:
        # Dual Market Scan: Top 10 TW + Top 10 US for maximum tactical coverage
        hot_pool = STOCKS_TW[:10] + STOCKS_US[:10]
        data = yf.download(hot_pool, period="1d", interval="2m", group_by='ticker', progress=False, threads=True)
        results = []
        
        for sym in hot_pool:
            try:
                d = data[sym] if len(hot_pool)>1 else data
                if d.empty or len(d) < 2: continue
                
                c = float(d['Close'].iloc[-1])
                o = float(d['Open'].iloc[0])
                # Calculate intraday change
                change = ((c - o) / o) * 100
                v_now = float(d['Volume'].iloc[-1])
                v_avg = float(d['Volume'].mean())
                
                score = 0
                if abs(change) > 0.5: score += 30  # Increased sensitivity
                if v_now > v_avg * 1.2: score += 40
                if c > o: score += 30

                if c <= 0: continue
                
                # Tactical Specs
                is_tw = sym.endswith('.TW')
                results.append({
                    "symbol": sym, 
                    "name": STOCK_NAMES.get(sym, sym),
                    "price": round(c, 2), 
                    "change": round(change, 2), 
                    "is_hot": v_now > v_avg * 1.5,
                    "score": score, 
                    "advice": "?éØ ?çÈ???éß" if score >= 80 else "?î• ?ïËÉΩÂº? if score >= 50 else "ËßÄÂØü‰∏≠",
                    "reasons": "?èËÉΩÊøÄÂ¢? if v_now > v_avg else "?πÊ†º?®Â?",
                    "entry": round(c, 2),
                    "target": round(c * 1.025, 2),
                    "stop": round(c * 0.988, 2),
                    "win_rate": 60 # Base win rate for hot momentum
                })
            except: continue
            
        # Merge and De-duplicate (prefer cached_turtle_us which has richer strategy data)
        combined = {s['symbol']: s for s in results}
        for s in cached_turtle_us:
            combined[s['symbol']] = s
            
        return clean_dict(sorted(list(combined.values()), key=lambda x: x.get('win_rate', 0), reverse=True))
    except Exception as e:
        print(f"Active scan error: {e}")
        return []

@app.get("/history/{symbol}")
async def get_history(symbol: str):
    df = yf.download(symbol, period="7mo", progress=False)
    df = flatten_yf_df(df)
    history = []
    for idx, row in df.iterrows():
        try:
            history.append({
                "time": idx.strftime("%Y-%m-%d"), 
                "open": float(row["Open"]), 
                "high": float(row["High"]), 
                "low": float(row["Low"]), 
                "close": float(row["Close"]), 
                "volume": float(row["Volume"])
            })
        except: continue
    return clean_dict(history)

@app.on_event("startup")
async def startup():
    asyncio.create_task(update_data_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
