import time
import datetime
import subprocess
import sys
from pynput import mouse, keyboard
import threading

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
                print(f"No activity detected for {self.inactivity_timeout} seconds. Shutting down...")
                self.shutdown_system()
                break
            
            remaining_time = self.inactivity_timeout - inactive_time
            print(f"\rTime until shutdown: {int(remaining_time)} seconds", end='', flush=True)
            
            time.sleep(1)
    
    def shutdown_system(self):
        """Initiate Windows shutdown"""
        try:
            # Force immediate shutdown - no warning, no countdown
            subprocess.run(['shutdown', '/s', '/t', '0', '/f'], shell=True)
            print("\nForce shutdown initiated.")
            self.stop()
        except Exception as e:
            print(f"\nError initiating shutdown: {e}")
    
    def start(self):
        """Start monitoring activity"""
        print(f"Activity monitor started. System will shutdown after {self.inactivity_timeout} seconds of inactivity.")
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