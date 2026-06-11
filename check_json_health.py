import json
import sys

def check_health():
    try:
        with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return

    if 'stocks' not in data:
        print("Missing 'stocks' key!")
        return
        
    stocks = data['stocks']
    print(f"Total stocks: {len(stocks)}")
    
    # Check for missing crucial fields
    for i, s in enumerate(stocks):
        for key in ['symbol', 'close', 'ma60', 'signal', 'change']:
            if key not in s:
                print(f"Stock at index {i} missing '{key}'")
                
    print("JSON health check passed.")

check_health()
