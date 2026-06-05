# wake_word.py
"""
Wake Word Detection - Custom wake word with always-listening mode.
Part of enhanced JARVIS system for hands-free activation.
"""

import json
from pathlib import Path
import threading
import time
import audioop
import wave

# Configuration storage
_WAKE_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "wake_word.json"

# Default wake word
DEFAULT_WAKE_WORD = "jarvis"

# Current configuration
_wake_config = {
    "enabled": True,
    "wake_word": DEFAULT_WAKE_WORD,
    "always_listen": False,
    "sensitivity": 0.6
}


def _load_config():
    """Load wake word configuration."""
    global _wake_config
    try:
        if _WAKE_CONFIG_PATH.exists():
            _wake_config = json.loads(_WAKE_CONFIG_PATH.read_text())
    except:
        pass


def _save_config():
    """Save wake word configuration."""
    try:
        _WAKE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _WAKE_CONFIG_PATH.write_text(json.dumps(_wake_config, indent=2))
    except Exception as e:
        print(f"[WakeWord] Config save error: {e}")


def set_wake_word(word: str) -> str:
    """Set custom wake word."""
    global _wake_config
    _wake_config["wake_word"] = word.lower()
    _save_config()
    return f"Wake word set to: {word}"


def get_status() -> str:
    """Get wake word status."""
    _load_config()
    return (
        f"Wake Word: {_wake_config.get('wake_word', DEFAULT_WAKE_WORD)}\n"
        f"Enabled: {_wake_config.get('enabled', True)}\n"
        f"Always Listen: {_wake_config.get('always_listen', False)}"
    )


def enable_always_listen(enable: bool = True) -> str:
    """Enable/disable always listening mode."""
    global _wake_config
    _wake_config["always_listen"] = enable
    _save_config()
    return f"Always listening: {'enabled' if enable else 'disabled'}"


def wake_word(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for wake word actions."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    try:
        if action == "set":
            return set_wake_word(params.get("word", "jarvis"))
        
        elif action == "status":
            return get_status()
        
        elif action == "always_on":
            return enable_always_listen(True)
        
        elif action == "always_off":
            return enable_always_listen(False)
        
        elif action == "enable":
            _wake_config["enabled"] = True
            _save_config()
            return "Wake word enabled."
        
        elif action == "disable":
            _wake_config["enabled"] = False
            _save_config()
            return "Wake word disabled."
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Wake word error: {e}"
