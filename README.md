# AutoShutdown

A Windows background application that automatically shuts down your computer after 5 minutes of keyboard/mouse inactivity.

## Features

- Monitors keyboard and mouse activity
- 5-minute inactivity timer
- 30-second shutdown warning
- Runs in background (no console window)
- Auto-starts with Windows

## Easy Installation (No Python Required)

### For Users - Download and Install

1. Download the latest release from [Releases](https://github.com/gnabolla/autoshutdown/releases)
2. Extract the ZIP file
3. Right-click `install.bat` and select **Run as administrator**
4. That's it! AutoShutdown is now running and will start automatically with Windows

### Uninstall

1. Right-click `uninstall.bat` and select **Run as administrator**
2. The program will be completely removed

## For Developers

### Build from Source

```bash
# Clone the repository
git clone https://github.com/gnabolla/autoshutdown.git
cd autoshutdown

# Install dependencies
pip install -r requirements.txt

# Build executable
python build.py

# The executable will be in the dist/ folder
```

### Run from Source

```bash
python auto_shutdown.py
```

## How It Works

1. The program runs silently in the background
2. It monitors all keyboard and mouse activity
3. After 5 minutes of no activity, it initiates Windows shutdown
4. You get a 30-second warning to save your work
5. To cancel shutdown, open Command Prompt and type: `shutdown /a`

## System Requirements

- Windows 7 or later
- Administrator privileges (for shutdown command)

## Safety

- The program gives a 30-second warning before shutdown
- You can cancel the shutdown at any time with `shutdown /a`
- Uninstall anytime using the uninstall.bat script