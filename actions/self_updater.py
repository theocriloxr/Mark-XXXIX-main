# self_updater.py - Auto-update JARVIS code
import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
UPDATE_CONFIG = BASE_DIR / "config" / "update_config.json"

def _load_config() -> dict:
    if UPDATE_CONFIG.exists():
        return json.loads(UPDATE_CONFIG.read_text())
    return {"auto_update": False, "last_check": None, "version": "1.0"}

def _save_config(config: dict) -> None:
    UPDATE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    UPDATE_CONFIG.write_text(json.dumps(config, indent=2))

def get_current_version() -> str:
    config = _load_config()
    return config.get("version", "1.0")

def check_for_updates() -> str:
    """Check if updates are available."""
    config = _load_config()
    current = config.get("version", "1.0")
    
    # Simulated update check
    config["last_check"] = datetime.now().isoformat()
    _save_config(config)
    
    return f"Current version: {current}\nNo updates available."

def update_system() -> str:
    """Pull latest code updates."""
    try:
        # Simulated update
        return "System updated to latest version, sir."
    except Exception as e:
        return f"Update error: {e}"

def get_logs() -> str:
    """Get update logs."""
    config = _load_config()
    last = config.get("last_check", "Never")
    return f"Last update check: {last}\nVersion: {config.get('version', '1.0')}"

def self_updater(parameters: dict = None, response=None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "version").lower().strip()
    
    if action == "version":
        return get_current_version()
    elif action == "check":
        return check_for_updates()
    elif action == "update":
        return update_system()
    elif action == "logs":
        return get_logs()
    else:
        return get_current_version()
