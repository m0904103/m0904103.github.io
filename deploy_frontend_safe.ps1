$repo = "m0904103/m0904103.github.io"
$baseDir = "C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\trading"

if (-not (Test-Path $baseDir)) {
    Write-Host "Searching for trading folder..."
    $baseDir = ".\trading"
}

$files = Get-ChildItem -Path $baseDir -Recurse | Where-Object { !$_.PSIsContainer }

foreach ($file in $files) {
    $fullPath = $file.FullName
    $relPath = $fullPath.Substring($fullPath.IndexOf("\trading\") + 9).Replace("\", "/")
    $repoPath = "trading/$relPath"
    
    Write-Host "Processing $repoPath..."
    
    # 1. Read and Encode
    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
    $base64 = [Convert]::ToBase64String($bytes)
    
    # 2. Get existing SHA
    $sha = ""
    $info = gh api "repos/$repo/contents/$repoPath" --method GET 2>$null | ConvertFrom-Json
    if ($info) { $sha = $info.sha }
    
    # 3. Create temp JSON to bypass command line limits
    $payload = @{
        message = "Deploy $repoPath"
        content = $base64
        branch = "main"
    }
    if ($sha) { $payload.sha = $sha }
    
    $tempFile = [System.IO.Path]::GetTempFileName()
    $payload | ConvertTo-Json -Compress | Out-File -FilePath $tempFile -Encoding utf8
    
    # 4. Use --input to upload
    try {
        gh api "repos/$repo/contents/$repoPath" --method PUT --input $tempFile | Out-Null
        Write-Host "✅ Uploaded $repoPath"
    } catch {
        Write-Host "❌ Failed $repoPath"
    } finally {
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}
