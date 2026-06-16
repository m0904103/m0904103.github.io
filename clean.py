import json
import math

def clean_nans(obj):
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    return obj

data = json.load(open('frontend/public/scan_results.json', encoding='utf-8'))
cleaned = clean_nans(data)
json.dump(cleaned, open('trading/scan_results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
json.dump(cleaned, open('frontend/public/scan_results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
