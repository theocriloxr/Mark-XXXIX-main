"""
System Tray Icon for JARVIS - OS-Level Integration
Creates a system tray icon for background operation without terminal dependency.
"""

import sys
import threading
import os
from pathlib import Path

# Try to_import pystray, install if missing
try:
    from pystray import MenuItem as Item
    import pystray
except ImportError:
    import subprocess
    print("[Tray] Installing pystray...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pystray", "-q"])
    from pystray import MenuItem as Item
    import pystray

from PIL import Image
import io


def _create_default_icon():
    """Create a simple JARVIS icon image."""
    from PIL import ImageDraw
    
    # Create a 64x64 blue square with "J"
    size = 64
    img = Image.new("RGB", (size, size), color=(0, 85, 170))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple circle
    draw.ellipse([8, 8, 56, 56], outline=(255, 255, 255), width=3)
    
    # Draw "J" in center
    draw.text([20, 18], "J", fill=(255, 255, 255))
    
    return img


def _get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()


class JarvisTray:
    """System tray management for JARVIS."""
    
    def __init__(self, on_restart=None, on_view_logs=None, on_shutdown=None):
        self.on_restart = on_restart
        self.on_view_logs = on_view_logs
        self.on_shutdown = on_shutdown
        self._icon = None
        self._thread = None
        self._running = False
    
    def _create_menu(self):
        return (
            Item("Restart JARVIS", self._on_restart),
            Item("View Logs", self._on_view_logs),
            Item("Separator", lambda: None),
            Item("Shutdown", self._on_shutdown),
        )
    
    def _on_restart(self):
        if self.on_restart:
            self.on_restart()
    
    def _on_view_logs(self):
        if self.on_view_logs:
            self.on_view_logs()
    
    def _on_shutdown(self):
        if self.on_shutdown:
            self.on_shutdown()
        self.stop()
    
    def start(self):
        """Start the system tray icon."""
        if self._running:
            return
        
        self._running = True
        
        # Create icon image
        try:
            icon_path = BASE_DIR / "face.png"
            if icon_path.exists():
                image = Image.open(icon_path).resize((64, 64))
            else:
                image = _create_default_icon()
        except Exception:
            image = _create_default_icon()
        
        # Create the icon
        self._icon = pystray.Icon(
            "JARVIS",
            image,
            "JARVIS - MARK XXXIX",
            self._create_menu()
        )
        
        # Run in separate thread
        def run_icon():
            try:
                self._icon.run()
            except Exception as e:
                print(f"[Tray] Icon error: {e}")
        
        self._thread = threading.Thread(target=run_icon, daemon=True)
        self._thread.start()
        
        print("[Tray] ✅ System tray icon started")
    
    def stop(self):
        """Stop the system tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
        self._running = False
        print("[Tray] System tray stopped")


def get_tray_icon(on_restart=None, on_view_logs=None, on_shutdown=None):
    """Get or create the system tray icon."""
    return JarvisTray(on_restart, on_view_logs, on_shutdown)


# === WATCHDOG FOR AUTO-RECOVERY ===

class Watchdog:
    """Monitors main.py and auto-restarts if crashed."""
    
    def __init__(self, main_path: str = None, restart_delay: int = 5):
        self.main_path = main_path or str(BASE_DIR / "main.py")
        self.restart_delay = restart_delay
        self._running = False
        self._process = None
    
    def _check_process(self):
        """Check if main.py is running."""
        import psutil
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'main.py' in ' '.join(cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    
    def start(self):
        """Start the watchdog."""
        if self._running:
            return
        
        self._running = True
        
        def watch():
            import time
            while self._running:
                if not self._check_process():
                    print(f"[Watchdog] JARVIS not running, restarting in {self.restart_delay}s...")
                    time.sleep(self.restart_delay)
                    if self._running and not self._check_process():
                        try:
                            import subprocess
                            subprocess.Popen(
                                [sys.executable, self.main_path],
                                detached=True,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                            )
                            print("[Watchdog] ✅ JARVIS restarted")
                        except Exception as e:
                            print(f"[Watchdog] Restart failed: {e}")
                time.sleep(10)
        
        thread = threading.Thread(target=watch, daemon=True)
        thread.start()
        
        print("[Watchdog] ✅ Started")
    
    def stop(self):
        """Stop the watchdog."""
        self._running = False


def tray_icon(parameters: dict = None, player=None, session_memory=None) -> str:
    """Main dispatcher for tray_icon tool."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if action == "start":
        tray = get_tray_icon()
        tray.start()
        return "System tray icon started, sir."
    
    elif action == "stop":
        tray = get_tray_icon()
        tray.stop()
        return "System tray icon stopped."
    
    elif action == "status":
        return "System tray: Ready to start. Say 'start tray icon' to activate."
    
    else:
        return f"Unknown action: {action}. Use start, stop, or status."


if __name__ == "__main__":
    # Test the tray icon
    print("[Test] Starting system tray icon...")
    tray = get_tray_icon(
        on_restart=lambda: print("Restart requested"),
        on_view_logs=lambda: print("View logs requested"),
        on_shutdown=lambda: print("Shutdown requested")
    )
    tray.start()
    
    import time
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        pass
    
    tray.stop()
    print("[Test] Done")
