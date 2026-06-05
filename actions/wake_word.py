# wake_word.py
"""
Wake Word System - Custom wake word detection with always-listening mode.
Enhanced JARVIS system for voice activation control.
"""

import json
import threading
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
CONFIG_FILE = BASE_DIR / "config" / "wake_config.json"

# Default wake words - user can customize
DEFAULT_WAKE_WORDS = ["hey jarvis", "okay jarvis", "jarvis"]

# Current wake word configuration
_wake_word_config = {
    "enabled": True,
    "wake_words": DEFAULT_WAKE_WORDS,
    "always_listen": False,  # Enable always-listening mode
    "sensitivity": 0.8,
    "timeout_seconds": 30,  # Timeout for continuous listening
}

# State
_is_listening = False
_last_wake_time = 0
_wake_event: Optional[threading.Event] = None
_listen_callback: Optional[Callable] = None


def _load_config() -> dict:
    """Load wake word configuration."""
    global _wake_word_config
    
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            _wake_word_config.update(data)
        except:
            pass
    
    return _wake_word_config


def _save_config() -> None:
    """Save wake word configuration."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(_wake_word_config, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def set_wake_word(wake_word: str) -> str:
    """Set custom wake word."""
    global _wake_word_config
    
    # Clean and validate
    word = wake_word.lower().strip()
    
    if len(word) < 2:
        return "Wake word too short (minimum 2 characters)"
    
    if len(word) > 20:
        return "Wake word too long (maximum 20 characters)"
    
    # Add to wake words list
    if word not in _wake_word_config["wake_words"]:
        _wake_word_config["wake_words"].append(word)
    
    _save_config()
    
    return f"Wake word set to: '{word}'"


def get_wake_words() -> str:
    """Get current wake words."""
    _load_config()
    
    words = _wake_word_config["wake_words"]
    always = _wake_word_config.get("always_listen", False)
    
    lines = [
        f"Configured wake words ({len(words)}):",
        f"  • " + "\n  • ".join(words),
        f"Always listening: {'ENABLED' if always else 'DISABLED'}"
    ]
    
    return "\n".join(lines)


def enable_always_listen(enable: bool = True, timeout: int = 30) -> str:
    """Enable or disable always-listening mode."""
    global _wake_word_config
    
    _load_config()
    _wake_word_config["always_listen"] = enable
    _wake_word_config["timeout_seconds"] = timeout
    
    _save_config()
    
    if enable:
        return f"Always-listening enabled (timeout: {timeout}s)"
    else:
        return "Always-listening disabled"


def set_sensitivity(level: float) -> str:
    """Set wake word sensitivity (0.1-1.0)."""
    global _wake_word_config
    
    sensitivity = max(0.1, min(1.0, float(level)))
    
    _load_config()
    _wake_word_config["sensitivity"] = sensitivity
    
    _save_config()
    
    return f"Sensitivity set to {sensitivity:.1f}"


def check_wake_word(audio_text: str) -> bool:
    """
    Check if audio/text contains a wake word.
    Called by the main audio processing loop.
    """
    _load_config()
    
    if not _wake_word_config.get("enabled", True):
        return False
    
    global _last_wake_time
    
    text_lower = audio_text.lower()
    
    # Check for any configured wake word
    for wake_word in _wake_word_config.get("wake_words", []):
        if wake_word in text_lower:
            _last_wake_time = time.time()
            return True
    
    # Check if in always-listen mode
    if _wake_word_config.get("always_listen", False):
        timeout = _wake_word_config.get("timeout_seconds", 30)
        
        # If recently triggered, stay active
        if time.time() - _last_wake_time < timeout:
            return True
    
    return False


def start_listening(callback: Optional[Callable] = None) -> str:
    """Start always-listening mode with callback."""
    global _is_listening, _listen_callback, _wake_event
    
    _load_config()
    
    if not _wake_word_config.get("enabled", True):
        return "Wake words are disabled"
    
    _is_listening = True
    _listen_callback = callback
    _wake_event = threading.Event()
    _wake_event.set()
    
    return "Started listening for wake word..."


def stop_listening() -> str:
    """Stop always-listening mode."""
    global _is_listening, _wake_event
    
    _is_listening = False
    
    if _wake_event:
        _wake_event.clear()
    
    return "Stopped listening"


def get_status() -> str:
    """Get wake word system status."""
    _load_config()
    
    lines = [
        "Wake Word System Status:",
        f"  Enabled: {_wake_word_config.get('enabled', True)}",
        f"  Always Listen: {_wake_word_config.get('always_listen', False)}",
        f"  Timeout: {_wake_word_config.get('timeout_seconds', 30)}s",
        f"  Sensitivity: {_wake_word_config.get('sensitivity', 0.8)}",
        f"  Words: {', '.join(_wake_word_config.get('wake_words', []))}"
    ]
    
    return "\n".join(lines)


def wake_word(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for wake word system."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[wake] {action}")
    
    try:
        if action == "set":
            return set_wake_word(params.get("wake_word", ""))
        elif action == "words":
            return get_wake_words()
        elif action == "enable":
            return enable_always_listen(True, int(params.get("timeout", 30)))
        elif action == "disable":
            return enable_always_listen(False)
        elif action == "sensitivity":
            return set_sensitivity(float(params.get("level", 0.8)))
        elif action == "start":
            return start_listening()
        elif action == "stop":
            return stop_listening()
        elif action == "status":
            return get_status()
        else:
            return get_status()
    except Exception as e:
        return f"Wake word error: {e}"
