import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('trading/scan_results.json', encoding='utf-8'))
stocks = data.get('stocks', [])
# Filter for US stocks (no .TW or .TWO)
us_stocks = [s for s in stocks if not s['symbol'].endswith('.TW') and not s['symbol'].endswith('.TWO')]

# We want stocks above MA60 (Strong trend)
strong_us_stocks = [s for s in us_stocks if s.get('change') is not None and s.get('close') is not None and s.get('ma60') is not None and s['close'] > s['ma60']]

print("--- 🚀 美股強勢突破 (Top US Gainers Above MA60) ---")
strong_us_stocks.sort(key=lambda x: x.get('change', 0), reverse=True)
for s in strong_us_stocks[:10]:
    print(f"{s['symbol']} ({s.get('name', '')}) : {s.get('change', 0)}% - {s.get('sector', '')}")

print("\n--- 🛡️ 美股低接名單 (Safe Entries, Below but near MA60) ---")
# Pullbacks near MA60
pullbacks = [s for s in us_stocks if s.get('close') is not None and s.get('ma60') is not None and s['close'] <= s['ma60']]
for s in pullbacks:
    s['gap60'] = (s['close'] - s['ma60']) / s['ma60'] * 100

safe_entries = [s for s in pullbacks if -5 <= s['gap60'] <= 0]
safe_entries.sort(key=lambda x: x['gap60'], reverse=True)
for s in safe_entries[:10]:
    print(f"{s['symbol']} ({s.get('name', '')}) : {s.get('change', 0)}% - {s.get('sector', '')} | 距離季線: {s['gap60']:.1f}%")
