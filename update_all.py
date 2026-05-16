import os
import shutil
import subprocess
import json
from datetime import datetime

def run_cmd(cmd, cwd=None):
    print(f"Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0:
        print(f"Error (Code {result.returncode}): {result.stderr}")
    else:
        # Avoid UnicodeEncodeError when printing to a non-UTF8 terminal
        try:
            print(result.stdout)
        except UnicodeEncodeError:
            print(result.stdout.encode('ascii', errors='ignore').decode('ascii'))
    return result.returncode == 0

python_path = r'C:\Users\manpo\AppData\Local\Programs\Python\Python313\python.exe'
root_dir = r'c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud'
frontend_dir = os.path.join(root_dir, 'frontend')
public_dir = os.path.join(frontend_dir, 'public')

print(f"--- Starting Full Update at {datetime.now()} ---")

# 1. Run Scan
if run_cmd(f'"{python_path}" check_us.py', root_dir):
    # 2. Copy Results to Public
    src = os.path.join(root_dir, 'scan_results.json')
    dst = os.path.join(public_dir, 'scan_results.json')
    shutil.copy2(src, dst)
    print(f"Copied scan_results.json to {dst}")
    
    # 2b. Extract indices and save to index_results.json
    try:
        with open(src, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'indices' in data:
                idx_path = os.path.join(public_dir, 'index_results.json')
                with open(idx_path, 'w', encoding='utf-8') as f2:
                    json.dump(data['indices'], f2, ensure_ascii=False, indent=2)
                print(f"Updated {idx_path}")
    except Exception as e:
        print(f"Error updating indices: {e}")

    # Also copy to guru_army_data_v9.json for redundant loading
    dst2 = os.path.join(public_dir, 'guru_army_data_v9.json')
    shutil.copy2(src, dst2)
    print(f"Copied scan_results.json to {dst2}")

    # 3. Build Frontend (Clean assets first to avoid stale code)
    assets_path = os.path.join(frontend_dir, 'dist', 'assets')
    if os.path.exists(assets_path):
        print(f"Cleaning {assets_path}...")
        try:
            shutil.rmtree(assets_path)
        except:
            pass # Continue if locked, build will overwrite some
        
    if run_cmd('npm run build', frontend_dir):
        # 4. Upload
        run_cmd(f'"{python_path}" upload_frontend.py', root_dir)

print(f"--- Full Update Complete at {datetime.now()} ---")
