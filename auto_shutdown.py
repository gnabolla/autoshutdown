import time
import datetime
import subprocess
import sys
from pynput import mouse, keyboard
import threading
import tkinter as tk
from tkinter import messagebox
import queue

class ActivityMonitor:
    def __init__(self, inactivity_timeout=300):  # 5 minutes = 300 seconds
        self.inactivity_timeout = inactivity_timeout
        self.last_activity = time.time()
        self.running = True
        self.activity_lock = threading.Lock()
        self.warning_active = False
        self.warning_window = None
        self.countdown_value = 30
        self.activity_queue = queue.Queue()
        
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
            # If warning is active, signal to close it
            if self.warning_active:
                self.activity_queue.put("activity_detected")
    
    def show_warning_dialog(self):
        """Show warning dialog with countdown"""
        self.warning_active = True
        self.countdown_value = 30
        
        # Create warning window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create custom dialog window
        self.warning_window = tk.Toplevel(root)
        self.warning_window.title("Inactivity Warning")
        self.warning_window.geometry("400x200")
        self.warning_window.resizable(False, False)
        
        # Center the window
        self.warning_window.update_idletasks()
        width = self.warning_window.winfo_width()
        height = self.warning_window.winfo_height()
        x = (self.warning_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.warning_window.winfo_screenheight() // 2) - (height // 2)
        self.warning_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make it always on top
        self.warning_window.attributes("-topmost", True)
        self.warning_window.lift()
        
        # Prevent closing with X button
        self.warning_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Warning message
        message_label = tk.Label(
            self.warning_window,
            text="System will shutdown due to inactivity!",
            font=("Arial", 14, "bold"),
            fg="red"
        )
        message_label.pack(pady=20)
        
        # Countdown label
        countdown_label = tk.Label(
            self.warning_window,
            text=f"Shutting down in {self.countdown_value} seconds",
            font=("Arial", 12)
        )
        countdown_label.pack(pady=10)
        
        # Instruction label
        instruction_label = tk.Label(
            self.warning_window,
            text="Move mouse or press any key to continue using",
            font=("Arial", 10),
            fg="blue"
        )
        instruction_label.pack(pady=10)
        
        def update_countdown():
            try:
                # Check for activity
                try:
                    self.activity_queue.get_nowait()
                    # Activity detected, close dialog
                    self.warning_active = False
                    self.warning_window.destroy()
                    root.quit()
                    return
                except queue.Empty:
                    pass
                
                if self.countdown_value > 0 and self.warning_active:
                    countdown_label.config(text=f"Shutting down in {self.countdown_value} seconds")
                    self.countdown_value -= 1
                    self.warning_window.after(1000, update_countdown)
                elif self.warning_active:
                    # Time's up, proceed with shutdown
                    self.warning_active = False
                    self.warning_window.destroy()
                    root.quit()
                    self.perform_shutdown()
            except:
                # Window was destroyed
                pass
        
        # Start countdown
        update_countdown()
        
        # Run the dialog
        root.mainloop()
    
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
                self.show_warning_dialog()
                # Reset the timer after dialog closes (either by activity or shutdown)
                with self.activity_lock:
                    self.last_activity = time.time()
            
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