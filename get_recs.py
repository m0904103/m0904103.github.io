import json
try:
    with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    stocks = [s for s in data.get('stocks', []) if s.get('market') == 'us' and s.get('signal') == 'Strong Buy']
    for s in stocks:
        s['dev'] = abs((s['close'] - s['ma60']) / s['ma60'])
    stocks.sort(key=lambda x: x['dev'])
    
    print('Top Strong Buy Recommendations:')
    for s in stocks[:5]:
        dev_pct = s['dev'] * 100
        print(f"- {s['symbol']} ({s['name']}): Price {s['close']}, MA60 {s['ma60']}, Dev: {dev_pct:.2f}% | Sector: {s.get('sector', 'Unknown')}")
except Exception as e:
    print('Error:', e)
