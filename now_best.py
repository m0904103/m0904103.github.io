import json
import os

try:
    with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tw_stocks = [s for s in data.get('stocks', []) if s.get('market') == 'tw']
    
    best_picks = []
    for s in tw_stocks:
        if s.get('signal') in ['Strong Buy', 'Buy']:
            close = s.get('close', 0)
            ma60 = s.get('ma60', 0)
            if ma60 > 0 and close > ma60:
                deviation = (close - ma60) / ma60
                if 0 <= deviation <= 0.05:
                    best_picks.append({
                        'symbol': s.get('symbol'),
                        'name': s.get('name'),
                        'close': close,
                        'deviation': deviation,
                        'signal': s.get('signal'),
                        'note': s.get('condition_note', '')
                    })
    
    best_picks.sort(key=lambda x: x['deviation'])
    
    print(f'Found {len(best_picks)} great setups in Taiwan market:')
    for p in best_picks[:15]:
        print(f"- {p['name']} ({p['symbol']}): Price {p['close']}, Dev {p['deviation']*100:.2f}%, {p['signal']}, Note: {p['note']}")

except Exception as e:
    print('Error:', e)
