import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

triple_bottoms = []
for s in data['stocks']:
    patterns = s.get('patterns', {}) or s.get('pattern', {})
    if not patterns: continue
    
    if 'triple_bottom' in patterns or '三重底' in json.dumps(patterns, ensure_ascii=False):
        if s.get('close') and s.get('ma60') and s['close'] >= s['ma60']:
            diff_pct = (s['close'] - s['ma60']) / s['ma60'] * 100
            triple_bottoms.append((s, diff_pct))

triple_bottoms.sort(key=lambda x: x[1])

with open('best_triple_bottoms.txt', 'w', encoding='utf-8') as f:
    if not triple_bottoms:
        f.write('No Triple Bottom stocks found above MA60.\n')
    else:
        for s, diff in triple_bottoms:
            f.write(f"{s['symbol']} {s['name']}: {s['close']} | MA60: {s['ma60']:.2f} | Diff: +{diff:.2f}% | Market: {s['market']}\n")
