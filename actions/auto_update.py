# auto_update.py
"""
Auto-Update System - JARVIS can update its own code and learn from interactions
"""

import os
import sys
import json
import re
import shutil
import time
from pathlib import Path
from datetime import datetime

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
LEARNING_FILE = BASE_DIR / "memory" / "learned.json"
VERSION_FILE = BASE_DIR / "memory" / "version.json"

def _get_version() -> dict:
    if VERSION_FILE.exists():
        try:
            return json.loads(VERSION_FILE.read_text())
        except:
            pass
    return {"version": "1.0.0", "last_update": "", "changelog": []}

def _save_version(v: dict) -> None:
    VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    VERSION_FILE.write_text(json.dumps(v, indent=2))

def get_current_version() -> str:
    v = _get_version()
    return f"JARVIS v{v['version']}"

def get_changelog() -> str:
    v = _get_version()
    changes = v.get("changelog", [])
    if not changes:
        return "No updates yet."
    lines = [f"Version {v['version']}:"]
    for c in changes[-10:]:
        lines.append(f"  - {c}")
    return "\n".join(lines)

def check_for_updates() -> str:
    current = _get_version()
    return f"Current: {current['version']} | Last update: {current.get('last_update', 'Never')}"

def save_learned(pattern: str, command_type: str, success: bool = True) -> str:
    if LEARNING_FILE.exists():
        try:
            data = json.loads(LEARNING_FILE.read_text())
        except:
            data = {"patterns": [], "commands": []}
    else:
        data = {"patterns": [], "commands": []}
    
    data["patterns"].append({
        "pattern": pattern,
        "type": command_type,
        "success": success,
        "timestamp": datetime.now().isoformat()
    })
    
    if len(data["patterns"]) > 1000:
        data["patterns"] = data["patterns"][-500:]
    
    LEARNING_FILE.parent.mkdir(parents=True, exist_ok=True)
    LEARNING_FILE.write_text(json.dumps(data, indent=2))
    return "Learned pattern saved."

def analyze_performance() -> str:
    if not LEARNING_FILE.exists():
        return "No performance data yet."
    
    data = json.loads(LEARNING_FILE.read_text())
    patterns = data.get("patterns", [])
    
    if not patterns:
        return "No patterns analyzed."
    
    successful = sum(1 for p in patterns if p.get("success"))
    total = len(patterns)
    success_rate = (successful / total * 100) if total > 0 else 0
    
    return (
        f"Performance Analysis:\n"
        f"  Total Commands: {total}\n"
        f"  Successful: {successful}\n"
        f"  Success Rate: {success_rate:.1f}%"
    )

def backup_code() -> str:
    backup_dir = BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"jarvis_backup_{timestamp}"
    
    backup_path = backup_dir / backup_name
    backup_path.mkdir()
    
    for item in BASE_DIR.iterdir():
        if item.name in ["backups", "__pycache__", ".git", "venv", "env"]:
            continue
        if item.is_file():
            shutil.copy2(item, backup_path / item.name)
        elif item.is_dir():
            shutil.copytree(item, backup_path / item.name, ignore=shutil.ignore_errors)
    
    return f"Code backed up to: {backup_name}"

def restore_backup(backup_name: str) -> str:
    backup_dir = BASE_DIR / "backups"
    backup_path = backup_dir / backup_name
    
    if not backup_path.exists():
        return f"Backup not found: {backup_name}"
    
    for item in backup_path.iterdir():
        dest = BASE_DIR / item.name
        if item.is_file():
            shutil.copy2(item, dest)
        elif item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
    
    return f"Restored from: {backup_name}"

def list_backups() -> str:
    backup_dir = BASE_DIR / "backups"
    if not backup_dir.exists():
        return "No backups available."
    
    backups = sorted(backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    if not backups:
        return "No backups available."
    
    lines = ["Available backups:"]
    for b in backups[:10]:
        mtime = datetime.fromtimestamp(b.stat().st_mtime)
        lines.append(f"  - {b.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")
    return "\n".join(lines)

def apply_patch(patch_code: str) -> str:
    """Apply a code patch to modify JARVIS behavior."""
    try:
        import google.generativeai as genai
        from config.api_keys import _get_api_key
        
        genai.configure(api_key=_get_api_key())
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""Apply this patch to the JARVIS code:
{patch_code}

Return the modified code file content. Only change what's necessary."""
        
        response = model.generate_content(prompt)
        return "Patch applied (simulation)"
    except:
        return "Auto-patch requires AI configuration."

def auto_update(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "version").lower().strip()
    
    try:
        if action == "version":
            return get_current_version()
        
        elif action == "changelog":
            return get_changelog()
        
        elif action == "check":
            return check_for_updates()
        
        elif action == "performance":
            return analyze_performance()
        
        elif action == "backup":
            return backup_code()
        
        elif action == "restore":
            return restore_backup(params.get("backup_name", ""))
        
        elif action == "list_backups":
            return list_backups()
        
        elif action == "learn":
            return save_learned(
                params.get("pattern", ""),
                params.get("command_type", ""),
                params.get("success", True)
            )
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Error: {e}"
