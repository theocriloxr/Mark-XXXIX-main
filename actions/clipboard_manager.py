# clipboard_manager.py - Enhanced clipboard with history and AI
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

try:
    import pyperclip
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
HISTORY_FILE = BASE_DIR / "memory" / "clipboard_history.json"
MAX_HISTORY = 50

def _load_history() -> List[dict]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except:
            return []
    return []

def _save_history(history: List[dict]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Keep only last MAX_HISTORY
    history = history[-MAX_HISTORY:]
    HISTORY_FILE.write_text(json.dumps(history, indent=2))

def _add_to_history(content: str, clip_type: str = "text") -> None:
    history = _load_history()
    entry = {
        "content": content[:500],  # Limit size
        "type": clip_type,
        "timestamp": datetime.now().isoformat()
    }
    history.append(entry)
    _save_history(history)

def get_clipboard() -> str:
    """Get current clipboard."""
    if _PYPERCLIP:
        try:
            content = pyperclip.paste()
            if content:
                return content
        except:
            pass
    return "Clipboard empty."

def set_clipboard(text: str) -> str:
    """Set clipboard."""
    if _PYPERCLIP:
        pyperclip.copy(text)
        _add_to_history(text)
        return f"Copied to clipboard: {text[:50]}..."
    return "pyperclip not available"

def get_history(search: str = "", limit: int = 10) -> str:
    """Get clipboard history."""
    history = _load_history()
    
    if search:
        history = [h for h in history if search.lower() in h.get("content", "").lower()]
    
    if not history:
        return "No clipboard history."
    
    lines = ["Clipboard History:"]
    for h in history[-limit:]:
        content = h.get("content", "")[:50]
        ts = h.get("timestamp", "")[:19]
        lines.append(f"  [{ts}] {content}...")
    
    return "\n".join(lines)

def clear_history() -> str:
    """Clear clipboard history."""
    _save_history([])
    return "Clipboard history cleared."

def clipboard_manager(parameters: dict = None, response=None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "get").lower().strip()
    
    if action == "get":
        return get_clipboard()
    elif action == "set":
        return set_clipboard(params.get("text", ""))
    elif action == "history":
        return get_history(
            params.get("search", ""),
            int(params.get("limit", 10))
        )
    elif action == "clear":
        return clear_history()
    else:
        return get_clipboard()
