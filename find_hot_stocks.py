import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Hot topics / AI / Tech / Semiconductors
hot_keywords = ['半導體', '科技', '軟體', 'AI', '伺服器']
hot_symbols = ['NVDA', 'MSFT', 'AAPL', 'TSM', 'AMD', 'AVGO', 'QCOM', 'ASML', 'AMAT', 'ADBE', 'PLTR', 'ARM', 'SMCI', 'META', 'GOOGL', 'AMZN']

results = []
for s in data['stocks']:
    if s['market'] != 'us':
        continue
    
    is_hot = s['symbol'] in hot_symbols
    
    if is_hot:
        patterns = s.get('patterns', {}) or s.get('pattern', {})
        pattern_names = []
        if 'triple_bottom' in patterns or '三重底' in json.dumps(patterns, ensure_ascii=False):
            pattern_names.append('三重底')
        if 'double_bottom' in patterns or 'W底' in json.dumps(patterns, ensure_ascii=False):
            pattern_names.append('W底')
            
        if s.get('close') and s.get('ma60'):
            diff_pct = (s['close'] - s['ma60']) / s['ma60'] * 100
            if s['close'] >= s['ma60']:
                results.append((s, diff_pct, pattern_names))

results.sort(key=lambda x: x[1])

with open('hot_tech_stocks.txt', 'w', encoding='utf-8') as f:
    for s, diff, p in results:
        p_str = ", ".join(p) if p else "無明顯底部型態"
        f.write(f"{s['symbol']} {s['name']}: {s['close']} | MA60: {s['ma60']:.2f} | Diff: +{diff:.2f}% | 型態: {p_str}\n")
