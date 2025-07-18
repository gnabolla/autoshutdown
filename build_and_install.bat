@echo off
title AutoShutdown Build and Install
color 0A

echo ========================================
echo    AutoShutdown Build and Install
echo ========================================
echo.
echo This will build AutoShutdown from source and install it.
echo.

:: Check for Python
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorLevel% NEQ 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

:: Build executable
echo.
echo Building AutoShutdown.exe...
python build.py
if %errorLevel% NEQ 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

:: Check if exe was created
if not exist "dist\AutoShutdown.exe" (
    echo ERROR: AutoShutdown.exe was not created!
    pause
    exit /b 1
)

echo.
echo Build successful! Now installing...
echo.

:: Run installer
call install.bat