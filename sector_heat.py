import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('trading/scan_results.json', encoding='utf-8'))
stocks = [s for s in data.get('stocks', []) if not s['symbol'].endswith('.TW') and not s['symbol'].endswith('.TWO')]

sectors = {}
for s in stocks:
    sector = s.get('sector', 'Unknown')
    change = s.get('change', 0)
    if change is not None:
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(change)

print("--- US Sector Heatmap ---")
avg_sectors = []
for sec, changes in sectors.items():
    if len(changes) >= 2: # Only look at sectors with at least 2 stocks
        avg_change = sum(changes) / len(changes)
        avg_sectors.append((sec, avg_change, len(changes)))

avg_sectors.sort(key=lambda x: x[1], reverse=True)

for sec, avg, count in avg_sectors:
    print(f"Sector: {sec:<20} | Avg Change: {avg:>5.2f}% | Count: {count}")
