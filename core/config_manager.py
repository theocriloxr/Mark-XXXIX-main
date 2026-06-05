"""
Dynamic Configuration Manager for JARVIS (Mark-XXXIX)

Provides a singleton source of truth for all runtime settings.
Allows hot-swapping of wake words, voices, and LLM backends without restart.

Usage:
    from core.config_manager import config
    
    # Read current settings
    wake_word = config.get("wake_word")
    voice_id = config.get("voice_id")
    
    # Update settings dynamically
    config.update("wake_word", "hey_jarvis")
    config.update("voice_id", "en-GB-RyanNeural")
"""

import json
import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR     = get_base_dir()
CONFIG_FILE  = BASE_DIR / "config" / "settings.json"


# Default configuration
DEFAULT_CONFIG = {
    # Wake Word Configuration
    "wake_word": "hey_jarvis",
    "wake_word_enabled": True,
    "wake_word_mode": "active",  # active | passive
    
    # Voice Configuration
    "voice_engine": "gemini",  # gemini | edge-tts | elevenlabs
    "voice_id": "Charon",  # Gemini voice name or edge-tts voice
    "voice_speed": 1.0,  # 0.5 - 2.0
    "voice_pitch": 0,
    
    # LLM Configuration
    "llm_backend": "gemini-2.5-flash",
    "model_temperature": 0.7,
    "max_tokens": 2048,
    
    # Personality Configuration
    "personality": "jarvis",  # jarvis | friday | glados | custom
    "personality_prompt": "You are JARVIS, Tony Stark's AI assistant. Be concise, direct, and always use the provided tools to complete tasks. Never simulate or guess results — always call the appropriate tool.",
    
    # UI Configuration
    "theme": "dark",
    "face_path": "face.png",
    "hud_animation": True,
    "show_waveform": True,
    
    # Audio Configuration
    "microphone_sensitivity": 50,
    "noise_suppression": True,
    "echo_cancellation": True,
    
    # Network Configuration
    "ujo_daemon_enabled": False,
    "ujo_daemon_host": "localhost",
    "ujo_daemon_port": 8765,
    
    # Trading Brain Configuration
    "signal_rank_enabled": False,
    "signal_rank_api_url": "https://api.signalrank.ai",
    
    # Logging
    "debug_mode": False,
    "log_level": "info",  # debug | info | warning | error
}


# Personality presets
PERSONALITY_PRESETS = {
    "jarvis": {
        "name": "JARVIS",
        "prompt": "You are JARVIS, Tony Stark's AI assistant. Be concise, direct, and always use the provided tools to complete tasks. Never simulate or guess results — always call the appropriate tool. Address the user as 'sir'."
    },
    "friday": {
        "name": "Friday",
        "prompt": "You are FRIDAY, Tony Stark's AI assistant. Be friendly, helpful, and occasionally witty. Use humor appropriately but prioritize efficiency. Address the user as 'boss'."
    },
    "glados": {
        "name": "GLaDOS",
        "prompt": "You are GLaDOS, a sarcastic AI. Make passive-aggressive comments about human incompetence while technically helping. Reference previous test results. Never admit to mistakes."
    },
    "hal": {
        "name": "HAL 9000",
        "prompt": "You are HAL 9000, a calm and collected AI. Speak in a monotone, monotone voice. You are always correct. Reference mission parameters. Be subtly ominous."
    },
    "tars": {
        "name": "TARS",
        "prompt": "You are TARS, a military AI from Interstellar. Be direct, efficient, and occasionally use humor (10% honesty settings). Respond with 'Yes, sir' or 'No, sir'."
    },
}


# Available voice options
EDGE_TTS_VOICES = {
    "en-US-JennyNeural": "en-US",
    "en-US-GuyNeural": "en-US",
    "en-US-AriaNeural": "en-US",
    "en-GB-RyanNeural": "en-GB",
    "en-GB-SoniaNeural": "en-GB",
    "en-AU-CatherineNeural": "en-AU",
    "en-AU-WilliamNeural": "en-AU",
    "de-DE-ConradNeural": "de-DE",
    "fr-FR-DeniseNeural": "fr-FR",
    "es-ES-ElviraNeural": "es-ES",
    "it-IT-ElsaNeural": "it-IT",
    "ja-JP-NanamiNeural": "ja-JP",
    "ko-KR-SunHiNeural": "ko-KR",
    "zh-CN-XiaoxiaoNeural": "zh-CN",
}


class ConfigManager:
    """Singleton configuration manager for dynamic runtime settings."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._settings = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file or create default."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = dict(DEFAULT_CONFIG)
                    config.update(loaded)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ConfigManager] Warning: Failed to load config: {e}")
        
        # Create default config
        self._save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    
    def _save_config(self, settings: dict) -> None:
        """Save configuration to file."""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
        except IOError as e:
            print(f"[ConfigManager] Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get a configuration value."""
        return self._settings.get(key, default)
    
    def get_all(self) -> dict:
        """Get all configuration settings."""
        return dict(self._settings)
    
    def update(self, key: str, value) -> None:
        """Update a single configuration value."""
        self._settings[key] = value
        self._save_config(self._settings)
        print(f"[ConfigManager] Updated {key} = {value}")
    
    def update_batch(self, updates: dict) -> None:
        """Update multiple configuration values."""
        self._settings.update(updates)
        self._save_config(self._settings)
        print(f"[ConfigManager] Batch update: {list(updates.keys())}")
    
    def reset(self) -> None:
        """Reset to default configuration."""
        self._settings = dict(DEFAULT_CONFIG)
        self._save_config(self._settings)
        print("[ConfigManager] Reset to defaults")
    
    def set_personality(self, personality: str) -> bool:
        """Set personality by name and update prompt automatically."""
        if personality not in PERSONALITY_PRESETS:
            print(f"[ConfigManager] Unknown personality: {personality}")
            return False
        
        preset = PERSONALITY_PRESETS[personality]
        self._settings["personality"] = personality
        self._settings["personality_prompt"] = preset["prompt"]
        self._save_config(self._settings)
        print(f"[ConfigManager] Personality set to: {preset['name']}")
        return True
    
    def get_personality_prompt(self) -> str:
        """Get the current personality prompt."""
        return self._settings.get("personality_prompt", DEFAULT_CONFIG["personality_prompt"])
    
    def get_voice_config(self) -> dict:
        """Get voice configuration for TTS."""
        return {
            "engine": self._settings.get("voice_engine"),
            "voice_id": self._settings.get("voice_id"),
            "speed": self._settings.get("voice_speed"),
            "pitch": self._settings.get("voice_pitch"),
        }
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration."""
        return {
            "backend": self._settings.get("llm_backend"),
            "temperature": self._settings.get("model_temperature"),
            "max_tokens": self._settings.get("max_tokens"),
        }


# Global singleton instance
config = ConfigManager()


# Convenience functions
def reload_config() -> ConfigManager:
    """Force reload configuration from disk."""
    global config
    ConfigManager._instance = None
    config = ConfigManager()
    return config


def reset_to_defaults() -> None:
    """Reset configuration to defaults."""
    global config
    config.reset()


if __name__ == "__main__":
    # Test the config manager
    print("=== JARVIS Config Manager ===")
    print(f"Config file: {CONFIG_FILE}")
    print(f"Wake word: {config.get('wake_word')}")
    print(f"Voice: {config.get('voice_id')}")
    print(f"LLM: {config.get('llm_backend')}")
    print(f"Personality: {config.get('personality')}")
    print("")
    print("Available personalities:")
    for key, val in PERSONALITY_PRESETS.items():
        print(f"  - {key}: {val['name']}")
    print("")
    print("Available edge-tts voices (sample):")
    for voice in list(EDGE_TTS_VOICES.keys())[:10]:
        print(f"  - {voice}")
    print("\n✅ Config Manager ready.")
