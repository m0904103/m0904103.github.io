import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
stocks = {s['symbol']: s['name'] for s in data.get('stocks', [])}

symbols = ['6112.TW', '2912.TW', '6213.TW', '1402.TW', '5871.TW', '3558.TWO', '3017.TW', '3029.TW']
for sym in symbols:
    print(f"{sym}: {stocks.get(sym, 'Unknown')}")
