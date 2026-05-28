"""
price_updater.py
================
輕量級即時價格更新器 (v1.0)
- 只更新 close / price / change 欄位，不重新計算 MA60/RSI/MACD
- 使用 yfinance fast_info，比 download(period="2y") 輕量 99%
- 安全頻率：每 30 分鐘一次，不觸碰 Yahoo Finance 速率限制
- 台股使用 TWSE 官方 OpenAPI（完全免費，無限制）
"""

import json
import os
import sys
import time
import requests
import yfinance as yf
from datetime import datetime

# ===== 路徑設定 =====
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATHS = [
    os.path.join(SCRIPT_DIR, "trading", "scan_results.json"),
    os.path.join(SCRIPT_DIR, "frontend", "public", "scan_results.json"),
    os.path.join(SCRIPT_DIR, "scan_results.json"),
]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== 台股即時價格：TWSE 官方 OpenAPI =====
def get_tw_price_official(symbol_tw):
    """
    使用 TWSE openapi.twse.com.tw 抓台股即時價格（完全免費、官方、無速率限制）
    symbol_tw 格式：'2330.TW' 或 '2330.TWO'
    """
    code = symbol_tw.replace(".TW", "").replace(".TWO", "")
    is_otc = ".TWO" in symbol_tw

    try:
        if is_otc:
            # 上櫃股票用 OTC API
            url = f"https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes?symbolId={code}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data and len(data) > 0:
                item = data[0]
                close = float(item.get("Close", 0) or 0)
                open_p = float(item.get("Open", 0) or 0)
                change = round(close - open_p, 2) if close and open_p else 0
                change_pct = round((change / open_p) * 100, 2) if open_p else 0
                return close, change_pct
        else:
            # 上市股票用 TWSE API
            url = f"https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
            resp = requests.get(url, timeout=8)
            data = resp.json()
            for item in data:
                if item.get("Code") == code:
                    close = float(item.get("ClosingPrice", 0) or 0)
                    open_p = float(item.get("OpeningPrice", 0) or 0)
                    change = round(close - open_p, 2) if close and open_p else 0
                    change_pct = round((change / open_p) * 100, 2) if open_p else 0
                    return close, change_pct
    except Exception as e:
        print(f"    [TWSE API Error] {symbol_tw}: {e}")
    return None, None

# ===== 美股即時價格：yfinance fast_info（超輕量）=====
def get_us_price_fast(symbol):
    """
    使用 yfinance Ticker.fast_info — 只抓單一快照，比 download(period='2y') 輕量 99%
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None)
        prev_close = getattr(info, "previous_close", None) or getattr(info, "regular_market_previous_close", None)
        if price and prev_close and prev_close > 0:
            change_pct = round(((price - prev_close) / prev_close) * 100, 2)
            return round(float(price), 2), change_pct
    except Exception as e:
        print(f"    [fast_info Error] {symbol}: {e}")
    return None, None

# ===== 主程式 =====
def main():
    print(f"\n{'='*60}")
    print(f"⚡ 輕量價格更新器 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # 找到存在的 JSON 檔案
    target_paths = [p for p in JSON_PATHS if os.path.exists(p)]
    if not target_paths:
        print("❌ 找不到 scan_results.json，請確認路徑。")
        sys.exit(1)

    # 以第一個路徑為主讀取
    data = load_json(target_paths[0])
    stocks = data if isinstance(data, list) else data.get("stocks", [])

    updated_count = 0
    tw_batch_done = False
    tw_all_prices = {}

    # 預先一次性抓取所有台股（TWSE API 一次回傳全部，極省請求次數）
    try:
        print("\n📡 預先批量下載台股報價（TWSE OpenAPI，一次請求）...")
        resp = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", timeout=10)
        for item in resp.json():
            code = item.get("Code", "")
            try:
                close = float(item.get("ClosingPrice", 0) or 0)
                open_p = float(item.get("OpeningPrice", 0) or 0)
                chg_pct = round(((close - open_p) / open_p) * 100, 2) if open_p > 0 else 0
                tw_all_prices[code] = (close, chg_pct)
            except:
                pass
        tw_batch_done = True
        print(f"    ✅ 成功下載 {len(tw_all_prices)} 筆台股報價")
    except Exception as e:
        print(f"    ⚠️ TWSE 批量下載失敗: {e}，將逐一查詢")

    # 逐一更新每檔股票的價格
    us_symbols_to_update = [s for s in stocks if isinstance(s, dict) and s.get("market") == "us"]
    print(f"\n📈 更新美股 {len(us_symbols_to_update)} 檔...")

    for i, stock in enumerate(us_symbols_to_update):
        sym = stock.get("symbol", "")
        price, change_pct = get_us_price_fast(sym)
        if price:
            stock["price"] = price
            stock["close"] = price
            stock["change"] = change_pct
            updated_count += 1
            print(f"    ✅ {sym}: ${price:>8.2f}  ({change_pct:+.2f}%)")
        else:
            print(f"    ⚠️ {sym}: 無法取得報價，保留舊值 ${stock.get('close', 0):.2f}")
        # 每 10 檔休息 1 秒，避免觸發速率限制
        if (i + 1) % 10 == 0:
            time.sleep(1)

    # 更新台股
    tw_symbols_to_update = [s for s in stocks if isinstance(s, dict) and s.get("market") == "tw"]
    print(f"\n🇹🇼 更新台股 {len(tw_symbols_to_update)} 檔...")
    for stock in tw_symbols_to_update:
        sym = stock.get("symbol", "")
        code = sym.replace(".TW", "").replace(".TWO", "")
        if tw_batch_done and code in tw_all_prices:
            price, chg_pct = tw_all_prices[code]
        else:
            price, chg_pct = get_tw_price_official(sym)

        if price and price > 0:
            stock["price"] = price
            stock["close"] = price
            stock["change"] = chg_pct
            updated_count += 1
            print(f"    ✅ {sym}: NT${price:>8.2f}  ({chg_pct:+.2f}%)")
        else:
            print(f"    ⚠️ {sym}: 無法取得報價")

    # 寫回所有 JSON 路徑
    for path in target_paths:
        save_json(path, data)
        print(f"\n💾 已儲存: {path}")

    print(f"\n{'='*60}")
    print(f"✅ 完成！共更新 {updated_count} 檔股票即時價格")
    print(f"   MA60 / RSI / 回測 等指標保持不變（每日收盤後才重算）")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
