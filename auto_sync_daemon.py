import time
import subprocess
import os
import sys
import socket
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ============================================================
# 單例鎖定 (Singleton Lock) - 確保只有一個複本在執行
# 使用 socket 佔用一個固定的本機 port 作為互斥鎖
# ============================================================
_SINGLETON_PORT = 47892  # 任意選一個不常用的 port
_singleton_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    _singleton_socket.bind(('127.0.0.1', _SINGLETON_PORT))
except OSError:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  auto_sync_daemon 已經在執行中，本次啟動自動退出。")
    sys.exit(0)
# ============================================================

repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] High-Frequency Market Sync Daemon started (singleton lock acquired on port {_SINGLETON_PORT})...")

def is_market_open():
    now = datetime.now()
    weekday = now.weekday() # 0 = Monday, 6 = Sunday
    hour = now.hour
    minute = now.minute
    current_time_val = hour * 60 + minute

    if weekday < 5: # Mon - Fri
        # TW Session: 08:40 - 13:45
        if 8 * 60 + 40 <= current_time_val <= 13 * 60 + 45:
            return True
        # US Session: 21:00 - 04:30
        if current_time_val >= 21 * 60 or current_time_val <= 4 * 60 + 30:
            return True
    return False

while True:
    try:
        now = datetime.now()
        market_status = "ACTIVE TRADING" if is_market_open() else "OFF-HOURS"
        print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] [{market_status}] Starting sync iteration...")
        
        # 1. Sync Regular Army
        subprocess.run([sys.executable, "sync_regular_army_2026.py"], check=False)
        
        # 2. Scan TW Big Data
        subprocess.run([sys.executable, "scan_tw_big_data.py"], check=False)
        
        # 3. Build Frontend
        frontend_dir = os.path.join(repo_root, "frontend")
        subprocess.run("npm run build", cwd=frontend_dir, shell=True, check=False)
        
        # 4. Upload & Deploy
        subprocess.run([sys.executable, "upload_frontend.py"], check=False)
        
        sleep_sec = 30 if is_market_open() else 180
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sync cycle complete! Sleeping {sleep_sec}s...")
        time.sleep(sleep_sec)
        
    except Exception as e:
        print(f"[ERROR] Sync cycle exception: {e}")
        time.sleep(30)
