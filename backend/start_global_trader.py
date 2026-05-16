
import os
import sys
import time
import uvicorn
from pyngrok import ngrok, conf
from app import app
import threading

# 設定 UTF-8 輸出避免編碼錯誤
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_api():
    print("\n[1/3] Starting Python API Core...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

def start_tunnel():
    print("[2/3] Opening Global Secure Tunnel (Ngrok)...")
    
    try:
        # 啟動隧道
        public_url = ngrok.connect(8000).public_url
        
        print("\n" + "="*60)
        print(" GLOBAL MODE ACTIVE ")
        print("="*60)
        print(f"\nPublic URL: {public_url}")
        print("\nCopy this URL into your iPhone App settings (Gear icon).")
        print("\n" + "="*60)
        print("Keep this window open to maintain connection.")
        print("="*60 + "\n")
        
    except Exception as e:
        print("\n[!] Tunnel failed to start.")
        if "authentication failed" in str(e).lower():
            print("\n>>> ERROR: Missing Authtoken.")
            print("Please run: ngrok config add-authtoken YOUR_TOKEN")
        else:
            print(f"Error detail: {e}")

if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()
    
    time.sleep(2)
    start_tunnel()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        ngrok.kill()
