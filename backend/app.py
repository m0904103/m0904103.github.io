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
    # Ensure symbol is pure digits
    clean_sym = symbol.replace(".TW", "").replace(".TWO", "")
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{clean_sym}.tw|otc_{clean_sym}.tw"
    try:
        # TWSE API often has SSL cert issues on cloud servers
        resp = requests.get(url, timeout=5, verify=False)
        data = resp.json()
        if 'msgArray' in data and len(data['msgArray']) > 0:
            info = data['msgArray'][0]
            # 'z' is latest price, 'tv' is latest volume, 'v' is total volume
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

# Enable CORS for React frontend
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
    "2324.TW": "仁寶", "3037.TW": "欣興", "2409.TW": "友達", "3481.TW": "群創",
    "0050.TW": "元大台灣50", "0056.TW": "元大高股息", "00878.TW": "國泰永續高股息"
}

STOCKS_TW = list(STOCK_NAMES.keys())
STOCKS_US = [
    "AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "JPM", "JNJ", "AMD", 
    "NFLX", "ADBE", "CRM", "PYPL", "V", "UNH", "XOM", "ORCL", "MA", "XLE", 
    "QQQ", "SPY", "SMH", "SOXX", "LLY", "PLTR", "TSM", "AVGO", "MU", "DELL", 
    "MARA", "MSTR", "IGV", "MGV", "DXYZ", "XOVR", "SARK", "VTI", "VGT", "VOO", 
    "ASML", "FTNT"
]

INDICES = {
    "台股加權": "^TWII",
    "費城半導體": "^SOX",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "VIX (恐慌)": "^VIX"
}

executor = ThreadPoolExecutor(max_workers=10)
cached_scan_results_tw = []
cached_scan_results_us = []
cached_active_results = []
cached_indices_results = {}
last_update = None
last_error = "None"
VERSION = "1.1.2"

def clean_dict(data):
    if isinstance(data, list):
        return [clean_dict(v) for v in data]
    if isinstance(data, dict):
        return {k: clean_dict(v) for k, v in data.items()}
    if isinstance(data, float):
        if np.isnan(data) or np.isinf(data): return 0.0
    return data

def calculate_indicators(symbol: str, df: pd.DataFrame, market: str = "us") -> Dict:
    try:
        if df.empty or len(df) < 60: return None
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # Base Indicators
        sma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator()
        sma50 = ta.trend.SMAIndicator(close, window=50).sma_indicator()
        sma200 = ta.trend.SMAIndicator(close, window=200).sma_indicator()
        
        # RSI & MACD
        rsi_indicator = ta.momentum.RSIIndicator(close, window=14)
        rsi = rsi_indicator.rsi()
        macd_obj = ta.trend.MACD(close)
        macd_diff = macd_obj.macd_diff()
        macd_line = macd_obj.macd()
        macd_sig = macd_obj.macd_signal()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close)
        bb_width = ((bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg()) * 100
        
        # Volume Analysis
        avg_vol = df['Volume'].rolling(window=20).mean()
        rvol = float(df['Volume'].iloc[-1] / avg_vol.iloc[-1]) if not avg_vol.iloc[-1] == 0 else 1.0
        
        latest_close = float(close.iloc[-1])
        latest_rsi = float(rsi.iloc[-1])
        latest_sma20 = float(sma20.iloc[-1])
        latest_sma50 = float(sma50.iloc[-1])
        latest_sma200 = float(sma200.iloc[-1])
        
        # MACD Cross Detection
        macd_signal_status = "Neutral"
        if macd_line.iloc[-1] > macd_sig.iloc[-1] and macd_line.iloc[-2] <= macd_sig.iloc[-2]:
            macd_signal_status = "Golden Cross"
        elif macd_line.iloc[-1] < macd_sig.iloc[-1] and macd_line.iloc[-2] >= macd_sig.iloc[-2]:
            macd_signal_status = "Death Cross"
            
        if market == "tw":
            # Taiwan "Regular Army" Logic (Trend + KD + MACD)
            is_regular = latest_close > latest_sma50
            stoch = ta.momentum.StochasticOscillator(high, low, close)
            latest_k = float(stoch.stoch().iloc[-1])
            latest_d = float(stoch.stoch_signal().iloc[-1])
            
            strength = 0
            if is_regular: strength += 40
            if latest_k > latest_d: strength += 30
            if macd_line.iloc[-1] > macd_sig.iloc[-1]: strength += 30
            
            signal = "Strong Buy" if strength >= 90 else "Buy" if strength >= 70 else "Hold"
            
            return {
                "symbol": symbol,
                "name": STOCK_NAMES.get(symbol, symbol),
                "close": round(latest_close, 2),
                "rsi": round(latest_rsi, 1),
                "strength": strength,
                "signal": signal,
                "reasons": f"正規軍:{'是' if is_regular else '否'} | RVOL:{round(rvol,1)}",
                "is_regular": is_regular,
                "rvol": round(rvol, 2)
            }
        else:
            # US Professional Technical Logic (Trend + Momentum + Volatility)
            price_vs_sma20 = "Above" if latest_close > latest_sma20 else "Below"
            price_vs_sma50 = "Above" if latest_close > latest_sma50 else "Below"
            bbw = float(bb_width.iloc[-1])
            volatility = "High" if bbw > 15 else "Medium" if bbw > 8 else "Low"
            
            # Entry/Exit Levels (ATR Based)
            atr = ta.volatility.AverageTrueRange(high, low, close).average_true_range().iloc[-1]
            buy_price = latest_close
            stop_loss = latest_close - (atr * 1.5)
            take_profit = latest_close + (atr * 3.0)
            
            # Expert Multi-Factor Score
            score = 0
            if latest_close > latest_sma50: score += 25
            if latest_close > latest_sma20: score += 15
            if macd_signal_status == "Golden Cross": score += 30
            if 30 < latest_rsi < 60: score += 10 # Healthy RSI
            if rvol > 1.2: score += 20 # Institutional interest
            
            signal = "Strong Buy" if score >= 80 else "Buy" if score >= 60 else "Sell" if score < 30 else "Hold"
            
            return {
                "symbol": symbol,
                "name": STOCK_NAMES.get(symbol, symbol),
                "close": round(latest_close, 2),
                "sma20": round(latest_sma20, 2),
                "sma50": round(latest_sma50, 2),
                "rsi": round(latest_rsi, 1),
                "price_vs_sma20": price_vs_sma20,
                "macd_signal": macd_signal_status,
                "rvol": round(rvol, 2),
                "volatility": volatility,
                "buy_price": round(buy_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "signal": signal,
                "score": score,
                "market": "us"
            }
    except Exception as e:
        print(f"Error {symbol}: {e}")
        return None

def turtle_logic(symbol: str, df: pd.DataFrame) -> Dict:
    try:
        df = df.copy()
        c = df['Close'].iloc[-1]
        p = df['Close'].iloc[-2]
        h = df['High'].iloc[-1]
        l = df['Low'].iloc[-1]
        v = df['Volume'].iloc[-1]
        
        # Turtle Strategy Indicators (1-day Breakout)
        high_1 = df['High'].iloc[-2] # Previous day high
        low_1 = df['Low'].iloc[-2]  # Previous day low
        
        # ATR (2-day)
        tr = np.maximum(df['High'] - df['Low'], 
                        np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                                   abs(df['Low'] - df['Close'].shift(1))))
        atr = tr.rolling(window=2).mean().iloc[-1]

        # Regular Army Indicators (Yan Laoshi)
        df['MA60'] = df['Close'].rolling(window=60).mean()
        ma60 = df['MA60'].iloc[-1]
        
        change = ((c - p) / p) * 100
        
        # Turtle Signal Logic
        signal = "觀望"
        if c > high_1 and v > 50000: signal = "🎯 買入突破"
        elif c < low_1 and v > 50000: signal = "📉 賣出跌破"
        
        # Score for UI sorting
        score = 0
        if signal == "🎯 買入突破": score = 100
        elif signal == "📉 賣出跌破": score = 90
        elif c > p: score = 50
        else: score = 20

        return {
            "symbol": symbol.replace(".TW",""),
            "name": STOCK_NAMES.get(symbol, symbol),
            "price": round(c, 2),
            "change": round(change, 2),
            "signal": signal,
            "advice": signal,
            "reasons": f"突破 {round(high_1, 2)}" if signal == "🎯 買入突破" else f"跌破 {round(low_1, 2)}" if signal == "📉 賣出跌破" else "區間震盪",
            "score": score,
            "ma60_status": "Above" if c > ma60 else "Below",
            "key_high": round(high_1, 2),
            "key_low": round(low_1, 2),
            "atr": round(atr, 2),
            "target": round(c + 2 * atr, 2) if signal == "🎯 買入突破" else round(c * 1.03, 2),
            "stop": round(c - 1.5 * atr, 2)
        }
    except: return None

async def update_data_loop():
    global cached_scan_results_tw, cached_scan_results_us, cached_indices_results, last_update, last_error
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=10)

    while True:
        try:
            # Phase 1: Batch Index Update
            try:
                new_indices = {}
                for name, sym in INDICES.items():
                    try:
                        df_sym = await asyncio.wait_for(
                            loop.run_in_executor(executor, lambda s=sym: yf.Ticker(s).history(period="5d", interval="1d")),
                            timeout=15
                        )
                        if df_sym is None or df_sym.empty or len(df_sym) < 2: continue
                        
                        c = float(df_sym['Close'].iloc[-1])
                        p = float(df_sym['Close'].iloc[-2])
                        if np.isnan(c) or np.isnan(p): continue
                        
                        change = ((c - p) / p) * 100
                        new_indices[name] = {
                            "close": round(c, 2), 
                            "change": round(change, 2), 
                            "signal": "Buy" if change >= 0 else "Sell"
                        }
                    except Exception as e:
                        print(f"Error parsing index {name}: {e}")
                
                if new_indices:
                    cached_indices_results = new_indices
            except Exception as e:
                last_error = f"Index batch error: {e}"
                print(last_error)

            # Phase 2: Batch Stock Update (TW)
            try:
                df_tw = await asyncio.wait_for(
                    loop.run_in_executor(executor, lambda: yf.download(STOCKS_TW, period="1mo", interval="1d", progress=False)),
                    timeout=45
                )
                new_tw = []
                for s in STOCKS_TW:
                    try:
                        if len(STOCKS_TW) > 1:
                            if s not in df_tw.columns.levels[1]: continue
                            df_s = df_tw.xs(s, axis=1, level=1).dropna(subset=['Close'])
                        else:
                            df_s = df_tw.dropna(subset=['Close'])
                            
                        res = calculate_indicators(s, df_s, "tw")
                        if res: new_tw.append(res)
                    except Exception as inner_e: 
                        continue
                if new_tw: cached_scan_results_tw = new_tw
            except Exception as e:
                last_error = f"Batch TW error: {e}"
                print(last_error)

            # Phase 3: Batch Stock Update (US)
            try:
                df_us = await asyncio.wait_for(
                    loop.run_in_executor(executor, lambda: yf.download(STOCKS_US, period="1mo", interval="1d", progress=False)),
                    timeout=45
                )
                new_us = []
                for s in STOCKS_US:
                    try:
                        if len(STOCKS_US) > 1:
                            if s not in df_us.columns.levels[1]: continue
                            df_s = df_us.xs(s, axis=1, level=1).dropna(subset=['Close'])
                        else:
                            df_s = df_us.dropna(subset=['Close'])
                            
                        res = calculate_indicators(s, df_s, "us")
                        if res: new_us.append(res)
                    except: continue
                if new_us: cached_scan_results_us = new_us
            except Exception as e:
                last_error = f"Batch US error: {e}"
                print(last_error)

            # Phase 4: Active Market Scan (Turtle Strategy)
            try:
                # Use smaller chunks for hot stocks to avoid Yahoo blocking
                hot_pool = STOCKS_TW[:20]
                # Fetch key prices once a day or once an hour
                df_active = await asyncio.wait_for(
                    loop.run_in_executor(executor, lambda: yf.download(hot_pool, period="5d", interval="1d", progress=False)),
                    timeout=30
                )
                
                active_list = []
                is_multi = isinstance(df_active.columns, pd.MultiIndex)
                for s in hot_pool:
                    try:
                        d_s = df_active.xs(s, axis=1, level=1).dropna() if is_multi else df_active.dropna()
                        if d_s.empty or len(d_s) < 2: continue
                        
                        # Real-time price from TWSE (Anti-Block)
                        rt = get_twse_realtime(s)
                        if rt['price']:
                            d_s.iloc[-1, d_s.columns.get_loc('Close')] = rt['price']
                            
                        res = turtle_logic(s, d_s)
                        if res:
                            res["is_hot"] = rt['volume'] > 50000
                            active_list.append(res)
                    except: continue
                
                if active_list:
                    cached_active_results = sorted(active_list, key=lambda x: x.get('score', 0), reverse=True)
            except Exception as e:
                print(f"Active scan loop error: {e}")

            last_update = datetime.datetime.now().strftime("%H:%M:%S")
        except Exception as e: 
            last_error = f"Loop error: {e}"
            print(last_error)
        await asyncio.sleep(120)

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "version": VERSION,
        "last_update": last_update, 
        "last_error": last_error
    }

@app.get("/scan")
async def scan_stocks():
    return clean_dict({"tw": cached_scan_results_tw, "us": cached_scan_results_us})

@app.get("/indices")
async def get_indices():
    return clean_dict(cached_indices_results)

@app.get("/market/active")
async def get_active_market():
    return clean_dict(cached_active_results)

@app.get("/history/{symbol}")
async def get_history(symbol: str):
    df = yf.download(symbol, period="1y", progress=False)
    history = []
    for idx, row in df.iterrows():
        history.append({"time": idx.strftime("%Y-%m-%d"), "open": float(row["Open"]), "high": float(row["High"]), "low": float(row["Low"]), "close": float(row["Close"]), "volume": float(row["Volume"])})
    return clean_dict(history)

@app.on_event("startup")
async def startup():
    asyncio.create_task(update_data_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
