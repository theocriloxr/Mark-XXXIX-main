# backup_tool.py
"""
Backup Tool - Directory backup and restore.
Part of enhanced JARVIS system for data safety.
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import difflib


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()
BACKUP_DIR = BASE_DIR / "backups"


def create_backup(source: str, name: str = "") -> str:
    """Create a backup of a directory."""
    try:
        src = Path(source).expanduser().resolve()
        if not src.exists():
            return f"Source not found: {source}"
        
        if not name:
            name = src.name + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        dest = BACKUP_DIR / name
        
        if src.is_dir():
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.pyc", "__pycache__", ".git", "venv"))
        else:
            shutil.copy2(src, dest)
        
        return f"Backup created: {name}"
    except Exception as e:
        return f"Backup error: {e}"


def list_backups() -> str:
    """List all backups."""
    if not BACKUP_DIR.exists():
        return "No backups yet."
    
    backups = sorted(BACKUP_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    if not backups:
        return "No backups found."
    
    lines = ["Available backups:"]
    for b in backups[:20]:
        size = b.stat().st_size
        if size > 1024*1024:
            size_str = f"{size/1024/1024:.1f} MB"
        else:
            size_str = f"{size/1024:.1f} KB"
        lines.append(f"  {b.name} ({size_str})")
    
    return "\n".join(lines)


def restore_backup(name: str, destination: str = "") -> str:
    """Restore a backup."""
    try:
        backup = BACKUP_DIR / name
        if not backup.exists():
            return f"Backup not found: {name}"
        
        if not destination:
            destination = str(backup.parent.parent / ("restored_" + name))
        
        if backup.is_dir():
            shutil.copytree(backup, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(backup, destination)
        
        return f"Restored to: {destination}"
    except Exception as e:
        return f"Restore error: {e}"


def backup_tool(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for backup tool."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
    try:
        if action == "create":
            return create_backup(
                params.get("source", ""),
                params.get("name", "")
            )
        
        elif action == "list":
            return list_backups()
        
        elif action == "restore":
            return restore_backup(
                params.get("name", ""),
                params.get("destination", "")
            )
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Backup tool error: {e}"
