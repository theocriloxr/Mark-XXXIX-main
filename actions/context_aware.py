# context_aware.py
"""
Context Awareness - JARVIS understands current context and can be proactive.
Enhanced sentience module for better user assistance.
"""

import json
import platform
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
from collections import deque

def _get_base_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
CONTEXT_FILE = BASE_DIR / "memory" / "context.json"


# Context tracking
class ContextTracker:
    def __init__(self):
        self.current_context: dict = {}
        self.context_history: deque = deque(maxlen=50)
        self.active_app: str = ""
        self.current_project: str = ""
        self.last_interaction: float = time.time()
        self.user_mood: str = "neutral"
        self.time_context: str = ""  # morning, afternoon, evening, night
        self.work_mode: bool = False
        
    def update_time_context(self):
        """Update time-based context."""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            self.time_context = "morning"
        elif 12 <= hour < 17:
            self.time_context = "afternoon"
        elif 17 <= hour < 21:
            self.time_context = "evening"
        else:
            self.time_context = "night"
        
        # Work hours (9-5 weekdays)
        self.work_mode = 9 <= hour < 17 and datetime.now().weekday() < 5
    
    def update_from_audio(self, transcript: str):
        """Update context from user's voice input."""
        text_lower = transcript.lower()
        
        # Detect emotions/patterns
        if any(w in text_lower for w in ["happy", "great", "awesome", "excellent"]):
            self.user_mood = "happy"
        elif any(w in text_lower for w in ["angry", "frustrated", "annoyed"]):
            self.user_mood = "frustrated"
        elif any(w in text_lower for w in ["tired", "exhausted", "sleepy"]):
            self.user_mood = "tired"
        else:
            self.user_mood = "neutral"
        
        self.last_interaction = time.time()
        
        # Add to history
        self.context_history.append({
            "transcript": transcript,
            "mood": self.user_mood,
            "timestamp": time.time()
        })
    
    def detect_project(self, path: str) -> str:
        """Detect if user is working on a project."""
        target = Path(path)
        
        # Check for common project markers
        project_indicators = {
            "git": ".git",
            "node_modules": "node_modules",
            "package.json": "package.json",
            "requirements.txt": "requirements.txt",
            "Cargo.toml": "rust",
            "go.mod": "go",
            ".venv": "python",
            "venv": "python",
        }
        
        for indicator, proj_type in project_indicators.items():
            if (target / indicator).exists():
                self.current_project = f"{proj_type} project"
                return self.current_project
        
        # Check parent directories
        for parent in target.parents:
            for indicator, proj_type in project_indicators.items():
                if (parent / indicator).exists():
                    self.current_project = f"{proj_type} project at {parent.name}"
                    return self.current_project
        
        self.current_project = ""
        return ""
    
    def get_greeting(self) -> str:
        """Get appropriate greeting based on context."""
        greeting = f"Good {self.time_context}"
        
        if self.user_mood == "happy":
            greeting += "! You seem to be in great spirits!"
        elif self.user_mood == "frustrated":
            greeting += ". How can I help take some pressure off?"
        elif self.user_mood == "tired":
            greeting += ". Let me keep things efficient for you."
        
        if self.work_mode and self.time_context == "morning":
            greeting += " Ready to start the workday."
        
        return greeting
    
    def to_dict(self) -> dict:
        return {
            "time_context": self.time_context,
            "work_mode": self.work_mode,
            "user_mood": self.user_mood,
            "active_app": self.active_app,
            "current_project": self.current_project,
            "last_interaction": self.last_interaction,
        }


# Global tracker
_tracker = ContextTracker()


def get_context() -> str:
    """Get current context summary."""
    _tracker.update_time_context()
    ctx = _tracker.to_dict()
    
    lines = [
        "Current Context:",
        f"  Time: {ctx['time_context']} ({'work mode' if ctx['work_mode'] else 'personal'})",
        f"  Mood: {ctx['user_mood']}",
        f"  Project: {ctx['current_project'] or 'None detected'}",
        f"  Active: {ctx['active_app'] or 'Unknown'}",
    ]
    
    return "\n".join(lines)


def set_active_app(app_name: str) -> str:
    """Set the currently active application."""
    _tracker.active_app = app_name
    return f"Active app set to: {app_name}"


def get_suggestion() -> str:
    """Get proactive suggestion based on context."""
    _tracker.update_time_context()
    
    suggestions = []
    
    # Time-based suggestions
    if _tracker.time_context == "morning":
        suggestions.append("Good morning! Want me to check your schedule?")
    
    # Work mode suggestions
    if _tracker.work_mode:
        suggestions.append("You're in work hours - prioritizing tasks?")
    
    # Project-aware suggestions
    if _tracker.current_project:
        if "python" in _tracker.current_project.lower():
            suggestions.append("Need to run any code or tests?")
        elif "git" in _tracker.current_project.lower():
            suggestions.append("Check git status?")
    
    # Long inactivity
    idle_time = time.time() - _tracker.last_interaction
    if idle_time > 300:  # 5 minutes
        suggestions.append("You've been idle - anything I can help with?")
    
    if not suggestions:
        suggestions.append("At your service.")
    
    return " | ".join(suggestions)


def log_interaction(transcript: str) -> str:
    """Log user interaction for context."""
    _tracker.update_from_audio(transcript)
    return "Interaction logged"


def context_aware(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for context awareness."""
    params = parameters or {}
    action = params.get("action", "context").lower().strip()
    
    if player:
        player.write_log(f"[context] {action}")
    
    try:
        if action == "context":
            return get_context()
        elif action == "suggestion":
            return get_suggestion()
        elif action == "app":
            return set_active_app(params.get("app_name", ""))
        elif action == "greeting":
            return _tracker.get_greeting()
        elif action == "log":
            return log_interaction(params.get("transcript", ""))
        elif action == "project":
            return _tracker.detect_project(params.get("path", str(Path.home())))
        else:
            return get_context()
    except Exception as e:
        return f"Context error: {e}"
