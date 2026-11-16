# -*- coding: utf-8 -*-
"""
q_quant_888 × 統一金贏島 62欄原生 DATA 同步更新與 V4-Yen 高勝率對齊引擎
功能：
1. 讀取 scan_results.json 全站 260 檔標的（139 台股 + 121 美股），轉換為統一金贏島代碼。
2. 透過 PSCQuoteEngine.exe 一次抓取全站 260 檔的即時價格、漲跌幅、均價、五檔與內外盤比。
3. 將最新統一即時數據回寫進 scan_results.json（保留原有 V4-Yen 技術面/回測勝率指標並更新現價、漲跌幅、price_source 與內外盤資料）。
4. 嚴格對齊網站「V4-Yen 高勝率買進邏輯 (Strong Buy / Buy / 一號追蹤候選)」，報告盤中真實主力動向並推播 Telegram。
"""
import json
import os
import sqlite3
import ssl
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = r'C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io'
BRIDGE_DIR = os.path.join(BASE_DIR, 'psc_bridge')
SCAN_FILE = os.path.join(BASE_DIR, 'scan_results.json')
SYMBOLS_TXT = os.path.join(BRIDGE_DIR, 'all_260_symbols.txt')
OUT_JSON = os.path.join(BRIDGE_DIR, 'psc_all_quotes.json')
ENGINE_EXE = os.path.join(BRIDGE_DIR, 'PSCQuoteEngine.exe')
REPORT_TXT = os.path.join(BRIDGE_DIR, 'psc_live_dashboard.txt')
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'line_config.json')
DB_DIR = r'D:\PSC_Quant_DB'
INTRADAY_DB = os.path.join(DB_DIR, 'intraday_flow.db')


def log_intraday_and_get_deltas(quotes, now_str):
    """將金贏島 62 欄即時快照與完整五檔寫入 D 槽 SQLite，並計算近 15 分鐘外盤買氣加速度"""
    deltas = {}
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(INTRADAY_DB, timeout=10)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS intraday_snapshots (
                ts TEXT NOT NULL,
                symbol TEXT NOT NULL,
                trade_date TEXT,
                price REAL,
                avg_price REAL,
                in_size INTEGER,
                out_size INTEGER,
                bid5_vol INTEGER,
                ask5_vol INTEGER,
                total_vol INTEGER,
                PRIMARY KEY (ts, symbol)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sym_ts ON intraday_snapshots(symbol, ts)")

        rows = []
        for q in quotes:
            if q.get('price', 0) > 0:
                rows.append((
                    now_str, q['symbol'], str(q.get('date', '')),
                    float(q['price']), float(q.get('avg_price', 0)),
                    int(q.get('in_size', 0)), int(q.get('out_size', 0)),
                    int(q.get('bid5_vol', 0)), int(q.get('ask5_vol', 0)),
                    int(q.get('total_vol', 0))
                ))
        if rows:
            cur.executemany(
                "INSERT OR REPLACE INTO intraday_snapshots VALUES (?,?,?,?,?,?,?,?,?,?)",
                rows
            )
            conn.commit()

        cutoff = (datetime.strptime(now_str, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        today_prefix = now_str[:10]
        cur.execute("""
            SELECT symbol, in_size, out_size
            FROM intraday_snapshots
            WHERE ts >= ? AND ts <= ?
            ORDER BY ts ASC
        """, (today_prefix + ' 00:00:00', cutoff))
        base_map = {}
        for sym, in_s, out_s in cur.fetchall():
            base_map[sym] = (in_s, out_s)

        for q in quotes:
            sym = q['symbol']
            if sym in base_map:
                b_in, b_out = base_map[sym]
                d_in = max(0, int(q.get('in_size', 0)) - b_in)
                d_out = max(0, int(q.get('out_size', 0)) - b_out)
                deltas[sym] = (d_in, d_out)
        conn.close()
    except Exception as e:
        print(f"[DB] intraday_flow 寫入略過: {e}")
    return deltas

CORE_HOLDINGS = {
    'GOOGL': {'psc': 'GOOGL.US', 'name': '谷歌-A (持股5股)', 'cost': 299.142, 'stop': 291.50, 'target': 315.00},
    'VTI':   {'psc': 'VTI.US',   'name': 'VTI 全美股 (15股)', 'cost': 379.00,  'stop': 0.0,    'target': 0.0},
    'DIA':   {'psc': 'DIA.US',   'name': 'DIA 道瓊 (5股)',    'cost': 524.00,  'stop': 0.0,    'target': 0.0},
    '00406A.TW': {'psc': '00406A.TW', 'name': '主動中信台灣收益 (7張)', 'cost': 8.34, 'stop': 0.0, 'target': 0.0},
    '00981A.TW': {'psc': '00981A.TW', 'name': '主動統一台股增長 (追蹤觀察)', 'cost': 0.0, 'stop': 0.0, 'target': 0.0},
}

def to_psc_symbol(sym):
    s = str(sym).strip()
    if '.TW' in s or '.TWO' in s:
        return s.replace('.TWO', '.TW')
    if s[:4].isdigit():
        return s + '.TW'
    return s + '.US'

def sync_all_260_and_report(push_tg=False):
    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        scan_data = json.load(f)
    stocks = scan_data.get('stocks', [])

    # 收集全站 260 檔 + 核心持股對應
    psc_to_stock = {}
    all_psc_syms = []
    for s in stocks:
        sym = str(s.get('symbol', '')).strip()
        if not sym:
            continue
        ps = to_psc_symbol(sym)
        psc_to_stock[ps] = s
        if ps not in all_psc_syms:
            all_psc_syms.append(ps)

    for info in CORE_HOLDINGS.values():
        if info['psc'] not in all_psc_syms:
            all_psc_syms.append(info['psc'])

    with open(SYMBOLS_TXT, 'w', encoding='utf-8') as f:
        for ps in all_psc_syms:
            f.write(ps + '\n')

    # 等待 6000ms 確保 260 檔批次訂閱全數完成快照更新 (完全隱藏背景視窗)
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    subprocess.run([ENGINE_EXE, SYMBOLS_TXT, OUT_JSON, '6000'], check=False, startupinfo=si, creationflags=0x08000000)

    psc_data = {}
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, 'r', encoding='utf-8-sig') as f:
                psc_data = json.load(f)
        except Exception:
            psc_data = {}

    quotes = psc_data.get('quotes', []) if 'error' not in psc_data else []
    quote_map = {q['symbol']: q for q in quotes}
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today_compact = datetime.now().strftime('%Y%m%d')
    deltas_15m = log_intraday_and_get_deltas(quotes, now_str) if quotes else {}

    # 若台股盤中統一金贏島跨夜連線未刷新當日報價，自動啟動 TWSE 官方 0 延遲 MIS 即時行情雙源融合
    twse_live_map = {}
    tw_syms_all = [str(s.get('symbol', '')) for s in stocks if '.TW' in str(s.get('symbol', ''))]
    fresh_psc_tw = sum(1 for q in quotes if '.TW' in q.get('symbol', '') and str(q.get('date', '')) == today_compact)
    if fresh_psc_tw < 10 and tw_syms_all:
        try:
            sys.path.insert(0, BASE_DIR)
            import auto_sync
            twse_live_map = auto_sync.get_twse_prices(tw_syms_all)
            if '^TWII' in twse_live_map and twse_live_map['^TWII'].get('price'):
                if 'indices' not in scan_data or not isinstance(scan_data['indices'], dict):
                    scan_data['indices'] = {}
                scan_data['indices']['加權指數'] = {'close': twse_live_map['^TWII']['price']}
        except Exception as te:
            print(f"[TWSE-MIS] 雙源備援略過: {te}")

    # 將統一即時報價 + TWSE MIS 0延遲即時行情回寫更新進 scan_results.json
    updated_count = 0
    for s in stocks:
        sym = str(s.get('symbol', ''))
        ps = to_psc_symbol(sym)
        q = quote_map.get(ps)
        tw_q = twse_live_map.get(sym)
        use_tw_mis = bool(tw_q and tw_q.get('price', 0) > 0 and (not q or str(q.get('date', '')) != today_compact))
        if use_tw_mis:
            p = round(float(tw_q['price']), 2)
            pre = float(tw_q.get('prev_close') or s.get('close') or p)
            chg = round(((p - pre) / pre * 100), 2) if pre > 0 else s.get('change', 0)
            s['price'] = p
            s['close'] = p
            s['open'] = float(tw_q.get('open') or p)
            s['high'] = float(tw_q.get('high') or p)
            s['low'] = float(tw_q.get('low') or p)
            s['change'] = chg
            s['price_source'] = f"TWSE證交所即時 ({tw_q.get('date', today_compact)})"
            if s.get('technicals'):
                s['technicals']['chg_1d'] = chg
                ma60_v = float(s.get('ma60') or 0)
                if ma60_v > 0:
                    s['technicals']['bias_60ma'] = round((p - ma60_v) / ma60_v * 100.0, 2)
            ma60_p = float(s.get('ma60') or 0)
            if ma60_p > 0 and p < ma60_p:
                s['signal'] = 'Avoid'
                s['score'] = min(int(s.get('score', 50)), 58)
                s['erc_weight'] = 0.0
                if s.get('auto_order'):
                    s['auto_order']['gate_status'] = 'BLOCKED_BELOW_MA60'
                    s['auto_order']['gate_label'] = '🔴 盤中跌破季線熔斷禁買'
            elif chg <= -4.5:
                if s.get('signal') in ('Strong Buy', 'Buy'):
                    s['signal'] = 'Hold'
                    s['score'] = min(int(s.get('score', 50)), 75)
                    s['erc_weight'] = 0.0
                    if s.get('auto_order'):
                        s['auto_order']['gate_status'] = 'BLOCKED_INTRADAY_CRASH'
                        s['auto_order']['gate_label'] = f'🔴 盤中急殺熔斷 ({chg:+.1f}%)'
            updated_count += 1
        elif q and q['price'] > 0:
            p = round(q['price'], 2)
            pre = q['pre_close']
            chg = round(((p - pre) / pre * 100), 2) if pre > 0 else s.get('change', 0)
            s['price'] = p
            s['close'] = p
            s['change'] = chg
            s['price_source'] = f"統一金贏島即時 ({q['date']})"
            in_v = q['in_size']
            out_v = q['out_size']
            ratio = round(out_v / in_v, 2) if in_v > 0 else 1.0
            bid5 = q.get('bid5_vol', 0)
            ask5 = q.get('ask5_vol', 0)
            ob_ratio = round(bid5 / ask5, 2) if ask5 > 0 else 1.0
            d_in, d_out = deltas_15m.get(ps, (0, 0))
            s['psc_live'] = {
                'avg_price': round(q['avg_price'], 2),
                'in_size': in_v,
                'out_size': out_v,
                'out_in_ratio': ratio,
                'bid5_vol': bid5,
                'ask5_vol': ask5,
                'bid5_ask5_ratio': ob_ratio,
                'delta_in_15m': d_in,
                'delta_out_15m': d_out,
                'total_vol': q['total_vol'],
                'updated_at': now_str
            }
            # 盤中即時雙重熔斷防呆：① 跌破季線立即撤銷買訊、② 盤中急殺 <= -4.5% 或外內盤比 < 0.75 立即撤銷買訊
            ma60_p = float(s.get('ma60') or 0)
            if ma60_p > 0 and p < ma60_p:
                s['signal'] = 'Avoid'
                s['score'] = min(int(s.get('score', 50)), 58)
                s['erc_weight'] = 0.0
                if s.get('auto_order'):
                    s['auto_order']['gate_status'] = 'BLOCKED_BELOW_MA60'
                    s['auto_order']['gate_label'] = '🔴 盤中跌破季線熔斷禁買'
            elif chg <= -4.5:
                if s.get('signal') in ('Strong Buy', 'Buy'):
                    s['signal'] = 'Hold'
                    s['score'] = min(int(s.get('score', 50)), 75)
                    s['erc_weight'] = 0.0
                    if s.get('auto_order'):
                        s['auto_order']['gate_status'] = 'BLOCKED_INTRADAY_CRASH'
                        s['auto_order']['gate_label'] = f'🔴 盤中急殺熔斷 ({chg:+.1f}%)'
            elif chg <= -4.5 or ((in_v + out_v) > 50 and ratio < 0.75):
                if s.get('signal') in ('Strong Buy', 'Buy'):
                    s['signal'] = 'Hold'
                    s['score'] = min(int(s.get('score', 50)), 75)
                    s['erc_weight'] = 0.0
                    if s.get('auto_order'):
                        s['auto_order']['gate_status'] = 'BLOCKED_INTRADAY_CRASH'
                        s['auto_order']['gate_label'] = f'🔴 盤中急殺/內盤倒貨熔斷 ({chg:+.1f}% / 外內盤 {ratio:.2f}x)'
            updated_count += 1

    try:
        import rsi_closed_loop
        regime, quant_advisor = rsi_closed_loop.compute_dynamic_regime_and_erc(scan_data)
        scan_data['market_regime'] = regime
        scan_data['quant_advisor'] = quant_advisor
    except Exception as re_err:
        print(f"[RSI] 動態狀態略過: {re_err}")

    scan_data['last_updated'] = now_str
    scan_data['updated_at'] = now_str
    scan_data['update_sources'] = '統一證券金贏島 62欄原生DATA + V4-Yen雙師演算法 + Gen24 RSI走圖防套牢閉環'

    with open(SCAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, ensure_ascii=False, indent=2)

    # 同步寫入網站所有實際發布目錄下的 scan_results.json 與 live_portfolio.json
    import shutil
    for sub in ['', 'q_quant_888', 'trading', os.path.join('frontend', 'public')]:
        target_dir = os.path.join(BASE_DIR, sub) if sub else BASE_DIR
        if os.path.exists(target_dir):
            for fname in ['scan_results.json', 'live_portfolio.json']:
                dst = os.path.join(target_dir, fname)
                if os.path.abspath(dst) != os.path.abspath(SCAN_FILE):
                    shutil.copy2(SCAN_FILE, dst)

    # ──────────────────────────────────────────────
    # 產出 100% 對齊網站「高勝率買進邏輯」的戰情報告
    # ──────────────────────────────────────────────
    lines = []
    lines.append(f"🚀【q_quant_888 × 統一金贏島 62欄即時同步與高勝率買進報告】")
    lines.append(f"⏰ 同步時間：{now_str} ｜ 已將 {updated_count}/{len(stocks)} 檔統一即時數據寫回網站！\n")

    lines.append("🛡️ 【一、張大哥核心持倉即時體檢】")
    for orig_sym, info in CORE_HOLDINGS.items():
        q = quote_map.get(info['psc'])
        if not q or q['price'] <= 0:
            continue
        p = q['price']
        pre = q['pre_close']
        chg = ((p - pre) / pre * 100) if pre > 0 else 0
        in_v, out_v = q['in_size'], q['out_size']
        ratio = (out_v / in_v) if in_v > 0 else 1.0
        tag = "🟢外盤搶買" if out_v > in_v else "🔴內盤賣壓"
        cost_str = f" | 成本:{info['cost']:.2f} ({(p-info['cost'])/info['cost']*100:+.2f}%)" if info['cost'] > 0 else ""
        lines.append(f"• {info['name']} ({orig_sym}): {p:.2f} ({chg:+.2f}%) | {tag} (比 {ratio:.2f}){cost_str}")

    lines.append("\n🎯 【二、對齊網站 V4-Yen 高勝率買進標的（非亂槍追高）】")
    buy_targets = []
    watch_targets = []
    for s in stocks:
        sig = str(s.get('signal', ''))
        tactic = str(s.get('tactic', ''))
        bt = s.get('backtest') or {}
        wr = bt.get('win_rate', 0)
        ps = to_psc_symbol(s.get('symbol', ''))
        q = quote_map.get(ps)
        if not q or q['price'] <= 0:
            continue
        p = q['price']
        pre = q['pre_close']
        chg = ((p - pre) / pre * 100) if pre > 0 else 0
        in_v, out_v = q['in_size'], q['out_size']
        ratio = (out_v / in_v) if in_v > 0 else 1.0

        item = (wr, s.get('score', 0), s.get('symbol'), s.get('name'), sig, p, chg, ratio, q['avg_price'], tactic)
        if 'Buy' in sig:
            buy_targets.append(item)
        elif '一號追蹤候選' in tactic or (wr >= 70 and s.get('score', 0) >= 80):
            watch_targets.append(item)

    buy_targets.sort(reverse=True, key=lambda x: (x[0], x[1], x[7]))
    watch_targets.sort(reverse=True, key=lambda x: (x[0], x[1], x[7]))

    if buy_targets:
        lines.append("🔥 [已觸發買進/準觸發區]：")
        for wr, sc, sym, name, sig, p, chg, ratio, avg_p, tactic in buy_targets:
            flow = "🟢外盤買超" if ratio >= 1.0 else "🟡洗盤內盤"
            lines.append(f"• {name} ({sym}) [{sig}] 勝率:{wr}% 評分:{sc} | 現價 {p:.2f} ({chg:+.2f}%) | {flow} {ratio:.2f}x | 均價:{avg_p:.2f}")
    else:
        lines.append("• 目前暫無 Strong Buy / Buy 標的。")

    if watch_targets:
        lines.append("\n👀 [72%高勝率 守季線蓄勢候選]：")
        for wr, sc, sym, name, sig, p, chg, ratio, avg_p, tactic in watch_targets[:8]:
            flow = "🟢外盤搶" if ratio >= 1.0 else "🔴內盤洗"
            lines.append(f"• {name} ({sym}) 勝率:{wr}% 評分:{sc} | 現價 {p:.2f} ({chg:+.2f}%) | {flow} {ratio:.2f}x")

    try:
        import news_radar
        lines.extend(news_radar.get_news_digest_lines(limit=5, force='--force' in sys.argv))
    except Exception as ne:
        print(f"[News] 雷達略過: {ne}")

    report_str = "\n".join(lines)
    with open(REPORT_TXT, 'w', encoding='utf-8') as f:
        f.write(report_str)
    print(report_str)

    if push_tg and os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        tg_token = cfg.get('telegram_bot_token', '').strip()
        if tg_token:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            payload = json.dumps({'chat_id': '7660257976', 'text': report_str}).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            try:
                urllib.request.urlopen(req, context=ctx, timeout=20)
                print("\n[Telegram] 高勝率同步戰報已推送！")
            except Exception as e:
                print(f"\n[Telegram] 推送失敗: {e}")

    # 自動 Git Push 更新線上網站 (僅當帶 --git 參數時觸發，且每 3 分鐘同步一次網頁避免 GitHub Actions 塞車)
    if '--git' in sys.argv:
        now_min = datetime.now().minute
        if '--force' in sys.argv or (now_min % 3 == 0):
            try:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = 0
                cf = 0x08000000
                subprocess.run([
                    'git', 'add',
                    'scan_results.json', 'live_portfolio.json',
                    'q_quant_888/scan_results.json', 'q_quant_888/live_portfolio.json',
                    'trading/scan_results.json', 'trading/live_portfolio.json',
                    'frontend/public/scan_results.json', 'frontend/public/live_portfolio.json',
                    'news_radar.json', 'q_quant_888/news_radar.json'
                ], cwd=BASE_DIR, check=False, startupinfo=si, creationflags=cf)
                res = subprocess.run(['git', 'commit', '-m', f'auto(psc): sync live quotes {now_str}'], cwd=BASE_DIR, capture_output=True, text=True, startupinfo=si, creationflags=cf)
                if res.returncode == 0:
                    subprocess.run(['git', 'pull', '--rebase', '--autostash', '-X', 'ours', 'origin', 'main'], cwd=BASE_DIR, check=False, startupinfo=si, creationflags=cf)
                    subprocess.run(['git', 'push', 'origin', 'main'], cwd=BASE_DIR, check=False, startupinfo=si, creationflags=cf)
                    print("[GitHub] 已將統一即時數據自動同步至線上網站！")
            except Exception as ge:
                print(f"[GitHub] 自動推送異常: {ge}")


def is_psc_running():
    """偵測統一金贏島 (daqPSCAP.exe / DAQPSCAPProxy.exe) 是否正開啟運行中"""
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        out = subprocess.check_output(
            ['tasklist', '/FI', 'IMAGENAME eq daqPSCAP.exe', '/NH'],
            startupinfo=si, creationflags=0x08000000, text=True, errors='ignore'
        )
        if 'daqPSCAP.exe' in out:
            return True
    except Exception:
        pass
    return False


if __name__ == '__main__':
    # 只要張大哥開著統一金贏島 (daqPSCAP.exe)，不論是否為開盤時段皆 24 小時全天候時時同步！
    now = datetime.now()
    hm = now.hour * 100 + now.minute
    wd = now.weekday() # 0=Mon .. 6=Sun
    in_tw = (wd < 5) and (900 <= hm <= 1335)
    in_us = (wd < 5 and hm >= 2230) or (1 <= wd <= 5 and hm <= 505)
    psc_open = is_psc_running()
    # 每個交易日 15:45 後自動執行一次盤後真實籌碼/財報/日K/RSI帳本驗算閉環
    stamp_file = r'D:\PSC_Quant_DB\last_postmarket_enrich.txt'
    today_ymd = now.strftime('%Y-%m-%d')
    done_today = False
    if os.path.exists(stamp_file):
        try:
            with open(stamp_file, 'r', encoding='utf-8') as sf:
                done_today = (sf.read().strip() == today_ymd)
        except Exception:
            done_today = False

    if '--enrich' in sys.argv or (wd < 5 and hm >= 1545 and not done_today):
        try:
            import enrich_chips_fundamentals
            import rsi_closed_loop
            enrich_chips_fundamentals.main()
            rsi_closed_loop.main()
            with open(stamp_file, 'w', encoding='utf-8') as sf:
                sf.write(today_ymd)
        except Exception as ee:
            print(f"[PostMarket] 盤後閉環執行異常: {ee}")

    if '--force' in sys.argv or psc_open or in_tw or in_us:
        sync_all_260_and_report(push_tg='--notify' in sys.argv)
    else:
        print(f"[{now.strftime('%H:%M:%S')}] 統一金贏島未開啟且非開盤時段，靜默待命。")
