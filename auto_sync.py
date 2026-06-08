"""
auto_sync.py - 正規軍自動同步守護程式
每隔指定分鐘數自動更新 scan_results.json 並部署至 GitHub Pages。
支援 Yahoo Finance + TWSE 雙數據源 + 交叉驗證。
"""
import json
import os
import math
import time
import subprocess
import requests
import yfinance as yf
from datetime import datetime, timedelta
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 設定
# ==========================================
DATA_FILE = os.path.join('frontend', 'public', 'scan_results.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# TWSE 官方即時報價 API
TWSE_REALTIME_URL = "https://mis.twse.com.tw/stock/api/getStockInfo.asp"
TWSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://mis.twse.com.tw/stock/index.jsp",
    "Accept-Language": "zh-TW,zh;q=0.9",
}


# ==========================================
# 市場開盤狀態判斷
# ==========================================
def is_tw_trading_hours():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    open_t = now.replace(hour=9, minute=0, second=0, microsecond=0)
    close_t = now.replace(hour=13, minute=30, second=0, microsecond=0)
    return open_t <= now <= close_t


def is_us_trading_hours():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    # US market opens 21:30 Taiwan time, closes 04:00 next day
    us_open = now.replace(hour=21, minute=30, second=0, microsecond=0)
    return now >= us_open or now.hour < 4


def get_update_interval_minutes():
    """Return appropriate update interval based on market status."""
    if is_tw_trading_hours() or is_us_trading_hours():
        return 30  # Increased to 30 min to avoid IP bans
    else:
        return 60  # Every 60 min outside trading hours


# ==========================================
# TWSE 備援數據源
# ==========================================
def get_twse_prices(symbols):
    """Fetch TW stock prices from official TWSE real-time API."""
    prices = {}
    tw_syms = [s for s in symbols if '.TW' in s or '.TWO' in s]
    if not tw_syms:
        return prices

    codes = []
    for sym in tw_syms:
        code = sym.replace('.TW', '').replace('.TWO', '')
        codes.append(f"tse_{code}.tw")

    batch_size = 20
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i + batch_size]
        try:
            params = {"ex_ch": "|".join(batch), "json": "1", "delay": "0"}
            resp = requests.get(TWSE_REALTIME_URL, params=params, headers=TWSE_HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("msgArray", []):
                    code = item.get("c", "")
                    z = item.get("z", "-")
                    y = item.get("y", "-")  # y = yesterday close
                    if z and z != "-":
                        prices[f"{code}.TW"] = {
                            "price": round(float(z), 2),
                            "prev_close": round(float(y), 2) if y and y != "-" else None,
                            "source": "TWSE"
                        }
                time.sleep(0.3)
        except Exception as e:
            print(f"  [TWSE batch error: {e}]")
    return prices


# ==========================================
# 主同步邏輯（雙源 + 交叉驗證）
# ==========================================
def sync_once():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting sync... (TW={is_tw_trading_hours()}, US={is_us_trading_hours()})")

    if not os.path.exists(DATA_FILE):
        print("ERROR: scan_results.json not found!")
        return False

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_stocks = {s['symbol']: s for s in data.get('stocks', [])}
    all_symbols = list(existing_stocks.keys())
    tw_symbols = [s for s in all_symbols if '.TW' in s or '.TWO' in s]

    # Step 1: 先用 TWSE 抓台股即時報價（盤中）
    twse_prices = {}
    if is_tw_trading_hours():
        print(f"  Fetching TWSE real-time for {len(tw_symbols)} TW stocks...")
        twse_prices = get_twse_prices(tw_symbols)
        print(f"  TWSE returned {len(twse_prices)} prices.")

    # Step 2: 用 Yahoo Finance 更新全部股票
    updated_count = 0
    cross_check_alerts = []

    for sym in all_symbols:
        stock_obj = existing_stocks[sym]
        name = stock_obj.get('name', sym)
        try:
            # Yahoo Finance
            ticker = yf.Ticker(sym)
            df = ticker.history(period='120d')

            if df.empty:
                alt_sym = sym.replace('.TW', '.TWO') if '.TW' in sym else sym
                if alt_sym != sym:
                    df = yf.Ticker(alt_sym).history(period='120d')
                if df.empty:
                    print(f"  {sym}: No data from Yahoo.")
                    continue

            yahoo_close = round(float(df['Close'].iloc[-1]), 2)
            prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else yahoo_close

            # Try live price from Yahoo
            try:
                live = ticker.fast_info.last_price
                if live and not math.isnan(live) and live > 0:
                    yahoo_close = round(float(live), 2)
            except Exception:
                pass

            final_price = yahoo_close
            price_source = "Yahoo"

            # Step 3: 交叉驗證 (台股盤中 - 用 TWSE 為準)
            twse_entry = twse_prices.get(sym) or twse_prices.get(sym.replace('.TWO', '.TW'))
            if twse_entry:
                twse_price = twse_entry["price"]
                diff_pct = abs((twse_price - yahoo_close) / yahoo_close * 100) if yahoo_close > 0 else 0
                if diff_pct > 1.5:
                    cross_check_alerts.append(
                        f"  WARNING: {sym} Yahoo={yahoo_close} vs TWSE={twse_price} diff={diff_pct:.1f}%"
                    )
                # During TW trading hours, trust TWSE official price
                if is_tw_trading_hours():
                    final_price = twse_price
                    price_source = "TWSE"
                    if twse_entry.get("prev_close"):
                        prev_close = twse_entry["prev_close"]

            change = round(((final_price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0

            ma60 = round(float(df['Close'].rolling(60).mean().iloc[-1]), 2) if len(df) >= 60 else final_price
            is_regular = final_price > ma60
            signal = "Strong Buy" if is_regular else "Hold"

            stock_obj["close"] = final_price
            stock_obj["price_source"] = price_source
            stock_obj["ma60"] = ma60
            stock_obj["change"] = change
            stock_obj["signal"] = signal
            stock_obj["is_regular"] = is_regular
            stock_obj["market"] = "tw" if ".TW" in sym or ".TWO" in sym else "us"

            if "plan" not in stock_obj:
                stock_obj["plan"] = {}
            stock_obj["plan"]["entry"] = final_price
            stock_obj["plan"]["sl"] = ma60
            stock_obj["plan"]["tp"] = round(final_price * 1.25, 2)

            existing_stocks[sym] = stock_obj
            updated_count += 1

        except Exception as e:
            print(f"  {sym}: ERROR - {e}")

    # Print cross-check alerts
    if cross_check_alerts:
        print("\n  === DATA CROSS-CHECK ALERTS ===")
        for alert in cross_check_alerts:
            print(alert)
        print()

    # Re-assemble data
    data['stocks'] = list(existing_stocks.values())
    data['indices'] = data.get('indices', {})
    data['last_updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')  # UTC ISO format - timezone safe

    # Sort stocks: US first, then Taiwan
    data['stocks'].sort(key=lambda x: (x.get('market') != 'us', x.get('symbol')))

    def clean_nans(obj):
        if isinstance(obj, dict):
            return {k: clean_nans(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nans(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
        return obj
        
    data = clean_nans(data)

    # Save to file
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)

    print(f"  Updated {updated_count}/{len(all_symbols)} stocks.")
    return True


def deploy_to_github():
    """Build frontend and push to GitHub using the official script."""
    try:
        import shutil
        npm_cmd = shutil.which("npm") or "npm.cmd"
        print("  Building frontend...")
        subprocess.run(
            [npm_cmd, "run", "build"],
            cwd=os.path.join(SCRIPT_DIR, 'frontend'),
            check=True, timeout=120
        )
        print("  Running upload_frontend.py...")
        subprocess.run(
            [sys.executable, "upload_frontend.py"],
            cwd=SCRIPT_DIR,
            check=True, timeout=120
        )
        print(f"  Pushed: auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Deploy error: {e}")
        return False


# ==========================================
# 主循環 - 持續運行守護程式
# ==========================================
def run_daemon():
    print("=" * 60)
    print("  REGULAR ARMY AUTO-SYNC DAEMON STARTED")
    print("  Dual Source: Yahoo Finance + TWSE Official API")
    print("  Cross-validation enabled.")
    print("=" * 60)

    while True:
        try:
            ok = sync_once()
            if ok:
                deploy_to_github()
        except Exception as e:
            print(f"  Daemon cycle error: {e}")

        interval = get_update_interval_minutes()
        next_time = datetime.now() + timedelta(minutes=interval)
        print(f"  Next sync at {next_time.strftime('%H:%M')} (in {interval} min)")
        time.sleep(interval * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    if args.once:
        sync_once()
        deploy_to_github()
    else:
        run_daemon()
