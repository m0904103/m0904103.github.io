import os, subprocess, base64, json, urllib.request

def deploy_data():
    try:
        # Get GitHub Token using gh CLI
        token_bytes = subprocess.check_output(["gh", "auth", "token"])
        token = token_bytes.decode('utf-8').strip()
    except Exception as e:
        print("Error: Could not get GitHub token. Please run 'gh auth login'.", e)
        return

    # Files to upload
    files_to_upload = [
        {"local": r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\public\scan_results.json", "remote": "scan_results.json"},
        {"local": r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\public\scan_results.json", "remote": "frontend/public/scan_results.json"}
    ]

    for f_info in files_to_upload:
        local_path = f_info['local']
        remote_path = f_info['remote']
        
        if not os.path.exists(local_path):
            print(f"Skipping {local_path}, not found.")
            continue

        with open(local_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')

        url = f"https://api.github.com/repos/m0904103/m0904103.github.io/contents/{remote_path}"

        # Get existing SHA
        req_get = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        })
        sha = ""
        try:
            with urllib.request.urlopen(req_get) as response:
                data = json.loads(response.read().decode())
                sha = data['sha']
        except:
            pass

        payload = {
            "message": f"Strategic Data Sync: 2026 Regular Army Updates ({remote_path})",
            "content": content,
            "branch": "main",
            "sha": sha
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "python-urllib"
        }, method="PUT")

        try:
            with urllib.request.urlopen(req) as response:
                print(f"Success: {remote_path} uploaded (Status {response.status})")
        except Exception as e:
            print(f"Error: {remote_path} upload failed: {e}")

if __name__ == "__main__":
    deploy_data()
