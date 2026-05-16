import requests
import json

url = "https://m0904103-github-io.onrender.com/scan"
try:
    print(f"Checking API: {url}")
    r = requests.get(url, timeout=10)
    data = r.json()
    
    version = data.get('backend_version', 'v4.7.x or older')
    print(f"Backend Version: {version}")
    
    tw_stocks = data.get('tw', [])
    us_stocks = data.get('us', [])
    print(f"Total TW stocks: {len(tw_stocks)}")
    print(f"Total US stocks: {len(us_stocks)}")
    
    if tw_stocks:
        print("\nTW Sample (is_regular?):", tw_stocks[0].get('symbol'), tw_stocks[0].get('is_regular'))
    if us_stocks:
        print("US Sample (is_regular?):", us_stocks[0].get('symbol'), us_stocks[0].get('is_regular'))

    # Check Active Market (Turtle)
    url_active = "https://m0904103-github-io.onrender.com/market/active"
    r_active = requests.get(url_active, timeout=10)
    active_data = r_active.json()
    print(f"Total Active/Turtle stocks: {len(active_data)}")
    if active_data:
        print("Active Sample:", active_data[0].get('symbol'), "Breakout:", active_data[0].get('is_breakout'))

except Exception as e:
    print(f"Error checking API: {e}")
