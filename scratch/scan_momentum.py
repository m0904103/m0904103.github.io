import urllib.request
import json

url = 'https://m0904103.github.io/trading/scan_results.json'
try:
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    print("🚀 TOP MOMENTUM STOCKS FOR DAY TRADING:")
    
    tw_stocks = [s for s in data.get('stocks', []) if s.get('market') == 'tw' and s.get('is_regular', False) and s.get('change', 0) > 4]
    tw_stocks.sort(key=lambda x: x.get('change', 0), reverse=True)
    
    for s in tw_stocks[:10]:
        print(f"[{s['symbol']}] {s['name']}: Change={s['change']}%, Close={s['close']}, WinRate={s.get('backtest',{}).get('win_rate', 'N/A')}%")
except Exception as e:
    print("Error:", e)
