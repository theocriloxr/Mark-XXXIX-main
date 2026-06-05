# wake_word.py
"""
Wake Word Configuration - Always listening mode and custom wake word.
"""

import json
import sys
from pathlib import Path
from threading import Lock


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
CONFIG_FILE = BASE_DIR / "config" / "wake_word.json"
_lock = Lock()

# Default wake word
DEFAULT_WAKE_WORD = "jarvis"


def _load_config() -> dict:
    """Load wake word configuration."""
    if not CONFIG_FILE.exists():
        return {"enabled": True, "word": DEFAULT_WAKE_WORD, "mode": "active"}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except:
        return {"enabled": True, "word": DEFAULT_WAKE_WORD, "mode": "active"}


def _save_config(config: dict) -> None:
    """Save wake word configuration."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def set_wake_word(word: str) -> str:
    """Set custom wake word."""
    config = _load_config()
    config["word"] = word.lower().strip()
    _save_config(config)
    return f"Wake word set to: {word}"


def get_wake_word() -> str:
    """Get current wake word."""
    config = _load_config()
    return config.get("word", DEFAULT_WAKE_WORD)


def enable_listening() -> str:
    """Enable always listening mode."""
    config = _load_config()
    config["enabled"] = True
    _save_config(config)
    return "Always listening enabled."


def disable_listening() -> str:
    """Disable always listening mode."""
    config = _load_config()
    config["enabled"] = False
    _save_config(config)
    return "Always listening disabled."


def get_status() -> str:
    """Get wake word status."""
    config = _load_config()
    word = config.get("word", DEFAULT_WAKE_WORD)
    enabled = config.get("enabled", True)
    mode = config.get("mode", "active")
    return f"Wake Word: '{word}' | Listening: {enabled} | Mode: {mode}"


def wake_word(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for wake word configuration."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[wake_word] {action}")
    
    try:
        if action == "set":
            word = params.get("word", "jarvis")
            if not word:
                return "Please specify a wake word."
            return set_wake_word(word)
        elif action == "get":
            return get_wake_word()
        elif action == "enable":
            return enable_listening()
        elif action == "disable":
            return disable_listening()
        elif action == "status":
            return get_status()
        else:
            return get_status()
    except Exception as e:
        return f"Wake word error: {e}"
