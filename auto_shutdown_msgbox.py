import time
import datetime
import subprocess
import sys
from pynput import mouse, keyboard
import threading
import ctypes
from ctypes import wintypes

class ActivityMonitor:
    def __init__(self, inactivity_timeout=300):  # 5 minutes = 300 seconds
        self.inactivity_timeout = inactivity_timeout
        self.last_activity = time.time()
        self.running = True
        self.activity_lock = threading.Lock()
        self.warning_active = False
        self.warning_thread = None
        
        # Set up listeners
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity, on_release=self.on_activity)
        self.mouse_listener = mouse.Listener(
            on_move=self.on_activity,
            on_click=self.on_activity,
            on_scroll=self.on_activity
        )
    
    def on_activity(self, *args):
        """Update last activity timestamp on any keyboard/mouse event"""
        with self.activity_lock:
            self.last_activity = time.time()
            # If warning is active, cancel it
            if self.warning_active:
                self.warning_active = False
    
    def show_warning_countdown(self):
        """Show Windows message box with countdown in separate thread"""
        self.warning_active = True
        countdown = 30
        
        # Create a custom message box thread
        def countdown_thread():
            while countdown > 0 and self.warning_active:
                # Use Windows MessageBox API
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32
                
                # MB_SYSTEMMODAL = 0x1000 (always on top)
                # MB_ICONWARNING = 0x30
                # MB_OKCANCEL = 0x1
                MB_SYSTEMMODAL = 0x1000
                MB_ICONWARNING = 0x30
                MB_OK = 0x0
                
                message = f"System will shutdown in {countdown} seconds due to inactivity!\n\nMove mouse or press any key to cancel."
                title = "AutoShutdown Warning"
                
                # Non-blocking message box check
                hwnd = user32.FindWindowW(None, title)
                if hwnd == 0:  # Window doesn't exist, create it
                    # Show message box in a separate thread to make it non-blocking
                    def show_msgbox():
                        result = user32.MessageBoxW(0, message, title, MB_OK | MB_ICONWARNING | MB_SYSTEMMODAL)
                    
                    import threading
                    msgbox_thread = threading.Thread(target=show_msgbox)
                    msgbox_thread.daemon = True
                    msgbox_thread.start()
                
                time.sleep(1)
                countdown -= 1
                
                # Check if user became active
                if not self.warning_active:
                    # Close the message box if it exists
                    hwnd = user32.FindWindowW(None, title)
                    if hwnd != 0:
                        user32.PostMessageW(hwnd, 0x10, 0, 0)  # WM_CLOSE
                    return
            
            # If countdown finished and still no activity, shutdown
            if self.warning_active:
                self.perform_shutdown()
        
        # Start countdown in separate thread
        self.warning_thread = threading.Thread(target=countdown_thread)
        self.warning_thread.daemon = True
        self.warning_thread.start()
    
    def perform_shutdown(self):
        """Actually perform the shutdown"""
        try:
            # Shutdown with no additional warning since we already warned
            subprocess.run(['shutdown', '/s', '/t', '0', '/f'], shell=True)
            print("\nShutdown initiated.")
            self.stop()
        except Exception as e:
            print(f"\nError initiating shutdown: {e}")
    
    def check_inactivity(self):
        """Check if system has been inactive for the timeout period"""
        while self.running:
            with self.activity_lock:
                inactive_time = time.time() - self.last_activity
            
            if inactive_time >= self.inactivity_timeout and not self.warning_active:
                print(f"\nNo activity detected for {self.inactivity_timeout} seconds. Showing warning...")
                self.show_warning_countdown()
            
            remaining_time = self.inactivity_timeout - inactive_time
            if remaining_time > 0 and not self.warning_active:
                print(f"\rTime until warning: {int(remaining_time)} seconds", end='', flush=True)
            
            time.sleep(1)
    
    def start(self):
        """Start monitoring activity"""
        print(f"Activity monitor started. Warning will appear after {self.inactivity_timeout} seconds of inactivity.")
        print("Press Ctrl+C to stop monitoring.\n")
        
        # Start listeners
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        # Start inactivity checker in main thread
        try:
            self.check_inactivity()
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")
            self.stop()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.warning_active = False
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

if __name__ == "__main__":
    # Create monitor with 5 minute timeout
    monitor = ActivityMonitor(inactivity_timeout=300)
    monitor.start()