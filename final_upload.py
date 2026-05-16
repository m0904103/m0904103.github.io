import os, subprocess, base64, json, urllib.request

token = subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()

# SOURCE is the root folder now
base_path = r"C:\Users\manpo\OneDrive\桌面\m0904103_github_io"
files_to_upload = [
    (os.path.join(base_path, "app.py"), "app.py"),
    (os.path.join(base_path, "requirements.txt"), "requirements.txt"),
    (os.path.join(base_path, "runtime.txt"), "runtime.txt"),
    (os.path.join(base_path, "index.html"), "index.html")
]

for local_path, repo_path in files_to_upload:
    with open(local_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')

    url = f"https://api.github.com/repos/m0904103/m0904103.github.io/contents/{repo_path}"
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

    import datetime
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "message": f"Master v6.0 Deployment - {now_str}",
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
        print(f"Uploaded {repo_path}: {response.status}")
