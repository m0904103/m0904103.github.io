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
import ssl
import subprocess
import sys
import urllib.request
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = r'C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io'
BRIDGE_DIR = os.path.join(BASE_DIR, 'psc_bridge')
SCAN_FILE = os.path.join(BASE_DIR, 'scan_results.json')
SYMBOLS_TXT = os.path.join(BRIDGE_DIR, 'all_260_symbols.txt')
OUT_JSON = os.path.join(BRIDGE_DIR, 'psc_all_quotes.json')
ENGINE_EXE = os.path.join(BRIDGE_DIR, 'PSCQuoteEngine.exe')
REPORT_TXT = os.path.join(BRIDGE_DIR, 'psc_live_dashboard.txt')
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'line_config.json')

CORE_HOLDINGS = {
    'GOOGL': {'psc': 'GOOGL.US', 'name': '谷歌-A (持股5股)', 'cost': 299.142, 'stop': 291.50, 'target': 315.00},
    'VTI':   {'psc': 'VTI.US',   'name': 'VTI 全美股 (15股)', 'cost': 379.00,  'stop': 0.0,    'target': 0.0},
    'DIA':   {'psc': 'DIA.US',   'name': 'DIA 道瓊 (5股)',    'cost': 524.00,  'stop': 0.0,    'target': 0.0},
    '00406A.TW': {'psc': '00406A.TW', 'name': '主動中信台灣收益', 'cost': 0.0, 'stop': 0.0, 'target': 0.0},
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

    # 等待 6000ms 確保 260 檔批次訂閱全數完成快照更新
    subprocess.run([ENGINE_EXE, SYMBOLS_TXT, OUT_JSON, '6000'], check=False)

    if not os.path.exists(OUT_JSON):
        print("❌ 找不到統一報價輸出檔")
        return

    with open(OUT_JSON, 'r', encoding='utf-8-sig') as f:
        psc_data = json.load(f)

    if 'error' in psc_data:
        print(f"❌ 統一金贏島連線錯誤: {psc_data['error']}")
        return

    quotes = psc_data.get('quotes', [])
    quote_map = {q['symbol']: q for q in quotes}
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 將統一即時報價回寫更新進 scan_results.json
    updated_count = 0
    for s in stocks:
        ps = to_psc_symbol(s.get('symbol', ''))
        q = quote_map.get(ps)
        if q and q['price'] > 0:
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
            s['psc_live'] = {
                'avg_price': round(q['avg_price'], 2),
                'in_size': in_v,
                'out_size': out_v,
                'out_in_ratio': ratio,
                'total_vol': q['total_vol'],
                'updated_at': now_str
            }
            updated_count += 1

    scan_data['last_updated'] = now_str
    scan_data['updated_at'] = now_str
    scan_data['update_sources'] = '統一證券金贏島 62欄原生DATA + V4-Yen雙師演算法'

    with open(SCAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, ensure_ascii=False, indent=2)

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

if __name__ == '__main__':
    sync_all_260_and_report(push_tg='--notify' in sys.argv)
