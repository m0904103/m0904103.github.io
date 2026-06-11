import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = []
for s in data['stocks']:
    close = s.get('close') or 0
    ma60 = s.get('ma60') or 0
    if not close or not ma60 or ma60 <= 0:
        continue
    
    # Must be above or very close to MA60
    if close < ma60 * 0.99: 
        continue

    diff_pct = (close - ma60) / ma60 * 100
    
    # Must have a good backtest win rate (> 40%)
    backtest = s.get('backtest', {}) or {}
    win_rate = backtest.get('win_rate', 0)
    total_return = backtest.get('total_return', 0)
    
    if win_rate < 40 or total_return <= 0:
        continue

    patterns = s.get('patterns', {}) or {}
    pattern_names = []
    if isinstance(patterns, dict):
        if 'triple_bottom' in patterns:
            pattern_names.append('Three Bottom')
        if 'w_bottom' in patterns or 'double_bottom' in patterns:
            pattern_names.append('W Bottom')
        if 'abc_wave' in patterns and patterns['abc_wave'].get('pattern_en') != 'ABC_FALLING':
            pattern_names.append('ABC Bottom')

    score = 0
    # Closeness to MA60
    if diff_pct <= 2.0:
        score += 40
    elif diff_pct <= 5.0:
        score += 30
    elif diff_pct <= 10.0:
        score += 15

    # Win rate boosts score
    score += (win_rate / 2)
    
    # Patterns boost score
    score += len(pattern_names) * 10

    if score > 50:
        results.append({
            'symbol': s['symbol'],
            'name': s.get('name', ''),
            'close': close,
            'ma60': round(ma60, 2),
            'diff': round(diff_pct, 2),
            'patterns': '+'.join(pattern_names) if pattern_names else 'None',
            'win_rate': win_rate,
            'total_return': total_return,
            'market': s.get('market', ''),
            'score': round(score, 2)
        })

results.sort(key=lambda x: x['score'], reverse=True)

print("=== Professor Yen's Quantitative Holy Grail ===")
for r in results[:5]:
    mkt = "[US]" if r['market'] == 'us' else "[TW]"
    print(f"{mkt} {r['symbol']} {r['name']}")
    print(f"   Patterns: {r['patterns']}")
    print(f"   Close:{r['close']} | MA60:{r['ma60']} | Diff:+{r['diff']}%")
    print(f"   Backtest Win Rate: {r['win_rate']}% | Return: +{r['total_return']}% | Quant Score: {r['score']}")
    print()
