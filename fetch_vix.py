"""
台指 VIX 爬蟲腳本 - 輕量化版本 (免 Playwright)
"""
import os
import json
import re
import requests
from datetime import datetime

def fetch_vix():
    vix_val = None
    source = None

    print("Fetching Taiwan VIX...")

    # Method 1: TAIFEX VolatilityQuotes (No playwright needed)
    print("Trying TAIFEX VolatilityQuotes...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        url = 'https://mis.taifex.com.tw/futures/VolatilityQuotes/'
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            content = r.content.decode('utf-8', errors='ignore')
            # Extract number like 17.35 or 38.59
            nums = re.findall(r'(\d{2,3}\.\d{2})', content)
            valid = [float(n) for n in nums if 5.0 < float(n) < 120.0]
            if valid:
                vix_val = valid[0]
                source = "TAIFEX VolatilityQuotes"
                print(f"  [OK] Found: {vix_val}")
    except Exception as e:
        print(f"  [ERROR] TAIFEX failed: {e}")

    # Method 2: TAIFEX index page HTML content (fallback)
    if vix_val is None:
        print("Trying TAIFEX index page fallback...")
        try:
            r = requests.get('https://www.taifex.com.tw/cht/index', headers=headers, timeout=15)
            if r.status_code == 200:
                content = r.content.decode('big5', errors='ignore')
                nums = re.findall(r'>(\d{2,3}\.\d{2})<', content)
                valid = [float(n) for n in nums if 5.0 < float(n) < 120.0]
                if valid:
                    vix_val = valid[0]
                    source = "TAIFEX index"
                    print(f"  [OK] Found: {vix_val}")
        except Exception as e:
            print(f"  [ERROR] TAIFEX fallback failed: {e}")

    # Save result
    if vix_val is not None:
        data_to_save = {
            "vix": round(float(vix_val), 2),
            "source": source,
            "last_updated": datetime.now().isoformat()
        }
        os.makedirs("trading", exist_ok=True)
        out_path = "trading/vix.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4)
        print(f"\n[SUCCESS] Saved VIX {vix_val} from [{source}] -> {out_path}")
        return True
    else:
        print("\n[WARN] All sources failed. Checking for existing vix.json to preserve...")
        if os.path.exists("trading/vix.json"):
            print("  Existing vix.json preserved (not overwritten).")
        return False

if __name__ == "__main__":
    fetch_vix()
