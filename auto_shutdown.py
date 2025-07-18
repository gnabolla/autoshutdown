import time
import subprocess
import sys
from pynput import mouse, keyboard
import threading
from collections import deque

class ActivityMonitor:
    def __init__(self, inactivity_timeout=300):  # 5 minutes = 300 seconds
        self.inactivity_timeout = inactivity_timeout
        self.last_activity = time.time()
        self.running = True
        self.activity_lock = threading.Lock()
        
        # Track stuck keys
        self.pressed_keys = {}  # key: timestamp when first pressed
        self.stuck_key_timeout = 60  # Consider key stuck after 60 seconds
        
        # Track mouse clicks for autoclicker detection
        self.click_history = deque(maxlen=10)  # Store last 10 click timestamps
        self.click_intervals = deque(maxlen=9)   # Store intervals between clicks
        self.autoclicker_detected = False
        self.last_real_activity = time.time()
        
        # Set up listeners
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press, 
            on_release=self.on_key_release
        )
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_activity
        )
    
    def detect_autoclicker(self):
        """Detect if clicks are from an autoclicker based on timing patterns"""
        if len(self.click_intervals) < 5:
            return False
        
        # Calculate standard deviation of click intervals
        avg_interval = sum(self.click_intervals) / len(self.click_intervals)
        variance = sum((x - avg_interval) ** 2 for x in self.click_intervals) / len(self.click_intervals)
        std_dev = variance ** 0.5
        
        # Autoclickers have very consistent intervals (low standard deviation)
        # Human clicks are more random
        if std_dev < 0.05 and avg_interval < 2.0:  # Very consistent clicks, less than 2 seconds apart
            return True
        
        # Check if all intervals are nearly identical (another autoclicker sign)
        if len(set(round(interval, 2) for interval in self.click_intervals)) == 1:
            return True
        
        return False
    
    def on_key_press(self, key):
        """Track when keys are pressed"""
        with self.activity_lock:
            key_str = str(key)
            current_time = time.time()
            
            # If this is a new key press, record it
            if key_str not in self.pressed_keys:
                self.pressed_keys[key_str] = current_time
                self.last_activity = current_time  # Reset activity timer
                self.last_real_activity = current_time
            else:
                # Key is already pressed, check if it's stuck
                press_duration = current_time - self.pressed_keys[key_str]
                if press_duration < self.stuck_key_timeout:
                    # Not stuck yet, still counts as activity
                    self.last_activity = current_time
                    self.last_real_activity = current_time
                # If stuck (>60 seconds), don't update activity
    
    def on_key_release(self, key):
        """Remove key from pressed keys when released"""
        with self.activity_lock:
            key_str = str(key)
            if key_str in self.pressed_keys:
                del self.pressed_keys[key_str]
                self.last_activity = time.time()
                self.last_real_activity = time.time()
    
    def on_mouse_click(self, x, y, button, pressed):
        """Track mouse clicks and detect autoclickers"""
        if pressed:  # Only track press events, not releases
            with self.activity_lock:
                current_time = time.time()
                
                # Add click to history
                if self.click_history:
                    interval = current_time - self.click_history[-1]
                    self.click_intervals.append(interval)
                self.click_history.append(current_time)
                
                # Check for autoclicker
                if self.detect_autoclicker():
                    if not self.autoclicker_detected:
                        print("\nAutoclicker detected! Ignoring automated clicks.")
                        self.autoclicker_detected = True
                else:
                    # Real click
                    self.last_activity = current_time
                    self.last_real_activity = current_time
                    self.autoclicker_detected = False
    
    def on_mouse_move(self, x, y):
        """Track mouse movement"""
        with self.activity_lock:
            # Mouse movement is usually real activity (autoclickers don't move mouse)
            self.last_activity = time.time()
            self.last_real_activity = time.time()
    
    def on_mouse_activity(self, *args):
        """Update last activity timestamp on scroll events"""
        with self.activity_lock:
            self.last_activity = time.time()
            self.last_real_activity = time.time()
    
    def check_inactivity(self):
        """Check if system has been inactive for the timeout period"""
        while self.running:
            with self.activity_lock:
                # Use real activity time if autoclicker is detected
                if self.autoclicker_detected:
                    inactive_time = time.time() - self.last_real_activity
                else:
                    inactive_time = time.time() - self.last_activity
                
                # Clean up old stuck keys
                current_time = time.time()
                stuck_keys = []
                for key, press_time in self.pressed_keys.items():
                    if current_time - press_time > self.stuck_key_timeout:
                        stuck_keys.append(key)
                
                if stuck_keys:
                    print(f"\nIgnoring stuck keys: {', '.join(stuck_keys)}")
            
            if inactive_time >= self.inactivity_timeout:
                print(f"\nNo real activity detected for {self.inactivity_timeout} seconds.")
                
                # Use Windows shutdown with built-in warning
                subprocess.run([
                    'shutdown', '/s', '/t', '30', 
                    '/c', 'System will shutdown in 30 seconds due to inactivity. Close this dialog to cancel.'
                ], shell=True)
                
                print("Shutdown warning issued. User can cancel with: shutdown /a")
                
                # Reset timer and wait to see if user cancels
                with self.activity_lock:
                    self.last_activity = time.time()
                    self.last_real_activity = time.time()
                
                # Wait a bit before checking again
                time.sleep(35)
            
            remaining_time = self.inactivity_timeout - inactive_time
            if remaining_time > 0:
                status = " (autoclicker detected)" if self.autoclicker_detected else ""
                print(f"\rTime until shutdown warning: {int(remaining_time)} seconds{status}", end='', flush=True)
            
            time.sleep(1)
    
    def start(self):
        """Start monitoring activity"""
        print(f"Activity monitor started. Shutdown warning after {self.inactivity_timeout} seconds of inactivity.")
        print(f"Keys pressed for more than {self.stuck_key_timeout} seconds will be ignored (stuck key detection).")
        print("Autoclicker detection enabled - automated clicks will be ignored.")
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