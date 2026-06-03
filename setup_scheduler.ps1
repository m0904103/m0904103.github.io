# setup_scheduler.ps1
# 以系統管理員身分執行此腳本，自動設定 Windows 工作排程器
# 讓正規軍自動同步系統在開機後自動啟動

$ScriptDir = "C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud"
$PythonPath = (Get-Command python | Select-Object -ExpandProperty Source)
$TaskName = "RegularArmy_AutoSync"

Write-Host "Setting up Regular Army Auto-Sync Task Scheduler..." -ForegroundColor Cyan
Write-Host "Python path: $PythonPath" -ForegroundColor Gray
Write-Host "Script dir: $ScriptDir" -ForegroundColor Gray

$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "auto_sync.py" `
    -WorkingDirectory $ScriptDir

$Trigger = New-ScheduledTaskTrigger -AtLogOn

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 23) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

# Remove existing task if any
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Force

Write-Host "`nTask '$TaskName' registered successfully!" -ForegroundColor Green
Write-Host "The auto-sync daemon will start automatically on next login." -ForegroundColor Green
Write-Host "`nTo start it NOW, run:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
