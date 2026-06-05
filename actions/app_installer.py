# app_installer.py
"""
App Installer - Install/uninstall applications via winget, pip, brew, npm
"""

import subprocess
import sys
from pathlib import Path

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()

def _run_command(cmd: list) -> tuple:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def install_app(app_name: str, source: str = "winget") -> str:
    source = source.lower()
    
    if source == "pip":
        cmd = [sys.executable, "-m", "pip", "install", app_name]
    elif source == "npm":
        cmd = ["npm", "install", "-g", app_name]
    elif source == "brew":
        cmd = ["brew", "install", app_name]
    elif source == "winget":
        cmd = ["winget", "install", "--id", app_name, "--silent", "--accept-package-agreements"]
    else:
        return f"Unknown source: {source}"
    
    code, out, err = _run_command(cmd)
    if code == 0:
        return f"Installed: {app_name}"
    return f"Failed: {err[:100]}"

def uninstall_app(app_name: str, source: str = "winget") -> str:
    source = source.lower()
    
    if source == "pip":
        cmd = [sys.executable, "-m", "pip", "uninstall", app_name, "-y"]
    elif source == "npm":
        cmd = ["npm", "uninstall", "-g", app_name]
    elif source == "brew":
        cmd = ["brew", "uninstall", app_name]
    elif source == "winget":
        cmd = ["winget", "uninstall", "--id", app_name, "--silent"]
    else:
        return f"Unknown source: {source}"
    
    code, out, err = _run_command(cmd)
    if code == 0:
        return f"Uninstalled: {app_name}"
    return f"Failed: {err[:100]}"

def list_apps(source: str = "pip") -> str:
    source = source.lower()
    
    if source == "pip":
        cmd = [sys.executable, "-m", "pip", "list"]
    elif source == "npm":
        cmd = ["npm", "list", "-g", "--depth=0"]
    elif source == "brew":
        cmd = ["brew", "list"]
    else:
        return f"Unknown source: {source}"
    
    code, out, err = _run_command(cmd)
    if code == 0:
        lines = out.strip().split("\n")[:20]
        return f"{source.upper()} packages:\n" + "\n".join(lines)
    return f"Error: {err[:100]}"

def search_app(app_name: str, source: str = "pip") -> str:
    source = source.lower()
    
    if source == "pip":
        cmd = [sys.executable, "-m", "pip", "search", app_name]
    elif source == "npm":
        cmd = ["npm", "search", app_name]
    else:
        return f"Search not supported for: {source}"
    
    code, out, err = _run_command(cmd)
    if code == 0:
        lines = out.strip().split("\n")[:10]
        return "\n".join(lines)
    return f"Error: {err[:100]}"

def app_installer(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    app_name = params.get("app_name", "").strip()
    source = params.get("source", "winget").strip()
    
    try:
        if action == "install":
            if not app_name:
                return "Specify app_name."
            return install_app(app_name, source)
        
        elif action == "uninstall":
            if not app_name:
                return "Specify app_name."
            return uninstall_app(app_name, source)
        
        elif action == "list":
            return list_apps(source)
        
        elif action == "search":
            if not app_name:
                return "Specify app_name."
            return search_app(app_name, source)
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Error: {e}"
