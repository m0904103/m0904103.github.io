import json
with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
avgo = next((s for s in data['stocks'] if s['symbol'] == 'AVGO'), None)
if avgo:
    print(f"AVGO: Close {avgo['close']}, Change {avgo['change']}%, MA60 {avgo['ma60']}")
else:
    print('AVGO not found')
