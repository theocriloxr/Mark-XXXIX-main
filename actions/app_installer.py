# app_installer.py
"""
App Installer - Install or uninstall applications.
Supports winget, pip, brew, npm.
Part of enhanced JARVIS system.
"""

import subprocess
import platform
import sys
from pathlib import Path

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
OS = platform.system().lower()


def list_installed_apps(source: str = "winget", category: str = "") -> str:
    """List installed applications."""
    try:
        if OS == "windows" and source == "winget":
            result = subprocess.run(
                ["winget", "list"],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout[:2000]
        elif source == "pip":
            result = subprocess.run(
                ["pip", "list"],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout[:2000]
        elif source == "npm":
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0"],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout[:2000]
        elif OS == "darwin" and source == "brew":
            result = subprocess.run(
                ["brew", "list", "--formula"],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout[:2000]
        
        return f"Unable to list apps from {source}"
    except Exception as e:
        return f"Error listing apps: {e}"


def install_app(app_name: str, source: str = "winget") -> str:
    """Install an application."""
    try:
        if OS == "windows" and source == "winget":
            result = subprocess.run(
                ["winget", "install", "--id", app_name, "--silent", "--accept-package-agreements", "--accept-source-agreements"],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully installed {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        elif source == "pip":
            result = subprocess.run(
                ["pip", "install", app_name],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully installed {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        elif source == "npm":
            result = subprocess.run(
                ["npm", "install", "-g", app_name],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully installed {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        elif OS == "darwin" and source == "brew":
            result = subprocess.run(
                ["brew", "install", app_name],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully installed {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        return f"Unknown source: {source}"
    except subprocess.TimeoutExpired:
        return f"Installation timed out for {app_name}"
    except Exception as e:
        return f"Installation error: {e}"


def uninstall_app(app_name: str, source: str = "winget") -> str:
    """Uninstall an application."""
    try:
        if OS == "windows" and source == "winget":
            result = subprocess.run(
                ["winget", "uninstall", "--id", app_name, "--silent"],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully uninstalled {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        elif source == "pip":
            result = subprocess.run(
                ["pip", "uninstall", app_name, "-y"],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully uninstalled {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        elif source == "npm":
            result = subprocess.run(
                ["npm", "uninstall", "-g", app_name],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully uninstalled {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        elif OS == "darwin" and source == "brew":
            result = subprocess.run(
                ["brew", "uninstall", app_name],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return f"Successfully uninstalled {app_name}"
            return f"Failed: {result.stderr[:500]}"
        
        return f"Unknown source: {source}"
    except Exception as e:
        return f"Uninstallation error: {e}"


def search_apps(query: str, source: str = "winget") -> str:
    """Search for an application to install."""
    try:
        if OS == "windows" and source == "winget":
            result = subprocess.run(
                ["winget", "search", query],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout[:2000]
        
        return f"Search not supported for {source}"
    except Exception as e:
        return f"Search error: {e}"


def app_installer(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for app installer."""
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    app_name = params.get("app_name", "")
    source = params.get("source", "winget").lower().strip()
    
    # Determine default source by OS
    if source == "pip" or source == "npm":
        pass  # keep as is
    elif OS == "darwin":
        source = "brew"
    elif OS == "linux":
        source = "pip"
    else:
        source = "winget"
    
    if player:
        player.write_log(f"[app_installer] {action}")
    
    try:
        if action == "install":
            if not app_name:
                return "Please specify app_name"
            return install_app(app_name, source)
        elif action == "uninstall":
            if not app_name:
                return "Please specify app_name"
            return uninstall_app(app_name, source)
        elif action == "list":
            return list_installed_apps(source)
        elif action == "search":
            if not app_name:
                return "Please specify app_name"
            return search_apps(app_name, source)
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"App installer error: {e}"
