@echo off
REM VCOS Windows Startup Script
REM Boots ScreenArc and watches for videos to process
echo ========================================
echo Starting VCOS Boot System...
echo ========================================
cd /d %~dp0
cd vcos
python scripts\boot_vcos.py
if errorlevel 1 (
    echo.
    echo Error starting VCOS. Check the error messages above.
    pause
)
