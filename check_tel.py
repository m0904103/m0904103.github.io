import json
with open('q_quant_888/scan_results.json', encoding='utf-8') as f:
    data = json.load(f)
tel = next((s for s in data.get('stocks', []) if s['symbol'] == 'TEL'), None)
if tel:
    print(json.dumps(tel, indent=2))
else:
    print("TEL not found")
