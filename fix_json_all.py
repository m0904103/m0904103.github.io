import json
import os

paths = [
    'frontend/public/scan_results.json',
    'scan_results.json',
    'trading/scan_results.json',
    'q_quant_888/scan_results.json'
]

for p in paths:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        last_brace = content.rfind('}')
        valid_obj = None
        while last_brace > 0:
            sub = content[:last_brace+1]
            try:
                valid_obj = json.loads(sub)
                break
            except Exception:
                last_brace = content.rfind('}', 0, last_brace)
        if valid_obj:
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(valid_obj, f, ensure_ascii=False, indent=2)
            print(f"Fixed {p}: valid JSON saved, stocks count = {len(valid_obj.get('stocks', []))}")
        else:
            print(f"Failed to fix {p}")
