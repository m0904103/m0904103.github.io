import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('trading/scan_results.json', encoding='utf-8'))
stocks = data.get('stocks', [])
tw_stocks = [s for s in stocks if s['symbol'].endswith('.TW') or s['symbol'].endswith('.TWO')]

# Top 10 Gainers Above MA60
filtered = [s for s in tw_stocks if s.get('change') is not None and s.get('close') is not None and s.get('ma60') is not None and s['close'] > s['ma60']]
filtered.sort(key=lambda x: x.get('change', 0), reverse=True)

print("--- 🚀 強勢突破 (Top 10 TW Gainers Above MA60) ---")
for s in filtered[:10]:
    gap20 = (s['close'] - s['ma20']) / s['ma20'] * 100 if s.get('ma20') else 0
    print(f"{s['symbol']} ({s.get('name', '')}) : {s.get('change', 0)}% - {s.get('sector', '')} | 乖離月線: {gap20:.1f}%")

# Pullbacks close to MA20 (Safe Entries)
pullbacks = [s for s in tw_stocks if s.get('close') is not None and s.get('ma60') is not None and s.get('ma20') is not None and s['close'] > s['ma60']]
for s in pullbacks:
    s['gap20'] = (s['close'] - s['ma20']) / s['ma20'] * 100
    
safe_entries = [s for s in pullbacks if 0 <= s['gap20'] <= 3]
safe_entries.sort(key=lambda x: x['gap20'])

print("\n--- 🛡️ 月線有撐 (Safe Entries near MA20) ---")
for s in safe_entries[:10]:
    print(f"{s['symbol']} ({s.get('name', '')}) : {s.get('change', 0)}% - {s.get('sector', '')} | 乖離月線: {s['gap20']:.1f}%")
