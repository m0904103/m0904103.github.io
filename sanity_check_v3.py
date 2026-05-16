import json
import os

DATA_FILE = r'c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\public\scan_results.json'

def sanity_check():
    if not os.path.exists(DATA_FILE):
        print("Data file missing!")
        return
        
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', [])
    
    print(f"Total Stocks in DB: {len(stocks)}")
    
    # Check Space Economy
    space_tw = [s['symbol'] for s in stocks if s['sector'] == '太空經濟' and s['market'] == 'tw']
    space_us = [s['symbol'] for s in stocks if s['sector'] == '太空經濟' and s['market'] == 'us']
    
    # Check Memory
    memory_tw = [s['symbol'] for s in stocks if s['sector'] == '記憶體' and s['market'] == 'tw']
    memory_us = [s['symbol'] for s in stocks if s['sector'] == '記憶體' and s['market'] == 'us']
    
    print("\n[太空經濟] Results:")
    print(f"  - TAIWAN ({len(space_tw)}): {', '.join(space_tw)}")
    print(f"  - USA ({len(space_us)}): {', '.join(space_us)}")
    
    print("\n[記憶體] Results:")
    print(f"  - TAIWAN ({len(memory_tw)}): {', '.join(memory_tw)}")
    print(f"  - USA ({len(memory_us)}): {', '.join(memory_us)}")
    
    if len(space_tw) > 0 and len(space_us) > 0:
        print("\n✅ SANITY CHECK PASSED: Multi-market logic is armed.")
    else:
        print("\n❌ SANITY CHECK FAILED: Missing market data.")

if __name__ == "__main__":
    sanity_check()
