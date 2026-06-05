# wake_word.py
"""
Wake Word Configuration - Always listening mode and custom wake word.

Implements:
1. Configurable wake word settings
2. Background openWakeWord listener thread
3. Integration with PyQt6 system tray
"""

import json
import logging
import sys
import threading
from pathlib import Path
from threading import Lock
from typing import Optional, Callable

logger = logging.getLogger(__name__)

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
CONFIG_FILE = BASE_DIR / "config" / "wake_word.json"
_lock = Lock()

# Default wake word
DEFAULT_WAKE_WORD = "jarvis"


def _load_config() -> dict:
    """Load wake word configuration."""
    if not CONFIG_FILE.exists():
        return {"enabled": True, "word": DEFAULT_WAKE_WORD, "mode": "active"}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except:
        return {"enabled": True, "word": DEFAULT_WAKE_WORD, "mode": "active"}


def _save_config(config: dict) -> None:
    """Save wake word configuration."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def set_wake_word(word: str) -> str:
    """Set custom wake word."""
    config = _load_config()
    config["word"] = word.lower().strip()
    _save_config(config)
    return f"Wake word set to: {word}"


def get_wake_word() -> str:
    """Get current wake word."""
    config = _load_config()
    return config.get("word", DEFAULT_WAKE_WORD)


def enable_listening() -> str:
    """Enable always listening mode."""
    config = _load_config()
    config["enabled"] = True
    _save_config(config)
    return "Always listening enabled."


def disable_listening() -> str:
    """Disable always listening mode."""
    config = _load_config()
    config["enabled"] = False
    _save_config(config)
    return "Always listening disabled."


def get_status() -> str:
    """Get wake word status."""
    config = _load_config()
    word = config.get("word", DEFAULT_WAKE_WORD)
    enabled = config.get("enabled", True)
    mode = config.get("mode", "active")
    return f"Wake Word: '{word}' | Listening: {enabled} | Mode: {mode}"


# === BACKGROUND WAKE WORD LISTENER ===

class WakeWordListener:
    """
    Background wake word listener using openWakeWord.
    Runs in a separate daemon thread for continuous listening.
    """
    
    def __init__(
        self,
        callback: Optional[Callable] = None,
        wake_word: str = "jarvis",
        threshold: float = 0.5
    ):
        """
        Initialize the wake word listener.
        
        Args:
            callback: Function to call when wake word is detected
            wake_word: Wake word to listen for (default: "jarvis")
            threshold: Detection threshold (0.0-1.0, default: 0.5)
        """
        self.callback = callback
        self.wake_word = wake_word
        self.threshold = threshold
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._model = None
        self._audio = None
        self._stream = None
        
    def _init_audio(self) -> bool:
        """Initialize audio stream and wake word model."""
        try:
            import numpy as np
            import pyaudio
            from openwakeword.model import Model
            
            # Initialize openWakeWord model
            # It automatically downloads default models if missing
            logger.info(f"Loading openWakeWord model: {self.wake_word}")
            self._model = Model(wakeword_models=[self.wake_word])
            
            # Audio Stream Configuration (16kHz, mono required by openWakeWord)
            self._chunk_size = 1280
            self._audio = pyaudio.PyAudio()
            self._stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=self._chunk_size
            )
            return True
            
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            logger.info("Install with: pip install openwakeword pyaudio")
            return False
        except Exception as e:
            logger.error(f"Audio init failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start the background wake word listener."""
        if self._running:
            logger.warning("Wake word listener already running")
            return True
            
        if not self._init_audio():
            return False
            
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        
        logger.info(f"✅ Wake word listener started. Say '{self.wake_word}' to activate.")
        return True
    
    def _listen_loop(self):
        """Main listening loop - runs in background thread."""
        import numpy as np
        
        logger.info("[WakeWord] Listening loop started")
        
        while self._running:
            try:
                # Read audio data from microphone
                data = self._stream.read(self._chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Feed to openWakeWord model
                prediction = self._model.predict(audio_data)
                
                # Check if any score passes threshold
                for word, score in prediction.items():
                    if score > self.threshold:
                        logger.info(f"[WakeWord] Detected '{word}' with confidence {score:.2f}")
                        if self.callback:
                            # Call the callback in a separate thread to avoid blocking
                            threading.Thread(
                                target=self.callback,
                                daemon=True
                            ).start()
                        # Reset model to prevent multiple triggers
                        self._model.reset()
                        break
                        
            except Exception as e:
                logger.error(f"[WakeWord] Error in listening loop: {e}")
                # Try to continue
                if self._running:
                    import time
                    time.sleep(0.5)
                    
        logger.info("[WakeWord] Listening loop stopped")
    
    def stop(self):
        """Stop the wake word listener."""
        self._running = False
        
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except:
                pass
                
        if self._audio:
            try:
                self._audio.terminate()
            except:
                pass
                
        logger.info("Wake word listener stopped")
    
    @property
    def is_running(self) -> bool:
        return self._running


# === GLOBAL LISTENER INSTANCE ===

_listener_instance: Optional[WakeWordListener] = None
_listener_callback: Optional[Callable] = None


def start_listener(callback: Optional[Callable] = None) -> str:
    """Start the background wake word listener."""
    global _listener_instance, _listener_callback
    
    if _listener_instance and _listener_instance.is_running:
        return "Wake word listener already running."
    
    config = _load_config()
    word = config.get("word", DEFAULT_WAKE_WORD)
    
    _listener_callback = callback
    _listener_instance = WakeWordListener(
        callback=callback,
        wake_word=word,
        threshold=0.5
    )
    
    if _listener_instance.start():
        return f"Wake word listener started. Say '{word}' to activate JARVIS."
    else:
        return "Failed to start wake word listener. Check dependencies: pip install openwakeword pyaudio"


def stop_listener() -> str:
    """Stop the background wake word listener."""
    global _listener_instance
    
    if _listener_instance:
        _listener_instance.stop()
        _listener_instance = None
        return "Wake word listener stopped."
    
    return "Wake word listener not running."


def get_listener_status() -> str:
    """Get listener status."""
    global _listener_instance
    
    if _listener_instance:
        return f"Wake word listener: Active (say '{_listener_instance.wake_word}')"
    return "Wake word listener: Inactive"


# === MAIN DISPATCHER ===

def wake_word(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for wake word configuration."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[wake_word] {action}")
    
    try:
        if action == "set":
            word = params.get("word", "jarvis")
            if not word:
                return "Please specify a wake word."
            return set_wake_word(word)
        elif action == "get":
            return get_wake_word()
        elif action == "enable":
            return enable_listening()
        elif action == "disable":
            return disable_listening()
        elif action == "start":
            # Start actual listener
            return start_listener()
        elif action == "stop":
            # Stop actual listener
            return stop_listener()
        elif action == "status":
            return get_status() + " | " + get_listener_status()
        else:
            return get_status()
    except Exception as e:
        return f"Wake word error: {e}"
