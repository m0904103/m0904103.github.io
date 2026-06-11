import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hot_symbols = ['NVDA', 'MSFT', 'AAPL', 'TSM', 'AMD', 'AVGO', 'QCOM', 'ASML', 'AMAT', 'ADBE', 'PLTR', 'ARM', 'SMCI', 'META', 'GOOGL', 'AMZN', '2330.TW', '3017.TW', '2317.TW', '2382.TW', '2454.TW']

candidates = []

for s in data['stocks']:
    close = s.get('close', 0)
    ma60 = s.get('ma60', 99999)
    patterns = s.get('patterns', {}) or s.get('pattern', {})
    
    if close <= ma60:
        continue # Not Regular Army
    
    diff_pct = (close - ma60) / ma60 * 100
    if diff_pct > 3.0: # Too far from MA60, risk is high
        continue
        
    has_bottom = False
    pattern_names = []
    if isinstance(patterns, dict):
        if 'triple_bottom' in patterns or '三重底' in json.dumps(patterns, ensure_ascii=False):
            has_bottom = True
            pattern_names.append('三重底')
        if 'double_bottom' in patterns or 'w_bottom' in patterns or 'W底' in json.dumps(patterns, ensure_ascii=False):
            has_bottom = True
            pattern_names.append('W底')
            
    is_hot = s['symbol'] in hot_symbols
    win_rate = s.get('backtest', {}).get('win_rate', 0)
    
    # Scoring system
    score = 0
    if has_bottom: score += 30
    if diff_pct < 1.0: score += (1.0 - diff_pct) * 20 # Closer is better
    if diff_pct < 2.0: score += 10
    if is_hot: score += 20
    if win_rate > 60: score += 10
    if win_rate > 70: score += 10
    
    if has_bottom: # We strongly prefer stocks with an actual bottom pattern
        candidates.append({
            'symbol': s['symbol'],
            'name': s.get('name', ''),
            'close': close,
            'ma60': ma60,
            'diff': diff_pct,
            'patterns': ", ".join(pattern_names),
            'win_rate': win_rate,
            'is_hot': is_hot,
            'score': score,
            'market': s['market']
        })

candidates.sort(key=lambda x: x['score'], reverse=True)

with open('best_entry.txt', 'w', encoding='utf-8') as f:
    f.write("=== 最佳進場標的推薦 (Top Entries) ===\n")
    for c in candidates[:10]:
        hot_str = "[熱門題材]" if c['is_hot'] else ""
        f.write(f"{c['symbol']} {c['name']} {hot_str}\n")
        f.write(f"現價: {c['close']} | MA60: {c['ma60']} (距離: +{c['diff']:.2f}%)\n")
        f.write(f"型態: {c['patterns']} | 勝率: {c['win_rate']}%\n")
        f.write(f"綜合推薦分數: {c['score']:.1f}\n")
        f.write("-" * 40 + "\n")
