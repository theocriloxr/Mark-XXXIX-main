# context_aware.py - Context awareness for enhanced sentience
"""
JARVIS Context Awareness Module
Tracks current context, active applications, project awareness,
time-based context, and provides proactive assistance.
"""

import json
import os
import platform
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

_OS = platform.system().lower()


class ContextState:
    def __init__(self):
        self._lock = threading.Lock()
        self._current_app: str = ""
        self._current_project: str = ""
        self._last_activity: str = ""
        self._activity_time: float = 0
        self._user_state: str = "unknown"  # working, idle, sleeping, meeting
        self._time_context: str = ""
        self._learned_patterns: dict = {}
        self._load_patterns()
    
    def _load_patterns(self):
        try:
            config = _get_config_dir() / "patterns.json"
            if config.exists():
                self._learned_patterns = json.loads(config.read_text())
        except:
            pass
    
    def _save_patterns(self):
        try:
            config = _get_config_dir()
            config.mkdir(parents=True, exist_ok=True)
            (config / "patterns.json").write_text(json.dumps(self._learned_patterns, indent=2))
        except:
            pass
    
    def _get_config_dir() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent / "config"
        return Path(__file__).resolve().parent.parent / "config"


import sys

def _get_config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config"
    return Path(__file__).resolve().parent.parent / "config"


def get_current_app() -> str:
    """Detect the currently active application."""
    try:
        if _OS == "windows":
            import ctypes
            from ctypes import wintypes
            
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.UINT),
                    ("dwTime", wintypes.DWORD),
                ]
            
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            elapsed = (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000
            
            # Get foreground window
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length:
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value
            return ""
        elif _OS == "darwin":
            result = subprocess.run(
                ["osascript", "-e", 'tell app "System Events" to get name of first process whose frontmost is true'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
        else:
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
    except:
        return ""


def detect_current_project() -> str:
    """Detect if user is in a coding project."""
    try:
        home = Path.home()
        # Check common project directories
        project_paths = [
            home / "Desktop",
            home / "Documents",
            home / "Projects",
            home / "Code",
            home / "workspace",
        ]
        
        for path in project_paths:
            if not path.exists():
                continue
            # Check for common project files
            indicators = [".git", "package.json", "Cargo.toml", "requirements.txt", "pyproject.toml", "Makefile"]
            for item in path.iterdir():
                if item.is_dir() and item.name in (".git", "node_modules", "venv", "__pycache__"):
                    continue
                if item.name in indicators:
                    return f"Project: {item.parent.name}"
        return ""
    except:
        return ""


def get_time_context() -> str:
    """Get time-based context (morning, work hours, evening, etc.)."""
    hour = datetime.now().hour
    
    if 5 <= hour < 9:
        return "morning_early"
    elif 9 <= hour < 12:
        return "morning_work"
    elif 12 <= hour < 13:
        return "lunch_time"
    elif 13 <= hour < 17:
        return "afternoon_work"
    elif 17 <= hour < 21:
        return "evening"
    elif 21 <= hour < 23:
        return "night"
    else:
        return "late_night"


def get_user_state() -> str:
    """Determine user state based on activity."""
    state = ContextState()
    time_since = time.time() - state._activity_time
    
    if time_since < 60:
        return "active"
    elif time_since < 300:
        return "idle"
    else:
        return "away"


def update_activity(activity: str):
    """Update the current activity."""
    state = ContextState()
    with state._lock:
        state._last_activity = activity
        state._activity_time = time.time()


def learn_pattern(action: str, outcome: str):
    """Learn a pattern from user behavior."""
    state = ContextState()
    if action not in state._learned_patterns:
        state._learned_patterns[action] = []
    state._learned_patterns[action].append({
        "outcome": outcome,
        "timestamp": time.time()
    })
    state._save_patterns()


def get_suggestion() -> Optional[str]:
    """Get proactive suggestion based on context."""
    state = ContextState()
    time_ctx = get_time_context()
    project = detect_current_project()
    
    suggestions = []
    
    # Time-based suggestions
    if time_ctx == "morning_early":
        suggestions.append("Good morning! Would you like me to check your schedule for today?")
    elif time_ctx == "evening":
        suggestions.append("It's evening. Would you like me to set a reminder for tomorrow?")
    
    # Project-based suggestions
    if project and "Project:" in project:
        suggestions.append(f"You're working on a project. Want me to check for updates or run tests?")
    
    if suggestions:
        return suggestions[0]
    return None


def get_full_context() -> str:
    """Get complete context summary."""
    app = get_current_app()
    project = detect_current_project()
    time_ctx = get_time_context()
    
    parts = []
    if app:
        parts.append(f"App: {app}")
    if project:
        parts.append(project)
    parts.append(f"Time: {time_ctx}")
    
    return " | ".join(parts) if parts else "No context available"


# Global context state
_context_state = None


def get_context_state() -> ContextState:
    global _context_state
    if _context_state is None:
        _context_state = ContextState()
    return _context_state


def context_aware(parameters: dict = None, response=None, player=None) -> str:
    """Main dispatcher for context awareness."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if action == "status":
        return get_full_context()
    elif action == "app":
        return get_current_app() or "Unknown"
    elif action == "project":
        return detect_current_project() or "None detected"
    elif action == "time":
        return get_time_context()
    elif action == "suggest":
        return get_suggestion() or "No suggestions"
    elif action == "learn":
        learn_pattern(params.get("action", params.get("outcome", ""))
        return "Pattern learned"
    else:
        return get_full_context()
