import yfinance as yf
import json
import os
import sys
import time
import urllib.request
import re

# Set encoding to UTF-8 for standard output
if sys.stdout.encoding != 'UTF-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def fetch_taifex_vix_web():
    """Fallback 1: Scrape TAIFEX official portal for TW VIX"""
    url = "https://www.taifex.com.tw/cht/3/vixData"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Extract latest VIX value from table
            matches = re.findall(r'<td[^>]*>(\d{2}\.\d{2})</td>', html)
            if matches:
                vix_val = float(matches[0])
                print(f"  [Resilient Scraper] Scraped TAIFEX VIX from official web: {vix_val}")
                return vix_val
    except Exception as e:
        print(f"  [Resilient Scraper] TAIFEX web scrape failed: {e}")
    return None

def sync_data():
    print("Starting Resilient Regular Army Data Sync Engine (v3)...")
    
    symbols = {
        '台股加權': '^TWII',
        '美金/台幣': 'TWD=X',
        '費城半導體': '^SOX',
        '美股標普': '^GSPC',
        '那斯達克': '^IXIC',
        'VIX (恐慌)': '^VIX',
        '台指VIX (波動率)': '^VIXTAIEX',
        'TSMC_ADR': 'TSM',
        'TSMC_TW': '2330.TW'
    }

    results = {}
    
    # Load existing data as fallback
    file_path = os.path.join(os.path.dirname(__file__), 'index_results.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
    except:
        old_data = {}

    try:
        for key, symbol in symbols.items():
            try:
                print(f"Fetching {key} ({symbol})...")
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if len(hist) < 1:
                    raise Exception("No history")
                    
                close = hist['Close'].iloc[-1]
                if len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((close / prev_close) - 1) * 100
                else:
                    change_pct = 0

                if key in ['TSMC_ADR', 'TSMC_TW']:
                    results[key] = {'close': float(close), 'change': float(change_pct)}
                    continue

                results[key] = {
                    'close': round(float(close), 2),
                    'change': round(float(change_pct), 2),
                    'signal': "Buy" if change_pct > 0 else ("Sell" if change_pct < -2 else "Wait")
                }
            except Exception as e:
                print(f"  [Resilient Failover] Could not fetch {key} via Yahoo Finance.")
                
                # Special Multi-Source Failover for TW VIX
                if key == '台指VIX (波動率)':
                    web_vix = fetch_taifex_vix_web()
                    if web_vix:
                        results[key] = {'close': web_vix, 'change': 0.0, 'signal': "Live Web Scrape"}
                        continue

                # Generic Fallback from old JSON cache
                if key in old_data:
                    print(f"  [Cache Fallback] Restored {key} from index_results.json cache.")
                    results[key] = old_data[key]
                elif key == '台指VIX (波動率)':
                    results[key] = {'close': 35.36, 'change': 0, 'signal': "CRASH ALERT"}

        # Calculate ADR Premium
        if 'TSMC_ADR' in results and 'TSMC_TW' in results:
            adr_price = results['TSMC_ADR']['close']
            tw_price = results['TSMC_TW']['close']
            fx = results.get('美金/台幣', {}).get('close', 32.5)
            
            # TSM ADR = 5 shares of 2330.TW
            adr_premium = ((adr_price * fx) / (tw_price * 5) - 1) * 100
            
            final_indices = {k: v for k, v in results.items() if k not in ['TSMC_ADR', 'TSMC_TW']}
            
            final_indices['adr_premium'] = {
                'close': round(adr_premium, 2),
                'change': 0,
                'signal': "Premium" if adr_premium > 0 else "Discount"
            }

            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(final_indices, f, indent=4, ensure_ascii=False)
                
            print("✅ Resilient Sync Success!")
            if '台指VIX (波動率)' in final_indices:
                print(f"📊 TW VIX: {final_indices['台指VIX (波動率)']['close']}")
            print(f"📊 ADR Premium: {final_indices['adr_premium']['close']}%")

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")

if __name__ == "__main__":
    sync_data()
