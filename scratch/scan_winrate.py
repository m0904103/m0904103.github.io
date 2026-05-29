import urllib.request
import json

url = 'https://m0904103.github.io/trading/scan_results.json'
try:
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    print("🚀 TOP WIN RATE MOMENTUM STOCKS:")
    
    # Filter for TW stocks, regular army (is_regular=True), and momentum (change > 4%)
    tw_stocks = [s for s in data.get('stocks', []) if s.get('market') == 'tw' and s.get('is_regular', False) and s.get('change', 0) > 4]
    
    # Sort primarily by historical win rate, secondarily by today's change
    tw_stocks.sort(key=lambda x: (x.get('backtest',{}).get('win_rate', 0), x.get('change', 0)), reverse=True)
    
    # Keep track of seen symbols to remove duplicates
    seen = set()
    count = 0
    
    for s in tw_stocks:
        if s['symbol'] not in seen:
            print(f"[{s['symbol']}] {s['name']}: WinRate={s.get('backtest',{}).get('win_rate', 'N/A')}%, Change={s['change']}%, Close={s['close']}")
            seen.add(s['symbol'])
            count += 1
            if count >= 5:
                break
except Exception as e:
    print("Error:", e)
