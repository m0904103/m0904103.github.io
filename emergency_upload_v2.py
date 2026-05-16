import os, subprocess, base64, json, urllib.request

token = subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()

# Source files are in the backend folder
base_path = r"C:\Users\manpo\OneDrive\桌面\m0904103_github_io\backend"
files_to_upload = [
    (os.path.join(base_path, "app.py"), "app.py"),
    (os.path.join(base_path, "requirements.txt"), "requirements.txt")
]

for local_path, repo_path in files_to_upload:
    print(f"Uploading {local_path} to {repo_path}...")
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
    except Exception as e:
        print(f"No existing {repo_path} found, or error: {e}")

    payload = {
        "message": f"Fixing root deployment: {repo_path}",
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
            print(f"Successfully uploaded {repo_path}: {response.status}")
    except Exception as e:
        print(f"Failed to upload {repo_path}: {e}")
