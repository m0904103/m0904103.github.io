import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = [s for s in data.get('stocks', []) if s.get('market') == 'tw']
candidates = []

for s in stocks:
    close = float(s.get('close', 0))
    ma60 = float(s.get('ma60', 0))
    ma200 = float(s.get('ma200', 0)) if s.get('ma200') else None
    if close <= 0 or ma60 <= 0: continue
    
    bias60 = ((close - ma60) / ma60) * 100
    isAboveMa60 = close >= ma60
    isAboveMa200 = (close >= ma200) if ma200 else True
    
    if isAboveMa60 and isAboveMa200 and (0.0 <= bias60 <= 4.0):
        chips = s.get('chips', {})
        funds = s.get('fundamentals', {})
        score = 50 + 30 + 20
        if chips.get('foreign_buy'): score += 10
        if funds.get('three_rates_rising'): score += 10
        score = min(99, score)
        bt_wr = s.get('backtest', {}).get('win_rate', 0) if isinstance(s.get('backtest'), dict) else 0
        candidates.append({
            'symbol': s.get('symbol'),
            'name': s.get('name'),
            'sector': s.get('sector', ''),
            'close': close,
            'ma60': ma60,
            'bias60': bias60,
            'score': score,
            'foreign_buy': chips.get('foreign_buy', False),
            'three_rates': funds.get('three_rates_rising', False),
            'bt_wr': bt_wr,
            'tactic': s.get('tactic', '')
        })

candidates.sort(key=lambda x: (x['score'], x['bt_wr'], -abs(x['bias60'])), reverse=True)

print('=== TAIWAN INTRADAY HIGH CONVICTION BUY CANDIDATES (0%~4% SWEET ZONE) ===')
for i, c in enumerate(candidates[:15]):
    fb = '外資買超' if c['foreign_buy'] else '        '
    tr = '三率三升' if c['three_rates'] else '        '
    print('%2d. %-9s %-8s | 現價: %8.2f | MA60: %8.2f | 乖離: %+5.2f%% | 評分: %2d分 | 勝率: %4.1f%% | %s %s' % (i+1, c['symbol'], c['name'], c['close'], c['ma60'], c['bias60'], c['score'], c['bt_wr'], fb, tr))
