"""
Neural Decoding - BCI Integration for Thought Control

JARVIS integrates with consumer-grade Brain-Computer Interfaces:
- OpenBCI, Muse, Neurosity headbands
- Maps brainwave states (Alpha, Beta, Gamma) to digital workflow
- Triggers actions based on cognitive states

Cognitive States:
- Focused (Beta high): Code is compiling, stay quiet
- Relaxed (Alpha high): Brainstorming mode
- Confused (Theta high): Need help, highlight the issue
- Searching (Gamma): Looking for a word

Usage:
    from core.neural_decoding import NeuralDecoder, start_neural_decoding
    
    start_neural_decoding()
    
    # Get current cognitive state
    state = get_cognitive_state()
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# BCI devices
OPENBCI = "openbci"
MUSE = "muse"
NEUROSITY = "neurosity"

# Brainwave bands
DELTA = "delta"  # 0.5-4 Hz - Deep sleep
THETA = "theta"  # 4-8 Hz - Drowsiness, meditation
ALPHA = "alpha"  # 8-13 Hz - Relaxed, calm
BETA = "beta"   # 13-30 Hz - Focused, active thinking
GAMMA = "gamma"  # 30-100 Hz - High-level info processing


@dataclass
class BrainwaveRecord:
    """Brainwave data record."""
    delta: float = 0
    theta: float = 0
    alpha: float = 0
    beta: float = 0
    gamma: float = 0
    cognitive_state: str = "unknown"
    timestamp: float = 0
    confidence: float = 0


class NeuralDecoder:
    """
    Neural decoding from BCI devices.
    Maps brainwaves to cognitive states.
    """
    
    def __init__(self):
        self.is_running = False
        self._enabled = True
        
        # Device config
        self._device_config: Dict[str, Any] = {}
        
        # Current brainwaves
        self._current_waves: BrainwaveRecord = BrainwaveRecord()
        self._wave_history: deque = deque(maxlen=100)
        
        # State thresholds
        self._thresholds = {
            "focused": {"beta": 30, "alpha": 20},
            "relaxed": {"alpha": 30, "beta": 15},
            "confused": {"theta": 25},
            "searching": {"gamma": 20}
        }
        
        # Lock
        self._lock = threading.Lock()
        
        # Statistics
        self._sample_count = 0
        self._state_changes = 0
        self._last_state = "unknown"
        
        # Initialize device
        self._init_device()
    
    def _init_device(self):
        """Initialize BCI device."""
        # Stub - configure device
        self._device_config = {
            "device": "muse",
            "enabled": False
        }
        
        logger.info("[NeuralDecoder] Initialized")
    
    def start(self):
        """Start neural decoding."""
        if self.is_running:
            return
        
        self.is_running = True
        thread = threading.Thread(target=self._decode_loop, daemon=True)
        thread.start()
        
        logger.info("[NeuralDecoder] Started")
    
    def stop(self):
        """Stop neural decoding."""
        self.is_running = False
        logger.info("[NeuralDecoder] Stopped")
    
    def _decode_loop(self):
        """Main decoding loop."""
        while self.is_running:
            try:
                # Read brainwaves
                waves = self._read_brainwaves()
                
                # Determine cognitive state
                state = self._classify_state(waves)
                waves.cognitive_state = state
                
                with self._lock:
                    self._current_waves = waves
                    self._wave_history.append(waves)
                
                self._sample_count += 1
                
                # Detect state change
                if state != self._last_state:
                    self._state_changes += 1
                    self._on_state_change(state)
                    self._last_state = state
                
            except Exception as e:
                logger.debug(f"[NeuralDecoder] Decode error: {e}")
            
            # Sample every 2 seconds
            time.sleep(2)
    
    def _read_brainwaves(self) -> BrainwaveRecord:
        """Read brainwaves from device."""
        # In production, use device SDK
        # For now, simulate
        
        waves = BrainwaveRecord(
            delta=10,
            theta=15,
            alpha=25,
            beta=30,
            gamma=20,
            timestamp=time.time()
        )
        
        return waves
    
    def _classify_state(self, waves: BrainwaveRecord) -> str:
        """Classify cognitive state from brainwaves."""
        thresholds = self._thresholds
        
        # Focused: High beta, low alpha
        if waves.beta > thresholds["focused"]["beta"]:
            return "focused"
        
        # Relaxed: High alpha, low beta
        if waves.alpha > thresholds["relaxed"]["alpha"]:
            return "relaxed"
        
        # Confused: High theta
        if waves.theta > thresholds["confused"]["theta"]:
            return "confused"
        
        # Searching: High gamma
        if waves.gamma > thresholds["searching"]["gamma"]:
            return "searching"
        
        return "neutral"
    
    def _on_state_change(self, new_state: str):
        """Handle cognitive state change."""
        logger.info(f"[NeuralDecoder] State: {new_state}")
        
        # Trigger actions based on state
        if new_state == "confused":
            # Could highlight code issue, show help
            pass
        elif new_state == "focused":
            # Enable quiet mode
            pass
    
    def get_cognitive_state(self) -> str:
        """Get current cognitive state."""
        with self._lock:
            return self._current_waves.cognitive_state
    
    def get_brainwaves(self) -> BrainwaveRecord:
        """Get current brainwave data."""
        with self._lock:
            return self._current_waves
    
    def get_state_summary(self) -> str:
        """Get state summary."""
        waves = self.get_brainwaves()
        state = self.get_cognitive_state()
        
        return (
            f"State: {state} | "
            f"Beta: {waves.beta:.0f} | "
            f"Alpha: {waves.alpha:.0f} | "
            f"Theta: {waves.theta:.0f}"
        )
    
    def get_state_history(self, count: int = 10) -> List[Dict]:
        """Get state history."""
        with self._lock:
            history = list(self._wave_history)[-count:]
        
        return [
            {
                "state": w.cognitive_state,
                "beta": w.beta,
                "alpha": w.alpha,
                "theta": w.theta,
                "timestamp": w.timestamp
            }
            for w in history
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get decoder statistics."""
        return {
            "sample_count": self._sample_count,
            "state_changes": self._state_changes,
            "current_state": self.get_cognitive_state(),
            "status": "running" if self.is_running else "stopped"
        }
    
    def configure_device(self, device: str, api_key: str = None) -> str:
        """Configure BCI device."""
        self._device_config = {
            "device": device,
            "api_key": api_key,
            "enabled": True
        }
        return f"Device configured: {device}"
    
    def set_thresholds(self, state: str, band: str, value: float):
        """Set state thresholds."""
        if state in self._thresholds:
            self._thresholds[state][band] = value
    
    def enable(self):
        """Enable neural decoding."""
        self._enabled = True
    
    def disable(self):
        """Disable neural decoding."""
        self._enabled = False


# === GLOBAL INSTANCE ===

_neural_decoder: Optional[NeuralDecoder] = None


def get_neural_decoder() -> NeuralDecoder:
    """Get global neural decoder."""
    global _neural_decoder
    if _neural_decoder is None:
        _neural_decoder = NeuralDecoder()
    return _neural_decoder


def start_neural_decoding() -> str:
    """Start neural decoding."""
    decoder = get_neural_decoder()
    decoder.start()
    return "Neural decoding started."


def stop_neural_decoding() -> str:
    """Stop neural decoding."""
    get_neural_decoder().stop()
    return "Neural decoding stopped."


def get_cognitive_state() -> str:
    """Get current cognitive state."""
    return get_neural_decoder().get_cognitive_state()


# === DISPATCHER ===

def neural_decoding(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for neural decoding."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[NeuralDecoding] {action}")
    
    decoder = get_neural_decoder()
    
    try:
        if action == "status":
            return decoder.get_state_summary()
        
        elif action == "state":
            return decoder.get_cognitive_state()
        
        elif action == "brainwaves":
            waves = decoder.get_brainwaves()
            return f"Beta: {waves.beta} | Alpha: {waves.alpha} | Theta: {waves.theta}"
        
        elif action == "history":
            history = decoder.get_state_history()
            if history:
                lines = ["State History:"]
                for h in history[:5]:
                    lines.append(f"- {h['state']}")
                return "\n".join(lines)
            return "No history"
        
        elif action == "configure":
            device = params.get("device", "muse")
            api_key = params.get("api_key", "")
            return decoder.configure_device(device, api_key)
        
        elif action == "enable":
            decoder.enable()
            return "Neural decoding enabled."
        
        elif action == "disable":
            decoder.disable()
            return "Neural decoding disabled."
        
        else:
            return decoder.get_state_summary()
    
    except Exception as e:
        return f"NeuralDecoding error: {e}"


if __name__ == "__main__":
    print("=== Neural Decoding Test ===")
    
    decoder = get_neural_decoder()
    print(decoder.get_state_summary())
    
    print("\n✅ Neural Decoding ready")
