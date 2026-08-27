import time
import subprocess
import os
import sys
from datetime import datetime

repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Market Sync Daemon started...")

while True:
    try:
        now = datetime.now()
        print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled sync iteration...")
        
        # 1. Sync Regular Army
        subprocess.run([sys.executable, "sync_regular_army_2026.py"], check=False)
        
        # 2. Scan TW Big Data
        subprocess.run([sys.executable, "scan_tw_big_data.py"], check=False)
        
        # 3. Build Frontend
        frontend_dir = os.path.join(repo_root, "frontend")
        subprocess.run("npm run build", cwd=frontend_dir, shell=True, check=False)
        
        # 4. Upload & Deploy
        subprocess.run([sys.executable, "upload_frontend.py"], check=False)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sync cycle complete! Sleeping 10 minutes...")
    except Exception as e:
        print(f"[ERROR] Sync cycle exception: {e}")
        
    time.sleep(600)
