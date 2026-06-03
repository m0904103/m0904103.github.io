# setup_scheduler_user.ps1
# 不需要系統管理員，在目前使用者身分下設定工作排程器

$ScriptDir = "C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud"
$PythonPath = (Get-Command python | Select-Object -ExpandProperty Source 2>$null)
if (-not $PythonPath) {
    $PythonPath = "python"
}
$TaskName = "RegularArmy_AutoSync"

Write-Host "Setting up Regular Army Auto-Sync (User mode)..." -ForegroundColor Cyan

$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "auto_sync.py" `
    -WorkingDirectory $ScriptDir

# Trigger: At logon of current user
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 23) `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Force

if ($?) {
    Write-Host "Task '$TaskName' registered OK!" -ForegroundColor Green
    Write-Host "Starting it now..." -ForegroundColor Yellow
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 2
    $status = (Get-ScheduledTask -TaskName $TaskName).State
    Write-Host "Task state: $status" -ForegroundColor Cyan
} else {
    Write-Host "Registration failed. Will run as background job instead." -ForegroundColor Red
}
