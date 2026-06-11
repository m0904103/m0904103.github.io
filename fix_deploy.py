import re
import os

print("Fetching and resetting to remote main...")
os.system('git fetch origin main')
os.system('git reset --hard origin/main')

print("Repairing NaN in JSON...")
with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
    content = f.read()
    
fixed = re.sub(r':\s*NaN\b', ': null', content)
fixed = re.sub(r':\s*Infinity\b', ': null', fixed)

with open('frontend/public/scan_results.json', 'w', encoding='utf-8') as f:
    f.write(fixed)
    
print("Building and deploying frontend...")
os.system('cd frontend && npm run build && cd .. && python upload_frontend.py')
print("Deploy script finished.")
