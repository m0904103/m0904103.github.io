import os
import subprocess
import base64
import json
import urllib.request
import time

def deploy():
    print("--- [DEPLOY] START ---")
    
    # 1. Get GitHub Token
    try:
        token = subprocess.check_output(['gh', 'auth', 'token'], shell=True).decode('utf-8').strip()
        print(f"[OK] GitHub Token acquired (m0904103)")
    except Exception as e:
        print(f"[ERROR] Failed to get token: {e}. Please run 'gh auth login'")
        return

    repo = "m0904103/m0904103.github.io"
    base_dir = r"C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\trading"
    
    # 2. Scan files
    files_to_upload = []
    for root, dirs, filenames in os.walk(base_dir):
        for f in filenames:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, base_dir)
            repo_path = f"trading/{rel_path.replace('\\', '/')}"
            files_to_upload.append((full_path, repo_path))

    print(f"[INFO] Preparing to upload {len(files_to_upload)} files...")

    # 3. Upload one by one
    for local_path, repo_path in files_to_upload:
        try:
            with open(local_path, 'rb') as f:
                content_bytes = f.read()
                content_b64 = base64.b64encode(content_bytes).decode('utf-8')

            url = f"https://api.github.com/repos/{repo}/contents/{repo_path}"
            
            # Get existing SHA
            sha = ""
            req_get = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Mozilla/5.0"
            })
            try:
                with urllib.request.urlopen(req_get) as response:
                    res_data = json.loads(response.read().decode())
                    sha = res_data['sha']
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    print(f"[WARN] Error checking {repo_path}: {e}")

            # Upload/Update
            payload = {
                "message": f"Deploy: {repo_path} (updated via script)",
                "content": content_b64,
                "branch": "main"
            }
            if sha:
                payload["sha"] = sha

            req_put = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }, 
                method="PUT"
            )

            with urllib.request.urlopen(req_put) as response:
                print(f"[OK] Success: {repo_path}")
            
            time.sleep(0.1)

        except Exception as e:
            print(f"[ERROR] Failed: {repo_path} | Error: {e}")

    print("--- [DEPLOY] FINISHED ---")

if __name__ == "__main__":
    deploy()
