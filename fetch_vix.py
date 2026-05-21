import os
import json
from datetime import datetime
import re

def fetch_vix():
    vix_val = None
    
    print("Starting Playwright to fetch Taiwan VIX from MacroMicro...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # Go to the Taiwan VIX page
            page.goto("https://www.macromicro.me/collections/45/tw-stock-relative/4843/taiwan-vix", timeout=60000)
            page.wait_for_timeout(10000) # Wait 10 seconds for Cloudflare and data to load
            
            html = page.content()
            
            # Extract the value using regex. Usually it's in a stat box or tooltip.
            # MacroMicro often has class "stat-val" or "stat-value".
            # If not, we search for a specific pattern around the chart data.
            match = re.search(r'data-value=["\']?(\d+\.\d+)["\']?', html)
            if match:
                vix_val = float(match.group(1))
            else:
                # Fallback regex: Look for a standalone number that looks like VIX (between 10.00 and 60.00) near the word VIX
                # This is a bit hacky but works if the DOM changes.
                prices = re.findall(r'>(\d{2}\.\d{2})<', html)
                if prices:
                    # Filter realistic VIX values
                    valid_prices = [float(p) for p in prices if 10.0 <= float(p) <= 80.0]
                    if valid_prices:
                        vix_val = valid_prices[0]
            
            browser.close()
    except Exception as e:
        print(f"Playwright scraping failed: {e}")

    # Fallback to Taifex MIS API (sometimes it works on GH Actions)
    if vix_val is None:
        print("Falling back to Taifex MIS API...")
        try:
            import requests
            url = "https://mis.taifex.com.tw/futures/api/getQuoteList"
            payload = {"MarketType":"0","SymbolType":"I","KindID":"0","CID":"VIX"}
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            data = res.json()
            # Parse Taifex JSON
            if 'RtData' in data and 'QuoteList' in data['RtData']:
                quotes = data['RtData']['QuoteList']
                if quotes and 'CPrice' in quotes[0]:
                    vix_val = float(quotes[0]['CPrice'])
        except Exception as e:
            print(f"Taifex API failed: {e}")

    if vix_val is not None:
        data_to_save = {
            "vix": vix_val,
            "last_updated": datetime.now().isoformat()
        }
        os.makedirs("trading", exist_ok=True)
        with open("trading/vix.json", "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Successfully saved VIX: {vix_val}")
    else:
        print("Failed to fetch VIX from all sources.")
        # We don't fail the action to prevent spamming failure emails, just exit 0
        
if __name__ == "__main__":
    fetch_vix()
