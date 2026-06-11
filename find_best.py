import json

with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== 🇺🇸 美股強勢推薦 (Regular Army Pullback) ===")
us_stocks = [s for s in data['stocks'] if s.get('market') == 'us' and s.get('close', 0) > s.get('ma60', 99999)]
us_stocks.sort(key=lambda s: (s['close'] - s['ma60']) / s['ma60'])
for s in us_stocks[:5]:
    diff = (s['close'] - s['ma60']) / s['ma60'] * 100
    print(f"{s['symbol']} {s['name']}: 現價 ${s['close']} | MA60 ${s['ma60']:.2f} (距離 +{diff:.1f}%) | 勝率 {s.get('win_rate',0)}%")

print("\n=== 🇹🇼 台股明日伏擊 (Regular Army Pullback) ===")
tw_stocks = [s for s in data['stocks'] if s.get('market') == 'tw' and s.get('close', 0) > s.get('ma60', 99999)]
tw_stocks.sort(key=lambda s: (s['close'] - s['ma60']) / s['ma60'])
for s in tw_stocks[:5]:
    diff = (s['close'] - s['ma60']) / s['ma60'] * 100
    print(f"{s['symbol']} {s['name']}: 現價 ${s['close']} | MA60 ${s['ma60']:.2f} (距離 +{diff:.1f}%) | 勝率 {s.get('win_rate',0)}%")
