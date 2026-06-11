import os
import re
import auto_sync
import sys

print("Running auto_sync.sync_once()...")
try:
    auto_sync.sync_once()
except Exception as e:
    print(f"Sync error: {e}")

print("Repairing JSON just in case...")
try:
    with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
        content = f.read()
    fixed = re.sub(r':\s*NaN\b', ': null', content)
    fixed = re.sub(r':\s*Infinity\b', ': null', fixed)
    with open('frontend/public/scan_results.json', 'w', encoding='utf-8') as f:
        f.write(fixed)
except Exception as e:
    print(f"JSON repair error: {e}")

print("Building and deploying...")
os.system('cd frontend && npm run build && cd .. && python upload_frontend.py')
print("Complete!")
