# clipboard_manager.py
"""
Enhanced Clipboard Manager with history and search
"""

import json
import os
import sys
import threading
from pathlib import Path

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
CLIPBOARD_FILE = BASE_DIR / "memory" / "clipboard_history.json"

_MAX_HISTORY = 50

def _load_history() -> list:
    if CLIPBOARD_FILE.exists():
        try:
            return json.loads(CLIPBOARD_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return []

def _save_history(history: list) -> None:
    CLIPBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    CLIPBOARD_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")

def _add_to_history(text: str, label: str = "") -> None:
    history = _load_history()
    entry = {"text": text, "label": label}
    history.insert(0, entry)
    history = history[:_MAX_HISTORY]
    _save_history(history)

def clipboard_manager(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "get").lower().strip()
    
    try:
        import pyperclip
        _HAS_PYPERCLIP = True
    except:
        _HAS_PYPERCLIP = False
    
    if action == "set":
        text = params.get("text", "")
        label = params.get("label", "")
        if _HAS_PYPERCLIP:
            pyperclip.copy(text)
        _add_to_history(text, label)
        return f"Clipboard set: {text[:50]}{'...' if len(text) > 50 else ''}"
    
    elif action == "get":
        if _HAS_PYPERCLIP:
            text = pyperclip.paste()
            return f"Current: {text[:100]}{'...' if len(text) > 100 else ''}"
        return "Clipboard read unavailable."
    
    elif action == "search":
        query = params.get("query", "").lower()
        history = _load_history()
        results = [h for h in history if query in h.get("text", "").lower()]
        if results:
            lines = [f"Found {len(results)}:"]
            for h in results[:10]:
                label = h.get("label", "")
                text = h.get("text", "")[:50]
                lines.append(f"  {'['+label+']' if label else ''} {text}")
            return "\n".join(lines)
        return f"No matches for: {query}"
    
    elif action == "history":
        history = _load_history()
        if not history:
            return "No clipboard history."
        lines = ["Clipboard history:"]
        for i, h in enumerate(history[:20]):
            label = h.get("label", "")
            text = h.get("text", "")[:40]
            lines.append(f"  {i+1}. {'['+label+']' if label else ''} {text}")
        return "\n".join(lines)
    
    elif action == "clear":
        _save_history([])
        return "Clipboard history cleared."
    
    else:
        return f"Unknown action: {action}"
