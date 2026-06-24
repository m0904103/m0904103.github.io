import json
data = json.load(open('trading/scan_results.json', encoding='utf-8'))
dell = [s for s in data['stocks'] if s['symbol'] == 'DELL'][0]
print(f'DELL: Close={dell['close']}, MA60={dell['ma60']}')
