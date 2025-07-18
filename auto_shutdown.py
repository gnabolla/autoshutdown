import time
import subprocess
import sys
from pynput import mouse, keyboard
import threading
import ctypes

class ActivityMonitor:
    def __init__(self, inactivity_timeout=300):  # 5 minutes = 300 seconds
        self.inactivity_timeout = inactivity_timeout
        self.last_activity = time.time()
        self.running = True
        self.activity_lock = threading.Lock()
        
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
    
    def check_inactivity(self):
        """Check if system has been inactive for the timeout period"""
        while self.running:
            with self.activity_lock:
                inactive_time = time.time() - self.last_activity
            
            if inactive_time >= self.inactivity_timeout:
                print(f"\nNo activity detected for {self.inactivity_timeout} seconds.")
                
                # Use Windows shutdown with built-in warning
                # /t 30 gives 30 second warning with popup
                # /c provides the message
                subprocess.run([
                    'shutdown', '/s', '/t', '30', 
                    '/c', 'System will shutdown in 30 seconds due to inactivity. Close this dialog to cancel.'
                ], shell=True)
                
                print("Shutdown warning issued. User can cancel with: shutdown /a")
                
                # Reset timer and wait to see if user cancels
                with self.activity_lock:
                    self.last_activity = time.time()
                
                # Wait a bit before checking again
                time.sleep(35)
            
            remaining_time = self.inactivity_timeout - inactive_time
            if remaining_time > 0:
                print(f"\rTime until shutdown warning: {int(remaining_time)} seconds", end='', flush=True)
            
            time.sleep(1)
    
    def start(self):
        """Start monitoring activity"""
        print(f"Activity monitor started. Shutdown warning after {self.inactivity_timeout} seconds of inactivity.")
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
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

if __name__ == "__main__":
    # Create monitor with 5 minute timeout
    monitor = ActivityMonitor(inactivity_timeout=300)
    monitor.start()