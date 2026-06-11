import re
import json
import os
import shutil

file_path = 'scan_results.json'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'<<<<<<<.*?\n', '', content)
content = re.sub(r'=======\n', '', content)
content = re.sub(r'>>>>>>>.*?\n', '', content)

content = re.sub(r':\s*NaN\b', ': null', content)
content = re.sub(r':\s*Infinity\b', ': null', content)
content = re.sub(r':\s*-Infinity\b', ': null', content)

try:
    data = json.loads(content)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Successfully repaired scan_results.json')
    
    shutil.copy2(file_path, 'frontend/public/scan_results.json')
    
    os.system('git add scan_results.json frontend/public/scan_results.json')
    os.system('git commit -m "Fix merge conflict markers"')
    os.system('git push origin main -f')
    os.system('python upload_frontend.py')
    
except Exception as e:
    print('Failed to parse repaired JSON:', e)
