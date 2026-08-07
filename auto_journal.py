import json
import os
import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')
import datetime

SCAN_FILE = 'frontend/public/scan_results.json'
JOURNAL_FILE = 'data/trade_journal.json'
TODAY = datetime.date.today().strftime('%Y-%m-%d')

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print(f"[{TODAY}] 啟動顏氏量化 2.0 自動復盤與決策快照模組...")
    
    scan_data = load_json(SCAN_FILE)
    stocks = scan_data.get('stocks', [])
    if not stocks:
        print("未找到 scan_results.json 數據。")
        return
        
    # Build a lookup for current prices
    current_market = {s['symbol']: s for s in stocks}
    
    # Load or initialize journal
    journal = load_json(JOURNAL_FILE)
    if 'entries' not in journal:
        journal['entries'] = []
        
    entries = journal['entries']
    
    print("\n--- 1. 執行 T+N 日自動回測與結算 ---")
    active_entries = [e for e in entries if e['status'] == 'Tracking']
    win_count = 0
    loss_count = 0
    
    for entry in active_entries:
        sym = entry['symbol']
        if sym in current_market:
            current_stock = current_market[sym]
            curr_price = current_stock.get('close', 0)
            
            # Risk Management Check (Stop Loss)
            # Rule: If it falls below its original MA60 or drops > 5%
            sl_price = entry.get('ma60', entry['entry_price'] * 0.95)
            if curr_price < sl_price:
                entry['status'] = 'Loss'
                entry['exit_price'] = curr_price
                entry['exit_date'] = TODAY
                entry['return_pct'] = round((curr_price - entry['entry_price']) / entry['entry_price'] * 100, 2)
                print(f"⚠️ 停損觸發: {sym} 跌破防線, {entry['entry_price']} -> {curr_price} ({entry['return_pct']}%)")
                loss_count += 1
                continue
                
            # Profit Target Check (Take Profit)
            # Rule: If it gains > 10%
            tp_price = entry['entry_price'] * 1.10
            if curr_price >= tp_price:
                entry['status'] = 'Win'
                entry['exit_price'] = curr_price
                entry['exit_date'] = TODAY
                entry['return_pct'] = round((curr_price - entry['entry_price']) / entry['entry_price'] * 100, 2)
                print(f"🏆 獲利達標: {sym} 突破 10%, {entry['entry_price']} -> {curr_price} ({entry['return_pct']}%)")
                win_count += 1
                
    print(f"今日結算: 獲利 {win_count} 筆, 停損 {loss_count} 筆。追蹤中: {len(active_entries) - win_count - loss_count} 筆。")
    
    print("\n--- 2. 決策快照：記錄今日季線防守區標的 ---")
    new_entries_count = 0
    recent_entry_symbols = [e['symbol'] for e in entries if e['status'] == 'Tracking']
    
    for s in stocks:
        sym = s['symbol']
        close = s.get('close')
        ma60 = s.get('ma60')
        ma200 = s.get('ma200')
        
        if not close or not ma60:
            continue
            
        # Teacher Yen's Strict Pullback Rule (0% to +4% bias) and must be above MA200
        bias = (close - ma60) / ma60 * 100
        is_above_ma200 = True
        if ma200:
            is_above_ma200 = close >= ma200
            
        if is_above_ma200 and 0 <= bias <= 4:
            # Check if it's already being tracked
            if sym not in recent_entry_symbols:
                entries.append({
                    "date": TODAY,
                    "symbol": sym,
                    "name": s.get('name', ''),
                    "entry_price": close,
                    "ma60": ma60,
                    "bias": round(bias, 2),
                    "status": "Tracking",
                    "exit_price": None,
                    "exit_date": None,
                    "return_pct": None,
                    "reason": f"季線防守區, 乖離率 +{round(bias, 2)}%"
                })
                print(f"📸 快照建檔: {sym} ({s.get('name', '')}) 進入季線防守區, 買點 ${close}")
                new_entries_count += 1
                recent_entry_symbols.append(sym)
                
    print(f"今日新增 {new_entries_count} 筆觀察標的。")
    
    save_json(JOURNAL_FILE, journal)
    print("✅ 決策快照與回測結算完成。")

if __name__ == "__main__":
    main()
