@echo off
echo Building AutoShutdown with Windows native dialog...
pip install pynput pyinstaller
pyinstaller --onefile --noconsole --name=AutoShutdown --hidden-import=pynput.keyboard._win32 --hidden-import=pynput.mouse._win32 --uac-admin auto_shutdown_simple.py
echo Build complete! Check dist folder.