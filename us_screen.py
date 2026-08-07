import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('frontend/public/scan_results.json', encoding='utf-8'))
stocks = data.get('stocks', [])
# Filter for US stocks (no .TW or .TWO)
us_stocks = [s for s in stocks if not s['symbol'].endswith('.TW') and not s['symbol'].endswith('.TWO')]

# We want stocks above MA60 (Strong trend)
strong_us_stocks = [s for s in us_stocks if s.get('change') is not None and s.get('close') is not None and s.get('ma60') is not None and s['close'] > s['ma60']]

print("--- 🚀 美股強勢突破 (Top US Gainers Above MA60) ---")
strong_us_stocks.sort(key=lambda x: x.get('change', 0), reverse=True)
for s in strong_us_stocks[:10]:
    print(f"{s['symbol']} ({s.get('name', '')}) : {s.get('change', 0)}% - {s.get('sector', '')}")

print("\n--- 🛡️ 季線防守區 (Pullback Support, 絕佳買點) ---")
# Pullbacks resting ON TOP of MA60 (0% to +5%)
support_entries = [s for s in us_stocks if s.get('close') is not None and s.get('ma60') is not None and 0 <= ((s['close'] - s['ma60']) / s['ma60'] * 100) <= 5]
for s in support_entries:
    s['gap60'] = (s['close'] - s['ma60']) / s['ma60'] * 100
support_entries.sort(key=lambda x: x['gap60'])
for s in support_entries[:10]:
    print(f"{s['symbol']} ({s.get('name', '')}) : {s.get('change', 0)}% - {s.get('sector', '')} | 乖離季線: +{s['gap60']:.1f}%")

print("\n--- ⚠️ 跌破季線警戒區 (Broken Trend, 嚴禁抄底) ---")
# Broken below MA60 (0% to -5%)
broken_trend = [s for s in us_stocks if s.get('close') is not None and s.get('ma60') is not None and -5 <= ((s['close'] - s['ma60']) / s['ma60'] * 100) < 0]
for s in broken_trend:
    s['gap60'] = (s['close'] - s['ma60']) / s['ma60'] * 100
broken_trend.sort(key=lambda x: x['gap60'], reverse=True)
for s in broken_trend[:10]:
    print(f"{s['symbol']} ({s.get('name', '')}) : {s.get('change', 0)}% - {s.get('sector', '')} | 落後季線: {s['gap60']:.1f}% (須等待站回)")
