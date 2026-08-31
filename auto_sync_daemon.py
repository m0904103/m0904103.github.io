import time
import subprocess
import os
import sys
import socket
import tempfile
import psutil
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ============================================================
# 單例鎖定 v2 — PID 檔案鎖（跨 Python 版本均有效）
# 無論從 pythoncore 或 Windows Store 版 Python 啟動
# 都能正確偵測到另一個複本正在執行
# ============================================================
_LOCK_FILE = os.path.join(tempfile.gettempdir(), "auto_sync_daemon.lock")

def _check_and_acquire_lock():
    if os.path.exists(_LOCK_FILE):
        try:
            with open(_LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            # 檢查該 PID 是否真的還活著
            if psutil.pid_exists(old_pid):
                proc = psutil.Process(old_pid)
                cmdline = " ".join(proc.cmdline())
                if "auto_sync_daemon" in cmdline:
                    return False  # 確實有另一個在跑，退出
        except Exception:
            pass  # 舊的 lock 檔案損毀或 PID 已不存在，繼續覆寫
    # 寫入自己的 PID
    with open(_LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True

if not _check_and_acquire_lock():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  auto_sync_daemon 已經在執行中，本次啟動自動退出。")
    sys.exit(0)

import atexit
atexit.register(lambda: os.remove(_LOCK_FILE) if os.path.exists(_LOCK_FILE) else None)
# ============================================================

repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] High-Frequency Market Sync Daemon started (PID lock acquired: {_LOCK_FILE})...")

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
