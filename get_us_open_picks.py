import json

try:
    with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    us_stocks = []
    
    for s in data.get('stocks', []):
        if s.get('market') == 'us' and s.get('signal') == 'Strong Buy':
            close = s.get('close', 0)
            ma60 = s.get('ma60', 0)
            if ma60 > 0 and close >= ma60:
                dev = (close - ma60) / ma60 * 100
                if 0 <= dev <= 2.5: # Strict 2.5% deviation for maximum safety
                    us_stocks.append({
                        'symbol': s.get('symbol'),
                        'name': s.get('name'),
                        'close': close,
                        'change': s.get('change', 0),
                        'ma60': ma60,
                        'dev': dev,
                        'note': s.get('condition_note', '')
                    })
    
    # Sort by deviation ascending
    us_stocks.sort(key=lambda x: x['dev'])
    
    print('--- LIVE US OPEN PICKS (Dev < 2.5%) ---')
    for p in us_stocks[:7]:
        print(f"{p['symbol']} {p['name']:<15} | Price: {p['close']} (Chg: {p['change']}%) | MA60: {p['ma60']} | Dev: {p['dev']:.2f}%")

except Exception as e:
    print('Error:', e)
