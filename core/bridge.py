"""
OS Bridge - Universal OS Abstraction Layer

Cross-platform abstraction for JARVIS:
- Detects host OS (Windows, macOS, Linux)
- Unified API for window tracking, notifications, resources

Usage:
    from core.bridge import bridge
    
    window = bridge.get_active_window_title()
    bridge.notify("JARVIS", "Task complete!")
"""

import logging
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Get base directory
def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


class OSBridge:
    """
    Universal OS Abstraction Layer.
    Provides cross-platform APIs for common operations.
    """
    
    def __init__(self):
        self.os_type = platform.system()  # 'Windows', 'Darwin', 'Linux'
        self.is_apple_silicon = (
            self.os_type == "Darwin" and platform.processor() == "arm"
        )
        self._pygetwindow_available = False
        
        # Check for pygetwindow on Windows
        if self.os_type == "Windows":
            try:
                import pygetwindow as gw
                self._gw = gw
                self._pygetwindow_available = True
            except ImportError:
                self._gw = None
                self._pygetwindow_available = False
        
        logger.info(f"[BRIDGE] Initialized on {self.os_type}")
    
    def get_active_window_title(self) -> str:
        """
        Get the currently active window title.
        Cross-platform implementation.
        
        Returns:
            str: Window title or fallback message
        """
        try:
            if self.os_type == "Windows":
                return self._get_active_window_windows()
            elif self.os_type == "Darwin":
                return self._get_active_window_macos()
            elif self.os_type == "Linux":
                return self._get_active_window_linux()
        except Exception as e:
            logger.debug(f"[BRIDGE] Get window error: {e}")
            return "Desktop"
    
    def _get_active_window_windows(self) -> str:
        """Windows implementation using pygetwindow or ctypes."""
        if self._pygetwindow_available and self._gw:
            try:
                active_win = self._gw.getActiveWindow()
                if active_win and active_win.title:
                    return active_win.title.strip()
            except Exception:
                pass
        
        # Fallback: ctypes
        try:
            import ctypes
            from ctypes import wintypes
            
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length:
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value.strip()
        except Exception:
            pass
        
        return "Desktop"
    
    def _get_active_window_macos(self) -> str:
        """macOS implementation using AppleScript."""
        try:
            script = (
                'tell application "System Events" to get name of '
                'first process whose frontmost is true'
            )
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"[BRIDGE] macOS window error: {e}")
        return "Desktop"
    
    def _get_active_window_linux(self) -> str:
        """Linux implementation using xprop."""
        try:
            # Get active window ID
            result = subprocess.run(
                ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Parse window ID from output
                output = result.stdout.strip()
                if output:
                    # Output format: _NET_ACTIVE_WINDOW(WINDOW): window id # 0x1234567
                    window_id = output.split("#")[-1].strip()
                    if window_id:
                        # Get window name
                        name_result = subprocess.run(
                            ["xprop", "-id", window_id, "WM_NAME"],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        if name_result.returncode == 0:
                            # Parse name from output
                            name_output = name_result.stdout.strip()
                            if "WM_NAME" in name_output:
                                name = name_output.split("=")[-1].strip('"')
                                return name
        except Exception as e:
            logger.debug(f"[BRIDGE] Linux window error: {e}")
        return "Desktop"
    
    def notify(self, title: str, message: str, duration: int = 5) -> None:
        """
        Show native OS notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Display duration in seconds
        """
        try:
            if self.os_type == "Windows":
                self._notify_windows(title, message, duration)
            elif self.os_type == "Darwin":
                self._notify_macos(title, message)
            elif self.os_type == "Linux":
                self._notify_linux(title, message)
        except Exception as e:
            logger.debug(f"[BRIDGE] Notify error: {e}")
    
    def _notify_windows(self, title: str, message: str, duration: int):
        """Windows notification using win10toast."""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=duration, threaded=True)
        except ImportError:
            # Fallback: ctypes message box (non-blocking)
            try:
                import ctypes
                from ctypes import wintypes
                
                MB_OK = 0x0
                MB_ICONINFORMATION = 0x40
                
                ctypes.windll.user32.MessageBoxW(
                    None,
                    message,
                    title,
                    MB_OK | MB_ICONINFORMATION
                )
            except Exception:
                pass
    
    def _notify_macos(self, title: str, message: str):
        """macOS notification using AppleScript."""
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], timeout=5)
        except Exception:
            pass
    
    def _notify_linux(self, title: str, message: str):
        """Linux notification using notify-send."""
        try:
            subprocess.run(
                ["notify-send", title, message],
                timeout=5
            )
        except Exception:
            pass
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get standardized hardware telemetry.
        
        Returns:
            dict: CPU, RAM, OS info
        """
        try:
            import psutil
            
            return {
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "os": self.os_type,
                "is_apple_silicon": self.is_apple_silicon
            }
        except ImportError:
            return {
                "cpu": 0,
                "ram": 0,
                "os": self.os_type,
                "is_apple_silicon": self.is_apple_silicon
            }
    
    def is_elevated(self) -> bool:
        """
        Check if running with elevated privileges.
        
        Returns:
            bool: True if elevated
        """
        try:
            if self.os_type == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            elif self.os_type == "Darwin":
                # Check EUID
                import os
                return os.geteuid() == 0
            elif self.os_type == "Linux":
                import os
                return os.geteuid() == 0
        except Exception:
            return False
    
    def get_battery_status(self) -> Optional[Dict[str, Any]]:
        """
        Get battery status (if available).
        
        Returns:
            dict: Battery info or None
        """
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "charging": battery.is_plugged_in,
                    "time_left": battery.secsleft
                }
        except Exception:
            pass
        return None
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network connection info.
        
        Returns:
            dict: Network status
        """
        try:
            import psutil
            net = psutil.net_io_counters()
            return {
                "bytes_sent": net.bytes_sent,
                "bytes_recv": net.bytes_recv,
                "packets_sent": net.packets_sent,
                "packets_recv": net.packets_recv
            }
        except Exception:
            return {}
    
    def open_url(self, url: str) -> bool:
        """
        Open URL in default browser.
        
        Args:
            url: URL to open
            
        Returns:
            bool: Success
        """
        try:
            if self.os_type == "Windows":
                import os
                os.startfile(url)
            elif self.os_type == "Darwin":
                subprocess.run(["open", url], timeout=5)
            elif self.os_type == "Linux":
                subprocess.run(["xdg-open", url], timeout=5)
            return True
        except Exception as e:
            logger.debug(f"[BRIDGE] Open URL error: {e}")
            return False
    
    def get_process_count(self) -> int:
        """Get number of running processes."""
        try:
            import psutil
            return len(psutil.pids())
        except Exception:
            return 0
    
    def get_boot_time(self) -> float:
        """Get system boot time (timestamp)."""
        try:
            import psutil
            return psutil.boot_time()
        except Exception:
            return 0


# === GLOBAL INSTANCE ===

_bridge: Optional[OSBridge] = None


def get_bridge() -> OSBridge:
    """Get global OS Bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = OSBridge()
    return _bridge


# Shortcut
bridge = get_bridge()


# === DISPATCHER ===

def os_bridge(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for OS Bridge."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[OSBridge] {action}")
    
    try:
        b = get_bridge()
        
        if action == "status":
            res = b.get_resource_usage()
            return (
                f"OS: {b.os_type} | "
                f"CPU: {res['cpu']:.0f}% | "
                f"RAM: {res['ram']:.0f}%"
            )
        
        elif action == "window":
            return b.get_active_window_title()
        
        elif action == "notify":
            title = params.get("title", "JARVIS")
            message = params.get("message", "")
            b.notify(title, message)
            return "Notification sent"
        
        elif action == "battery":
            batt = b.get_battery_status()
            if batt:
                status = "Charging" if batt["charging"] else "Discharging"
                return f"Battery: {batt['percent']}% ({status})"
            return "Battery info not available"
        
        elif action == "network":
            net = b.get_network_info()
            if net:
                sent = net.get("bytes_sent", 0) / 1024 / 1024
                recv = net.get("bytes_recv", 0) / 1024 / 1024
                return f"Network: ↓{recv:.1f}MB ↑{sent:.1f}MB"
            return "Network info not available"
        
        elif action == "processes":
            count = b.get_process_count()
            return f"Running processes: {count}"
        
        elif action == "elevated":
            return f"Elevated privileges: {b.is_elevated()}"
        
        else:
            res = b.get_resource_usage()
            return f"OS: {b.os_type}, CPU: {res['cpu']:.0f}%, RAM: {res['ram']:.0f}%"
    
    except Exception as e:
        return f"OSBridge error: {e}"


if __name__ == "__main__":
    # Test
    print("=== OS Bridge Test ===")
    
    b = get_bridge()
    print(f"OS: {b.os_type}")
    print(f"Apple Silicon: {b.is_apple_silicon}")
    print(f"Window: {b.get_active_window_title()}")
    
    res = b.get_resource_usage()
    print(f"CPU: {res['cpu']:.0f}%")
    print(f"RAM: {res['ram']:.0f}%")
    
    print("\n✅ OS Bridge ready")
