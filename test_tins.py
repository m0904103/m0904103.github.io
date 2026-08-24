import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data.get('stocks', [])
globalIndices = data.get('indices', {})

def calc_tins(stock, globalIndices):
    if not stock or not stock.get('close') or not stock.get('ma60'):
        return 50
    score = 50
    close = float(stock['close'])
    ma60 = float(stock['ma60'])
    biasPct = ((close - ma60) / ma60) * 100
    ma200 = float(stock.get('ma200')) if stock.get('ma200') else None
    isAboveMa60 = close >= ma60
    isBelowMa200 = ma200 and close < ma200
    
    if isBelowMa200: score -= 40
    if isAboveMa60: score += 30
    else: score -= 25
        
    isSweetZone = isAboveMa60 and (0.0 <= biasPct <= 4.0)
    if isSweetZone: score += 20
    elif isAboveMa60 and biasPct > 4.0: score -= 15
        
    chips = stock.get('chips', {})
    if chips and chips.get('foreign_buy'): score += 10
        
    funds = stock.get('fundamentals', {})
    if funds and funds.get('three_rates_rising'): score += 10
        
    twVix = globalIndices.get('台指 VIX (波動率)', {}).get('close', 20)
    if twVix > 35: score -= 15
        
    return max(10, min(99, score))

scored_tw, scored_us = [], []

for s in stocks:
    score = calc_tins(s, globalIndices)
    s_copy = dict(s)
    s_copy['tins_score'] = score
    s_copy['bias60'] = ((float(s['close']) - float(s['ma60'])) / float(s['ma60'])) * 100
    if s.get('market') == 'tw': scored_tw.append(s_copy)
    else: scored_us.append(s_copy)

scored_tw.sort(key=lambda x: (x['tins_score'], -abs(x['bias60'])), reverse=True)
scored_us.sort(key=lambda x: (x['tins_score'], -abs(x['bias60'])), reverse=True)

print('=== TAIWAN TOP 5-STAR WIN-RATE RANKING (TINs >= 85) ===')
tw_star5 = [s for s in scored_tw if s['tins_score'] >= 85]
for i, s in enumerate(tw_star5[:15]):
    bt_wr = s.get('backtest', {}).get('win_rate', 0) if isinstance(s.get('backtest'), dict) else 0
    print('Rank %2d: Score %2d | %-10s %-8s | Price: %8.2f | MA60: %8.2f | Bias60: %+6.2f%% | BT WinRate: %4.1f%%' % (i+1, s['tins_score'], s['symbol'], s.get('name', ''), float(s['close']), float(s['ma60']), s['bias60'], bt_wr))

print('\n=== US TOP 5-STAR WIN-RATE RANKING (TINs >= 85) ===')
us_star5 = [s for s in scored_us if s['tins_score'] >= 85]
for i, s in enumerate(us_star5[:15]):
    bt_wr = s.get('backtest', {}).get('win_rate', 0) if isinstance(s.get('backtest'), dict) else 0
    print('Rank %2d: Score %2d | %-10s %-12s | Price: $%7.2f | MA60: $%7.2f | Bias60: %+6.2f%% | BT WinRate: %4.1f%%' % (i+1, s['tins_score'], s['symbol'], s.get('name', ''), float(s['close']), float(s['ma60']), s['bias60'], bt_wr))

print('\nTotal 5-Star: TW = %d / %d, US = %d / %d' % (len(tw_star5), len(scored_tw), len(us_star5), len(scored_us)))
