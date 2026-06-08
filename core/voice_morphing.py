"""
Voice Morphing System - JARVIS Voice Customization
===============================================

Allows JARVIS to modify voice properties:
- Pitch control
- Speed control  
- Accent overlay
- Gender options
- Emotional tonal variations

Usage:
    from core.voice_morphing import set_pitch, set_speed, set_accent, get_voice_settings
    
    # Adjust pitch (0.5 = lower, 1.0 = normal, 1.5 = higher)
    set_pitch(1.2)
    
    # Adjust speed (0.5 = slow, 1.0 = normal, 2.0 = fast)
    set_speed(1.0)
    
    # Set accent (american, british, irish, australian, indian)
    set_accent("irish")
    
    # Get current settings
    settings = get_voice_settings()
"""

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def _get_base_dir() -> Path:
    """Get base directory."""
    import sys
    from pathlib import Path
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
VOICE_CONFIG = BASE_DIR / "config" / "voice_morphing.json"


# Voice properties
class VoiceProperties:
    """Voice morphing settings."""
    pitch: float = 1.0          # 0.5 to 2.0 (1.0 = default)
    speed: float = 1.0          # 0.5 to 2.0 (1.0 = default)
    volume: float = 1.0         # 0.0 to 1.0
    pitch_shift: int = 0        # semitones (-12 to +12)
    rate: int = 0              # words per minute adjustment (-50 to +50)
    accent: str = ""            # "" = default, or specific accent
    gender: str = "neutral"     # male, female, neutral
    emphasis: str = "normal"   # minimal, normal, strong
    pauses: bool = True        # natural pauses
    
    def to_dict(self) -> dict:
        return {
            "pitch": self.pitch,
            "speed": self.speed,
            "volume": self.volume,
            "pitch_shift": self.pitch_shift,
            "rate": self.rate,
            "accent": self.accent,
            "gender": self.gender,
            "emphasis": self.emphasis,
            "pauses": self.pauses
        }


# Valid options
VALID_ACCENTS = [
    "",  # Default
    "american",
    "british", 
    "irish",
    "australian",
    "indian",
    "canadian",
    "southafrican"
]

VALID_GENDERS = ["male", "female", "neutral"]


def _default_properties() -> VoiceProperties:
    """Create default voice properties."""
    return VoiceProperties()


def _load_properties() -> VoiceProperties:
    """Load from config."""
    if not VOICE_CONFIG.exists():
        return _default_properties()
    
    try:
        with open(VOICE_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)
        props = VoiceProperties()
        props.pitch = data.get("pitch", 1.0)
        props.speed = data.get("speed", 1.0)
        props.volume = data.get("volume", 1.0)
        props.pitch_shift = data.get("pitch_shift", 0)
        props.rate = data.get("rate", 0)
        props.accent = data.get("accent", "")
        props.gender = data.get("gender", "neutral")
        props.emphasis = data.get("emphasis", "normal")
        props.pauses = data.get("pauses", True)
        return props
    except Exception:
        return _default_properties()


def _save_properties(props: VoiceProperties) -> None:
    """Save to config."""
    try:
        VOICE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(VOICE_CONFIG, "w", encoding="utf-8") as f:
            json.dump(props.to_dict(), f, indent=4)
    except Exception as e:
        print(f"[VoiceMorphing] Save error: {e}")


# Global instance
_props_lock = threading.Lock()
_current_properties: Optional[VoiceProperties] = None


def get_voice_properties() -> VoiceProperties:
    """Get current voice properties."""
    global _current_properties
    with _props_lock:
        if _current_properties is None:
            _current_properties = _load_properties()
        return _current_properties


def _set_voice_properties(props: VoiceProperties) -> None:
    """Set new voice properties."""
    global _current_properties
    with _props_lock:
        _current_properties = props
        _save_properties(props)


# === VOICE MORPHING OPERATIONS ===

def set_pitch(pitch: float) -> str:
    """
    Set voice pitch.
    
    Args:
        pitch: 0.5 (deep) to 2.0 (high), 1.0 = default
    
    Returns:
        str: Confirmation message
    """
    if pitch < 0.5 or pitch > 2.0:
        return "Pitch must be between 0.5 and 2.0"
    
    props = get_voice_properties()
    props.pitch = pitch
    _set_voice_properties(props)
    
    desc = "deep" if pitch < 0.8 else "normal" if pitch == 1.0 else "high" if pitch > 1.3 else ""
    return f"Pitch set to {pitch:.1f} ({desc})."


def set_speed(speed: float) -> str:
    """
    Set speaking speed.
    
    Args:
        speed: 0.5 (slow) to 2.0 (fast), 1.0 = default
    
    Returns:
        str: Confirmation message
    """
    if speed < 0.5 or speed > 2.0:
        return "Speed must be between 0.5 and 2.0"
    
    props = get_voice_properties()
    props.speed = speed
    _set_voice_properties(props)
    
    desc = "slow" if speed < 0.8 else "normal" if speed == 1.0 else "fast" if speed > 1.2 else ""
    return f"Speed set to {speed:.1f} ({desc})."


def set_volume(volume: float) -> str:
    """
    Set volume level.
    
    Args:
        volume: 0.0 (silent) to 1.0 (max)
    
    Returns:
        str: Confirmation message
    """
    if volume < 0.0 or volume > 1.0:
        return "Volume must be between 0.0 and 1.0"
    
    props = get_voice_properties()
    props.volume = volume
    _set_voice_properties(props)
    
    pct = int(volume * 100)
    return f"Volume set to {pct}%."


def set_accent(accent: str) -> str:
    """
    Set accent/regional voice.
    
    Args:
        accent: Valid accents
    
    Returns:
        str: Confirmation message
    """
    accent = accent.strip().lower()
    
    if accent not in VALID_ACCENTS:
        valid = ", ".join([a for a in VALID_ACCENTS if a])
        return f"Invalid accent. Valid: {valid}"
    
    props = get_voice_properties()
    props.accent = accent
    _set_voice_properties(props)
    
    if accent:
        return f"Accent set to {accent}."
    return "Accent set to default."


def set_gender(gender: str) -> str:
    """
    Set voice gender characteristics.
    
    Args:
        gender: male, female, neutral
    
    Returns:
        str: Confirmation message
    """
    gender = gender.strip().lower()
    
    if gender not in VALID_GENDERS:
        valid = ", ".join(VALID_GENDERS)
        return f"Invalid gender. Valid: {valid}"
    
    props = get_voice_properties()
    props.gender = gender
    _set_voice_properties(props)
    
    return f"Voice gender set to {gender}."


def set_pitch_shift(semitones: int) -> str:
    """
    Shift pitch by semitones.
    
    Args:
        semitones: -12 to +12
    
    Returns:
        str: Confirmation message
    """
    if semitones < -12 or semitones > 12:
        return "Semitones must be between -12 and +12"
    
    props = get_voice_properties()
    props.pitch_shift = semitones
    _set_voice_properties(props)
    
    direction = "up" if semitones > 0 else "down" if semitones < 0 else "default"
    return f"Pitch shifted {abs(semitones)} semitones {direction}."


def set_rate(wpm: int) -> str:
    """
    Adjust speaking rate in words per minute.
    
    Args:
        wpm: -50 to +50
    
    Returns:
        str: Confirmation message
    """
    if wpm < -50 or wpm > 50:
        return "Rate must be between -50 and +50"
    
    props = get_voice_properties()
    props.rate = wpm
    _set_voice_properties(props)
    
    direction = "faster" if wpm > 0 else "slower" if wpm < 0 else "default"
    return f"Speaking rate adjusted {abs(wpm)} wpm ({direction})."


def set_natural_pauses(enabled: bool) -> str:
    """Enable/disable natural pauses."""
    props = get_voice_properties()
    props.pauses = enabled
    _set_voice_properties(props)
    
    return f"Natural pauses {'enabled' if enabled else 'disabled'}."


def reset_voice() -> str:
    """Reset all voice settings to default."""
    props = _default_properties()
    _set_voice_properties(props)
    return "Voice settings reset to defaults."


def get_voice_settings() -> dict:
    """Get all voice settings."""
    return get_voice_properties().to_dict()


def get_voice_settings_display() -> str:
    """Get formatted voice settings display."""
    props = get_voice_properties()
    
    return f"""
╔══════════════════════════════════════╗
║      VOICE MORPHING SETTINGS        ║
╠══════════════════════════════════════╣
║  Pitch:       {props.pitch:<6.1f}  (0.5-2.0)     ║
║  Speed:      {props.speed:<6.1f}  (0.5-2.0)     ║
║  Volume:     {props.volume:<6.1f}  (0.0-1.0)     ║
║  Pitch Shift:{props.pitch_shift:>+5}  (±12 semitones)║
║  Rate:       {props.rate:>+5}  (±50 wpm)    ║
║  Accent:     {props.accent or 'default':<11}             ║
║  Gender:     {props.gender:<8}             ║
║  Pauses:     {props.pauses}               ║
╚══════════════════════════════════════╝
    """.strip()


# === PRESETS ===

def apply_preset(preset: str) -> str:
    """
    Apply a voice preset.
    
    Presets:
    - deep: Deep, slow, authoritative
    - fast: Quick, energetic
    - whisper: Quiet, slow
    - broadcast: Professional, clear
    - friday: Warm, friendly
    - edith: Military, crisp
    """
    presets = {
        "deep": {"pitch": 0.7, "speed": 0.85, "accent": "", "gender": "male"},
        "fast": {"pitch": 1.1, "speed": 1.3, "accent": "", "gender": "neutral"},
        "whisper": {"pitch": 0.8, "speed": 0.7, "volume": 0.5, "gender": "neutral"},
        "broadcast": {"pitch": 1.0, "speed": 1.0, "accent": "american", "gender": "male"},
        "friday": {"pitch": 1.0, "speed": 1.0, "accent": "irish", "gender": "female"},
        "edith": {"pitch": 0.9, "speed": 1.2, "accent": "american", "gender": "female"},
    }
    
    preset = preset.strip().lower()
    
    if preset not in presets:
        valid = ", ".join(presets.keys())
        return f"Invalid preset. Available: {valid}"
    
    props = get_voice_properties()
    settings = presets[preset]
    props.pitch = settings["pitch"]
    props.speed = settings["speed"]
    props.volume = settings.get("volume", 1.0)
    props.accent = settings.get("accent", "")
    props.gender = settings["gender"]
    _set_voice_properties(props)
    
    return f"Applied '{preset}' voice preset."


# === DISPATCHER ===

def voice_morphing(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for voice morphing."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[VoiceMorphing] {action}")
    
    try:
        if action == "pitch":
            pitch = params.get("pitch", 1.0)
            return set_pitch(float(pitch))
        
        elif action == "speed":
            speed = params.get("speed", 1.0)
            return set_speed(float(speed))
        
        elif action == "volume":
            volume = params.get("volume", 1.0)
            return set_volume(float(volume))
        
        elif action == "accent":
            accent = params.get("accent", "")
            return set_accent(accent)
        
        elif action == "gender":
            gender = params.get("gender", "neutral")
            return set_gender(gender)
        
        elif action == "pitch_shift":
            semitones = params.get("semitones", 0)
            return set_pitch_shift(int(semitones))
        
        elif action == "rate":
            wpm = params.get("wpm", 0)
            return set_rate(int(wpm))
        
        elif action == "preset":
            preset = params.get("preset", "")
            if not preset:
                return "Please specify preset"
            return apply_preset(preset)
        
        elif action == "reset":
            return reset_voice()
        
        elif action == "status" or action == "info":
            return get_voice_settings_display()
        
        elif action == "settings":
            return str(get_voice_settings())
        
        else:
            return get_voice_settings_display()
    
    except Exception as e:
        return f"VoiceMorphing error: {e}"


if __name__ == "__main__":
    print("=== Voice Morphing Test ===")
    
    # Show presets
    print("Available presets: deep, fast, whisper, broadcast, friday, edith")
    
    # Test preset
    print("\nApplying 'friday' preset...")
    print(apply_preset("friday"))
    
    # Show settings
    print("\n" + get_voice_settings_display())
    
    # Reset
    print("\n" + reset_voice())
    
    print("\n✅ Voice Morphing ready")
