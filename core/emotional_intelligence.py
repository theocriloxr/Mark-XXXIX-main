"""
Emotional Intelligence Module - JARVIS Mood & Sentiment Awareness
=====================================================

JARVIS can detect and respond to user emotions:
- Mood detection (frustrated/excited/calm)
- Adaptive tone matching
- Stress detection
- Contextual emotional responses

Usage:
    from core.emotional_intelligence import detect_mood, respond_to_emotion, get_emotional_state
    
    # Detect user mood from text
    mood = detect_mood("I'm so frustrated with this!")
    
    # Get current emotional state
    state = get_emotional_state()
"""

import re
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


# Emotional states
EMOTIONAL_STATES = [
    "neutral",
    "happy",
    "excited",
    "calm",
    "worried",
    "frustrated",
    "angry",
    "sad",
    "confused",
    "surprised",
    "focused",
    "tired",
    "bored"
]


# Mood keywords for detection
MOOD_KEYWORDS = {
    "happy": ["happy", "great", "awesome", "amazing", "love", "wonderful", "fantastic", "excited", "yay"],
    "sad": ["sad", "depressed", "unhappy", "miserable", "down", "upset", "disappointed"],
    "frustrated": ["frustrated", "annoyed", "mad", "angry", "irritated", "ugh", "seriously", "ughh", "stupid"],
    "worried": ["worried", "anxious", "nervous", "concerned", "scared", "afraid", "panic"],
    "excited": ["excited", "pumped", "thrilled", "can't wait", "awesome", "cool", "sweet"],
    "calm": ["calm", "relaxed", "peaceful", "fine", "okay", "alright"],
    "confused": ["confused", "lost", "don't understand", "what", "huh", "don't get it"],
    "tired": ["tired", "exhausted", "sleepy", "drained", "fatigued", "beat"],
    "focused": ["focus", "concentrating", "working", "busy", "in the zone"],
    "bored": ["bored", "nothing to do", "boring", "stuck", "waiting"]
}


# Response templates
RESPONSE_TEMPLATES = {
    "happy": [
        "I'm glad to hear that!",
        "That's wonderful!",
        "Happy to help with the good vibes.",
        "Excellent news!"
    ],
    "sad": [
        "I'm sorry you're feeling that way.",
        "Would you like to talk about it?",
        "I'm here to help.",
        "Everything will be okay."
    ],
    "frustrated": [
        "Let's work through this together.",
        "I understand your frustration.",
        "Take a deep breath. We'll solve this.",
        "I'm here to help, not to judge."
    ],
    "worried": [
        "Let's assess the situation.",
        "I'll help you figure this out.",
        "Stay calm, we've got this.",
        "One step at a time."
    ],
    "excited": [
        "I love the energy!",
        "That's exciting!",
        "Let's make it happen!",
        "I'm ready when you are."
    ],
    "calm": [
        "Understood.",
        "As you wish.",
        "I'm at your service.",
        "Keeping things steady."
    ],
    "confused": [
        "Let me clarify.",
        "I'll explain step by step.",
        "Let's break it down.",
        "No problem, I'll help you understand."
    ],
    "tired": [
        "Take care of yourself.",
        "Maybe time for a break?",
        "I can handle things while you rest.",
        "Rest when you need to."
    ],
    "focused": [
        "I'm on it.",
        "Keeping the focus.",
        "Working on it now.",
        "Let's get this done."
    ],
    "bored": [
        "Want me to find something interesting?",
        "I could use the time to learn something new.",
        "How about we try something different?",
        "Any tasks I can help with?"
    ]
}


@dataclass
class EmotionalState:
    """User emotional state."""
    primary_mood: str = "neutral"
    confidence: float = 0.0
    intensity: float = 0.5  # 0-1 scale
    triggers: List[str] = None
    timestamp: float = 0
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []


import time

# Global emotional tracking
_emotional_lock = threading.Lock()
_current_state: EmotionalState = EmotionalState()
_mood_history: List[EmotionalState] = []


def get_current_state() -> EmotionalState:
    """Get current emotional state."""
    with _emotional_lock:
        return _current_state


def _set_current_state(state: EmotionalState) -> None:
    """Set current emotional state."""
    global _current_state
    with _emotional_lock:
        _current_state = state
        _mood_history.append(state)
        if len(_mood_history) > 50:
            _mood_history.pop(0)


def detect_mood(text: str) -> EmotionalState:
    """
    Detect mood from text input.
    
    Args:
        text: User input text
    
    Returns:
        EmotionalState with detected mood
    """
    text_lower = text.lower()
    
    # Score each emotion
    scores: Dict[str, float] = {}
    
    for mood, keywords in MOOD_KEYWORDS.items():
        score = 0
        triggers = []
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
                triggers.append(keyword)
        if triggers:
            scores[mood] = score
    
    if not scores:
        return EmotionalState(primary_mood="neutral", confidence=0.0, timestamp=time.time())
    
    # Find primary mood
    primary_mood = max(scores, key=scores.get)
    confidence = min(1.0, scores[primary_mood] / 3.0)  # Normalize
    
    # Calculate intensity based on exclamation/question marks
    intensity = 0.5
    if "!" in text:
        intensity = min(1.0, intensity + 0.2)
    if "?" in text:
        intensity = min(1.0, intensity + 0.1)
    if text.isupper():
        intensity = 1.0
    
    # Get triggers
    triggers = list(scores.keys())[:3]  # Top 3
    
    state = EmotionalState(
        primary_mood=primary_mood,
        confidence=confidence,
        intensity=intensity,
        triggers=triggers,
        timestamp=time.time()
    )
    
    _set_current_state(state)
    return state


def get_response_for_mood(mood: str) -> str:
    """Get contextual response for mood."""
    import random
    
    if mood not in RESPONSE_TEMPLATES:
        mood = "neutral"
    
    responses = RESPONSE_TEMPLATES.get(mood, ["I'm here."])
    return random.choice(responses)


def adapt_tone(user_mood: str, base_response: str) -> str:
    """
    Adapt response tone to user mood.
    
    Args:
        user_mood: Detected mood  
        base_response: Base response to adapt
    
    Returns:
        Modified response
    """
    # Short responses adapt naturally
    if len(base_response) < 20:
        return base_response
    
    # Add emotional adaptation
    if user_mood == "frustrated":
        # Shorter, more direct
        return base_response[:100] + "."
    
    elif user_mood == "tired":
        # More concise
        words = base_response.split()[:8]
        return " ".join(words) + "."
    
    return base_response


def get_emotional_summary() -> str:
    """Get summary of emotional state."""
    state = get_current_state()
    
    if state.primary_mood == "neutral":
        return "Emotional state: Neutral"
    
    conf_pct = int(state.confidence * 100)
    int_pct = int(state.intensity * 100)
    
    return f"Mood: {state.primary_mood.title()} (confidence: {conf_pct}%, intensity: {int_pct}%)"


def get_mood_history(count: int = 5) -> List[EmotionalState]:
    """Get recent mood history."""
    with _emotional_lock:
        return _mood_history[-count:]


def clear_mood_history() -> str:
    """Clear mood history."""
    global _mood_history
    with _emotional_lock:
        _mood_history = []
    return "Mood history cleared."


# === PRESETS FOR DIFFERENT PERSONALITIES ===

def get_response_for_personality(mood: str, personality: str) -> str:
    """Get personality-specific response."""
    import random
    
    # Base responses
    base_responses = RESPONSE_TEMPLATES.get(mood, ["Understood."])
    
    if personality == "friday":
        # Warmer, more female AI feel
        warm_additions = {
            "frustrated": ["I know, sweetie. Let's fix this.", "Oh dear, let's sort this out."],
            "worried": ["It's okay, I've got you.", "Don't worry, we're in this together."],
            "excited": ["I know, right?!", "This is so exciting!"],
            "calm": ["As you like it, darling.", "All peaceful like."]
        }
        if mood in warm_additions:
            base_responses = warm_additions[mood] + base_responses
    
    elif personality == "edith":
        # Military, crisp
        military_additions = {
            "frustrated": ["Acknowledging frustration. Solutions incoming.", "Defensive protocols engaged."],
            "worried": ["Threat assessment in progress.", "All sources monitored."],
            "excited": ["Targets aligned.", "Mission parameters met."],
            "calm": ["All clear.", "Perimeter secure."]
        }
        if mood in military_additions:
            base_responses = military_additions[mood] + base_responses
    
    elif personality == "stealth":
        # Quiet, minimal
        quiet_responses = {
            "frustrated": ["Working.", "Solving."],
            "worried": ["Noted.", "Monitoring."],
            "excited": ["Affirmative.", "Confirmed."]
        }
        if mood in quiet_responses:
            return quiet_responses[mood]
    
    return random.choice(base_responses)


# === DISPATCHER ===

def emotional_intelligence(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for emotional intelligence."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[EmotionalAI] {action}")
    
    try:
        if action == "detect":
            text = params.get("text", "")
            if not text:
                return "Please provide text to analyze"
            
            state = detect_mood(text)
            return f"Mood: {state.primary_mood} (confidence: {state.confidence:.0%})"
        
        elif action == "respond":
            mood = params.get("mood", "neutral")
            return get_response_for_mood(mood)
        
        elif action == "adapt":
            text = params.get("text", "")
            if not text:
                return "Please provide text"
            
            # Detect mood and adapt
            state = detect_mood(text)
            base_resp = params.get("response", "I'll help with that.")
            adapted = adapt_tone(state.primary_mood, base_resp)
            return adapted
        
        elif action == "history":
            count = int(params.get("count", 5))
            history = get_mood_history(count)
            if not history:
                return "No mood history"
            
            return ", ".join([s.primary_mood for s in history])
        
        elif action == "clear":
            return clear_mood_history()
        
        elif action == "status":
            return get_emotional_summary()
        
        else:
            return get_emotional_summary()
    
    except Exception as e:
        return f"EmotionalAI error: {e}"


if __name__ == "__main__":
    print("=== Emotional Intelligence Test ===")
    
    # Test mood detection
    test_phrases = [
        "I'm so frustrated with this!",
        "This is amazing!",
        "I'm a bit confused.",
        "Let's get this done.",
        "I'm tired..."
    ]
    
    for phrase in test_phrases:
        state = detect_mood(phrase)
        print(f"'{phrase}' -> {state.primary_mood} ({state.confidence:.0%})")
    
    # Test responses
    print("\nResponses:")
    for mood in ["happy", "frustrated", "excited", "tired"]:
        print(f"{mood}: {get_response_for_mood(mood)}")
    
    print("\n✅ Emotional Intelligence ready")
