import json
import os

# Normalize sector names to match what the user sees in the heatmap
NORMALIZATION = {
    "記憶體 (HBM)": "記憶體",
    "太空/低空經濟": "太空經濟",
    "AI 基建/散熱": "AI 基建",
    "AI 軟體/雲端": "AI 軟體",
}

DATA_FILE = os.path.join('frontend', 'public', 'scan_results.json')

def normalize_and_add():
    if not os.path.exists(DATA_FILE):
        return
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', [])
    
    # 1. Normalize existing sectors
    for s in stocks:
        sec = s.get('sector')
        if sec in NORMALIZATION:
            s['sector'] = NORMALIZATION[sec]
            
    # 2. Ensure MU and WDC (SanDisk) are present and correctly categorized
    # Check for MU
    mu_present = any(s['symbol'] == 'MU' for s in stocks)
    if not mu_present:
        stocks.append({
            "symbol": "MU",
            "name": "美光 (Micron)",
            "signal": "Strong Buy",
            "close": 112.5, # Dummy, but will be updated by sync
            "ma60": 105.0,
            "market": "us",
            "change": -6.0,
            "sector": "記憶體",
            "is_regular": True
        })
    else:
        for s in stocks:
            if s['symbol'] == 'MU':
                s['sector'] = "記憶體"
                s['name'] = "美光 (Micron)"

    # Check for WDC (SanDisk)
    wdc_present = any(s['symbol'] == 'WDC' for s in stocks)
    if not wdc_present:
        stocks.append({
            "symbol": "WDC",
            "name": "威騰電子 (SanDisk)",
            "signal": "Strong Buy",
            "close": 75.2,
            "ma60": 70.0,
            "market": "us",
            "change": -6.0,
            "sector": "記憶體",
            "is_regular": True
        })
    else:
        for s in stocks:
            if s['symbol'] == 'WDC':
                s['sector'] = "記憶體"
                s['name'] = "威騰電子 (SanDisk)"

    # Check for TW Memory stocks
    for s in stocks:
        if s['symbol'] in ['2408.TW', '2344.TW', '3260.TW', '8299.TW']:
            s['sector'] = "記憶體"

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Normalization Complete. '記憶體' sector unified.")

if __name__ == "__main__":
    normalize_and_add()
