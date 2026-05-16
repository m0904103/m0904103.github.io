import os, subprocess, base64, json, urllib.request

token_bytes = subprocess.check_output(["gh", "auth", "token"])
token = token_bytes.decode('utf-8').strip()

file_path = r"c:\Users\manpo\OneDrive\桌面\m0904103_github_io\backend\app.py"
with open(file_path, 'rb') as f:
    content = base64.b64encode(f.read()).decode('utf-8')

url = "https://api.github.com/repos/m0904103/m0904103.github.io/contents/backend/app.py"

req_get = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
})
sha = ""
try:
    with urllib.request.urlopen(req_get) as response:
        data = json.loads(response.read().decode())
        sha = data['sha']
except Exception as e:
    print("Could not get existing sha, might be new file or error:", e)

payload = {
    "message": "Update backend API logic for Render deployment",
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
        print("Backend Upload Success:", response.status)
except Exception as e:
    print("Backend Upload Error:", str(e))
