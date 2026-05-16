import os, subprocess, base64, json, urllib.request

token_bytes = subprocess.check_output(["gh", "auth", "token"])
token = token_bytes.decode('utf-8').strip()

file_path = r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\main.py"
with open(file_path, 'rb') as f:
    content = base64.b64encode(f.read()).decode('utf-8')

# Get sha of existing main.py
req_get = urllib.request.Request("https://api.github.com/repos/m0904103/AI_Stock_Scanner_Cloud/contents/main.py", headers={
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

url = "https://api.github.com/repos/m0904103/AI_Stock_Scanner_Cloud/contents/main.py"
payload = {
    "message": "Fix main.py encoding",
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
        print("Success:", response.status)
except Exception as e:
    print("Error:", str(e))
