# clipboard_manager.py
"""
Enhanced Clipboard Manager with history and search.
Part of enhanced JARVIS system.
"""

import json
import threading
from pathlib import Path
import sys
from datetime import datetime

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
HISTORY_FILE = BASE_DIR / "memory" / "clipboard_history.json"
MAX_HISTORY = 50
_lock = threading.Lock()

# In-memory clipboard history
_clipboard_history = []
_current_clipboard = ""


def _load_history() -> list:
    """Load clipboard history from file."""
    global _clipboard_history
    if HISTORY_FILE.exists():
        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                _clipboard_history = data[-MAX_HISTORY:]
        except:
            _clipboard_history = []


def _save_history() -> None:
    """Save clipboard history to file."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        HISTORY_FILE.write_text(
            json.dumps(_clipboard_history, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def set_clipboard(text: str, label: str = "") -> str:
    """Set clipboard content and save to history."""
    global _current_clipboard
    
    try:
        import pyperclip
        pyperclip.copy(text)
    except:
        # Fallback: use pyautogui or other method
        try:
            import pyautogui
            pyautogui.write(text)
        except:
            return "Failed to set clipboard: no clipboard library available"
    
    _current_clipboard = text
    
    # Add to history
    entry = {
        "text": text[:500] if len(text) > 500 else text,
        "label": label,
        "timestamp": datetime.now().isoformat()
    }
    
    with _lock:
        _clipboard_history.append(entry)
        if len(_clipboard_history) > MAX_HISTORY:
            _clipboard_history = _clipboard_history[-MAX_HISTORY:]
    
    _save_history()
    return f"Clipboard set ({len(text)} chars)"


def get_clipboard() -> str:
    """Get current clipboard content."""
    global _current_clipboard
    
    try:
        import pyperclip
        _current_clipboard = pyperclip.paste()
        return _current_clipboard
    except:
        try:
            import pyautogui
            pyautogui.hotkey("ctrl", "c")
            import time
            time.sleep(0.1)
        except:
            pass
    
    return _current_clipboard or "Clipboard empty"


def search_history(query: str) -> str:
    """Search clipboard history."""
    _load_history()
    
    results = []
    query_lower = query.lower()
    
    for entry in reversed(_clipboard_history):
        text = entry.get("text", "")
        label = entry.get("label", "")
        
        if query_lower in text.lower() or query_lower in label.lower():
            results.append(entry)
    
    if not results:
        return f"No matches found for: {query}"
    
    lines = [f"Found {len(results)} matches:"]
    for i, entry in enumerate(results[:10], 1):
        label = entry.get("label", "no label")
        text = entry.get("text", "")[:60]
        ts = entry.get("timestamp", "")[:16]
        lines.append(f"{i}. [{label}] {text}... ({ts})")
    
    return "\n".join(lines)


def get_history(count: int = 10) -> str:
    """Get clipboard history."""
    _load_history()
    
    if not _clipboard_history:
        return "No clipboard history"
    
    lines = ["Clipboard History:"]
    for i, entry in enumerate(_clipboard_history[-count:], 1):
        label = entry.get("label", "")
        text = entry.get("text", "")[:60]
        ts = entry.get("timestamp", "")[:16]
        lines.append(f"{i}. {text}... - [{label}] ({ts})")
    
    return "\n".join(lines)


def clear_history() -> str:
    """Clear clipboard history."""
    global _clipboard_history
    with _lock:
        _clipboard_history = []
    _save_history()
    return "Clipboard history cleared"


def clipboard_manager(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for clipboard manager."""
    params = parameters or {}
    action = params.get("action", "get").lower().strip()
    
    if player:
        player.write_log(f"[clipboard] {action}")
    
    try:
        if action == "set":
            return set_clipboard(
                params.get("text", ""),
                params.get("label", "")
            )
        elif action == "get":
            return get_clipboard()
        elif action == "search":
            return search_history(params.get("query", ""))
        elif action == "history":
            return get_history(int(params.get("count", 10)))
        elif action == "clear":
            return clear_history()
        else:
            return get_clipboard()
    except Exception as e:
        return f"Clipboard error: {e}"
