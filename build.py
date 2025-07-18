import PyInstaller.__main__
import os

# Build the executable
PyInstaller.__main__.run([
    'auto_shutdown.py',
    '--onefile',           # Single executable file
    '--noconsole',         # No console window
    '--name=AutoShutdown', # Executable name
    '--icon=NONE',         # No icon for now
    '--add-data=requirements.txt;.',  # Include requirements file
    '--hidden-import=pynput.keyboard._win32',
    '--hidden-import=pynput.mouse._win32',
    '--uac-admin',         # Request admin rights
    '--clean',             # Clean PyInstaller cache
])

print("\nBuild complete! Check the 'dist' folder for AutoShutdown.exe")