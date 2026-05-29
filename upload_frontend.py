import os
import shutil
import subprocess

# Use relative paths so it works both locally and on GitHub Actions (Linux)
repo_root = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(repo_root, "frontend", "dist")
trading_dir = os.path.join(repo_root, "trading")

def deploy():
    print("🚀 Starting deployment process...")
    
    # 1. Ensure dist directory exists
    if not os.path.exists(dist_dir):
        print(f"❌ Error: {dist_dir} does not exist. Please run 'npm run build' first.")
        return

    # 2. Clear out old files in trading directory
    print("🧹 Cleaning old files in trading directory...")
    if not os.path.exists(trading_dir):
        os.makedirs(trading_dir)
    else:
        for item in os.listdir(trading_dir):
            item_path = os.path.join(trading_dir, item)
            # Skip hidden files like .gitkeep if any exist
            if item.startswith('.'): continue
            
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    # 3. Copy dist files to trading directory
    print("📂 Copying new files to trading directory...")
    for item in os.listdir(dist_dir):
        s = os.path.join(dist_dir, item)
        d = os.path.join(trading_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    # 4. Git add, commit, push
    print("📦 Committing and pushing to GitHub...")
    try:
        os.chdir(repo_root)
        
        # Configure git identity if missing (useful for GitHub Actions)
        subprocess.run(["git", "config", "user.name", "AI Bot"], check=False)
        subprocess.run(["git", "config", "user.email", "bot@ai.com"], check=False)
        
        # Also ensure scan_results.json is copied over so frontend has latest data
        scan_src = os.path.join(repo_root, "frontend", "public", "scan_results.json")
        scan_dest = os.path.join(trading_dir, "scan_results.json")
        if os.path.exists(scan_src):
            shutil.copy2(scan_src, scan_dest)

        subprocess.run(["git", "add", "trading/"], check=True)
        # Commit might fail if there are no changes, so we don't check=True for commit
        commit_res = subprocess.run(["git", "commit", "-m", "Auto-deploy frontend to trading/"])
        if commit_res.returncode == 0:
            subprocess.run(["git", "push"], check=True)
            print("✅ Frontend successfully deployed to GitHub Pages via Git Push!")
        else:
            print("⚡ No changes to deploy. Everything is up to date!")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")

if __name__ == "__main__":
    deploy()
