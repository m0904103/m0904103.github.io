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

app = FastAPI(title="AI Stock Scanner API")

@app.get("/")
def health_check():
    return {"status": "war_room_online", "message": "AI 交易戰情室雲端核心運行中"}

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCKS_TW = [
    "2330.TW", "2317.TW", "2454.TW", "2382.TW", "2308.TW", "0050.TW", "0056.TW", "00878.TW", "1513.TW", "1519.TW", "2301.TW", "3231.TW", "6669.TW"
]

STOCKS_US = [
    "AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NFLX", "AMD", "SMH", "SOXX", "TSM"
]

INDICES = {
    "台股加權": "^TWII",
    "櫃買指數": "^TWO",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "VIX (恐慌)": "^VIX"
}

executor = ThreadPoolExecutor(max_workers=10)

# Memory Cache for instant responses
cached_scan_results_tw = []
cached_scan_results_us = []
cached_indices_results = {}
last_update = None

def to_1d(series_like):
    if series_like is None or (hasattr(series_like, 'empty') and series_like.empty):
        return pd.Series(dtype=float)
    if isinstance(series_like, pd.DataFrame):
        s = series_like.iloc[:, 0]
    else:
        s = series_like
    return pd.to_numeric(s.squeeze(), errors='coerce')

def to_float(val):
    try:
        if hasattr(val, 'iloc'):
            v = val.iloc[-1]
            return float(v)
        return float(val)
    except:
        return 0.0

def calculate_indicators(symbol: str, df: pd.DataFrame) -> Dict:
    try:
        if df.empty:
            return None

        close = to_1d(df['Close'])
        high  = to_1d(df['High'])
        low   = to_1d(df['Low'])

        if close.isna().all() or len(close.dropna()) < 10:
            return None

        # Technical Indicators
        rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
        sma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator()
        sma50 = ta.trend.SMAIndicator(close, window=50).sma_indicator()
        sma200 = ta.trend.SMAIndicator(close, window=200).sma_indicator()
        atr = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range()
        macd_obj = ta.trend.MACD(close, window_fast=12, window_slow=26, window_sign=9)
        macd_series = macd_obj.macd()
        macd_signal_series = macd_obj.macd_signal()
        # Indicator: MA60 (Life Line)
        sma60_series = ta.trend.SMAIndicator(close, window=60).sma_indicator()
        latest_sma60 = float(sma60_series.iloc[-1]) if not np.isnan(sma60_series.iloc[-1]) else 0
        
        # Indicator: KD (9, 3, 3)
        stoch = ta.momentum.StochasticOscillator(high=high, low=low, close=close, window=9, smooth_window=3)
        latest_k = float(stoch.stoch().iloc[-1])
        latest_d = float(stoch.stoch_signal().iloc[-1])
        
        # Latest values
        latest_close = float(close.iloc[-1])
        latest_rsi = float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else None
        latest_sma20 = float(sma20.iloc[-1]) if not np.isnan(sma20.iloc[-1]) else None
        latest_sma50 = float(sma50.iloc[-1]) if not np.isnan(sma50.iloc[-1]) else None
        latest_atr = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else None
        latest_macd = float(macd_series.iloc[-1]) if not np.isnan(macd_series.iloc[-1]) else None
        latest_macd_signal = float(macd_signal_series.iloc[-1]) if not np.isnan(macd_signal_series.iloc[-1]) else None
        
        # KD Signal Logic
        kd_signal_text = "Neutral"
        if latest_k < 25 and latest_k > latest_d: kd_signal_text = "Golden Cross"
        elif latest_k > 75 and latest_k < latest_d: kd_signal_text = "Death Cross"

        # MACD Signal Logic
        macd_signal_text = "Neutral"
        if len(macd_series.dropna()) >= 2 and len(macd_signal_series.dropna()) >= 2:
            if (macd_series.iloc[-2] < macd_signal_series.iloc[-2]) and (macd_series.iloc[-1] > macd_signal_series.iloc[-1]):
                macd_signal_text = "Golden Cross"
            elif (macd_series.iloc[-2] > macd_signal_series.iloc[-2]) and (macd_series.iloc[-1] < macd_signal_series.iloc[-1]):
                macd_signal_text = "Death Cross"

        # --- Turtle Strategy Logic ---
        high_20 = high.rolling(window=20).max()
        high_55 = high.rolling(window=55).max()
        low_10 = low.rolling(window=10).min()
        
        is_turtle_breakout = latest_close > high_20.iloc[-2] # Today's close > yesterday's 20d high
        turtle_n = latest_atr if latest_atr else 0
        position_sizing = round(10000 * 0.01 / (turtle_n * 1), 2) if turtle_n > 0 else 0 # Example: 1% risk on $10k

        # --- Professor Yen's Regular Army Logic ---
        is_regular_army = latest_close > latest_sma60
        # Expert Indicator: Volume Analysis
        avg_volume = to_1d(df['Volume']).rolling(window=20).mean().iloc[-1]
        latest_volume = float(to_1d(df['Volume']).iloc[-1])
        volume_spike = latest_volume > (avg_volume * 1.5) if not np.isnan(avg_volume) else False

        # Expert Indicator: Reward/Risk Ratio
        sl = latest_close - 1.5 * latest_atr if latest_atr else None
        tp = latest_close + 3.0 * latest_atr if latest_atr else None
        rr_ratio = 0
        if sl and tp and (latest_close - sl) > 0:
            rr_ratio = (tp - latest_close) / (latest_close - sl)

        # Trend Strength (0-100)
        strength = 0
        if is_regular_army: strength += 50
        if latest_macd > latest_macd_signal: strength += 25
        if latest_k > latest_d: strength += 25

        # Trading Signal (Professor Yen's Logic)
        signal = "Hold"
        reasons = []
        
        if is_regular_army:
            if kd_signal_text == "Golden Cross":
                signal = "Buy"
                reasons.append("生命線之上 + KD金叉")
            elif is_turtle_breakout:
                signal = "Buy"
                reasons.append("海龜突破 (正規軍)")
        else:
            if latest_close < latest_sma60:
                signal = "Sell"
                reasons.append("破生命線 (撤退)")

        return {
            'symbol': symbol,
            'close': round(float(latest_close), 2),
            'rsi': round(float(latest_rsi), 2) if latest_rsi is not None else None,
            'kd': f"{round(latest_k,1)}/{round(latest_d,1)}",
            'signal': str(signal),
            'reasons': ", ".join(reasons),
            'strength': strength if is_regular_army else 0,
            'is_strong': (signal == "Buy" and is_regular_army),
            'is_regular': bool(is_regular_army),
            'position_size': float(position_sizing),
            'buy_price': round(float(latest_close), 2),
            'stop_loss': round(float(latest_sma60), 2) if latest_sma60 else None,
            'take_profit': round(float(latest_close + 2.5 * latest_atr), 2) if latest_atr else None,
        }
    except Exception as e:
        print(f"Error calculating {symbol}: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    # Start the background task
    asyncio.create_task(update_data_loop())

async def update_data_loop():
    global cached_scan_results_tw, cached_scan_results_us, cached_indices_results, last_update
    while True:
        try:
            print("Refreshing data in background...")
            # 1. Update TW Stocks
            data_tw = yf.download(STOCKS_TW, period="1y", group_by='ticker', threads=True, progress=False)
            tasks_tw = []
            for symbol in STOCKS_TW:
                df = data_tw[symbol] if len(STOCKS_TW) > 1 else data_tw
                tasks_tw.append(asyncio.get_event_loop().run_in_executor(executor, calculate_indicators, symbol, df))
            results_tw = await asyncio.gather(*tasks_tw)
            cached_scan_results_tw = [r for r in results_tw if r is not None]

            # 2. Update US Stocks
            data_us = yf.download(STOCKS_US, period="1y", group_by='ticker', threads=True, progress=False)
            tasks_us = []
            for symbol in STOCKS_US:
                df = data_us[symbol] if len(STOCKS_US) > 1 else data_us
                tasks_us.append(asyncio.get_event_loop().run_in_executor(executor, calculate_indicators, symbol, df))
            results_us = await asyncio.gather(*tasks_us)
            cached_scan_results_us = [r for r in results_us if r is not None]

            # 3. Update Indices
            idx_data = yf.download(list(INDICES.values()), period="1y", group_by='ticker', threads=True, progress=False)
            idx_results = {}
            for name, sym in INDICES.items():
                try:
                    df = idx_data[sym] if len(INDICES) > 1 else idx_data
                    close = to_1d(df['Close'])
                    if close.empty: continue
                    latest_close = to_float(close)
                    sma20_series = ta.trend.SMAIndicator(close, window=20).sma_indicator()
                    latest_sma20 = to_float(sma20_series)
                    
                    signal = "Hold"
                    if latest_close > latest_sma20: signal = "Buy" if name != "VIX" else "Sell"
                    elif latest_close < latest_sma20: signal = "Sell" if name != "VIX" else "Buy"
                    idx_results[name] = {'symbol': sym, 'close': round(latest_close, 2), 'sma20': round(latest_sma20, 2), 'signal': signal}
                except Exception as ex:
                    print(f"Error updating index {name}: {ex}")
            cached_indices_results = idx_results
            last_update = datetime.datetime.now()
            print(f"Data refreshed at {last_update}")
        except Exception as e:
            print(f"Loop error: {e}")
        
        await asyncio.sleep(30) # Refresh every 30 seconds

@app.get("/scan")
async def scan_stocks():
    return {
        "tw": cached_scan_results_tw,
        "us": cached_scan_results_us
    }

@app.get("/indices")
async def get_indices():
    # Return cached data immediately
    return cached_indices_results

@app.get("/history/{symbol}")
async def get_history(symbol: str):
    df = yf.download(symbol, period="1y", progress=False)
    if df.empty:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Format for TradingView Lightweight Charts
    history = []
    for index, row in df.iterrows():
        history.append({
            "time": index.strftime("%Y-%m-%d"),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": float(row["Volume"]),
        })
    return history

@app.post("/notify")
async def send_notifications():
    # 1. Get scan results
    scan_results = await scan_stocks()
    strong_buy = [s for s in scan_results if s['signal'] == "Buy" and s['macd_signal'] == "Golden Cross"]
    
    # 2. Get indices for VIX
    indices = await get_indices()
    vix_val = indices.get("VIX", {}).get("close", 0.0)
    
    # 3. Telegram Config
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    CHAT_ID = os.environ.get("CHAT_ID")
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return {"status": "error", "message": "Telegram credentials not set"}

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if strong_buy:
        msg = f"🟢 <b>{today_str} AI 強勢股掃描結果</b>\n\n"
        msg += f"⚠️ VIX 波動率: {vix_val:.2f}\n\n"
        for row in strong_buy:
            msg += f"👉 <b>{row['symbol']}</b> (收盤: ${row['close']})\n"
            msg += f"   ➤ 買進價:{row['buy_price']} | 💥停損:{row['stop_loss']}\n"
            msg += "-"*20 + "\n"
    else:
        msg = f"🔴 <b>{today_str} 無符合條件的強勢股</b>\n\nVIX: {vix_val:.2f}"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            return {"status": "success", "message": "Telegram notification sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
