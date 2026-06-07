"""
Neural Mirror - UI Cognitive Adaptation

UI adaptation based on real-time brain states:
- Listens to neural_decoding for cognitive states
- Automatically adapts UI based on brain state:
  - Focused (Beta high) → Minimalist Mode
  - Stressed → Enlarged emergency buttons
  - Relaxed → Standard mode
  - Confused → Offer help, highlight issues

Usage:
    from core.neural_mirror import NeuralMirror, get_neural_mirror
    
    mirror = get_neural_mirror()
    mirror.start_adaptation()
    
    # Get current mode
    mode = mirror.get_current_mode()
"""

import logging
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Get base directory
def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


# UI Modes
MODE_STANDARD = "standard"
MODE_MINIMALIST = "minimalist"
MODE_FOCUSED = "focused"
MODE_STRESSED = "stressed"
MODE_RELAXED = "relaxed"
MODE_CONFUSED = "confused"


class NeuralMirror:
    """
    UI adaptation based on cognitive states.
    """
    
    def __init__(self):
        self.is_running = False
        self.current_mode = MODE_STANDARD
        
        # UI configuration for each mode
        self.ui_configs = {
            MODE_STANDARD: {
                "show_notifications": True,
                "button_size": 1.0,
                "color_palette": "default",
                "dim_dashboard": False,
            },
            MODE_MINIMALIST: {
                "show_notifications": False,
                "button_size": 0.8,
                "color_palette": "calm_blue",
                "dim_dashboard": True,
            },
            MODE_FOCUSED: {
                "show_notifications": False,
                "button_size": 0.8,
                "color_palette": "deep_blue",
                "dim_dashboard": True,
            },
            MODE_STRESSED: {
                "show_notifications": True,
                "button_size": 1.5,
                "color_palette": "warning",
                "dim_dashboard": False,
                "enlarge_emergency": True,
            },
            MODE_RELAXED: {
                "show_notifications": True,
                "button_size": 1.0,
                "color_palette": "default",
                "dim_dashboard": False,
            },
            MODE_CONFUSED: {
                "show_notifications": True,
                "button_size": 1.2,
                "color_palette": "help",
                "dim_dashboard": False,
                "show_help": True,
            }
        }
        
        # State history
        self.state_history = []
        self.mode_changes = 0
        self._lock = threading.Lock()
        
        # Reference to neural decoder
        self._decoder = None
        
        # UI callback
        self._ui_callback = None
        
        logger.info("[NEURAL_MIRROR] Initialized")
    
    def set_ui_callback(self, callback):
        """
        Set callback for UI updates.
        
        Args:
            callback: Function to call with UI config
        """
        self._ui_callback = callback
    
    def start_adaptation(self):
        """Start neural mirroring."""
        if self.is_running:
            return
        
        self.is_running = True
        thread = threading.Thread(target=self._adaptation_loop, daemon=True)
        thread.start()
        
        logger.info("[NEURAL_MIRROR] Adaptation started")
    
    def stop_adaptation(self):
        """Stop neural mirroring."""
        self.is_running = False
        logger.info("[NEURAL_MIRROR] Adaptation stopped")
    
    def _adaptation_loop(self):
        """Main adaptation loop."""
        while self.is_running:
            try:
                # Get cognitive state
                state = self._get_cognitive_state()
                
                # Map to UI mode
                new_mode = self._map_state_to_mode(state)
                
                # Update if changed
                if new_mode != self.current_mode:
                    self._apply_mode(new_mode)
                
                time.sleep(2)
            except Exception as e:
                logger.debug(f"[NEURAL_MIRROR] Loop error: {e}")
    
    def _get_cognitive_state(self) -> str:
        """Get current cognitive state from decoder."""
        if self._decoder is None:
            # Try to get decoder
            try:
                from core.neural_decoding import get_neural_decoder
                self._decoder = get_neural_decoder()
            except ImportError:
                return "neutral"
        
        if self._decoder:
            return self._decoder.get_cognitive_state()
        
        return "neutral"
    
    def _map_state_to_mode(self, state: str) -> str:
        """Map cognitive state to UI mode."""
        mapping = {
            "focused": MODE_FOCUSED,
            "relaxed": MODE_RELAXED,
            "confused": MODE_CONFUSED,
            "searching": MODE_MINIMALIST,
            "neutral": MODE_STANDARD,
            "stressed": MODE_STRESSED,
        }
        return mapping.get(state, MODE_STANDARD)
    
    def _apply_mode(self, mode: str):
        """Apply UI mode."""
        with self._lock:
            old_mode = self.current_mode
            self.current_mode = mode
            self.mode_changes += 1
            
            # Get config for new mode
            config = self.ui_configs.get(mode, self.ui_configs[MODE_STANDARD])
            
            # Update history
            self.state_history.append({
                "old_mode": old_mode,
                "new_mode": mode,
                "timestamp": time.time()
            })
            
            # Keep history limited
            if len(self.state_history) > 50:
                self.state_history = self.state_history[-50:]
            
            # Callback to UI
            if self._ui_callback:
                try:
                    self._ui_callback(config, mode)
                except Exception as e:
                    logger.debug(f"[NEURAL_MIRROR] UI callback error: {e}")
            
            logger.info(f"[NEURAL_MIRROR] Mode changed: {old_mode} → {mode}")
    
    def set_mode(self, mode: str) -> bool:
        """
        Manually set UI mode.
        
        Args:
            mode: Mode to set
            
        Returns:
            bool: Success
        """
        if mode not in self.ui_configs:
            return False
        
        self._apply_mode(mode)
        return True
    
    def get_current_mode(self) -> str:
        """Get current UI mode."""
        return self.current_mode
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current UI configuration."""
        return self.ui_configs.get(self.current_mode, self.ui_configs[MODE_STANDARD])
    
    def get_mode_history(self, count: int = 10) -> list:
        """Get mode change history."""
        return self.state_history[-count:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get mirror status."""
        return {
            "is_running": self.is_running,
            "current_mode": self.current_mode,
            "mode_changes": self.mode_changes,
            "config": self.get_current_config()
        }
    
    def enable_minimalist_mode(self):
        """Manually enable minimalist mode."""
        self.set_mode(MODE_MINIMALIST)
    
    def enable_focus_mode(self):
        """Manually enable focus mode."""
        self.set_mode(MODE_FOCUSED)
    
    def enable_standard_mode(self):
        """Manually enable standard mode."""
        self.set_mode(MODE_STANDARD)
    
    def enable_help_mode(self):
        """Manually enable help mode."""
        self.set_mode(MODE_CONFUSED)
    
    def enable_stress_mode(self):
        """Manually enable stress mode."""
        self.set_mode(MODE_STRESSED)


# === GLOBAL INSTANCE ===

_neural_mirror: Optional[NeuralMirror] = None


def get_neural_mirror() -> NeuralMirror:
    """Get global NeuralMirror instance."""
    global _neural_mirror
    if _neural_mirror is None:
        _neural_mirror = NeuralMirror()
    return _neural_mirror


# === DISPATCHER ===

def neural_mirror(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for Neural Mirror."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[NeuralMirror] {action}")
    
    try:
        mirror = get_neural_mirror()
        
        if action == "status":
            status = mirror.get_status()
            return (
                f"Mode: {status['current_mode']} | "
                f"Running: {status['is_running']}"
            )
        
        elif action == "start":
            mirror.start_adaptation()
            return "Neural adaptation started"
        
        elif action == "stop":
            mirror.stop_adaptation()
            return "Neural adaptation stopped"
        
        elif action == "mode":
            mode = params.get("mode", "")
            if mode:
                if mirror.set_mode(mode):
                    return f"Mode set to {mode}"
                return f"Invalid mode: {mode}"
            return f"Current mode: {mirror.get_current_mode()}"
        
        elif action == "minimalist":
            mirror.enable_minimalist_mode()
            return "Minimalist mode enabled"
        
        elif action == "focus":
            mirror.enable_focus_mode()
            return "Focus mode enabled"
        
        elif action == "standard":
            mirror.enable_standard_mode()
            return "Standard mode enabled"
        
        elif action == "help":
            mirror.enable_help_mode()
            return "Help mode enabled"
        
        elif action == "history":
            history = mirror.get_mode_history()
            if history:
                lines = ["Mode History:"]
                for h in history[-5:]:
                    lines.append(f"  {h['old_mode']} → {h['new_mode']}")
                return "\n".join(lines)
            return "No history"
        
        else:
            status = mirror.get_status()
            return f"Neural Mirror: {status['current_mode']}"
    
    except Exception as e:
        return f"NeuralMirror error: {e}"


if __name__ == "__main__":
    print("=== Neural Mirror Test ===")
    
    mirror = get_neural_mirror()
    
    # Test modes
    mirror.enable_focus_mode()
    print(f"Mode: {mirror.get_current_mode()}")
    print(f"Config: {mirror.get_current_config()}")
    
    mirror.enable_standard_mode()
    print(f"Mode: {mirror.get_current_mode()}")
    
    print("\n✅ Neural Mirror ready")
