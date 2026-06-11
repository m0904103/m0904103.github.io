import json

try:
    with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tw_stocks = []
    us_stocks = []
    
    for s in data.get('stocks', []):
        if s.get('signal') in ['Strong Buy', 'Buy']:
            close = s.get('close', 0)
            ma60 = s.get('ma60', 0)
            if ma60 > 0 and close >= ma60:
                dev = (close - ma60) / ma60 * 100
                if 0 <= dev <= 2.5: # Strict 2.5% deviation for maximum safety
                    item = {
                        'symbol': s.get('symbol'),
                        'name': s.get('name'),
                        'close': close,
                        'dev': dev,
                        'signal': s.get('signal'),
                        'note': s.get('condition_note', '')
                    }
                    if s.get('market') == 'tw':
                        tw_stocks.append(item)
                    elif s.get('market') == 'us':
                        us_stocks.append(item)
    
    tw_stocks.sort(key=lambda x: x['dev'])
    us_stocks.sort(key=lambda x: x['dev'])
    
    print('--- TW Picks (Final Close) ---')
    for p in tw_stocks[:5]:
        print(f"{p['symbol']} {p['name']}: Close {p['close']}, Dev {p['dev']:.2f}%")
        
    print('\n--- US Picks (Pre-market) ---')
    for p in us_stocks[:5]:
        print(f"{p['symbol']} {p['name']}: Close {p['close']}, Dev {p['dev']:.2f}%")

except Exception as e:
    print('Error:', e)
