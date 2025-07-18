@echo off
echo ========================================
echo    AutoShutdown Installer (No Python)
echo ========================================
echo.
echo This installer uses PowerShell (built into Windows).
echo.
pause

powershell -ExecutionPolicy Bypass -File "%~dp0INSTALL_NOW.ps1"