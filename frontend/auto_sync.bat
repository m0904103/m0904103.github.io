@echo off
title Regular Army Auto-Sync Engine
mode con: cols=60 lines=15
color 0C

:loop
cls
echo ======================================================
echo    REGULAR ARMY QUANT TERMINAL - AUTO SYNC ENGINE
echo ======================================================
echo [%DATE% %TIME%] Starting Market Sync...

"C:\Users\manpo\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\sync_vix.py"

echo.
echo ======================================================
echo Next sync in 5 minutes... (Press Ctrl+C to stop)
echo ======================================================

timeout /t 300 /nobreak
goto loop
