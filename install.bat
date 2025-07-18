@echo off
title AutoShutdown Installer
color 0A

echo ========================================
echo    AutoShutdown Installer v1.0
echo ========================================
echo.
echo This will install AutoShutdown to run automatically when Windows starts.
echo The program will shutdown your PC after 5 minutes of inactivity.
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

:: Check if executable exists
if not exist "dist\AutoShutdown.exe" (
    echo ERROR: AutoShutdown.exe not found!
    echo.
    echo Please build the project first:
    echo 1. Run: pip install -r requirements.txt
    echo 2. Run: python build.py
    echo.
    echo Or use build_and_install.bat to do everything automatically.
    pause
    exit /b 1
)

:: Create program directory
set "INSTALL_DIR=%ProgramFiles%\AutoShutdown"
echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy executable
echo Installing AutoShutdown...
copy /Y "dist\AutoShutdown.exe" "%INSTALL_DIR%\" >nul
if %errorLevel% NEQ 0 (
    echo ERROR: Failed to copy executable!
    pause
    exit /b 1
)

:: Create startup task
echo Setting up auto-start...
schtasks /create /tn "AutoShutdown" /tr "%INSTALL_DIR%\AutoShutdown.exe" /sc onlogon /rl highest /f >nul
if %errorLevel% NEQ 0 (
    echo ERROR: Failed to create startup task!
    pause
    exit /b 1
)

:: Start the program now
echo Starting AutoShutdown...
start "" "%INSTALL_DIR%\AutoShutdown.exe"

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo AutoShutdown has been installed and will run automatically at startup.
echo To uninstall, run uninstall.bat
echo.
pause