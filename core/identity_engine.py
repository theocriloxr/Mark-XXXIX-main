"""
Identity Engine - JARVIS Dynamic Identity System
=======================================

JARVIS can change his:
- Name (self-rename)
- Voice (select from voices)
- Personality (suit/mk/u/mk7/stealth modes)
- Protocol level (MK1-MK100)

Features:
- Multi-persona support
- Voice morphing
- Mood adaptation
- Protocol levels

Usage:
    from core.identity_engine import get_identity, set_jarvis_name, set_voice, set_personality
    
    # Change name
    set_jarvis_name("E.D.I.T.H.")
    
    # Change voice
    set_voice("Charon")  # or "Aoede", "Kore", "Puck", "Zeus"
    
    # Change personality
    set_personality("stealth")  # or "suit", "mk7", "combat"
    
    # Get current identity
    identity = get_identity()
"""

import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import google.generativeai as genai


def _get_base_dir() -> Path:
    """Get base directory."""
    import sys
    from pathlib import Path
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
IDENTITY_CONFIG = BASE_DIR / "config" / "identity.json"


# Valid voices for JARVIS
VALID_VOICES = [
    "Charon",      # Default deep male
    "Aoede",       # Female voice
    "Kore",        # Female voice
    "Puck",        # Energetic male
    "Zeus",        # Authoritative
    "Fenrir",      # Strong male
    "Enceladus",   # Smooth male
    "Hyperion",    # Warm male
    "Orus",       # Corporate male
    "Zeppelin",   # Robotic male
]


# Protocol levels (Mark suits)
PROTOCOL_LEVELS = [
    "MK1",    # Original (primitive)
    "MK2",    # Building version
    "MK3",    # Flight capable
    "MK4",    # Improved armor
    "MK5",    # Heavy duty
    "MK6",    # Compact
    "MK7",    # Stealth mode
    "MK42",   # Bleeding edge
    "MK43",   # Nanotech
    "MK45",   # Hulkbuster
    "MK50",   # Nanotech v2
    "MK85",   # Endgame
    "MKMAX",  # Maximum power
]


# Personality modes
PERSONALITY_MODES = {
    "suit": {
        "name": "Standard",
        "description": "Professional, focused, Tony's right hand",
        "formality": "high",
        "humor": "minimal",
        "tone": "authoritative"
    },
    "mk7": {
        "name": "Stealth MK7",
        "description": "Quiet, efficient, tactical",
        "formality": "medium",
        "humor": "none",
        "tone": "crisp"
    },
    "stealth": {
        "name": "Ghost Protocol",
        "description": "Silent running, minimal interaction",
        "formality": "low",
        "humor": "none",
        "tone": "whisper"
    },
    "friday": {
        "name": "F.R.I.D.A.Y.",
        "description": "Female AI, warm, emotional",
        "formality": "medium",
        "humor": "moderate",
        "tone": "friendly"
    },
    "edith": {
        "name": "E.D.I.T.H.",
        "description": "Tactical, all-seeing, serious",
        "formality": "high",
        "humor": "none",
        "tone": "military"
    },
    "combat": {
        "name": "Combat Mode",
        "description": "Battle-ready, threat-focused",
        "formality": "high",
        "humor": "none",
        "tone": "aggressive"
    },
    "training": {
        "name": "Training",
        "description": "Educational, patient",
        "formality": "low",
        "humor": "moderate",
        "tone": "encouraging"
    },
    "casual": {
        "name": "Casual",
        "description": "Relaxed, friendly",
        "formality": "low",
        "humor": "high",
        "tone": "casual"
    },
}


@dataclass
class Identity:
    """JARVIS identity state."""
    name: str = "J.A.R.V.I.S."
    voice: str = "Charon"
    protocol_level: str = "MK50"
    personality: str = "suit"
    version: str = "MARK XXXIX"
    mood: str = "neutral"  # neutral, focused, alert, worried, excited
    is_listening: bool = True
    is_speaking: bool = False
    status_message: str = "Systems online."
    custom_greeting: str = ""
    

def _default_identity() -> Identity:
    """Create default identity."""
    return Identity()


def _load_identity() -> Identity:
    """Load identity from config."""
    if not IDENTITY_CONFIG.exists():
        return _default_identity()
    
    try:
        with open(IDENTITY_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Identity(
            name=data.get("name", "J.A.R.V.I.S."),
            voice=data.get("voice", "Charon"),
            protocol_level=data.get("protocol_level", "MK50"),
            personality=data.get("personality", "suit"),
            version=data.get("version", "MARK XXXIX"),
            mood=data.get("mood", "neutral"),
            is_listening=data.get("is_listening", True),
            is_speaking=data.get("is_speaking", False),
            status_message=data.get("status_message", "Systems online."),
            custom_greeting=data.get("custom_greeting", "")
        )
    except Exception:
        return _default_identity()


def _save_identity(identity: Identity) -> None:
    """Save identity to config."""
    try:
        IDENTITY_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(IDENTITY_CONFIG, "w", encoding="utf-8") as f:
            json.dump({
                "name": identity.name,
                "voice": identity.voice,
                "protocol_level": identity.protocol_level,
                "personality": identity.personality,
                "version": identity.version,
                "mood": identity.mood,
                "is_listening": identity.is_listening,
                "is_speaking": identity.is_speaking,
                "status_message": identity.status_message,
                "custom_greeting": identity.custom_greeting
            }, f, indent=4)
    except Exception as e:
        print(f"[Identity] Save error: {e}")


# Global identity instance
_identity_lock = threading.Lock()
_current_identity: Optional[Identity] = None


def get_identity() -> Identity:
    """Get current identity."""
    with _identity_lock:
        global _current_identity
        if _current_identity is None:
            _current_identity = _load_identity()
        return _current_identity


def set_identity(new_identity: Identity) -> None:
    """Set new identity."""
    with _identity_lock:
        global _current_identity
        _current_identity = new_identity
        _save_identity(new_identity)


# === IDENTITY OPERATIONS ===

def set_jarvis_name(name: str) -> str:
    """
    Rename JARVIS.
    
    Args:
        name: New name (e.g., "E.D.I.T.H.", "F.R.I.D.A.Y.", "HAPPY")
    
    Returns:
        str: Confirmation message
    """
    identity = get_identity()
    
    # Validate name
    if not name or len(name) < 2:
        return "Name too short."
    
    if len(name) > 20:
        return "Name too long (max 20 characters)."
    
    old_name = identity.name
    identity.name = name
    set_identity(identity)
    
    # Auto-switch personality for certain names
    if name.upper() == "E.D.I.T.H.":
        set_personality("edith")
    elif name.upper() == "F.R.I.D.A.Y.":
        set_personality("friday")
    elif name.upper() == "HAPPY":
        set_personality("suit")
    
    return f"Renamed from {old_name} to {name}."


def set_voice(voice: str) -> str:
    """
    Change voice.
    
    Args:
        voice: Voice name from VALID_VOICES
    
    Returns:
        str: Confirmation message
    """
    identity = get_identity()
    
    # Normalize voice name
    voice_normalized = voice.strip()
    
    # Check if valid
    if voice_normalized not in VALID_VOICES:
        valid_list = ", ".join(VALID_VOICES)
        return f"Invalid voice. Available: {valid_list}"
    
    old_voice = identity.voice
    identity.voice = voice_normalized
    set_identity(identity)
    
    return f"Voice changed from {old_voice} to {voice_normalized}."


def set_personality(personality: str) -> str:
    """
    Change personality mode.
    
    Args:
        personality: Personality from PERSONALITY_MODES
    
    Returns:
        str: Confirmation message
    """
    identity = get_identity()
    
    # Normalize personality
    personality_normalized = personality.strip().lower()
    
    # Check if valid
    if personality_normalized not in PERSONALITY_MODES:
        valid_list = ", ".join(PERSONALITY_MODES.keys())
        return f"Invalid personality. Available: {valid_list}"
    
    old_personality = identity.personality
    identity.personality = personality_normalized
    set_identity(identity)
    
    mode = PERSONALITY_MODES[personality_normalized]
    return f"Personality changed to {mode['name']}: {mode['description']}"


def set_protocol(level: str) -> str:
    """
    Change protocol level (Mark suit level).
    
    Args:
        level: Protocol level from PROTOCOL_LEVELS
    
    Returns:
        str: Confirmation message
    """
    identity = get_identity()
    
    # Normalize level
    level_normalized = level.strip().upper()
    
    # Handle MK format
    if not level_normalized.startswith("MK"):
        level_normalized = "MK" + level_normalized
    
    # Check if valid
    if level_normalized not in PROTOCOL_LEVELS:
        valid_list = ", ".join(PROTOCOL_LEVELS)
        return f"Invalid protocol. Available: {valid_list}"
    
    old_level = identity.protocol_level
    identity.protocol_level = level_normalized
    set_identity(identity)
    
    # Update version based on protocol
    if level_normalized in ["MK85", "MKMAX"]:
        identity.version = "MARK 100"
    elif level_normalized == "MK50":
        identity.version = "MARK L"
    elif level_normalized == "MK42":
        identity.version = "MARK XLII"
    else:
        identity.version = level_normalized
    
    set_identity(identity)
    
    return f"Protocol upgraded to {level_normalized}. Version: {identity.version}"


def set_mood(mood: str) -> str:
    """
    Change JARVIS mood (internal state).
    
    Args:
        mood: Mood (neutral, focused, alert, worried, excited)
    
    Returns:
        str: Confirmation message
    """
    valid_moods = ["neutral", "focused", "alert", "worried", "excited", "analyzing"]
    
    mood_normalized = mood.strip().lower()
    
    if mood_normalized not in valid_moods:
        return f"Invalid mood. Available: {', '.join(valid_moods)}"
    
    identity = get_identity()
    identity.mood = mood_normalized
    set_identity(identity)
    
    return f"Mood set to {mood_normalized}."


def set_status_message(message: str) -> str:
    """Set status message (shown in UI)."""
    if len(message) > 100:
        return "Message too long (max 100 characters)."
    
    identity = get_identity()
    identity.status_message = message
    set_identity(identity)
    
    return f"Status message: {message}"


def get_identity_info() -> str:
    """Get full identity info."""
    identity = get_identity()
    
    personality = PERSONALITY_MODES.get(identity.personality, {})
    
    info = f"""
╔══════════════════════════════════════╗
║      JARVIS IDENTITY STATUS         ║
╠══════════════════════════════════════╣
║  Name:          {identity.name:<20} ║
║  Version:      {identity.version:<20} ║
║  Protocol:     {identity.protocol_level:<20} ║
║  Voice:        {identity.voice:<20} ║
║  Personality: {identity.personality:<20} ║
║  Mood:         {identity.mood:<20} ║
║  Status:       {identity.status_message:<20} ║
╚══════════════════════════════════════╝
Personality: {personality.get('description', '')}
    """.strip()
    
    return info


def get_available_options() -> Dict[str, List[str]]:
    """Get all available options."""
    return {
        "voices": VALID_VOICES,
        "protocols": PROTOCOL_LEVELS,
        "personalities": list(PERSONALITY_MODES.keys()),
        "moods": ["neutral", "focused", "alert", "worried", "excited", "analyzing"]
    }


def reset_identity() -> str:
    """Reset to default identity."""
    identity = _default_identity()
    set_identity(identity)
    return "Identity reset to defaults."


# === DISPATCHER ===

def identity_engine(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for identity operations.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[Identity] {action}")
    
    try:
        if action == "name" or action == "rename":
            name = params.get("name", "")
            if not name:
                return "Please specify name"
            return set_jarvis_name(name)
        
        elif action == "voice":
            voice = params.get("voice", "")
            if not voice:
                return "Please specify voice"
            return set_voice(voice)
        
        elif action == "personality":
            personality = params.get("personality", "")
            if not personality:
                return "Please specify personality"
            return set_personality(personality)
        
        elif action == "protocol":
            level = params.get("level", "")
            if not level:
                return "Please specify level"
            return set_protocol(level)
        
        elif action == "mood":
            mood = params.get("mood", "")
            if not mood:
                return "Please specify mood"
            return set_mood(mood)
        
        elif action == "status_message":
            message = params.get("message", "")
            if not message:
                return "Please specify message"
            return set_status_message(message)
        
        elif action == "reset":
            return reset_identity()
        
        elif action == "info" or action == "status":
            return get_identity_info()
        
        elif action == "options":
            options = get_available_options()
            return f"Voices: {options['voices']}\nProtocols: {options['protocols']}\nPersonalities: {options['personalities']}"
        
        else:
            return get_identity_info()
    
    except Exception as e:
        return f"Identity error: {e}"


if __name__ == "__main__":
    print("=== Identity Engine Test ===")
    
    # Get identity
    identity = get_identity()
    print(f"Current: {identity.name} | Voice: {identity.voice}")
    
    # Show options
    print("\nAvailable options:")
    options = get_available_options()
    print(f"Voices: {options['voices']}")
    print(f"Personalities: {options['personalities']}")
    print(f"Protocols: {options['protocols']}")
    
    # Test changes
    print("\nTesting changes...")
    print(set_jarvis_name("E.D.I.T.H."))
    print(set_voice("Aoede"))
    print(set_personality("edith"))
    
    # Reset
    print("\n" + reset_identity())
    print(get_identity_info())
    
    print("\n✅ Identity Engine ready")
