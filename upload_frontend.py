import os
import shutil
import subprocess

# Use relative paths so it works both locally and on GitHub Actions (Linux)
repo_root = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(repo_root, "frontend", "dist")
trading_dir = os.path.join(repo_root, "trading")
q_quant_dir = os.path.join(repo_root, "q_quant_888")

def deploy_to_target(target_dir):
    print(f"[CLEAN] Cleaning old files in {os.path.basename(target_dir)} directory...")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    else:
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if item.startswith('.'): continue
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    print(f"[COPY] Copying new files to {os.path.basename(target_dir)} directory...")
    for item in os.listdir(dist_dir):
        s = os.path.join(dist_dir, item)
        d = os.path.join(target_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    scan_src = os.path.join(repo_root, "frontend", "public", "scan_results.json")
    scan_dest = os.path.join(target_dir, "scan_results.json")
    if os.path.exists(scan_src):
        shutil.copy2(scan_src, scan_dest)

def deploy():
    print("[START] Starting deployment process...")
    
    if not os.path.exists(dist_dir):
        print(f"[ERROR] {dist_dir} does not exist. Please run 'npm run build' first.")
        return

    deploy_to_target(trading_dir)
    deploy_to_target(q_quant_dir)
    
    # Also deploy to root directory
    print("[COPY] Copying new files to root directory for root domain access...")
    for item in os.listdir(dist_dir):
        s = os.path.join(dist_dir, item)
        d = os.path.join(repo_root, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    scan_src = os.path.join(repo_root, "frontend", "public", "scan_results.json")
    scan_dest = os.path.join(repo_root, "scan_results.json")
    if os.path.exists(scan_src):
        shutil.copy2(scan_src, scan_dest)

    print("[GIT] Committing and pushing to GitHub...")
    try:
        os.chdir(repo_root)
        
        token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY")
        if token and repo:
            subprocess.run(["git", "remote", "set-url", "origin", f"https://x-access-token:{token}@github.com/{repo}.git"], check=False)

        subprocess.run(["git", "config", "user.name", "AI Bot"], check=False)
        subprocess.run(["git", "config", "user.email", "bot@ai.com"], check=False)
        
        subprocess.run(["git", "fetch", "origin", "main"], check=False)
        subprocess.run(["git", "reset", "--mixed", "origin/main"], check=False)
        subprocess.run(["git", "add", "-A"], check=True)
        commit_res = subprocess.run(["git", "commit", "-m", "Auto-deploy frontend to root, trading/ and q_quant_888/ with full source sync"])
        if commit_res.returncode == 0:
            push_res = subprocess.run(["git", "push", "origin", "main"], check=False)
            if push_res.returncode != 0:
                print("[RETRY] Re-syncing with remote and retrying push...")
                subprocess.run(["git", "fetch", "origin", "main"], check=False)
                subprocess.run(["git", "push", "origin", "main"], check=True)
            print("[OK] Frontend successfully deployed to GitHub Pages via Git Push!")
        else:
            print("[SKIP] No changes to deploy. Everything is up to date!")
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")

if __name__ == "__main__":
    deploy()
