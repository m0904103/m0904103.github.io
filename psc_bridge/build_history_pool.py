# -*- coding: utf-8 -*-
r"""
20 年大數據歷史日 K 資料池建置與真實回測引擎
將全站 260 檔標的（最長 20 年，2006~2026）存入 D:\PSC_Quant_DB\market_history.db，
並更新輕量 360 日（1.5 年含 MA60/MA200）JSON 至 q_quant_888/history/ 供前端圖表使用，
同時重算真實 5 年與 20 年雙師波段勝率寫回 scan_results.json。
r"""
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = r'C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io'
SCAN_FILE = os.path.join(BASE_DIR, 'scan_results.json')
WEB_DIR = os.path.join(BASE_DIR, 'q_quant_888')
DB_DIR = r'D:\PSC_Quant_DB'
HIST_DB = os.path.join(DB_DIR, 'market_history.db')


def run_v4_backtest(df, years_limit=None):
    r"""對齊顏老師第8講：站穩60MA＋布林下軌止跌反彈進場，買進日低點停損 / 突破上軌拉回停利r"""
    if df is None or len(df) < 80:
        return {'win_rate': 0.0, 'total_return': 0.0, 'trade_count': 0}

    sub = df.copy()
    if years_limit is not None:
        cutoff = sub.index.max() - pd.DateOffset(years=years_limit)
        sub = sub[sub.index >= cutoff]
        if len(sub) < 80:
            return {'win_rate': 0.0, 'total_return': 0.0, 'trade_count': 0}

    c = sub['Close']
    o = sub['Open']
    l = sub['Low']
    h = sub['High']
    ma20 = c.rolling(20).mean()
    std20 = c.rolling(20).std()
    bb_up = ma20 + 2 * std20
    bb_dn = ma20 - 2 * std20
    ma60 = c.rolling(60).mean()

    low9 = l.rolling(9).min()
    high9 = h.rolling(9).max()
    rsv = ((c - low9) / (high9 - low9).replace(0, np.nan)) * 100
    k_vals = []
    k = 50.0
    for v in rsv:
        k = (2 / 3) * k + (1 / 3) * v if pd.notna(v) else k
        k_vals.append(k)
    k_ser = pd.Series(k_vals, index=sub.index)

    trades = []
    in_pos = False
    entry_p = 0.0
    stop_p = 0.0
    hit_upper = False
    hold_days = 0

    for i in range(60, len(sub)):
        ci = float(c.iloc[i])
        oi = float(o.iloc[i])
        li = float(l.iloc[i])
        hi = float(h.iloc[i])
        m60 = float(ma60.iloc[i])
        m60_prev = float(ma60.iloc[i - 1])
        b_dn = float(bb_dn.iloc[i])
        b_up = float(bb_up.iloc[i])
        ki = float(k_ser.iloc[i])

        if not in_pos:
            # 站穩季線且季線向上 + 回測布林下軌甜蜜帶或KD<30止跌收紅K
            if ci > m60 and m60 >= m60_prev and ci > oi and (ci <= b_dn * 1.03 or ki < 30):
                in_pos = True
                entry_p = ci
                stop_p = li
                hit_upper = False
                hold_days = 0
        else:
            hold_days += 1
            if hi >= b_up:
                hit_upper = True
            exit_now = False
            if ci < stop_p:
                exit_now = True
            elif hit_upper and ci < b_up:
                exit_now = True
            elif hold_days >= 40:
                exit_now = True

            if exit_now:
                ret = (ci - entry_p) / entry_p
                trades.append(ret)
                in_pos = False

    if not trades:
        return {'win_rate': 0.0, 'total_return': 0.0, 'trade_count': 0}

    wins = sum(1 for r in trades if r > 0)
    comp = float(np.prod([1.0 + r for r in trades]) - 1.0)
    return {
        'win_rate': round(wins / len(trades) * 100, 1),
        'total_return': round(comp * 100, 1),
        'trade_count': len(trades)
    }


def main():
    os.makedirs(DB_DIR, exist_ok=True)
    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        scan_data = json.load(f)

    stocks = scan_data.get('stocks', [])
    symbols = [str(s.get('symbol', '')).strip() for s in stocks if s.get('symbol')]
    print(f"準備建置 20 年歷史日 K 資料池，共 {len(symbols)} 檔標的...")

    conn = sqlite3.connect(HIST_DB)
    cur = conn.cursor()
    cur.execute(r"""
        CREATE TABLE IF NOT EXISTS daily_bars (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            ma20 REAL,
            ma60 REAL,
            ma200 REAL,
            PRIMARY KEY (symbol, date)
        )
    r""")
    cur.execute(r"""
        CREATE TABLE IF NOT EXISTS backtest_summary (
            symbol TEXT PRIMARY KEY,
            bars_count INTEGER,
            start_date TEXT,
            end_date TEXT,
            win_rate_5y REAL,
            ret_5y REAL,
            trades_5y INTEGER,
            win_rate_20y REAL,
            ret_20y REAL,
            trades_20y INTEGER,
            updated_at TEXT
        )
    r""")
    conn.commit()

    # 分批下載 20 年 (2006-11-15 ~ 2026-11-15)
    start_dt = '2006-11-15'
    batch_size = 40
    downloaded = {}
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        print(f"下載批次 {i//batch_size + 1}/{(len(symbols)-1)//batch_size + 1} ({len(batch)} 檔)...")
        data = yf.download(batch, start=start_dt, auto_adjust=True, group_by='ticker', threads=True, progress=False)
        for sym in batch:
            try:
                df = data[sym] if len(batch) > 1 else data
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna(subset=['Close'])
                if not df.empty:
                    downloaded[sym] = df
            except Exception:
                pass

    # 若有 .TW 空檔則嘗試 .TWO
    missing_tw = [s for s in symbols if s not in downloaded and s.endswith('.TW')]
    if missing_tw:
        alt_map = {s.replace('.TW', '.TWO'): s for s in missing_tw}
        print(f"補抓櫃買 (.TWO) 標的 {len(alt_map)} 檔...")
        data2 = yf.download(list(alt_map.keys()), start=start_dt, auto_adjust=True, group_by='ticker', threads=True, progress=False)
        for alt, orig in alt_map.items():
            try:
                df = data2[alt] if len(alt_map) > 1 else data2
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna(subset=['Close'])
                if not df.empty:
                    downloaded[orig] = df
            except Exception:
                pass

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hist_dirs = [d for d in [os.path.join(BASE_DIR, 'history'), os.path.join(WEB_DIR, 'history')] if os.path.exists(d)]

    updated_bt = 0
    for s in stocks:
        sym = str(s.get('symbol', '')).strip()
        df = downloaded.get(sym)
        if df is None or df.empty:
            continue

        df = df.copy()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA60'] = df['Close'].rolling(60).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        rows = []
        for idx, r in df.iterrows():
            rows.append((
                sym, idx.strftime('%Y-%m-%d'),
                round(float(r['Open']), 4), round(float(r['High']), 4),
                round(float(r['Low']), 4), round(float(r['Close']), 4),
                int(r['Volume']) if pd.notna(r['Volume']) else 0,
                round(float(r['MA20']), 4) if pd.notna(r['MA20']) else None,
                round(float(r['MA60']), 4) if pd.notna(r['MA60']) else None,
                round(float(r['MA200']), 4) if pd.notna(r['MA200']) else None,
            ))
        cur.executemany("INSERT OR REPLACE INTO daily_bars VALUES (?,?,?,?,?,?,?,?,?,?)", rows)

        bt_5y = run_v4_backtest(df, years_limit=5)
        bt_20y = run_v4_backtest(df, years_limit=20)
        cur.execute(
            "INSERT OR REPLACE INTO backtest_summary VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                sym, len(df), df.index[0].strftime('%Y-%m-%d'), df.index[-1].strftime('%Y-%m-%d'),
                bt_5y['win_rate'], bt_5y['total_return'], bt_5y['trade_count'],
                bt_20y['win_rate'], bt_20y['total_return'], bt_20y['trade_count'],
                now_str
            )
        )

        # 更新 scan_results.json（優先採用 5Y 現代樣本，並附帶 20Y 欄位；若 5Y 樣本不足則用 20Y）
        last_ma60 = df['MA60'].iloc[-1]
        last_ma200 = df['MA200'].iloc[-1]
        if pd.notna(last_ma60):
            s['ma60'] = round(float(last_ma60), 2)
        if pd.notna(last_ma200):
            s['ma200'] = round(float(last_ma200), 2)

        chosen_bt = bt_5y if bt_5y['trade_count'] >= 3 else bt_20y
        s['backtest'] = {
            'win_rate': chosen_bt['win_rate'],
            'total_return': chosen_bt['total_return'],
            'trade_count': chosen_bt['trade_count'],
            'win_rate_20y': bt_20y['win_rate'],
            'total_return_20y': bt_20y['total_return'],
            'trade_count_20y': bt_20y['trade_count'],
            'history_years': round(len(df) / 252.0, 1)
        }
        updated_bt += 1

        # 寫出輕量 360 天（1.5 年）圖表 JSON 供前端繪圖
        tail_df = df.tail(360)
        chart_rows = []
        for idx, r in tail_df.iterrows():
            chart_rows.append({
                'time': idx.strftime('%Y-%m-%d'),
                'open': round(float(r['Open']), 2),
                'high': round(float(r['High']), 2),
                'low': round(float(r['Low']), 2),
                'close': round(float(r['Close']), 2),
                'ma60': round(float(r['MA60']), 2) if pd.notna(r['MA60']) else None,
                'ma200': round(float(r['MA200']), 2) if pd.notna(r['MA200']) else None,
                'volume': int(r['Volume']) if pd.notna(r['Volume']) else 0,
            })
        for hd in hist_dirs:
            with open(os.path.join(hd, f'{sym}.json'), 'w', encoding='utf-8') as hf:
                json.dump(chart_rows, hf, ensure_ascii=False)

    conn.commit()
    conn.close()

    scan_data['history_pool'] = {
        'db_path': HIST_DB,
        'symbols_synced': updated_bt,
        'max_years': 20,
        'chart_days': 360,
        'updated_at': now_str
    }
    with open(SCAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, ensure_ascii=False, indent=2)
    if os.path.exists(WEB_DIR):
        shutil.copy2(SCAN_FILE, os.path.join(WEB_DIR, 'scan_results.json'))
        shutil.copy2(SCAN_FILE, os.path.join(WEB_DIR, 'live_portfolio.json'))

    db_mb = os.path.getsize(HIST_DB) / (1024 * 1024)
    print(f"\n✅ 完成！已更新 {updated_bt}/{len(symbols)} 檔至 20 年 SQLite 資料池 ({HIST_DB}, {db_mb:.2f} MB) 與 360 天前端圖表 JSON。")


if __name__ == '__main__':
    main()
