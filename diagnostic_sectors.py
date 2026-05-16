import json
import os

DATA_FILE = r'c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\public\scan_results.json'

def diagnostic():
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found")
        return
        
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', [])
    sectors = {}
    
    print(f"Total Stocks: {len(stocks)}")
    
    for s in stocks:
        sec = s.get('sector', 'MISSING')
        market = s.get('market', 'UNKNOWN')
        if sec not in sectors:
            sectors[sec] = {'tw': 0, 'us': 0, 'symbols': []}
        sectors[sec][market] += 1
        sectors[sec]['symbols'].append(f"{s['symbol']} ({market})")
        
    print("\n--- Sector Distribution ---")
    for sec, info in sectors.items():
        print(f"Sector: [{sec}]")
        print(f"  - TAIWAN: {info['tw']} stocks")
        print(f"  - USA:    {info['us']} stocks")
        print(f"  - Examples: {', '.join(info['symbols'][:3])}")
        
    # Check for specific problematic sectors
    for target in ['太空經濟', '記憶體', 'AI 基建']:
        if target not in sectors:
            print(f"\n⚠️ WARNING: Sector '{target}' NOT FOUND in data!")

if __name__ == "__main__":
    diagnostic()
