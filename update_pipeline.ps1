$ErrorActionPreference = "Stop"

Write-Host "Starting automated hourly update..."
git pull --rebase origin main

Write-Host "Syncing market data..."
python sync_regular_army_2026.py

Write-Host "Running US screen..."
python us_screen.py > us_result.txt

Write-Host "Building frontend..."
cd frontend
npm run build
cd ..

Write-Host "Copying dist to trading folder..."
Copy-Item -Path "frontend\dist\*" -Destination "trading\" -Recurse -Force

Write-Host "Committing and pushing to GitHub..."
git add .
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "Automated hourly update: $timestamp"
git push origin main

Write-Host "Hourly update completed successfully!"
