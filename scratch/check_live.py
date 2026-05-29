import urllib.request
import json

url = 'https://m0904103.github.io/trading/scan_results.json'
try:
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    print("LIVE DATA FETCHED:")
    for x in data.get('stocks', []):
        if x['symbol'] in ['2467.TW', '4991.TWO']:
            print(f"{x['symbol']}: Close={x['close']}, Change={x['change']}%")
except Exception as e:
    print("Error:", e)
