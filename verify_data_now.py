import json
import datetime
import os
import subprocess

try:
    with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print('Last Updated:', data.get('last_updated'))
    
    stocks = data.get('stocks', [])
    tw_stocks = [s for s in stocks if s['market'] == 'tw']
    us_stocks = [s for s in stocks if s['market'] == 'us']
    
    print(f'Total TW Stocks: {len(tw_stocks)}')
    print(f'Total US Stocks: {len(us_stocks)}')
    
    s_tw = next((s for s in tw_stocks if s['symbol'] == '2330.TW'), None)
    if s_tw: print(f"TW Sample (2330.TW): Close={s_tw['close']}, Signal={s_tw['signal']}")
    
    s_us = next((s for s in us_stocks if s['symbol'] == 'MSFT'), None)
    if s_us: print(f"US Sample (MSFT): Close={s_us['close']}, Signal={s_us['signal']}")
    
    # Check if daemon is running
    proc = subprocess.run(['powershell', '-c', 'Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName'], capture_output=True, text=True)
    lines = proc.stdout.strip().split('\n')
    print('Python processes running:', len(lines) - 2 if proc.stdout.strip() else 0)

except Exception as e:
    print('Error:', e)
