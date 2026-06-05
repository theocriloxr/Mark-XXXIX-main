# self_updater.py
"""
Self-Updater - Auto-update JARVIS code and configuration.
Part of enhanced JARVIS system for self-improvement.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

try:
    import requests
    _REQUESTS = True
except ImportError:
    _REQUESTS = False


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


def check_for_updates() -> str:
    """Check for available updates."""
    # Check if running from git
    git_dir = BASE_DIR / ".git"
    if git_dir.exists():
        return "Git repository detected. Use 'git pull' to update."
    return "Not a git repository. Manual update required."


def get_version() -> str:
    """Get current version info."""
    version_file = BASE_DIR / "version.txt"
    if version_file.exists():
        return version_file.read_text().strip()
    return "1.0.0 (MARK XXXIX)"


def update_from_git() -> str:
    """Update from git repository."""
    if not (BASE_DIR / ".git").exists():
        return "Not a git repository."
    
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return f"Updated successfully: {result.stdout}"
        return f"Update failed: {result.stderr}"
    except FileNotFoundError:
        return "Git not found."
    except Exception as e:
        return f"Update error: {e}"


def backup_current() -> str:
    """Create backup of current installation."""
    try:
        backup_dir = BASE_DIR.parent / f"jarvis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copytree(BASE_DIR, backup_dir, ignore=shutil.ignore_patterns("*.pyc", "__pycache__", ".git", "venv", "*.egg-info"))
        return f"Backup created: {backup_dir.name}"
    except Exception as e:
        return f"Backup error: {e}"


def self_updater(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for self-updater."""
    params = parameters or {}
    action = params.get("action", "version").lower().strip()
    
    try:
        if action == "version":
            return get_version()
        
        elif action == "check":
            return check_for_updates()
        
        elif action == "update":
            return update_from_git()
        
        elif action == "backup":
            return backup_current()
        
        elif action == "restart":
            # This would restart the application
            import os
            os.execv(sys.executable, [sys.executable] + sys.argv)
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Self-updater error: {e}"
