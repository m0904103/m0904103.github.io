import json
import math
import os
import shutil

def clean_nans(obj):
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj

file_path = 'scan_results.json'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()
    
# json.loads automatically parses NaN as float('nan')
data = json.loads(text)
data = clean_nans(data)

# Save to all 3 locations
paths = [
    'scan_results.json',
    'frontend/public/scan_results.json',
    'trading/scan_results.json'
]

for p in paths:
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)

print('Cleaned NaNs and saved to all paths.')

os.system('git add scan_results.json frontend/public/scan_results.json trading/scan_results.json')
os.system('git commit -m "Final fix for NaNs and conflict markers"')
os.system('git push origin main -f')
print('Successfully pushed to GitHub!')
