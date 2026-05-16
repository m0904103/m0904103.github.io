import os, subprocess, base64, json, urllib.request

# Get token
token_bytes = subprocess.check_output(["gh", "auth", "token"])
token = token_bytes.decode('utf-8').strip()

# Read backend app.py (from our current workspace)
file_path = r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\backend\app.py"
with open(file_path, 'rb') as f:
    content = base64.b64encode(f.read()).decode('utf-8')

# Target Repository: m0904103.github.io
repo = "m0904103/m0904103.github.io"
target_path = "app.py"

# Get sha of existing file in the OTHER repo
req_get = urllib.request.Request(f"https://api.github.com/repos/{repo}/contents/{target_path}", headers={
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
url = f"https://api.github.com/repos/{repo}/contents/{target_path}"
payload = {
    "message": "Final Turtle v1.1.5 - Target Correct Repo",
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
        print(f"Success: {response.status}")
except Exception as e:
    print(f"Error: {str(e)}")
