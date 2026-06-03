@echo off
REM 正規軍自動同步服務 - 開機自動啟動版本
REM 此批次檔案會在背景持續運行 auto_sync.py

cd /d "C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud"

echo [%DATE% %TIME%] Regular Army Auto-Sync Starting...
python auto_sync.py >> sync_log.txt 2>&1
