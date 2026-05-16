import os, subprocess, base64, json, urllib.request

# Get token
token_bytes = subprocess.check_output(["gh", "auth", "token"])
token = token_bytes.decode('utf-8').strip()

# Read file
file_path = r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\.github\workflows\schedule.yml"
with open(file_path, 'rb') as f:
    content = base64.b64encode(f.read()).decode('utf-8')

# API URL
url = "https://api.github.com/repos/m0904103/AI_Stock_Scanner_Cloud/contents/.github/workflows/schedule.yml"

payload = {
    "message": "Add schedule workflow",
    "content": content,
    "branch": "main"
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "python-urllib"
}, method="PUT")

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.status)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("Error:", str(e))
