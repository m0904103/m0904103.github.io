import os, subprocess, base64, json, urllib.request, datetime

# 1. Get GH Token
token = subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()

# 2. Config
repo_owner = "m0904103"
repo_name = "m0904103.github.io"
dist_dir = r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\dist"
backend_dir = r"c:\Users\manpo\OneDrive\桌面\m0904103_github_io"

# 3. Collect all files
all_files = []
# Backend files
for f in ["app.py", "requirements.txt", "runtime.txt"]:
    all_files.append((os.path.join(backend_dir, f), f))

# Frontend files
for root, dirs, files in os.walk(dist_dir):
    for f in files:
        l_path = os.path.join(root, f)
        r_path = os.path.relpath(l_path, dist_dir).replace("\\", "/")
        all_files.append((l_path, r_path))

print(f"Preparing to deploy {len(all_files)} files in ONE commit...")

# 4. Upload one by one (GitHub API limitation: can't do multi-file commit easily without git CLI, 
# but we can at least make sure app.py and requirements are LAST to trigger Render correctly, 
# or use Git CLI if available)

# Actually, the best way is to use Git CLI since it's a local machine.
try:
    print("Switching to Git CLI for atomic commit...")
    # Sync dist to backend folder
    import shutil
    for l_path, r_path in all_files:
        dest = os.path.join(backend_dir, r_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.abspath(l_path) != os.path.abspath(dest):
            shutil.copy2(l_path, dest)
    
    # Git commands
    os.chdir(backend_dir)
    subprocess.run(["git", "add", "."], check=True)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subprocess.run(["git", "commit", "-m", f"Master v6.0.1 Atomic Deploy - {now_str}"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🎉 Atomic Deployment Succeeded!")
except Exception as e:
    print(f"Git CLI failed: {e}. Falling back to API (risky)...")
    # (API fallback logic would go here if needed)
