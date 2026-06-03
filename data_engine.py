import json
import os
import math
import time
import requests
import yfinance as yf
from datetime import datetime, timedelta
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# TWSE Official API - Backup Data Source
# ==========================================
TWSE_REALTIME_URL = "https://mis.twse.com.tw/stock/api/getStockInfo.asp"
TWSE_DAILY_URL = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
TWSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://mis.twse.com.tw/stock/index.jsp",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8",
}

def get_twse_realtime_prices(tw_symbols):
    """Fetch real-time prices from TWSE official API for a batch of TW stocks."""
    prices = {}
    try:
        # TWSE accepts comma-separated codes like "tse_2330.tw|tse_2317.tw"
        codes = []
        for sym in tw_symbols:
            code = sym.replace('.TW', '').replace('.TWO', '')
            codes.append(f"tse_{code}.tw")
        
        # Batch request (max 20 at a time to avoid timeout)
        batch_size = 20
        for i in range(0, len(codes), batch_size):
            batch = codes[i:i+batch_size]
            params = {"ex_ch": "|".join(batch), "json": "1", "delay": "0"}
            resp = requests.get(TWSE_REALTIME_URL, params=params, headers=TWSE_HEADERS, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                msg_array = data.get("msgArray", [])
                for item in msg_array:
                    code = item.get("c", "")
                    z = item.get("z", "-")  # z = current price
                    if z and z != "-":
                        prices[f"{code}.TW"] = round(float(z), 2)
            time.sleep(0.5)  # Be polite to TWSE server
    except Exception as e:
        print(f"  [TWSE API Error: {e}]")
    return prices


def get_price_yahoo(sym):
    """Fetch price from Yahoo Finance with full error handling."""
    try:
        ticker = yf.Ticker(sym)
        # Try fast_info first (live price)
        live_price = ticker.fast_info.last_price
        if live_price is not None and not math.isnan(live_price) and live_price > 0:
            return round(float(live_price), 2), "yahoo_live"
        # Fallback to history
        df = ticker.history(period='2d')
        if not df.empty:
            return round(float(df['Close'].iloc[-1]), 2), "yahoo_history"
    except Exception:
        pass
    return None, None


def is_tw_trading_hours():
    """Check if Taiwan stock market is currently open."""
    now = datetime.now()
    weekday = now.weekday()  # 0=Mon, 6=Sun
    if weekday >= 5:  # Weekend
        return False
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=13, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close


def is_us_trading_hours():
    """Check if US market is open (Taiwan time = +8h, US EST = -5h, so US open is 22:30 TW time)."""
    now = datetime.now()
    weekday = now.weekday()
    if weekday >= 5:
        return False
    us_open = now.replace(hour=21, minute=30, second=0, microsecond=0)
    us_close_next = now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return now >= us_open or now <= us_close_next.replace(hour=4, minute=0)


print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Taiwan market open: {is_tw_trading_hours()}")
print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] US market open: {is_us_trading_hours()}")
