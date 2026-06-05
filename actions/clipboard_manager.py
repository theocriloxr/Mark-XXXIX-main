# clipboard_manager.py
"""
Clipboard Manager - Enhanced clipboard with history.
Part of enhanced JARVIS system.
"""

import pyperclip
import json
from pathlib import Path
from datetime import datetime
from threading import Lock

try:
    import pyperclip
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False


# Clipboard history storage
ClipboardHistory = []
_MAX_HISTORY = 50
_history_lock = Lock()


def get_clipboard() -> str:
    """Get current clipboard content."""
    if _PYPERCLIP:
        return pyperclip.paste()
    return ""


def set_clipboard(text: str) -> str:
    """Set clipboard content."""
    if _PYPERCLIP:
        pyperclip.copy(text)
        _add_to_history(text)
        return "Copied to clipboard."
    return "pyperclip not available"


def _add_to_history(text: str):
    """Add text to clipboard history."""
    if not text or len(text) < 3:
        return
    
    with _history_lock:
        # Avoid duplicates
        for i, item in enumerate(ClipboardHistory):
            if item["text"] == text:
                ClipboardHistory.pop(i)
                break
        
        ClipboardHistory.insert(0, {
            "text": text,
            "time": datetime.now().isoformat()
        })
        
        # Trim history
        while len(ClipboardHistory) > _MAX_HISTORY:
            ClipboardHistory.pop()


def search_clipboard(query: str = "") -> str:
    """Search clipboard history."""
    if not query:
        return f"History: {len(ClipboardHistory)} items"
    
    query = query.lower()
    results = []
    
    for i, item in enumerate(ClipboardHistory):
        if query in item["text"].lower():
            results.append(f"{i}: {item['text'][:80]}...")
    
    if not results:
        return f"No matches for: {query}"
    
    return "\n".join(results[:10])


def clear_clipboard() -> str:
    """Clear clipboard history."""
    global ClipboardHistory
    with _history_lock:
        ClipboardHistory.clear()
    return "Clipboard history cleared"


def clipboard_manager(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for clipboard manager."""
    params = parameters or {}
    action = params.get("action", "get").lower().strip()
    
    try:
        if action == "get":
            return get_clipboard()[:500]
        
        elif action == "set":
            text = params.get("text", "")
            if text:
                return set_clipboard(text)
            return "No text provided."
        
        elif action == "search":
            return search_clipboard(params.get("query", ""))
        
        elif action == "clear":
            return clear_clipboard()
        
        elif action == "history":
            return f"History: {len(ClipboardHistory)} items"
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Clipboard error: {e}"
