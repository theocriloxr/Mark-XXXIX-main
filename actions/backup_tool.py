# backup_tool.py - Backup and restore directories
import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
BACKUP_DIR = BASE_DIR / "backups"
CONFIG_FILE = BASE_DIR / "config" / "backups.json"

def _load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {"backups": []}

def _save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

def create_backup(source: str, name: str = "") -> str:
    try:
        src = Path(source).expanduser().resolve()
        if not src.exists():
            return f"Source not found: {source}"
        
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        if not name:
            name = f"{src.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        dst = BACKUP_DIR / name
        shutil.copytree(src, dst)
        
        config = _load_config()
        config["backups"].append({
            "name": name,
            "source": str(src),
            "backup_path": str(dst),
            "created": datetime.now().isoformat()
        })
        _save_config(config)
        
        return f"Backup created: {name}"
    except Exception as e:
        return f"Backup error: {e}"

def list_backups() -> str:
    config = _load_config()
    backups = config.get("backups", [])
    if not backups:
        return "No backups found."
    
    lines = ["Backups:"]
    for b in backups:
        lines.append(f"  - {b['name']}: {b['source']} ({b['created'][:10]})")
    return "\n".join(lines)

def restore_backup(name: str, destination: str = "") -> str:
    try:
        config = _load_config()
        backups = config.get("backups", [])
        
        backup = None
        for b in backups:
            if b["name"] == name:
                backup = b
                break
        
        if not backup:
            return f"Backup not found: {name}"
        
        src = Path(backup["backup_path"])
        if not src.exists():
            return f"Backup source missing: {src}"
        
        if not destination:
            destination = backup["source"]
        
        dst = Path(destination)
        shutil.copytree(src, dst, dirs_exist_ok=True)
        
        return f"Restored to: {destination}"
    except Exception as e:
        return f"Restore error: {e}"

def delete_backup(name: str) -> str:
    try:
        config = _load_config()
        backups = config.get("backups", [])
        
        for b in backups:
            if b["name"] == name:
                path = Path(b["backup_path"])
                if path.exists():
                    shutil.rmtree(path)
                backups.remove(b)
                config["backups"] = backups
                _save_config(config)
                return f"Deleted backup: {name}"
        
        return f"Backup not found: {name}"
    except Exception as e:
        return f"Delete error: {e}"

def backup_tool(parameters: dict = None, response=None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
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
    elif action == "delete":
        return delete_backup(params.get("name", ""))
    else:
        return list_backups()
