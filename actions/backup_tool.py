# backup_tool.py
"""
Backup Tool - Directory backup and restore
"""

import shutil
import time
from pathlib import Path, PureWindowsPath
import sys
import platform
import json
import os

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

_OS = platform.system()

def backup_directory(source: str, backup_name: str = "") -> str:
    src = Path(source)
    if not src.exists():
        return f"Source not found: {source}"
    
    if not backup_name:
        backup_name = f"{src.name}_{int(time.time())}"
    
    dest = BACKUP_DIR / backup_name
    
    try:
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        
        size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
        size_mb = size / 1024 / 1024
        return f"Backed up: {source} -> {backup_name} ({size_mb:.1f} MB)"
    except Exception as e:
        return f"Backup failed: {e}"

def restore_backup(backup_name: str, dest: str) -> str:
    src = BACKUP_DIR / backup_name
    if not src.exists():
        return f"Backup not found: {backup_name}"
    
    try:
        dst = Path(dest)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
        return f"Restored: {backup_name} -> {dest}"
    except Exception as e:
        return f"Restore failed: {e}"

def list_backups() -> str:
    if not BACKUP_DIR.exists():
        return "No backups yet."
    
    items = []
    for item in sorted(BACKUP_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if item.is_dir():
            size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
            items.append(f"  {item.name} ({size/1024/1024:.1f} MB)")
        else:
            items.append(f"  {item.name} ({item.stat().st_size/1024:.1f} KB)")
    
    if not items:
        return "No backups found."
    return "Available backups:\n" + "\n".join(items)

def delete_backup(backup_name: str) -> str:
    src = BACKUP_DIR / backup_name
    if not src.exists():
        return f"Backup not found: {backup_name}"
    
    try:
        if src.is_dir():
            shutil.rmtree(src)
        else:
            src.unlink()
        return f"Deleted: {backup_name}"
    except Exception as e:
        return f"Delete failed: {e}"

def backup_tool(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    source = params.get("source", "").strip()
    backup_name = params.get("backup_name", "").strip()
    dest = params.get("destination", "").strip()
    
    try:
        if action == "backup":
            if not source:
                return "Specify source directory."
            return backup_directory(source, backup_name)
        
        elif action == "restore":
            if not backup_name or not dest:
                return "Specify backup_name and destination."
            return restore_backup(backup_name, dest)
        
        elif action == "list":
            return list_backups()
        
        elif action == "delete":
            if not backup_name:
                return "Specify backup_name."
            return delete_backup(backup_name)
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Error: {e}"
