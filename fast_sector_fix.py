import json
import os

STRATEGIC_MAPPING = {
    "太空/低空經濟": ["ASTS", "RKLB", "JOBY", "3491.TW", "2313.TW", "2634.TW", "8033.TW", "2314.TW", "6285.TW", "2630.TW"],
    "AI 基建/散熱": ["NVDA", "AVGO", "TSM", "VRT", "SMCI", "DELL", "2330.TW", "2317.TW", "2382.TW", "3017.TW", "6669.TW"],
    "AI 軟體/雲端": ["MSFT", "GOOGL", "META", "PLTR", "SNOW", "6231.TW", "3563.TW"],
    "核能/能源": ["CEG", "SMR", "OKLO", "VST", "1513.TW", "1519.TW", "1503.TW", "2308.TW"],
    "矽光子 (CPO)": ["3081.TW", "3363.TW", "4979.TW", "3163.TW", "6451.TW"],
    "記憶體 (HBM)": ["MU", "WDC", "2408.TW", "2344.TW", "3260.TW", "8299.TW"],
    "高階 PCB": ["2368.TW", "3037.TW", "2383.TW", "6274.TW", "2313.TW"]
}

DATA_FILE = os.path.join('frontend', 'public', 'scan_results.json')

def fast_fix():
    if not os.path.exists(DATA_FILE):
        return
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Reverse mapping for fast lookup
    symbol_to_sector = {}
    for sector, symbols in STRATEGIC_MAPPING.items():
        for sym in symbols:
            symbol_to_sector[sym] = sector
            
    updated = 0
    for stock in data.get('stocks', []):
        sym = stock.get('symbol')
        if sym in symbol_to_sector:
            stock['sector'] = symbol_to_sector[sym]
            updated += 1
            
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Fast Fix Complete: Updated {updated} stocks with strategic sectors.")

if __name__ == "__main__":
    fast_fix()
