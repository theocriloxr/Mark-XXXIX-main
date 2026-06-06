"""
Prediction Engine - Speculative Pre-Computation (Mind Reader)

JARVIS predicts your needs based on context and pre-computes responses
before you even speak. Like a CPU's branch predictor.

How it works:
1. Track window/app patterns over time
2. Detect workflow context (coding, trading, browsing)
3. Pre-fetch relevant data (trading signals, files, etc.)
4. Cache responses for instant delivery

Usage:
    from core.prediction_engine import PredictionEngine, start_prediction_engine
    
    # Start prediction engine
    start_prediction_engine()
    
    # Get predictions
    predictions = get_pending_predictions()
"""

import logging
import threading
import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default patterns that trigger predictions
APP_PATTERNS = {
    "vscode": {
        "context": "coding",
        "predictions": ["code_helper", "dev_agent"],
        "keywords": ["python", "javascript", "code", "debug"]
    },
    "terminal": {
        "context": "terminal_work",
        "predictions": ["terminal_commands"],
        "keywords": ["git", "npm", "pip", "docker"]
    },
    "chrome": {
        "context": "browsing",
        "predictions": ["web_search"],
        "keywords": ["search", "documentation", "api"]
    },
    "trading": {
        "context": "trading",
        "predictions": ["signal_rank_bridge"],
        "keywords": ["crypto", "stock", "chart", "binance"]
    },
    "excel": {
        "context": "data_work",
        "predictions": ["file_processor"],
        "keywords": ["csv", "data", "analysis"]
    }
}


class PredictionEngine(threading.Thread):
    """
    Background prediction engine.
    Monitors context and pre-computes responses.
    """
    
    def __init__(self):
        super().__init__(daemon=True)
        
        self.is_running = False
        self._enabled = True
        
        # Window history for pattern detection
        self._window_history: deque = deque(maxlen=50)
        self._context_history: deque = deque(maxlen=20)
        
        # Pending predictions (pre-computed responses)
        self._predictions: Dict[str, Any] = {}
        
        # Pattern callbacks
        self._pattern_callbacks: Dict[str, Callable] = {}
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def run(self):
        """Main prediction loop."""
        self.is_running = True
        
        logger.info("[PredictionEngine] Started")
        
        while self.is_running:
            try:
                # Check current context
                self._check_context()
                
                # Generate predictions based on context
                self._generate_predictions()
                
                # Sleep between checks
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"[PredictionEngine] Error: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop the prediction engine."""
        self.is_running = False
        logger.info("[PredictionEngine] Stopped")
    
    def _check_context(self):
        """Check current window context and detect patterns."""
        try:
            from core.context_tracker import get_window_tracker
            
            tracker = get_window_tracker()
            if not tracker:
                return
            
            current_window = tracker.get_current_window()
            if not current_window:
                return
            
            # Add to history
            with self._lock:
                self._window_history.append({
                    "window": current_window,
                    "timestamp": time.time()
                })
            
            # Detect context from window name
            window_lower = current_window.lower()
            
            for pattern_name, pattern_data in APP_PATTERNS.items():
                if pattern_name in window_lower:
                    context = pattern_data.get("context")
                    
                    with self._lock:
                        if context != self._context_history:
                            self._context_history.append(context)
                            logger.info(f"[PredictionEngine] Context: {context}")
                    
                    break
                    
        except Exception as e:
            logger.debug(f"[PredictionEngine] Context check: {e}")
    
    def _generate_predictions(self):
        """Generate predictions based on current context."""
        if not self._enabled:
            return
        
        with self._lock:
            if not self._context_history:
                return
            
            current_context = self._context_history[-1]
        
        # Generate appropriate predictions
        if current_context == "trading":
            self._predict_trading()
        elif current_context == "coding":
            self._predict_coding()
        elif current_context == "browsing":
            self._predict_browsing()
    
    def _predict_trading(self):
        """Pre-fetch trading signals."""
        try:
            # Import signal rank bridge
            from actions.signal_rank_bridge import signal_rank_bridge
            
            # Pre-fetch active signals
            result = signal_rank_bridge({
                "query": "active_signals"
            })
            
            with self._lock:
                self._predictions["trading_signals"] = {
                    "type": "trading",
                    "data": result,
                    "created_at": time.time()
                }
            
            logger.info("[PredictionEngine] Pre-fetched trading signals")
            
        except Exception as e:
            logger.debug(f"[PredictionEngine] Trading prediction: {e}")
    
    def _predict_coding(self):
        """Pre-fetch coding assistance."""
        # Could pre-load common code templates or documentation
        with self._lock:
            self._predictions["code_context"] = {
                "type": "coding",
                "data": "Ready for code assistance",
                "created_at": time.time()
            }
    
    def _predict_browsing(self):
        """Pre-fetch web search capabilities."""
        with self._lock:
            self._predictions["web_search"] = {
                "type": "browsing",
                "data": "Ready for web search",
                "created_at": time.time()
            }
    
    def add_prediction(self, key: str, data: Any):
        """Manually add a prediction."""
        with self._lock:
            self._predictions[key] = {
                "data": data,
                "created_at": time.time()
            }
    
    def get_prediction(self, key: str) -> Optional[Any]:
        """Get a prediction if available."""
        with self._lock:
            pred = self._predictions.get(key)
            
            if pred:
                # Check if stale (> 5 minutes)
                age = time.time() - pred.get("created_at", 0)
                if age > 300:
                    # Remove stale prediction
                    del self._predictions[key]
                    return None
                
                return pred.get("data")
        
        return None
    
    def get_all_predictions(self) -> Dict[str, Any]:
        """Get all pending predictions."""
        with self._lock:
            # Filter stale predictions
            now = time.time()
            valid = {}
            
            for key, pred in self._predictions.items():
                age = now - pred.get("created_at", 0)
                if age < 300:  # Within 5 minutes
                    valid[key] = pred
            
            return valid
    
    def clear_predictions(self):
        """Clear all predictions."""
        with self._lock:
            self._predictions.clear()
    
    def get_context(self) -> str:
        """Get current workflow context."""
        with self._lock:
            if self._context_history:
                return self._context_history[-1]
            return "unknown"
    
    def get_window_patterns(self) -> List[Dict[str, Any]]:
        """Get recent window patterns."""
        with self._lock:
            return list(self._window_history)
    
    def enable(self):
        """Enable predictions."""
        self._enabled = True
    
    def disable(self):
        """Disable predictions."""
        self._enabled = False


# === GLOBAL ENGINE ===

_engine: Optional[PredictionEngine] = None


def get_prediction_engine() -> PredictionEngine:
    """Get global prediction engine instance."""
    global _engine
    if _engine is None:
        _engine = PredictionEngine()
    return _engine


def start_prediction_engine() -> str:
    """Start the background prediction engine."""
    engine = get_prediction_engine()
    
    if not engine.is_running:
        engine.start()
        return "Prediction engine started. JARVIS will anticipate your needs."
    
    return "Prediction engine already running."


def stop_prediction_engine() -> str:
    """Stop the prediction engine."""
    global _engine
    
    if _engine:
        _engine.stop()
        _engine = None
    
    return "Prediction engine stopped."


def get_pending_predictions() -> Dict[str, Any]:
    """Get all pending predictions."""
    return get_prediction_engine().get_all_predictions()


def get_prediction(key: str) -> Optional[Any]:
    """Get a specific prediction."""
    return get_prediction_engine().get_prediction(key)


def get_current_context() -> str:
    """Get current workflow context."""
    return get_prediction_engine().get_context()


def add_prediction(key: str, data: Any):
    """Manually add a prediction."""
    get_prediction_engine().add_prediction(key, data)


# === INTEGRATION WITH CONTEXT TRACKER ===

def on_window_change(window_title: str):
    """
    Callback from context tracker when window changes.
    Triggers prediction generation.
    """
    engine = get_prediction_engine()
    
    # Add to history
    with engine._lock:
        engine._window_history.append({
            "window": window_title,
            "timestamp": time.time()
        })
    
    # Trigger context check
    engine._check_context()


if __name__ == "__main__":
    print("=== Prediction Engine Test ===")
    
    engine = get_prediction_engine()
    print(f"Context: {engine.get_context()}")
    
    # Add manual prediction
    add_prediction("test", {"message": "Test prediction"})
    print(f"Predictions: {get_pending_predictions()}")
    
    print("\n✅ Prediction Engine ready")
