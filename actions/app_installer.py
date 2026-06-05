# app_installer.py
"""
App Installer - Install/uninstall applications.
Part of enhanced JARVIS system for software management.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


_OS = platform.system()


def install_package(package: str) -> str:
    """Install a package via pip or system package manager."""
    try:
        # Try pip first
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return f"Installed: {package}"
        
        # Try system package manager
        if _OS == "windows":
            # Try winget
            result = subprocess.run(
                ["winget", "install", "--id", package, "-e", "--accept-source-agreements", "--accept-package-agreements"],
                capture_output=True,
                text=True,
                timeout=180
            )
        elif _OS == "darwin":
            result = subprocess.run(
                ["brew", "install", package],
                capture_output=True,
                text=True,
                timeout=180
            )
        else:
            # Linux
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", package],
                capture_output=True,
                text=True,
                timeout=180
            )
        
        if result.returncode == 0:
            return f"Installed: {package}"
        
        return f"Failed: {result.stderr}"
    except Exception as e:
        return f"Install error: {e}"


def uninstall_package(package: str) -> str:
    """Uninstall a package."""
    try:
        # Try pip first
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", package, "-y"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return f"Uninstalled: {package}"
        
        return f"Uninstalled from pip."
    except Exception as e:
        return f"Uninstall error: {e}"


def list_installed() -> str:
    """List installed packages."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        lines = result.stdout.strip().split("\n")[:20]
        return "Installed packages:\n" + "\n".join(lines)
    except Exception as e:
        return f"List error: {e}"


def app_installer(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for app installer."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
    try:
        if action == "install":
            return install_package(params.get("package", ""))
        
        elif action == "uninstall":
            return uninstall_package(params.get("package", ""))
        
        elif action == "list":
            return list_installed()
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"App installer error: {e}"
