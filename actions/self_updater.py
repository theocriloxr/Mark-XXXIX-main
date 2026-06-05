# self_updater.py
"""
Self-Updater - JARVIS can update its own code.
Part of enhanced JARVIS system with auto-update capability.
"""

import os
import sys
import subprocess
import shutil
import json
import re
from pathlib import Path
from datetime import datetime


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


def get_current_version() -> str:
    """Get current JARVIS version."""
    # Try to read from config
    config_file = BASE_DIR / "config" / "api_keys.json"
    try:
        if config_file.exists():
            data = json.loads(config_file.read_text(encoding="utf-8"))
            return data.get("jarvis_version", "1.0.0")
    except:
        pass
    return "1.0.0"


def get_update_source() -> str:
    """Get update source (URL or local path for updates)."""
    config_file = BASE_DIR / "config" / "api_keys.json"
    try:
        if config_file.exists():
            data = json.loads(config_file.read_text(encoding="utf-8"))
            return data.get("update_source", "")
    except:
        pass
    return ""


def check_for_updates() -> str:
    """Check if updates are available."""
    current = get_current_version()
    source = get_update_source()
    
    if not source:
        return f"Current version: {current}. No update source configured."
    
    try:
        # If source is a URL, check for new version
        if source.startswith("http"):
            import urllib.request
            req = urllib.request.Request(source)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest = data.get("version", current)
                if latest != current:
                    return f"Update available: {current} -> {latest}"
                return f"You're up to date (v{current})"
        
        # If source is a local path
        source_path = Path(source)
        if source_path.exists():
            version_file = source_path / "version.txt"
            if version_file.exists():
                latest = version_file.read_text().strip()
                if latest != current:
                    return f"Update available: {current} -> {latest}"
                return f"You're up to date (v{current})"
    
    except Exception as e:
        return f"Check failed: {e}"
    
    return f"Current version: {current}"


def download_update(target_version: str = "") -> str:
    """Download update package."""
    source = get_update_source()
    
    if not source:
        return "No update source configured."
    
    if not target_version:
        target_version = "latest"
    
    try:
        if source.startswith("http"):
            import urllib.request
            # Construct download URL
            url = f"{source}/download/{target_version}"
            dest = BASE_DIR / "updates" / f"jarvis_{target_version}.zip"
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            urllib.request.urlretrieve(url, dest)
            return f"Downloaded update to: {dest}"
        
        return "Download not implemented for local source"
    
    except Exception as e:
        return f"Download failed: {e}"


def apply_update(update_file: str = "") -> str:
    """Apply downloaded update."""
    if not update_file:
        return "No update file specified."
    
    update_path = Path(update_file)
    if not update_path.exists():
        return f"Update file not found: {update_file}"
    
    try:
        # Backup current
        backup_dir = BASE_DIR / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy current files to backup
        for item in BASE_DIR.iterdir():
            if item.is_file() and item.suffix in (".py", ".txt", ".json"):
                shutil.copy2(item, backup_dir / item.name)
        
        # Extract update
        import zipfile
        with zipfile.ZipFile(update_path, "r") as zf:
            zf.extractall(BASE_DIR)
        
        return f"Update applied. Backup at: {backup_dir}"
    
    except Exception as e:
        return f"Update failed: {e}"


def rollback() -> str:
    """Rollback to previous version from backup."""
    backup_dir = None
    for item in (BASE_DIR / "backup").iterdir():
        if item.is_dir():
            if backup_dir is None or item.stat().st_mtime > backup_dir.stat().st_mtime:
                backup_dir = item
    
    if not backup_dir:
        return "No backup found."
    
    try:
        # Restore from backup
        for item in backup_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, BASE_DIR / item.name)
        
        return f"Rolled back to: {backup_dir.name}"
    
    except Exception as e:
        return f"Rollback failed: {e}"


def get_available_branches() -> str:
    """Get available update branches."""
    source = get_update_source()
    
    if not source:
        return "No update source configured."
    
    if source.startswith("http"):
        return "Use check_for_updates to see available updates."
    
    return "Branches not implemented for local source"


def self_update(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for self-updater."""
    params = parameters or {}
    action = params.get("action", "check").lower().strip()
    
    if player:
        player.write_log(f"[SelfUpdater] {action}")
    
    try:
        if action == "check":
            return check_for_updates()
        elif action == "download":
            return download_update(params.get("version", ""))
        elif action == "apply":
            return apply_update(params.get("file", ""))
        elif action == "rollback":
            return rollback()
        elif action == "version":
            return f"Version: {get_current_version()}"
        elif action == "branches":
            return get_available_branches()
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Self-updater error: {e}"
