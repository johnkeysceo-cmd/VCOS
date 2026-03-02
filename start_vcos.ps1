# VCOS PowerShell Startup Script
# Boots ScreenArc and watches for videos to process

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting VCOS Boot System..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Change to vcos directory
Set-Location vcos

# Run boot script
python scripts\boot_vcos.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error starting VCOS. Check the error messages above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
