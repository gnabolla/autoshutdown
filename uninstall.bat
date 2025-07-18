@echo off
title AutoShutdown Uninstaller
color 0C

echo ========================================
echo    AutoShutdown Uninstaller
echo ========================================
echo.
echo This will completely remove AutoShutdown from your system.
echo.
pause

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: Administrator rights required!
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Kill running process
echo Stopping AutoShutdown...
taskkill /F /IM AutoShutdown.exe >nul 2>&1

:: Remove scheduled task
echo Removing startup task...
schtasks /delete /tn "AutoShutdown" /f >nul 2>&1

:: Remove program files
set "INSTALL_DIR=%ProgramFiles%\AutoShutdown"
echo Removing program files...
if exist "%INSTALL_DIR%" rmdir /S /Q "%INSTALL_DIR%"

echo.
echo ========================================
echo    Uninstall Complete!
echo ========================================
echo.
echo AutoShutdown has been removed from your system.
echo.
pause