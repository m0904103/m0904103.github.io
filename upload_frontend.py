import os
import subprocess
import base64
import json
import urllib.request

# Get GitHub token
try:
    token_bytes = subprocess.check_output(["gh", "auth", "token"])
    token = token_bytes.decode('utf-8').strip()
except Exception as e:
    print("Failed to get gh token:", e)
    exit(1)

dist_dir = r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\dist"
repo_owner = "m0904103"
repo_name = "m0904103.github.io"
base_path = "trading" # 上傳至 trading 子目錄

def upload_file(local_path, remote_path):
    with open(local_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{remote_path}"

    # Get SHA if file exists
    req_get = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    })
    sha = ""
    try:
        with urllib.request.urlopen(req_get) as response:
            data = json.loads(response.read().decode())
            sha = data['sha']
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"Error checking sha for {remote_path}: {e}")
    except Exception as e:
        print(f"Error checking sha for {remote_path}: {e}")

    # Upload file
    payload = {
        "message": f"Auto-deploy update to {remote_path}",
        "content": content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "python-urllib"
    }, method="PUT")

    try:
        with urllib.request.urlopen(req) as response:
            print(f"Uploaded {remote_path}: {response.status}")
    except Exception as e:
        print(f"Failed to upload {remote_path}: {e}")

# Walk through dist directory and upload
for root, dirs, files in os.walk(dist_dir):
    # Skip .git and other hidden directories
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    
    for file in files:
        if file.startswith('.'):
            continue
            
        local_path = os.path.join(root, file)
        # Calculate relative path from dist directory
        rel_path = os.path.relpath(local_path, dist_dir)
        # Convert Windows backslashes to forward slashes for GitHub
        if base_path:
            remote_path = f"{base_path}/{rel_path}".replace("\\", "/")
        else:
            remote_path = rel_path.replace("\\", "/")
        print(f"Uploading {local_path} to {remote_path}...")
        upload_file(local_path, remote_path)

print("Frontend upload complete!")
