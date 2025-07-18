# Quick Start Guide

## Option 1: Build and Install from Source (Recommended)

If you have the source code:

1. **Right-click** `build_and_install.bat`
2. Select **"Run as administrator"**
3. Wait for it to build and install automatically
4. Done! AutoShutdown is now running

## Option 2: Manual Build

If you have Python installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Build the executable
python build.py

# Install (run as admin)
install.bat
```

## Option 3: Pre-built Release

1. Download the latest release ZIP from GitHub
2. Extract all files
3. Right-click `install.bat` and run as administrator

## What Happens Next?

- AutoShutdown runs in the background (no window)
- It starts automatically when Windows boots
- Your PC will shutdown after 5 minutes of no keyboard/mouse activity
- You get a 30-second warning before shutdown

## To Stop Shutdown

If you see the shutdown warning:
1. Press `Win + R`
2. Type: `shutdown /a`
3. Press Enter

## To Uninstall

Right-click `uninstall.bat` and run as administrator