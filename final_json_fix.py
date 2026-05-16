import json
import os

DATA_FILE = r'c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\public\scan_results.json'

# Explicit mapping to fix any corrupted sector names
FIX_MAP = {
    "太空經濟": ["太空", "ӪŸg", "Space", "Space Economy"],
    "AI 基建": ["AI ", "Infrastructure", "AI Infrastructure"],
    "AI 軟體": ["AI n", "Software", "AI Software"],
    "記憶體": ["O", "Memory"],
    "矽光子 (CPO)": ["l (CPO)", "CPO"],
    "高階 PCB": [" PCB", "PCB"],
    "核能/能源": ["֯/෽", "Nuclear", "Energy"],
    "台股權值": ["Oql", "Weights"],
    "消費電子": ["q/", "Consumer"]
}

def final_fix():
    if not os.path.exists(DATA_FILE):
        return
        
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    stocks = data.get('stocks', [])
    updated = 0
    
    for s in stocks:
        sec = s.get('sector', '')
        # Try to find a match in the FIX_MAP
        found = False
        for correct_name, bad_variants in FIX_MAP.items():
            if sec == correct_name:
                found = True
                break
            for variant in bad_variants:
                if variant in sec:
                    s['sector'] = correct_name
                    updated += 1
                    found = True
                    break
            if found: break
            
        if not found and not sec:
            s['sector'] = "其他族群"
            
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Final Fix Complete: Repaired {updated} sector names.")

if __name__ == "__main__":
    final_fix()
