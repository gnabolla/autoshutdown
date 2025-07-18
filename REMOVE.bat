@echo off
echo Removing AutoShutdown...
taskkill /F /IM AutoShutdown.exe 2>nul
taskkill /F /IM powershell.exe /FI "WINDOWTITLE eq AutoShutdown*" 2>nul
schtasks /delete /tn "AutoShutdown" /f 2>nul
rmdir /S /Q "%ProgramFiles%\AutoShutdown" 2>nul
echo Done!