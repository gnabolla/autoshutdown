@echo off
cd /d "%~dp0"
echo Building AutoShutdown...
pip install pynput pyinstaller
python -c "import PyInstaller.__main__; PyInstaller.__main__.run(['auto_shutdown.py', '--onefile', '--noconsole', '--name=AutoShutdown', '--hidden-import=pynput.keyboard._win32', '--hidden-import=pynput.mouse._win32', '--clean'])"
if exist "dist\AutoShutdown.exe" (
    call install.bat
) else (
    echo Build failed!
    pause
)