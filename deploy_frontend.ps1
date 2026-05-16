$repo = "m0904103/m0904103.github.io"
# Use relative path to avoid encoding issues with "桌面"
$baseDir = ".\trading"

if (-not (Test-Path $baseDir)) {
    Write-Error "Could not find trading directory at $baseDir"
    exit
}

$files = Get-ChildItem -Path $baseDir -Recurse | Where-Object { !$_.PSIsContainer }

foreach ($file in $files) {
    # Calculate relative path manually to be safe
    $fullPath = $file.FullName
    $relPath = $fullPath.Substring($fullPath.IndexOf("\trading\") + 9).Replace("\", "/")
    $repoPath = "trading/$relPath"
    
    Write-Host "Deploying $repoPath..."
    
    # Read file content as Base64
    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
    $base64Content = [Convert]::ToBase64String($bytes)
    
    # Get SHA if file exists
    $sha = ""
    $jsonRaw = gh api "repos/$repo/contents/$repoPath" --method GET 2>$null
    if ($jsonRaw) {
        $json = $jsonRaw | ConvertFrom-Json
        $sha = $json.sha
    }
    
    if ($sha) {
        gh api "repos/$repo/contents/$repoPath" --method PUT -f message="Update frontend: $repoPath" -f content="$base64Content" -f sha="$sha" -f branch="main" | Out-Null
    } else {
        gh api "repos/$repo/contents/$repoPath" --method PUT -f message="Add frontend: $repoPath" -f content="$base64Content" -f branch="main" | Out-Null
    }
    
    Write-Host "✅ Uploaded $repoPath"
}
