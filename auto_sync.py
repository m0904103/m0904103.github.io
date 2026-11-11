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
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, timezone
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 設定
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'frontend', 'public', 'scan_results.json')

# TWSE 官方即時報價 API
import urllib3
urllib3.disable_warnings()
TWSE_REALTIME_URL = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
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
    return now >= us_open or now.hour <= 5


def get_update_interval_minutes():
    """Return appropriate update interval based on market status."""
    if is_tw_trading_hours() or is_us_trading_hours():
        return 5   # Upgraded to 5 min ultra-fast mode for live market tracking
    else:
        return 60  # Every 60 min outside trading hours


# ==========================================
# TWSE 備援數據源
# ==========================================
def get_twse_prices(symbols):
    """Fetch TW stock prices from official TWSE real-time API (0-delay, supports TSE & OTC + bid/ask fallback)."""
    prices = {}
    tw_syms = [s for s in symbols if '.TW' in s or '.TWO' in s]
    if not tw_syms:
        return prices

    codes = ["tse_t00.tw"]
    sym_map = {"t00": "^TWII"}
    for sym in tw_syms:
        code = sym.replace('.TWO', '').replace('.TW', '')
        prefix = "otc" if ".TWO" in sym else "tse"
        codes.append(f"{prefix}_{code}.tw")
        sym_map[code] = sym

    batch_size = 20
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i + batch_size]
        try:
            params = {"ex_ch": "|".join(batch), "json": "1", "delay": "0"}
            resp = requests.get(TWSE_REALTIME_URL, params=params, headers=TWSE_HEADERS, verify=False, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("msgArray", []):
                    code = item.get("c", "")
                    z = item.get("z", "-")
                    b = item.get("b", "").split("_")[0]
                    a = item.get("a", "").split("_")[0]
                    y = item.get("y", "-")
                    o_str = item.get("o", "-")
                    h_str = item.get("h", "-")
                    l_str = item.get("l", "-")
                    v_str = item.get("v", "0")
                    p_str = z if (z and z != "-") else (b if (b and b != "-") else a)
                    if p_str and p_str != "-":
                        p_val = round(float(p_str), 2)
                        full_sym = sym_map.get(code, f"{code}.TW")
                        prices[full_sym] = {
                            "price": p_val,
                            "prev_close": round(float(y), 2) if y and y != "-" else None,
                            "open": round(float(o_str), 2) if o_str and o_str != "-" else p_val,
                            "high": round(float(h_str), 2) if h_str and h_str != "-" else p_val,
                            "low": round(float(l_str), 2) if l_str and l_str != "-" else p_val,
                            "volume": float(v_str) * 1000.0 if v_str and v_str != "-" else 0.0,
                            "date": item.get("d", ""),
                            "source": "TWSE"
                        }
                time.sleep(0.25)
        except Exception as e:
            print(f"  [TWSE batch error: {e}]")
    return prices

def fetch_tw_institutional_data(existing_indices):
    """Fetch live Taiwan institutional buy/sell, margin balance, TAIFEX OI, PCR & VIX."""
    import re
    inst = dict(existing_indices or {})
    now = datetime.now()
    dates_to_try = [(now - timedelta(days=d)) for d in range(5) if (now - timedelta(days=d)).weekday() < 5]

    # 1. TWSE BFI82U (三大法人買賣超金額)
    for dt_obj in dates_to_try:
        ymd = dt_obj.strftime('%Y%m%d')
        try:
            r = requests.get(f'https://www.twse.com.tw/rwd/zh/fund/BFI82U?response=json&dayDate={ymd}', headers=TWSE_HEADERS, verify=False, timeout=8)
            j = r.json()
            if j.get('stat') == 'OK' and j.get('data'):
                rows = j['data']
                def parse_num(s):
                    return float(str(s).replace(',', '').strip())
                dealer = 0.0
                trust = 0.0
                foreign = 0.0
                total = 0.0
                for row in rows:
                    label = row[0]
                    val = parse_num(row[3]) / 1e8
                    if '合計' in label:
                        total = val
                    elif '外資' in label:
                        foreign += val
                    elif '投信' in label:
                        trust += val
                    elif '自營商' in label:
                        dealer += val
                inst['三大法人買賣超 (億)'] = {'close': round(total, 2)}
                inst['三大法人買賣超'] = {'close': round(total, 2)}
                inst['外資買賣超 (億)'] = {'close': round(foreign, 2)}
                inst['外資買賣超'] = {'close': round(foreign, 2)}
                inst['投信買賣超 (億)'] = {'close': round(trust, 2)}
                inst['投信買賣超'] = {'close': round(trust, 2)}
                inst['自營買賣超 (億)'] = {'close': round(dealer, 2)}
                inst['自營買賣超'] = {'close': round(dealer, 2)}
                print(f"  [TWSE BFI82U {ymd}] 三大法人={total:.2f}億, 外資={foreign:.2f}億, 投信={trust:.2f}億")
                break
        except Exception as e:
            print(f"  [TWSE BFI82U {ymd}] err: {e}")

    # 2. TWSE MI_MARGN (上市融資餘額)
    try:
        r_m = requests.get('https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?response=json&selectType=MS', headers=TWSE_HEADERS, verify=False, timeout=8)
        jm = r_m.json()
        for tb in jm.get('tables', []):
            for row in tb.get('data', []):
                if '融資金額' in row[0]:
                    bal_yi = round(float(str(row[-1]).replace(',', '').strip()) / 1e5, 2)
                    inst['上市融資餘額 (億)'] = {'close': bal_yi}
                    print(f"  [TWSE MI_MARGN] 上市融資餘額={bal_yi}億")
                    break
    except Exception as e:
        print(f"  [TWSE MI_MARGN] err: {e}")

    # 3. TAIFEX TXF/MXF/TMF Open Interest
    for dt_obj in dates_to_try:
        qdate = dt_obj.strftime('%Y/%m/%d')
        try:
            r_txf = requests.post('https://www.taifex.com.tw/cht/3/futContractsDateDown', data={
                'queryStartDate': qdate, 'queryEndDate': qdate, 'commodityId': 'TXF'
            }, headers=TWSE_HEADERS, verify=False, timeout=10)
            txt = r_txf.content.decode('big5', errors='ignore')
            lines = [l.strip() for l in txt.splitlines() if l.strip()]
            if len(lines) >= 4 and '外資及陸資' in txt:
                foreign_txf = None
                trust_txf = None
                dealer_txf = None
                for l in lines[1:]:
                    cols = l.split(',')
                    if len(cols) >= 14:
                        role = cols[2]
                        net_oi = int(cols[13])
                        if '外資' in role:
                            foreign_txf = net_oi
                        elif '投信' in role:
                            trust_txf = net_oi
                        elif '自營商' in role:
                            dealer_txf = net_oi
                if foreign_txf is not None:
                    inst['外資台指淨未平倉 (口)'] = {'close': foreign_txf}
                    inst['外資台指淨未平倉'] = {'close': foreign_txf}
                    inst['外資台指期未平倉'] = {'close': foreign_txf}
                    inst['外資台指期留倉 (純大台)'] = {'close': foreign_txf}
                    if trust_txf is not None:
                        inst['投信期貨未平倉'] = {'close': trust_txf}
                    if dealer_txf is not None:
                        inst['自營商期貨未平倉'] = {'close': dealer_txf}
                    print(f"  [TAIFEX TXF {qdate}] 外資淨未平倉={foreign_txf}口")
                    break
        except Exception as e:
            print(f"  [TAIFEX TXF {qdate}] err: {e}")

    # 4. TAIFEX Put/Call Ratio
    try:
        r_pcr = requests.post('https://www.taifex.com.tw/cht/3/pcRatio', data={
            'queryStartDate': (now - timedelta(days=10)).strftime('%Y/%m/%d'),
            'queryEndDate': now.strftime('%Y/%m/%d')
        }, headers=TWSE_HEADERS, verify=False, timeout=10)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', r_pcr.text, re.S)
        for row in rows[:10]:
            cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c)).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S)]
            if cells and '202' in cells[0] and len(cells) >= 7:
                pcr_val = float(cells[6].replace(',', ''))
                inst['全市場Put/Call Ratio'] = {'close': pcr_val}
                inst['全市場 P/C Ratio'] = {'close': pcr_val}
                print(f"  [TAIFEX PCR {cells[0]}] P/C Ratio={pcr_val}%")
                break
    except Exception as e:
        print(f"  [TAIFEX PCR] err: {e}")

    # 5. TAIFEX VIX
    try:
        r_vix = requests.get('https://mis.taifex.com.tw/futures/VolatilityQuotes/', headers=TWSE_HEADERS, verify=False, timeout=10)
        if r_vix.status_code == 200:
            nums = re.findall(r'(\d{2,3}\.\d{2})', r_vix.content.decode('utf-8', errors='ignore'))
            valid = [float(n) for n in nums if 5.0 < float(n) < 120.0]
            if valid:
                inst['台指VIX (波動率)'] = {'close': round(valid[0], 2)}
                inst['台指 VIX (波動率)'] = {'close': round(valid[0], 2)}
                print(f"  [TAIFEX VIX] 台指VIX={valid[0]}")
    except Exception as e:
        print(f"  [TAIFEX VIX] err: {e}")

    return inst

def get_taifex_oi(indices=None):
    """Return latest TAIFEX Foreign Institutional Net Open Interest."""
    if indices:
        for k in ['外資台指淨未平倉 (口)', '外資台指期未平倉', '外資台指淨未平倉']:
            if k in indices and indices[k].get('close') is not None:
                return int(indices[k]['close'])
    return -103473


def get_v4_macro_climate():
    """Calculate V4-Yen dual-market macro climate shields (SPY/TNX for US, TWII/TWD=X for TW)."""
    macro = {
        'us': {'market_ok': True, 'half_size': False, 'hint': '🟢 美股氣候穩健'},
        'tw': {'market_ok': True, 'half_size': False, 'hint': '🟢 台股氣候穩健'},
    }
    try:
        spy_t = yf.Ticker('SPY')
        spy = spy_t.history(period='1y').dropna(subset=['Close'])
        tnx = yf.Ticker('^TNX').history(period='1mo').dropna(subset=['Close'])
        if not spy.empty and len(spy) >= 65:
            spy_c = float(spy['Close'].iloc[-1])
            spy_ma60 = float(spy['Close'].rolling(60).mean().iloc[-1])
            spy_ma60_prev = float(spy['Close'].rolling(60).mean().iloc[-6])
            spy_ma200 = float(spy['Close'].rolling(200).mean().iloc[-1]) if len(spy) >= 200 else spy_ma60
            tnx_v = float(tnx['Close'].iloc[-1]) if not tnx.empty else 4.5
            bear = (spy_c < spy_ma60 * 0.96) or (spy_c < spy_ma200 and spy_ma60 < spy_ma60_prev)
            if bear:
                macro['us'] = {'market_ok': False, 'half_size': True, 'hint': f'🐻 美股熊市總開關啟動 (SPY {spy_c:.1f} < MA60 {spy_ma60:.1f} 或 MA200 {spy_ma200:.1f})'}
            elif tnx_v >= 4.90:
                macro['us'] = {'market_ok': True, 'half_size': True, 'hint': f'⚠️ 10Y美債殖利率偏高 ({tnx_v:.2f}%)，建議減半偵察 (SPY {spy_c:.1f} >= 季線 {spy_ma60:.1f})'}
            else:
                macro['us'] = {'market_ok': True, 'half_size': False, 'hint': f'🟢 美股氣候穩健 (SPY {spy_c:.1f} >= 季線 {spy_ma60:.1f}，10Y美債 {tnx_v:.2f}%)'}
    except Exception as e:
        print(f"  [V4 Macro US err] {e}")

    try:
        twii_t = yf.Ticker('^TWII')
        twii = twii_t.history(period='6mo').dropna(subset=['Close'])
        twd = yf.Ticker('TWD=X').history(period='2mo').dropna(subset=['Close'])
        if not twii.empty and len(twii) >= 60:
            last_px = None
            try:
                last_px = twii_t.fast_info.get('lastPrice')
            except Exception:
                pass
            tw_c = float(last_px or twii['Close'].iloc[-1])
            tw_m60 = float(twii['Close'].rolling(60).mean().iloc[-1])
            if tw_c < tw_m60 * 0.93:
                macro['tw'] = {'market_ok': False, 'half_size': True, 'hint': f'🐻 台股加權 ({tw_c:.0f}) 跌破季線 ({tw_m60:.0f}) 7% 以上，鎖住開槍'}
            elif not twd.empty and len(twd) >= 20:
                fx_c = float(twd['Close'].iloc[-1])
                fx_m20 = float(twd['Close'].rolling(20).mean().iloc[-1])
                if fx_c <= fx_m20 * 1.002:
                    macro['tw'] = {'market_ok': True, 'half_size': False, 'hint': f'🟢 台幣升值順風 ({fx_c:.2f} <= 月線 {fx_m20:.2f}，20日勝率80.4%)'}
                else:
                    macro['tw'] = {'market_ok': True, 'half_size': True, 'hint': f'⚠️ 台幣貶值逆風 ({fx_c:.2f} > 月線 {fx_m20:.2f}，歷史勝率68.4%)，減半輕試'}
    except Exception as e:
        print(f"  [V4 Macro TW err] {e}")
    return macro


def patch_tw_latest_bar(df, sym, twse_entry):
    """Ensure TW DataFrame reflects latest TWSE / fast_info bar when Yahoo daily Close lags or drops NaN."""
    if df is None or df.empty:
        return df, None, "Yahoo"

    last_idx = df.index[-1]
    last_date_str = last_idx.strftime('%Y-%m-%d') if hasattr(last_idx, 'strftime') else str(last_idx)[:10]
    yahoo_close = float(df['Close'].iloc[-1])

    # 1. Check TWSE MIS entry first (0-delay official Taiwan price)
    if twse_entry and twse_entry.get("price"):
        twse_px = float(twse_entry["price"])
        raw_d = str(twse_entry.get("date") or "")
        twse_date = f"{raw_d[:4]}-{raw_d[4:6]}-{raw_d[6:8]}" if len(raw_d) == 8 else last_date_str
        prev_c = twse_entry.get("prev_close")
        # If TWSE date is newer than Yahoo's last valid close row, append a clean bar
        if twse_date > last_date_str or (twse_date == last_date_str and abs(twse_px - yahoo_close) > 1e-6):
            new_row = {
                'Open': float(twse_entry.get('open') or twse_px),
                'High': float(twse_entry.get('high') or twse_px),
                'Low': float(twse_entry.get('low') or twse_px),
                'Close': twse_px,
                'Volume': float(twse_entry.get('volume') or df['Volume'].iloc[-1]),
            }
            if twse_date > last_date_str:
                new_idx = pd.Timestamp(f"{twse_date} 00:00:00", tz=df.index.tz)
                df = pd.concat([df, pd.DataFrame([new_row], index=[new_idx])])
            else:
                for col, val in new_row.items():
                    if col in df.columns:
                        df.iloc[-1, df.columns.get_loc(col)] = val
            return df, prev_c, "TWSE"
        return df, prev_c, "TWSE" if is_tw_trading_hours() else "Yahoo"

    # 2. Fallback to Yahoo fast_info when TWSE MIS missed the ticker (e.g. OTC mismatch)
    if '.TW' in sym or '.TWO' in sym:
        try:
            fi = yf.Ticker(sym).fast_info
            fi_px = fi.get('lastPrice')
            fi_prev = fi.get('previousClose') or fi.get('regularMarketPreviousClose')
            if fi_px and float(fi_px) > 0 and abs(float(fi_px) - yahoo_close) > max(0.01, yahoo_close * 0.002):
                fi_open = float(fi.get('open') or fi_px)
                fi_high = float(fi.get('dayHigh') or max(fi_open, float(fi_px)))
                fi_low = float(fi.get('dayLow') or min(fi_open, float(fi_px)))
                fi_vol = float(fi.get('lastVolume') or df['Volume'].iloc[-1])
                new_idx = last_idx + pd.Timedelta(days=1)
                new_row = {'Open': fi_open, 'High': fi_high, 'Low': fi_low, 'Close': float(fi_px), 'Volume': fi_vol}
                df = pd.concat([df, pd.DataFrame([new_row], index=[new_idx])])
                return df, (float(fi_prev) if fi_prev else yahoo_close), "Yahoo-Fast"
        except Exception:
            pass

    return df, None, "Yahoo"


# ==========================================
# 主同步邏輯（V4-Yen 雙源 + 交叉驗證）
# ==========================================
def sync_once():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting V4-Yen sync... (TW={is_tw_trading_hours()}, US={is_us_trading_hours()})")

    if not os.path.exists(DATA_FILE):
        print("ERROR: scan_results.json not found!")
        return False

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_stocks = {s['symbol']: s for s in data.get('stocks', [])}
    if len(existing_stocks) < 10:
        backup_file = os.path.join(SCRIPT_DIR, 'backup_scan_results.json')
        if os.path.exists(backup_file):
            print("  ⚠️ Warning: Current data stocks count < 10! Restoring from backup...")
            try:
                with open(backup_file, 'r', encoding='utf-8') as bf:
                    bdata = json.load(bf)
                    existing_stocks = {s['symbol']: s for s in bdata.get('stocks', [])}
            except Exception as e:
                print(f"  Backup restore error: {e}")

    all_symbols = list(existing_stocks.keys())
    tw_symbols = [s for s in all_symbols if '.TW' in s or '.TWO' in s]

    # Step 1: 一律向 TWSE 抓取台股官方最新報價（含盤中即時與盤後正式收盤價，補救 Yahoo 延遲）
    print(f"  Fetching TWSE official quotes for {len(tw_symbols)} TW stocks...")
    twse_prices = get_twse_prices(tw_symbols)
    print(f"  TWSE returned {len(twse_prices)} prices.")

    # Step 1.5: 計算 V4-Yen 雙市場總經氣候護盾
    v4_macro = get_v4_macro_climate()
    print(f"  V4-Yen Macro US: {v4_macro['us']['hint']}")
    print(f"  V4-Yen Macro TW: {v4_macro['tw']['hint']}")

    # Step 2: 用 Yahoo Finance 批量更新全部股票
    updated_count = 0
    cross_check_alerts = []

    print(f"  Bulk downloading {len(all_symbols)} tickers from Yahoo Finance...", flush=True)
    bulk_data = {}
    try:
        df_bulk = yf.download(all_symbols, period='1y', group_by='ticker', threads=True, progress=False)
        for sym in all_symbols:
            try:
                if len(all_symbols) == 1:
                    stock_df = df_bulk.dropna(subset=['Close'])
                else:
                    stock_df = df_bulk[sym].dropna(subset=['Close'])
                if not stock_df.empty and len(stock_df) >= 2:
                    bulk_data[sym] = stock_df
            except Exception:
                pass
    except Exception as e:
        print(f"  Bulk download notice: {e}", flush=True)

    for sym in all_symbols:
        stock_obj = existing_stocks[sym]
        name = stock_obj.get('name', sym)
        try:
            df = bulk_data.get(sym)
            if df is None or df.empty or 'Close' not in df.columns:
                try:
                    df = yf.Ticker(sym).history(period='1y')
                    if df is not None and not df.empty and 'Close' in df.columns:
                        df = df.dropna(subset=['Close'])
                except Exception:
                    pass

            if df is None or df.empty or 'Close' not in df.columns:
                print(f"  {sym}: No data available.", flush=True)
                continue

            df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
            if df.empty:
                print(f"  {sym}: No valid close data available.", flush=True)
                continue

            is_tw_sym = ('.TW' in sym or '.TWO' in sym)
            twse_entry = twse_prices.get(sym) or twse_prices.get(sym.replace('.TWO', '.TW'))
            yahoo_raw_close = round(float(df['Close'].iloc[-1]), 2)
            if twse_entry and twse_entry.get("price") and yahoo_raw_close > 0:
                diff_pct = abs((twse_entry["price"] - yahoo_raw_close) / yahoo_raw_close * 100)
                if diff_pct > 1.5:
                    cross_check_alerts.append(
                        f"  INFO: {sym} Yahoo={yahoo_raw_close} vs TWSE={twse_entry['price']} diff={diff_pct:.1f}% -> using TWSE/latest bar"
                    )

            override_prev = None
            price_source = "Yahoo"
            if is_tw_sym:
                df, override_prev, price_source = patch_tw_latest_bar(df, sym, twse_entry)

            final_price = round(float(df['Close'].iloc[-1]), 2)
            prev_close = float(override_prev) if (override_prev and override_prev > 0) else (float(df['Close'].iloc[-2]) if len(df) > 1 else final_price)

            # Also write latest 120-bar history file for K-line chart (both history/ and assets/)
            try:
                hist_dir = os.path.join(SCRIPT_DIR, 'frontend', 'public', 'history')
                assets_dir = os.path.join(SCRIPT_DIR, 'frontend', 'public', 'assets')
                os.makedirs(hist_dir, exist_ok=True)
                os.makedirs(assets_dir, exist_ok=True)
                df_copy = df.copy()
                df_copy['ma60_roll'] = df_copy['Close'].rolling(window=60).mean()
                hist_df = df_copy.tail(120)
                hist_records = []
                seen_dates = set()
                for idx_dt, row_h in hist_df.iterrows():
                    d_str = idx_dt.strftime('%Y-%m-%d') if hasattr(idx_dt, 'strftime') else str(idx_dt)[:10]
                    if d_str in seen_dates:
                        continue
                    seen_dates.add(d_str)
                    ma60_v = row_h.get('ma60_roll')
                    hist_records.append({
                        'time': d_str,
                        'open': round(float(row_h.get('Open', row_h['Close'])), 2),
                        'high': round(float(row_h.get('High', row_h['Close'])), 2),
                        'low': round(float(row_h.get('Low', row_h['Close'])), 2),
                        'close': round(float(row_h['Close']), 2),
                        'ma60': round(float(ma60_v), 2) if ma60_v is not None and not math.isnan(float(ma60_v)) else None,
                        'volume': int(float(row_h.get('Volume', 0) or 0))
                    })
                with open(os.path.join(hist_dir, f'{sym}.json'), 'w', encoding='utf-8') as hf:
                    json.dump(hist_records, hf, ensure_ascii=False)
                with open(os.path.join(assets_dir, f'history_{sym}.json'), 'w', encoding='utf-8') as af:
                    json.dump(hist_records, af, ensure_ascii=False)
            except Exception:
                pass

            change = round(((final_price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0

            # ==============================================================
            # 顏老師 V4-Yen 雙師 11.2 年大數據核心計量評級
            # ==============================================================
            valid_c = df['Close'].dropna()
            ma60_series = valid_c.rolling(60).mean()
            ma60 = round(float(ma60_series.iloc[-1]), 2) if len(valid_c) >= 60 else final_price
            ma60_prev5 = round(float(ma60_series.iloc[-6]), 2) if len(ma60_series.dropna()) >= 6 else ma60
            ma60_slope5 = round(ma60 - ma60_prev5, 4)
            ma200 = round(float(valid_c.iloc[-200:].mean()), 2) if len(valid_c) >= 200 else stock_obj.get('ma200')
            if ma200:
                stock_obj['ma200'] = ma200

            ma20 = float(valid_c.rolling(20).mean().iloc[-1]) if len(valid_c) >= 20 else final_price
            std20 = float(valid_c.rolling(20).std().iloc[-1]) if len(valid_c) >= 20 else final_price * 0.02
            if math.isnan(std20):
                std20 = final_price * 0.02
            bb_lower = round(ma20 - 2.0 * std20, 2)
            bb_upper = round(ma20 + 2.0 * std20, 2)

            low3 = float(df['Low'].iloc[-3:].min()) if len(df) >= 3 else float(df['Low'].iloc[-1])
            hl = df['High'] - df['Low']
            hc = (df['High'] - df['Close'].shift(1)).abs()
            lc = (df['Low'] - df['Close'].shift(1)).abs()
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            atr14 = float(tr.rolling(14).mean().iloc[-1]) if len(tr) >= 14 else final_price * 0.02
            if math.isnan(atr14) or atr14 <= 0:
                atr14 = final_price * 0.02

            vol20 = float(df['Volume'].iloc[-21:-1].mean()) if len(df) >= 22 else float(df['Volume'].mean() or 1.0)
            last_vol = float(df['Volume'].iloc[-1] or 0.0)
            vol_ratio = round(last_vol / vol20, 2) if vol20 > 0 else 1.0

            delta_c = valid_c.diff()
            gain = delta_c.clip(lower=0).rolling(14).mean()
            loss = (-delta_c.clip(upper=0)).rolling(14).mean()
            rs = gain / loss.replace(0, float('nan'))
            rsi_s = 100.0 - (100.0 / (1.0 + rs))
            rsi14 = float(rsi_s.iloc[-1]) if not rsi_s.empty and not pd.isna(rsi_s.iloc[-1]) else 50.0

            l9 = df['Low'].rolling(9).min()
            h9 = df['High'].rolling(9).max()
            rsv = 100.0 * (df['Close'] - l9) / (h9 - l9).replace(0, float('nan'))
            kd_k, kd_d = 50.0, 50.0
            for r_val in rsv:
                if pd.notna(r_val):
                    kd_k = (2.0 / 3.0) * kd_k + (1.0 / 3.0) * float(r_val)
                    kd_d = (2.0 / 3.0) * kd_d + (1.0 / 3.0) * kd_k

            day_open = float(df['Open'].iloc[-1])
            day_high = float(df['High'].iloc[-1])
            day_low = float(df['Low'].iloc[-1])
            close_pos = (final_price - day_low) / max(day_high - day_low, 1e-6) if day_high > day_low else 0.6

            mkt_key = 'tw' if is_tw_sym else 'us'
            macro_ok = bool(v4_macro[mkt_key]['market_ok'])

            # V4-Yen 六大鐵律檢定
            is_regular = final_price >= ma60
            is_trend_ok = bool(is_regular and ma60_slope5 > 0 and (ma200 is None or final_price >= ma200))
            is_sweet_spot = bool(final_price <= bb_lower * 1.05)
            is_kd_rsi_ok = bool(kd_k <= 50.0 and kd_k > kd_d and rsi14 <= 55.0)
            is_red_strong = bool(final_price >= day_open and close_pos >= 0.55)
            is_vol_ok = bool(0.90 <= vol_ratio <= 2.50)

            v4_trigger = bool(macro_ok and is_trend_ok and is_sweet_spot and is_kd_rsi_ok and is_red_strong and is_vol_ok)
            v4_watch = bool(is_trend_ok and is_sweet_spot and not v4_trigger)

            # Score & Signal aligned with V4-Yen
            score_val = 45
            if ma200 and final_price < ma200:
                score_val -= 30
            if is_regular:
                score_val += 15
            else:
                score_val -= 20
            if ma60_slope5 > 0:
                score_val += 10
            if is_sweet_spot:
                score_val += 12
            if is_kd_rsi_ok:
                score_val += 10
            if is_red_strong:
                score_val += 8
            if is_vol_ok:
                score_val += 5
            if stock_obj.get('chips', {}).get('foreign_buy'):
                score_val += 5
            if stock_obj.get('fundamentals', {}).get('three_rates_rising'):
                score_val += 5
            final_score = int(max(10, min(99, score_val)))
            stock_obj['score'] = final_score

            if v4_trigger:
                signal = "Strong Buy"
                v4_tactic = "🚨 V4-Yen 精選狙擊觸發！季線↑+BBL+KD金叉+強紅K+健康量能共振"
            elif macro_ok and is_trend_ok and is_sweet_spot and (is_kd_rsi_ok or is_red_strong):
                signal = "Buy"
                v4_tactic = "⚡ V4-Yen 準觸發區：站穩MA60↑回測BBL甜蜜帶，待尾盤確認共振"
            elif is_regular:
                signal = "Hold"
                if v4_watch:
                    v4_tactic = f"👀 V4-Yen 一號追蹤候選：守季線{ma60}(↑)且入BBL*1.05帶，靜待轉紅K與KD金叉"
                else:
                    v4_tactic = f"🛡️ 站穩季線({ma60})多方正規軍（續抱觀察，嚴守買進低點防線）"
            else:
                signal = "Avoid"
                v4_tactic = f"⚠️ 跌破季線生命線({ma60})或季線走弱，反彈不追高、保留現金"

            stock_obj['tactic'] = v4_tactic
            stock_obj['vol_ratio'] = vol_ratio
            stock_obj['engine'] = 'V4-Yen'
            stock_obj['technicals'] = {
                **(stock_obj.get('technicals') or {}),
                'bb_lower': bb_lower,
                'bb_upper': bb_upper,
                'bb_lower_touch': is_sweet_spot,
                'bb_bounce': bool(is_sweet_spot and is_red_strong),
                'kd_k': round(kd_k, 1),
                'kd_d': round(kd_d, 1),
                'kd_oversold': bool(kd_k <= 35.0 and kd_k > kd_d),
                'rsi14': round(rsi14, 1),
                'ma60_slope5': ma60_slope5,
                'atr14': round(atr14, 2),
                'close_pos': round(close_pos, 2),
                'v4_watch': v4_watch,
                'v4_trigger': v4_trigger,
                'engine': 'V4-Yen',
            }

            # --- LEVEL 3 VOLUME SURGE ---
            vol_surge = False
            if len(df) >= 6:
                try:
                    vol_today = df['Volume'].iloc[-1]
                    vol_5d_avg = df['Volume'].iloc[-6:-1].mean()
                    # Today's volume > 2x the 5-day average, and closed green or relatively flat
                    if vol_today > (vol_5d_avg * 2) and final_price >= prev_close:
                        vol_surge = True
                except Exception:
                    pass

            # --- LEVEL 2 K-LINE & GAP DETECTION ---
            gap_up = False
            k_pattern = None
            if len(df) >= 2:
                try:
                    today = df.iloc[-1]
                    yest = df.iloc[-2]
                    
                    # 1. Gap Up: Today's Low > Yesterday's High
                    if today['Low'] > yest['High']:
                        gap_up = True
                    
                    # 2. Engulfing (吞噬線)
                    yest_is_red = yest['Close'] < yest['Open']
                    today_is_green = today['Close'] > today['Open']
                    engulfs = today['Open'] <= yest['Close'] and today['Close'] >= yest['Open']
                    if yest_is_red and today_is_green and engulfs:
                        k_pattern = "Engulfing"
                    
                    # 3. Harami (母子線)
                    yest_body = abs(yest['Open'] - yest['Close'])
                    today_body = abs(today['Open'] - today['Close'])
                    yest_is_long_red = yest_is_red and (yest_body / yest['Open'] > 0.015) # At least 1.5% body
                    inside_body = max(today['Open'], today['Close']) < yest['Open'] and min(today['Open'], today['Close']) > yest['Close']
                    if yest_is_long_red and inside_body and today_body < (yest_body * 0.5):
                        k_pattern = "Harami"
                except Exception:
                    pass

            stock_obj["close"] = final_price
            stock_obj["price"] = final_price
            stock_obj["price_source"] = price_source
            stock_obj["ma60"] = ma60
            stock_obj["change"] = change
            stock_obj["signal"] = signal
            stock_obj["is_regular"] = is_regular
            stock_obj["market"] = "tw" if ".TW" in sym or ".TWO" in sym else "us"
            stock_obj["gap_up"] = gap_up
            stock_obj["k_pattern"] = k_pattern
            stock_obj["vol_surge"] = vol_surge

            if "plan" not in stock_obj:
                stock_obj["plan"] = {}
            stock_obj["plan"]["entry"] = final_price
            stock_obj["plan"]["sl"] = round(max(low3 - 1.2 * atr14, final_price * 0.93), 2)
            stock_obj["plan"]["tp"] = round(final_price * 1.08, 2)

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
    
    # Update Indices dynamically (US VIX, TAIEX ^TWII, USD/TWD, TSM ADR Premium)
    indices = data.get('indices', {})
    try:
        vix_df = yf.Ticker('^VIX').history(period='5d')
        if not vix_df.empty:
            indices['US VIX (恐慌)'] = {'close': round(float(vix_df['Close'].dropna().iloc[-1]), 2)}
    except Exception as e:
        print(f"  [Indices] Failed to update US VIX: {e}")

    try:
        twii_t = yf.Ticker('^TWII')
        twii_df = twii_t.history(period='5d').dropna(subset=['Close'])
        twii_fi = None
        try:
            twii_fi = twii_t.fast_info.get('lastPrice')
        except Exception:
            pass
        if "^TWII" in twse_prices and twse_prices["^TWII"].get("price"):
            indices['加權指數'] = {'close': round(float(twse_prices["^TWII"]["price"]), 2)}
        elif twii_fi:
            indices['加權指數'] = {'close': round(float(twii_fi), 2)}
        elif not twii_df.empty:
            indices['加權指數'] = {'close': round(float(twii_df['Close'].iloc[-1]), 2)}
    except Exception as e:
        print(f"  [Indices] Failed to update ^TWII: {e}")

    try:
        fx_df = yf.Ticker('TWD=X').history(period='5d').dropna(subset=['Close'])
        if not fx_df.empty:
            usd_twd = round(float(fx_df['Close'].iloc[-1]), 3)
            indices['美金/台幣'] = {'close': usd_twd}
    except Exception as e:
        print(f"  [Indices] Failed to update TWD=X: {e}")

    try:
        tnx_df = yf.Ticker('^TNX').history(period='5d').dropna(subset=['Close'])
        if not tnx_df.empty:
            indices['10Y美債殖利率'] = {'close': round(float(tnx_df['Close'].iloc[-1]), 2)}
    except Exception as e:
        print(f"  [Indices] Failed to update ^TNX: {e}")

    indices['V4_Yen_US_Macro'] = v4_macro['us']
    indices['V4_Yen_TW_Macro'] = v4_macro['tw']
    data['engine'] = 'V4-Yen'

    try:
        tsm_adr_p = existing_stocks.get('TSM', {}).get('close')
        tsm_tw_p = existing_stocks.get('2330.TW', {}).get('close')
        fx_p = indices.get('美金/台幣', {}).get('close', 32.8)
        if tsm_adr_p and tsm_tw_p and fx_p:
            indices['TSM_ADR'] = {'close': tsm_adr_p}
            indices['TSM_TW'] = {'close': tsm_tw_p}
            prem = round(((tsm_adr_p * fx_p / 5.0) - tsm_tw_p) / tsm_tw_p * 100, 2)
            indices['adr_premium'] = {'close': prem}
    except Exception as e:
        print(f"  [Indices] Failed to update ADR premium: {e}")
        
    # Dynamically fetch latest official TWSE + TAIFEX institutional & VIX data
    indices = fetch_tw_institutional_data(indices)
    
    data['indices'] = indices
    
    data['taifex_oi'] = get_taifex_oi(indices)
    now_utc = datetime.now(timezone.utc)
    data['last_updated'] = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')  # UTC ISO format - timezone safe
    data['updated_at'] = (now_utc + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S')

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

    if "^TWII" in twse_prices and twse_prices["^TWII"].get("price"):
        data["indices"]["加權指數"] = {"close": twse_prices["^TWII"]["price"]}

    tmp_file = DATA_FILE + ".tmp"
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
    os.replace(tmp_file, DATA_FILE)

    live_portfolio_file = os.path.join(SCRIPT_DIR, 'frontend', 'public', 'live_portfolio.json')
    with open(live_portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)

    print(f"  Updated {updated_count}/{len(all_symbols)} stocks.")
    return True


def deploy_to_github():
    """Run scan_tw_big_data.py, build frontend, and push to GitHub."""
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
