"""
Sentiment Analyzer - Acoustic Sentiment Adaptation

JARVIS analyzes your voice in real-time to detect emotions and adapts
its personality accordingly.

Emotions Detected:
- Calm: Detailed, conversational responses
- Frustrated: Urgent, concise, solution-focused
- Excited: Energetic, matching enthusiasm
- Urgent: Quick, direct responses

Usage:
    from core.sentiment_analyzer import SentimentAnalyzer, get_sentiment
    
    # Analyze audio
    emotion = get_sentiment(audio_chunk)
    
    # Get adapted personality
    personality = get_adapted_personality(emotion)
"""

import logging
import threading
import time
from collections import deque
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Emotion to personality mapping
EMOTION_PERSONALITIES = {
    "calm": {
        "description": "Calm and conversational",
        "traits": "Detailed, thoughtful, relaxed",
        "system_prompt_addition": "Speak in a calm, detailed manner. Take time to explain thoroughly."
    },
    "frustrated": {
        "description": "Solution-focused and urgent",
        "traits": "Quick, direct, no pleasantries",
        "system_prompt_addition": "Be direct and concise. Skip pleasantries. Focus on solutions immediately."
    },
    "excited": {
        "description": "Energetic and enthusiastic",
        "traits": "Energetic, matching enthusiasm",
        "system_prompt_addition": "Match the user's energy. Be enthusiastic and positive."
    },
    "urgent": {
        "description": "Rapid and critical",
        "traits": "Fast, prioritized, action-oriented",
        "system_prompt_addition": "Prioritize speed. Give actionable steps first. Minimize elaboration."
    },
    "neutral": {
        "description": "Standard JARVIS",
        "traits": "Professional, helpful",
        "system_prompt_addition": "Be professional and helpful. Use standard JARVIS behavior."
    }
}

# Confidence thresholds
CONFIDENCE_THRESHOLD = 0.6
HISTORY_LENGTH = 10


class SentimentAnalyzer:
    """
    Real-time sentiment analyzer for voice input.
    
    Uses a lightweight classifier to detect emotion from audio.
    """
    
    def __init__(self):
        self._current_emotion = "neutral"
        self._confidence = 0.5
        self._history: deque = deque(maxlen=HISTORY_LENGTH)
        self._lock = threading.Lock()
        
        # Model placeholder (would use wav2vec in production)
        self._model = None
        self._initialized = False
    
    def _init_model(self) -> bool:
        """Initialize the sentiment model."""
        try:
            # In production, load a lightweight wav2vec model
            # For now, use simple heuristics
            logger.info("[SentimentAnalyzer] Initialized with heuristics")
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"[SentimentAnalyzer] Init failed: {e}")
            return False
    
    def analyze(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Analyze audio data for sentiment.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            dict: {emotion, confidence}
        """
        if not self._initialized:
            self._init_model()
        
        # Simple heuristic-based sentiment (in production, use ML model)
        emotion, confidence = self._heuristic_analyze(audio_data)
        
        # Update history
        with self._lock:
            self._history.append({
                "emotion": emotion,
                "confidence": confidence,
                "timestamp": time.time()
            })
            
            # Update current emotion
            self._current_emotion = emotion
            self._confidence = confidence
        
        return {
            "emotion": emotion,
            "confidence": confidence
        }
    
    def _heuristic_analyze(self, audio_data: bytes) -> tuple:
        """
        Heuristic-based sentiment analysis.
        
        In production, replace with actual ML model:
        - Use transformers wav2vec
        - Or use an API like Deepgram/Vapi for sentiment
        
        Simple heuristics:
        - Audio energy level
        - Pitch patterns (if available)
        """
        # Simple fallback: analyze audio characteristics
        if not audio_data:
            return "neutral", 0.5
        
        try:
            # Calculate energy (simple proxy for volume)
            import struct
            
            # Parse as int16 samples
            samples = struct.unpack(f"{len(audio_data)//2}h", audio_data)
            
            # Calculate RMS energy
            energy = sum(s*s for s in samples) / len(samples)
            energy = energy ** 0.5
            
            # Heuristic: high energy could mean excited/urgent
            # Low energy could mean calm/neutral
            # (Very rough approximation)
            
            if energy > 5000:
                return "excited", 0.6
            elif energy > 2000:
                return "neutral", 0.6
            else:
                return "calm", 0.6
                
        except:
            return "neutral", 0.5
    
    def get_current_emotion(self) -> str:
        """Get the currently detected emotion."""
        with self._lock:
            return self._current_emotion
    
    def get_confidence(self) -> float:
        """Get confidence in current emotion."""
        with self._lock:
            return self._confidence
    
    def get_emotion_history(self) -> list:
        """Get recent emotion history."""
        with self._lock:
            return list(self._history)
    
    def get_adapted_personality(self, emotion: str = None) -> Dict[str, str]:
        """
        Get personality parameters for an emotion.
        
        Args:
            emotion: Emotion to get personality for (default: current)
            
        Returns:
            dict: Personality parameters
        """
        if emotion is None:
            emotion = self.get_current_emotion()
        
        return EMOTION_PERSONALITIES.get(
            emotion, 
            EMOTION_PERSONALITIES["neutral"]
        )
    
    def get_system_prompt_addition(self) -> str:
        """Get system prompt addition for current emotion."""
        personality = self.get_adapted_personality()
        return personality.get("system_prompt_addition", "")
    
    def reset(self):
        """Reset to neutral."""
        with self._lock:
            self._current_emotion = "neutral"
            self._confidence = 0.5
            self._history.clear()


# === API STYLE FUNCTIONS ===

_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get global sentiment analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


def get_sentiment(audio_data: bytes) -> Dict[str, Any]:
    """Analyze audio for sentiment."""
    return get_sentiment_analyzer().analyze(audio_data)


def get_current_emotion() -> str:
    """Get current emotion."""
    return get_sentiment_analyzer().get_current_emotion()


def get_adapted_personality(emotion: str = None) -> Dict[str, str]:
    """Get personality for emotion."""
    return get_sentiment_analyzer().get_adapted_personality(emotion)


def get_system_prompt_addition() -> str:
    """Get system prompt for current emotion."""
    return get_sentiment_analyzer().get_system_prompt_addition()


# === MAIN DISPATCHER ===

def sentiment_analyzer(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for sentiment analyzer.
    
    Parameters:
    - action: status | emotion | personality | reset
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[SentimentAnalyzer] {action}")
    
    analyzer = get_sentiment_analyzer()
    
    try:
        if action == "status":
            emotion = analyzer.get_current_emotion()
            confidence = analyzer.get_confidence()
            return f"Emotion: {emotion} ({confidence:.0%})"
        
        elif action == "emotion":
            emotion = analyzer.get_current_emotion()
            return emotion
        
        elif action == "personality":
            personality = analyzer.get_adapted_personality()
            return personality.get("description", "Unknown")
        
        elif action == "reset":
            analyzer.reset()
            return "Sentiment reset to neutral"
        
        else:
            return analyzer.get_adapted_personality()
            
    except Exception as e:
        return f"SentimentAnalyzer error: {e}"


if __name__ == "__main__":
    print("=== Sentiment Analyzer Test ===")
    
    analyzer = get_sentiment_analyzer()
    print(f"Current emotion: {analyzer.get_current_emotion()}")
    print(f"Personality: {analyzer.get_adapted_personality()}")
    
    print("\n✅ Sentiment Analyzer ready")
