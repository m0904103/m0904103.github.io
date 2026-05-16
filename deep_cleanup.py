import os, subprocess, base64, json, urllib.request

token = subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()

def delete_file(repo_path, sha):
    url = f"https://api.github.com/repos/m0904103/m0904103.github.io/contents/{repo_path}"
    payload = {"message": f"Deep Cleanup: {repo_path}", "sha": sha, "branch": "main"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Authorization": f"Bearer {token}"}, method="DELETE")
    urllib.request.urlopen(req)
    print(f"Deleted {repo_path}")

def list_and_delete_recursive(path):
    url = f"https://api.github.com/repos/m0904103/m0904103.github.io/contents/{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"})
    try:
        with urllib.request.urlopen(req) as response:
            items = json.loads(response.read().decode())
            for item in items:
                if item['type'] == 'dir':
                    list_and_delete_recursive(item['path'])
                else:
                    # Don't delete index.html or trading/ or app.py or requirements.txt or Procfile or runtime.txt
                    keep = ["index.html", "trading/", "app.py", "requirements.txt", "Procfile", "runtime.txt", ".git"]
                    if not any(k in item['path'] for k in keep):
                        delete_file(item['path'], item['sha'])
    except Exception as e:
        print(f"Error listing {path}: {e}")

# Delete backend/ folder
list_and_delete_recursive("backend")
# Delete render.yaml
try:
    url = "https://api.github.com/repos/m0904103/m0904103.github.io/contents/render.yaml"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        delete_file("render.yaml", data['sha'])
except: pass

print("Deep Cleanup Complete")
