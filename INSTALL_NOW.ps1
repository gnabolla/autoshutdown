# AutoShutdown Quick Installer
$ErrorActionPreference = "Stop"

Write-Host "AutoShutdown Installer" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green

# Create directories
$installDir = "$env:ProgramFiles\AutoShutdown"
Write-Host "Creating installation directory..."
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

# Download the Python script directly as exe alternative
Write-Host "Setting up AutoShutdown..."

# Create a VBScript launcher that runs Python script
$vbsContent = @'
Set objShell = CreateObject("Wscript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Python code embedded
pythonCode = _
"import time" & vbCrLf & _
"import datetime" & vbCrLf & _
"import subprocess" & vbCrLf & _
"import ctypes" & vbCrLf & _
"from ctypes import wintypes" & vbCrLf & _
"" & vbCrLf & _
"user32 = ctypes.windll.user32" & vbCrLf & _
"kernel32 = ctypes.windll.kernel32" & vbCrLf & _
"" & vbCrLf & _
"class LASTINPUTINFO(ctypes.Structure):" & vbCrLf & _
"    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]" & vbCrLf & _
"" & vbCrLf & _
"def get_idle_time():" & vbCrLf & _
"    lii = LASTINPUTINFO()" & vbCrLf & _
"    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)" & vbCrLf & _
"    user32.GetLastInputInfo(ctypes.byref(lii))" & vbCrLf & _
"    millis = kernel32.GetTickCount() - lii.dwTime" & vbCrLf & _
"    return millis / 1000.0" & vbCrLf & _
"" & vbCrLf & _
"while True:" & vbCrLf & _
"    idle = get_idle_time()" & vbCrLf & _
"    if idle >= 300:" & vbCrLf & _
"        subprocess.run(['shutdown', '/s', '/t', '30', '/c', 'Shutting down due to inactivity'], shell=True)" & vbCrLf & _
"        break" & vbCrLf & _
"    time.sleep(10)"

' Write Python script
Set tempFile = objFSO.CreateTextFile(objFSO.GetSpecialFolder(2) & "\autoshutdown_temp.py", True)
tempFile.Write pythonCode
tempFile.Close

' Run Python script hidden
objShell.Run "python " & objFSO.GetSpecialFolder(2) & "\autoshutdown_temp.py", 0, False
'@

# Create simple batch launcher that uses Windows idle detection
$batchContent = @'
@echo off
powershell.exe -WindowStyle Hidden -Command "while($true){$idle=[Math]::Floor((Get-CimInstance Win32_OperatingSystem).LastBootUpTime.AddMilliseconds([Environment]::TickCount-(Get-Process -Id $PID).StartTime.Subtract((Get-Date)).TotalMilliseconds).Subtract((Get-Date)).TotalSeconds);if($idle -ge 300){shutdown /s /t 30 /c 'Shutting down due to inactivity';break}Start-Sleep -Seconds 10}"
'@

# Even simpler - use PowerShell directly
$psScriptContent = @'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class IdleTime {
    [DllImport("user32.dll")]
    static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
    
    [StructLayout(LayoutKind.Sequential)]
    struct LASTINPUTINFO {
        public uint cbSize;
        public uint dwTime;
    }
    
    public static uint GetIdleTime() {
        LASTINPUTINFO info = new LASTINPUTINFO();
        info.cbSize = (uint)Marshal.SizeOf(info);
        GetLastInputInfo(ref info);
        return ((uint)Environment.TickCount - info.dwTime) / 1000;
    }
}
"@

# Create warning form
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$warningShown = $false

while ($true) {
    $idle = [IdleTime]::GetIdleTime()
    if ($idle -ge 300 -and -not $warningShown) {
        $warningShown = $true
        
        # Create and show warning form
        $form = New-Object System.Windows.Forms.Form
        $form.Text = "Inactivity Warning"
        $form.Size = New-Object System.Drawing.Size(400,200)
        $form.StartPosition = "CenterScreen"
        $form.TopMost = $true
        $form.FormBorderStyle = "FixedDialog"
        $form.MaximizeBox = $false
        $form.MinimizeBox = $false
        
        $label = New-Object System.Windows.Forms.Label
        $label.Location = New-Object System.Drawing.Point(50,30)
        $label.Size = New-Object System.Drawing.Size(300,20)
        $label.Text = "System will shutdown due to inactivity!"
        $label.Font = New-Object System.Drawing.Font("Arial",12,[System.Drawing.FontStyle]::Bold)
        $label.ForeColor = "Red"
        $form.Controls.Add($label)
        
        $countdownLabel = New-Object System.Windows.Forms.Label
        $countdownLabel.Location = New-Object System.Drawing.Point(100,60)
        $countdownLabel.Size = New-Object System.Drawing.Size(200,20)
        $countdownLabel.Text = "Shutting down in 30 seconds"
        $countdownLabel.Font = New-Object System.Drawing.Font("Arial",10)
        $form.Controls.Add($countdownLabel)
        
        $instructionLabel = New-Object System.Windows.Forms.Label
        $instructionLabel.Location = New-Object System.Drawing.Point(50,90)
        $instructionLabel.Size = New-Object System.Drawing.Size(300,20)
        $instructionLabel.Text = "Move mouse or press any key to continue using"
        $instructionLabel.Font = New-Object System.Drawing.Font("Arial",9)
        $instructionLabel.ForeColor = "Blue"
        $form.Controls.Add($instructionLabel)
        
        $countdown = 30
        $timer = New-Object System.Windows.Forms.Timer
        $timer.Interval = 1000
        $timer.Add_Tick({
            $script:countdown--
            $countdownLabel.Text = "Shutting down in $script:countdown seconds"
            
            # Check if user became active
            if ([IdleTime]::GetIdleTime() -lt 2) {
                $timer.Stop()
                $form.Close()
                $script:warningShown = $false
            }
            elseif ($script:countdown -le 0) {
                $timer.Stop()
                $form.Close()
                shutdown /s /t 0 /f
            }
        })
        
        $timer.Start()
        $form.ShowDialog()
    }
    elseif ($idle -lt 300) {
        $warningShown = $false
    }
    Start-Sleep -Seconds 5
}
'@

# Save the PowerShell script
$psScriptContent | Out-File -FilePath "$installDir\AutoShutdown.ps1" -Encoding UTF8

# Create a launcher batch file
@'
@echo off
cd /d "%~dp0"
start /b powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0AutoShutdown.ps1"
'@ | Out-File -FilePath "$installDir\AutoShutdown.bat" -Encoding ASCII

Write-Host "Creating startup task..."
$action = New-ScheduledTaskAction -Execute "$installDir\AutoShutdown.bat"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -Hidden -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "AutoShutdown" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null

Write-Host "Starting AutoShutdown..."
Start-Process "$installDir\AutoShutdown.bat" -WindowStyle Hidden

Write-Host ""
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "AutoShutdown is now running and will start automatically at login."
Write-Host "Your PC will shutdown after 5 minutes of inactivity."
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")