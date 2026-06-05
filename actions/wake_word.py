# wake_word.py
"""
Wake Word Configuration - Enable always-listening mode with custom wake word
"""

import json
import os
import sys
from pathlib import Path

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
CONFIG_FILE = BASE_DIR / "config" / "wake_word.json"

def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"word": "JARVIS", "enabled": True, "mode": "passive"}

def _save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")

def wake_word(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if action == "status" or action == "get":
        config = _load_config()
        return (
            f"Wake Word: '{config.get('word', 'JARVIS')}' | "
            f"Enabled: {config.get('enabled', True)} | "
            f"Mode: {config.get('mode', 'passive')}"
        )
    
    elif action == "set":
        word = params.get("word", "").strip()
        if word:
            config = _load_config()
            config["word"] = word
            _save_config(config)
            return f"Wake word set to: '{word}'"
        return "Specify word parameter."
    
    elif action in ("enable", "disable"):
        enabled = (action == "enable")
        config = _load_config()
        config["enabled"] = enabled
        _save_config(config)
        return f"Wake word {'enabled' if enabled else 'disabled'}."
    
    elif action == "mode":
        mode = params.get("mode", "passive").lower()
        if mode in ("active", "passive"):
            config = _load_config()
            config["mode"] = mode
            _save_config(config)
            return f"Mode set to: {mode}"
        return "Invalid mode. Use 'active' or 'passive'."
    
    else:
        return f"Unknown action: {action}"
