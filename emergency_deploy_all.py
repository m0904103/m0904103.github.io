import os, subprocess, base64, json, urllib.request

def deploy_src():
    try:
        # Get GitHub Token using gh CLI
        token_bytes = subprocess.check_output(["gh", "auth", "token"])
        token = token_bytes.decode('utf-8').strip()
    except Exception as e:
        print("Error:", e)
        return

    # Files to upload
    files_to_upload = [
        {"local": r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\src\App.jsx", "remote": "frontend/src/App.jsx"},
        {"local": r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\public\scan_results.json", "remote": "scan_results.json"}
    ]

    for f_info in files_to_upload:
        local_path = f_info['local']
        remote_path = f_info['remote']
        
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
            "message": f"Final Fix: App logic and data sync ({remote_path})",
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
                print(f"Success: {remote_path} uploaded")
        except Exception as e:
            print(f"Error: {remote_path} failed: {e}")

if __name__ == "__main__":
    deploy_src()
