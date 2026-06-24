import json

files = ['trading/scan_results.json', 'frontend/public/scan_results.json']
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    data['taifex_oi'] = -83605
    
    if 'indices' not in data:
        data['indices'] = {}
        
    data['indices']["台指 VIX (波動率)"] = {"close": 40.88}
    data['indices']["散戶小台多空比"] = {"close": 20.17}
    data['indices']["微台散戶多空比"] = {"close": 56.48}
    data['indices']["全市場 P/C Ratio"] = {"close": 134.59}
    
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

print("JSON updated successfully!")
