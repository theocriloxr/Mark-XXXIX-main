# backup_tool.py
"""
Backup Tool - Create and manage backups of directories and files.
Part of enhanced JARVIS system.
"""

import shutil
import os
import sys
import platform
import datetime
import hashlib
from pathlib import Path
from typing import Optional

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
BACKUP_DIR = BASE_DIR / "backups"
OS = platform.system().lower()

# Ensure backup directory exists
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def create_backup(source_path: str, name: str = "", compress: bool = True) -> str:
    """Create a backup of a directory or file."""
    try:
        source = Path(source_path).expanduser().resolve()
        
        if not source.exists():
            return f"Source not found: {source_path}"
        
        # Generate backup name
        if not name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"{source.name}_{timestamp}"
        
        # Create backup path
        if compress:
            backup_file = BACKUP_DIR / f"{name}.zip"
            shutil.make_archive(str(BACKUP_DIR / name), 'zip', source)
            return f"Backup created: {backup_file}"
        else:
            backup_dest = BACKUP_DIR / name
            if source.is_dir():
                shutil.copytree(source, backup_dest, dirs_exist_ok=True)
            else:
                shutil.copy2(source, backup_dest)
            return f"Backup created: {backup_dest}"
    
    except Exception as e:
        return f"Backup error: {e}"


def restore_backup(backup_name: str, destination: str = "") -> str:
    """Restore a backup."""
    try:
        backup_path = BACKUP_DIR / backup_name
        
        # Check for zip file
        if not backup_path.exists():
            zip_path = BACKUP_DIR / f"{backup_name}.zip"
            if zip_path.exists():
                backup_path = zip_path
            else:
                return f"Backup not found: {backup_name}"
        
        dest = Path(destination).expanduser().resolve() if destination else Path.home()
        
        if backup_path.suffix == '.zip':
            shutil.unpack_archive(backup_path, dest)
            return f"Restored to: {dest}"
        else:
            if backup_path.is_dir():
                shutil.copytree(backup_path, dest / backup_path.name, dirs_exist_ok=True)
            else:
                shutil.copy2(backup_path, dest)
            return f"Restored to: {dest}"
    
    except Exception as e:
        return f"Restore error: {e}"


def list_backups() -> str:
    """List available backups."""
    try:
        if not BACKUP_DIR.exists():
            return "No backups yet"
        
        files = []
        for item in BACKUP_DIR.iterdir():
            size = item.stat().st_size
            size_str = _format_size(size)
            files.append(f"  {item.name} ({size_str})")
        
        if not files:
            return "No backups available"
        
        return "Available backups:\n" + "\n".join(files)
    except Exception as e:
        return f"List error: {e}"


def delete_backup(backup_name: str) -> str:
    """Delete a backup."""
    try:
        backup_path = BACKUP_DIR / backup_name
        
        if not backup_path.exists():
            zip_path = BACKUP_DIR / f"{backup_name}.zip"
            if zip_path.exists():
                backup_path = zip_path
            else:
                return f"Backup not found: {backup_name}"
        
        if backup_path.is_dir():
            shutil.rmtree(backup_path)
        else:
            backup_path.unlink()
        
        return f"Deleted: {backup_name}"
    except Exception as e:
        return f"Delete error: {e}"


def _format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def backup_tool(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for backup tool."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
    if player:
        player.write_log(f"[backup] {action}")
    
    try:
        if action == "create":
            return create_backup(
                params.get("source", ""),
                params.get("name", ""),
                params.get("compress", True)
            )
        elif action == "restore":
            return restore_backup(
                params.get("backup_name", ""),
                params.get("destination", "")
            )
        elif action == "list":
            return list_backups()
        elif action == "delete":
            return delete_backup(params.get("backup_name", ""))
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Backup tool error: {e}"
