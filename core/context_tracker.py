# context_tracker.py - Omnipresent Context Awareness (Active Window Tracker)
"""
JARVIS Background Window Tracker
Lightweight background thread that checks what app you are using every 3 seconds
and updates JARVIS's short-term memory buffer.
"""

import threading
import time
from collections import deque
from typing import Optional

# Try to import pygetwindow - handle if not available
try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    gw = None
    PYGETWINDOW_AVAILABLE = False


class WindowTracker(threading.Thread):
    """
    Background thread that tracks the active window title.
    Runs as a daemon thread, checking every few seconds.
    """
    
    def __init__(self, check_interval: int = 3):
        """
        Initialize the window tracker.
        
        Args:
            check_interval: Seconds between window checks (default: 3)
        """
        super().__init__(daemon=True)
        self.check_interval = check_interval
        self.is_running = False
        
        # Keep the last 5 distinct window titles in a rolling buffer
        self.recent_windows: deque = deque(maxlen=5)
        self.current_window: Optional[str] = None
        
        # Lock for thread-safe access
        self._lock = threading.Lock()
    
    def run(self):
        """Main tracking loop - runs in background thread."""
        self.is_running = True
        
        while self.is_running:
            try:
                if PYGETWINDOW_AVAILABLE:
                    active_win = gw.getActiveWindow()
                    if active_win and active_win.title:
                        title = active_win.title.strip()
                        
                        # Only update if the window actually changed
                        if title != self.current_window and title != "":
                            with self._lock:
                                self.current_window = title
                                # Add to recent windows if not already there
                                if title not in self.recent_windows:
                                    self.recent_windows.appendleft(title)
                else:
                    # Fallback: try getting window info via ctypes on Windows
                    self._get_window_fallback()
            except Exception:
                pass  # Ignore OS-level permission errors for secure windows
            
            time.sleep(self.check_interval)
    
    def _get_window_fallback(self):
        """Fallback window detection using ctypes on Windows."""
        try:
            import ctypes
            from ctypes import wintypes
            
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length:
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.strip()
                
                if title != self.current_window and title != "":
                    with self._lock:
                        self.current_window = title
                        if title not in self.recent_windows:
                            self.recent_windows.appendleft(title)
        except Exception:
            pass
    
    def stop(self):
        """Stop the tracking thread."""
        self.is_running = False
    
    def get_current_window(self) -> Optional[str]:
        """Get the currently tracked window title."""
        with self._lock:
            return self.current_window
    
    def get_recent_windows(self) -> list:
        """Get list of recently used windows."""
        with self._lock:
            return list(self.recent_windows)
    
    def get_context_string(self) -> str:
        """
        Returns a formatted string for the LLM's system prompt.
        
        Returns:
            str: Context string describing current and recent windows
        """
        with self._lock:
            if not self.current_window:
                return "No active window context available."
            
            context = f"Currently focused window: '{self.current_window}'\n"
            
            # Add recent windows if available
            recent = list(self.recent_windows)
            if len(recent) > 1:
                # Skip the first one (current) and show the rest
                other_recent = [w for w in recent[1:] if w != self.current_window]
                if other_recent:
                    context += "Recently used windows: " + " -> ".join(other_recent[:3])
            
            return context


# Global window tracker instance
window_tracker: Optional[WindowTracker] = None


def get_window_tracker() -> WindowTracker:
    """
    Get the global window tracker instance.
    Creates the tracker if it doesn't exist.
    
    Returns:
        WindowTracker: The global window tracker instance
    """
    global window_tracker
    if window_tracker is None:
        window_tracker = WindowTracker()
    return window_tracker


def start_window_tracker() -> None:
    """Start the global window tracker in a background thread."""
    tracker = get_window_tracker()
    if not tracker.is_running:
        tracker.start()
        print("[ContextTracker] Window tracking started")


def stop_window_tracker() -> None:
    """Stop the global window tracker."""
    tracker = get_window_tracker()
    tracker.stop()


def is_tracker_running() -> bool:
    """Check if the window tracker is running."""
    tracker = get_window_tracker()
    return tracker.is_running
