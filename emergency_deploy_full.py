
import os, subprocess, base64, json, urllib.request

# Get token
token_bytes = subprocess.check_output(["gh", "auth", "token"])
token = token_bytes.decode('utf-8').strip()

repo = "m0904103/m0904103.github.io"
# 同步上傳後端程式碼、依賴庫與掃描結果
files_to_upload = [
    (r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\main_remote2_utf8.py", "main_remote2_utf8.py"),
    (r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\main.py", "main.py"),
    (r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\backend\app.py", "app.py"),
    (r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\requirements.txt", "requirements.txt"),
    (r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\scan_results.json", "scan_results.json"),
    (r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\index_results.json", "index_results.json")
]

for local_path, remote_path in files_to_upload:
    if not os.path.exists(local_path): continue
    
    with open(local_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')

    url = f"https://api.github.com/repos/{repo}/contents/{remote_path}"
    
    # Get sha
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

    # Upload
    payload = {
        "message": "Final System Recovery: Fixing RSI and Dependencies",
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
            print(f"Uploaded {remote_path}: Success {response.status}")
    except Exception as e:
        print(f"Error uploading {remote_path}: {str(e)}")

print("System Full Recovery Sync Complete!")
