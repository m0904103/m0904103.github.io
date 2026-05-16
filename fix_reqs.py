import os, subprocess, base64, json, urllib.request

token = subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()
file_path = r"c:\Users\manpo\OneDrive\桌面\m0904103_github_io\backend\requirements.txt"
with open(file_path, 'rb') as f:
    content = base64.b64encode(f.read()).decode('utf-8')

url = "https://api.github.com/repos/m0904103/m0904103.github.io/contents/backend/requirements.txt"
req_get = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
})
sha = ""
try:
    with urllib.request.urlopen(req_get) as response:
        data = json.loads(response.read().decode())
        sha = data['sha']
except: pass

payload = {
    "message": "Fix dependencies in requirements.txt",
    "content": content,
    "branch": "main",
    "sha": sha
}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "python-urllib"
}, method="PUT")

with urllib.request.urlopen(req) as response:
    print("Requirements Upload Success:", response.status)
