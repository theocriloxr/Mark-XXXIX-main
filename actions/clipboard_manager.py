# clipboard_manager.py
"""
Clipboard Manager - Enhanced clipboard with history and AI memory.
"""

import json
import os
import sys
import time
from pathlib import Path
from threading import Lock
from collections import deque


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
HISTORY_FILE = BASE_DIR / "config" / "clipboard_history.json"
_max_history = 50
_lock = Lock()


def _load_history() -> list:
    """Load clipboard history."""
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except:
        return []


def _save_history(history: list) -> None:
    """Save clipboard history."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        HISTORY_FILE.write_text(
json.dumps(history[-_max_history:], indent=2, ensure_ascii=False)
        )


def get_clipboard() -> str:
    """Get current clipboard content."""
    try:
        import pyperclip
        return pyperclip.paste()
    except:
        return "Clipboard access not available."


def copy_to_clipboard(text: str) -> str:
    """Copy text to clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        _add_to_history(text)
        return "Copied to clipboard."
    except Exception as e:
        return f"Copy failed: {e}"


def _add_to_history(text: str) -> None:
    """Add to clipboard history."""
    if not text or len(text) < 2:
        return
    
    history = _load_history()
    history.append({
        "text": text[:500],
        "timestamp": time.time()
    })
    _save_history(history)


def get_history(search: str = "", limit: int = 10) -> str:
    """Get clipboard history."""
    history = _load_history()
    
    if search:
        history = [h for h in history if search.lower() in h.get("text", "").lower()]
    
    if not history:
        return "No clipboard history."
    
    lines = ["Clipboard History:"]
    for h in history[-limit:]:
        ts = time.ctime(h.get("timestamp", 0))
        text = h.get("text", "")[:100]
        lines.append(f"  [{ts}] {text}")
    
    return "\n".join(lines)


def clear_history() -> str:
    """Clear clipboard history."""
    _save_history([])
    return "Clipboard history cleared."


def clipboard_manager(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "get").lower().strip()
    
    if player:
        player.write_log(f"[clipboard] {action}")
    
    try:
        if action == "get":
            return get_clipboard()
        elif action == "copy":
            return copy_to_clipboard(params.get("text", ""))
        elif action == "history":
            return get_history(
                params.get("search", ""),
                int(params.get("limit", 10))
            )
        elif action == "clear":
            return clear_history()
        else:
            return get_clipboard()
    except Exception as e:
        return f"Clipboard error: {e}"
