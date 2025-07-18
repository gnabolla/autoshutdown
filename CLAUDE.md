# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoShutdown is a Windows background application that monitors keyboard/mouse activity and forces computer shutdown after 5 minutes of inactivity. It runs as a background process with no UI and auto-starts with Windows.

**CRITICAL**: The application now uses Windows native shutdown dialog (`shutdown /s /t 30 /c "message"`), providing a 30-second warning that users can cancel.

## Build Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
python build.py

# Quick build and install (requires admin)
build_and_install.bat
```

## Core Architecture

The application consists of a single Python file (`auto_shutdown.py`) with one main class:

- **ActivityMonitor**: Handles all functionality including:
  - Thread-safe activity tracking using `threading.Lock()`
  - Concurrent keyboard/mouse listeners via `pynput`
  - Main loop checking inactivity every second
  - Windows shutdown execution via `subprocess`

## Installation Methods

1. **Python Required**: `build_and_install.bat` - Builds from source then installs
2. **No Python Required**: `INSTALL_WINDOWS.bat` - Uses PowerShell implementation in `INSTALL_NOW.ps1`

Installation creates:
- Program directory: `%ProgramFiles%\AutoShutdown`
- Task Scheduler entry: "AutoShutdown" (runs at login with highest privileges)

## Key Implementation Details

- **Inactivity timeout**: Hardcoded to 300 seconds (5 minutes)
- **Shutdown command**: `shutdown /s /t 30 /c "message"` (30-second warning with cancel option)
- **PyInstaller flags**: `--onefile --noconsole --uac-admin`
- **Hidden imports**: `pynput.keyboard._win32`, `pynput.mouse._win32`

## Testing and Development

```bash
# Run directly (for testing)
python auto_shutdown.py

# Remove installation
uninstall.bat  # or REMOVE.bat
```

## Important Notes

- Requires Windows administrator privileges
- No configuration options - all values hardcoded
- No activity logging or error handling beyond console output
- Multiple redundant installation scripts exist (install.bat, INSTALL_WINDOWS.bat, run_installer.bat)