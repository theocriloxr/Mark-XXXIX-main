# wake_word.py - Custom wake word detection and always-listening mode
import json
import os
import sys
import threading
import time
from pathlib import Path
from datetime import datetime

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
CONFIG_PATH = BASE_DIR / "config" / "wakeword_config.json"

# Default wake word settings
DEFAULT_CONFIG = {
    "enabled": True,
    "wake_word": "jarvis",
    "always_listening": True,
    "sensitivity": 0.6,
    "soundfeedback": True,
}

_config = {}
_listening = False
_callback = None

def _load_config() -> dict:
    """Load wake word configuration."""
    global _config
    if CONFIG_PATH.exists():
        try:
            _config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except:
            _config = dict(DEFAULT_CONFIG)
    else:
        _config = dict(DEFAULT_CONFIG)
    return _config

def _save_config(config: dict) -> None:
    """Save wake word configuration."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")

def set_wake_word(word: str) -> str:
    """Set custom wake word."""
    config = _load_config()
    config["wake_word"] = word.lower().strip()
    _save_config(config)
    return f"Wake word set to: {word}"

def get_status() -> str:
    """Get current wake word status."""
    config = _load_config()
    return (
        f"Wake Word Status:\n"
        f"  Wake Word: {config.get('wake_word', 'jarvis')}\n"
        f"  Always Listening: {config.get('always_listening', True)}\n"
        f"  Enabled: {config.get('enabled', True)}\n"
        f"  Sensitivity: {config.get('sensitivity', 0.6)}"
    )

def toggle_listening(enable: bool = True) -> str:
    """Toggle always-listening mode."""
    global _listening
    config = _load_config()
    config["always_listening"] = enable
    _save_config(config)
    _listening = enable
    if enable:
        return "Always-listening mode enabled. I'm always listening, sir."
    return "Always-listening mode disabled."

def set_callback(callback_func) -> None:
    """Set callback for wake word detection."""
    global _callback
    _callback = callback_func

def wake_word(parameters: dict = None, response=None, player=None) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    config = _load_config()
    
    if action == "set":
        return set_wake_word(params.get("word", "jarvis"))
    elif action == "status":
        return get_status()
    elif action == "listen":
        return toggle_listening(params.get("enable", True))
    elif action == "enable":
        config["enabled"] = True
        _save_config(config)
        return "Wake word enabled."
    elif action == "disable":
        config["enabled"] = False
        _save_config(config)
        return "Wake word disabled."
    else:
        return get_status()
