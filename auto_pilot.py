import subprocess
import time
import sys
from datetime import datetime

def run_step(command):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Executing: {command}")
    try:
        # Use shell=True for Windows powershell compatibility if needed, 
        # but here we use the full path to python
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("--- Success ---")
            print(result.stdout[-200:]) # Show last 200 chars of output
        else:
            print(f"--- Failed (Code {result.returncode}) ---")
            print(result.stderr)
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    python_path = r'C:\Users\manpo\AppData\Local\Programs\Python\Python313\python.exe'
    
    print("="*50)
    print("   2026 REGULAR ARMY - AUTO PILOT MODE   ")
    print("="*50)
    print(f"Interval: 10 minutes")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C to stop the automation.")
    
    try:
        while True:
            # Step 1: Scan Stocks
            run_step(f'"{python_path}" check_us.py')
            
            # Step 2: Upload Results
            run_step(f'"{python_path}" upload_frontend.py')
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sleeping for 10 minutes...")
            time.sleep(600) # 10 minutes
            
    except KeyboardInterrupt:
        print("\nAuto-pilot stopped by user.")
    except Exception as e:
        print(f"\nCritical Error in Auto-pilot: {str(e)}")

if __name__ == "__main__":
    main()
