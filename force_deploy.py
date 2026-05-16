import os
import subprocess
import base64
import json
import urllib.request
import time

def upload_file(token, repo, local_path, repo_path):
    try:
        with open(local_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')

        url = f"https://api.github.com/repos/{repo}/contents/{repo_path}"
        
        # 1. Get SHA
        sha = ""
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req) as res:
                sha = json.loads(res.read())['sha']
        except: pass

        # 2. Upload
        data = {
            "message": f"Force fix deployment: {repo_path}",
            "content": content,
            "branch": "main"
        }
        if sha: data["sha"] = sha

        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "Python-Urllib"
            },
            method="PUT"
        )
        
        with urllib.request.urlopen(req) as res:
            print(f"✅ SUCCESS: {repo_path}")
            return True
    except Exception as e:
        print(f"❌ FAILED: {repo_path} | Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting force deployment...")
    try:
        token = subprocess.check_output(['gh', 'auth', 'token'], shell=True).decode('utf-8').strip()
    except:
        print("Could not get token from gh CLI")
        exit(1)

    repo = "m0904103/m0904103.github.io"
    base_dir = r"C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\trading"
    
    # Files to fix
    files = [
        (os.path.join(base_dir, "index.html"), "trading/index.html"),
        (os.path.join(base_dir, "assets", "index-CFm-8QmK.css"), "trading/assets/index-CFm-8QmK.css"),
        (os.path.join(base_dir, "assets", "index-vsz9czNp.js"), "trading/assets/index-vsz9czNp.js"),
        (os.path.join(base_dir, "scan_results.json"), "trading/scan_results.json")
    ]

    for local, remote in files:
        upload_file(token, repo, local, remote)
        time.sleep(1) # Slow down to avoid secondary rate limits
