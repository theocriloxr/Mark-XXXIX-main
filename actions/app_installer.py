# app_installer.py - Install/uninstall applications
import platform
import subprocess
import sys
from pathlib import Path

_OS = platform.system().lower()

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()

def install_app(app_name: str, source: str = "winget") -> str:
    """Install an application."""
    try:
        if _OS == "windows":
            if source == "winget":
                result = subprocess.run(
                    ["winget", "install", "--id", app_name, "--silent", "--accept-package-agreements"],
                    capture_output=True, text=True, timeout=120
                )
            elif source == "pip":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", app_name],
                    capture_output=True, text=True, timeout=120
                )
            elif source == "npm":
                result = subprocess.run(
                    ["npm", "install", "-g", app_name],
                    capture_output=True, text=True, timeout=120
                )
            else:
                return f"Unknown source: {source}"
                
        elif _OS == "darwin":
            if source == "brew":
                result = subprocess.run(
                    ["brew", "install", app_name],
                    capture_output=True, text=True, timeout=120
                )
            elif source == "pip":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", app_name],
                    capture_output=True, text=True, timeout=120
                )
            elif source == "npm":
                result = subprocess.run(
                    ["npm", "install", "-g", app_name],
                    capture_output=True, text=True, timeout=120
                )
            else:
                return f"Unknown source: {source}"
        else:
            if source in ("pip", "npm"):
                if source == "pip":
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", app_name],
                        capture_output=True, text=True, timeout=120
                    )
                else:
                    result = subprocess.run(
                        ["npm", "install", "-g", app_name],
                        capture_output=True, text=True, timeout=120
                    )
            else:
                return f"Unsupported: {source}"
        
        if result.returncode == 0:
            return f"Installed: {app_name}"
        return f"Failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Install timed out"
    except Exception as e:
        return f"Error: {e}"

def uninstall_app(app_name: str, source: str = "winget") -> str:
    """Uninstall an application."""
    try:
        if _OS == "windows":
            if source == "winget":
                result = subprocess.run(
                    ["winget", "uninstall", "--id", app_name, "--silent"],
                    capture_output=True, text=True, timeout=60
                )
            elif source == "pip":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", app_name, "-y"],
                    capture_output=True, text=True, timeout=60
                )
            elif source == "npm":
                result = subprocess.run(
                    ["npm", "uninstall", "-g", app_name],
                    capture_output=True, text=True, timeout=60
                )
            else:
                return f"Unknown: {source}"
        elif _OS == "darwin":
            if source == "brew":
                result = subprocess.run(
                    ["brew", "uninstall", app_name],
                    capture_output=True, text=True, timeout=60
                )
            elif source == "pip":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", app_name, "-y"],
                    capture_output=True, text=True, timeout=60
                )
            else:
                return f"Unknown: {source}"
        else:
            if source == "pip":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", app_name, "-y"],
                    capture_output=True, text=True, timeout=60
                )
            else:
                return f"Unsupported: {source}"
        
        if result.returncode == 0:
            return f"Uninstalled: {app_name}"
        return f"Failed: {result.stderr}"
    except Exception as e:
        return f"Error: {e}"

def list_apps(category: str = "all") -> str:
    """List installed applications."""
    try:
        if category in ("pip", "all"):
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[2:12]
                return "Installed packages:\n" + "\n".join(lines)
        
        if _OS == "windows" and category == "winget":
            result = subprocess.run(
                ["winget", "list"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()[:500]
        
        return "No apps found."
    except Exception as e:
        return f"Error: {e}"

def app_installer(parameters: dict = None, response=None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    app_name = params.get("app_name", "")
    source = params.get("source", "pip" if not _OS == "windows" else "winget")
    
    if action == "install":
        return install_app(app_name, source)
    elif action == "uninstall":
        return uninstall_app(app_name, source)
    elif action == "list":
        return list_apps(params.get("category", "all"))
    elif action == "search":
        return f"Search for: {app_name} (use browser to search)"
    else:
        return list_apps("all")
