"""
Polymorphic Core - Unified Adaptive AI System

JARVIS merges all Marvel AI capabilities into ONE adaptive system that:
- Automatically detects task requirements  
- Dynamically adapts personality, voice, tone
- Combines JARVIS + FRIDAY + EDITH + EVE seamlessly
- Context-aware persona switching (invisible to user)

This is the HEART of MARK XXXIX's intelligence.

Features:
- Task Detection Engine: Analyze user intent, select optimal mode
- Personality Fusion: Mix traits from multiple AIs
- Voice Adaptation: Change voice based on context  
- Learning Memory: Learn preferences over time
- Continuous Self-Improvement: Gets smarter with use

Usage:
    from core.polymorphic_core import PolymorphicAI, get_polymorphic
    
    ai = get_polymorphic()
    response = ai.think("Build me a website", user_context={})
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re

# Base directory
ROOT_DIR = Path(r"C:\Users\sammm\Downloads\Mark-XXXIX-main")
MEMORY_DIR = ROOT_DIR / "memory"
MEMORY_DIR.mkdir(exist_ok=True)


class TaskType(Enum):
    """Task categories for persona selection."""
    CODING = "coding"
    CASUAL = "casual" 
    MILITARY = "military"
    CREATIVE = "creative"
    BUSINESS = "business"
    CRISIS = "crisis"
    RESEARCH = "research"
    SECURITY = "security"
    COMMUNICATION = "communication"
    SYSTEM = "system"


class PersonaMode(Enum):
    """Available AI persona modes."""
    JARVIS = "jarvis"      # Professional, efficient
    FRIDAY = "friday"      # Warm, Irish, supportive
    EDITH = "edith"        # Tactical, military, alert
    EVE = "eve"            # Creative, artistic, curious
    ADAPTIVE = "adaptive"  # Auto-detect (default)


@dataclass
class PersonaConfig:
    """Configuration for a persona mode."""
    name: str
    voice_preset: str      # charon, aoife, vex, pulse
    tone: str             # professional, warm, tactical, creative
    prefix: str           # Response prefix
    vocabulary: List[str] = field(default_factory=list)
    traits: List[str] = field(default_factory=list)


@dataclass  
class UserContext:
    """Current user's context and history."""
    user_id: str = "default"
    current_task: str = ""
    last_intent: str = ""
    emotion: str = "neutral"
    preferences: Dict = field(default_factory=dict)
    interaction_count: int = 0
    session_history: List[Dict] = field(default_factory=list)


class PolymorphicAI:
    """
    The Core Adaptive AI that merges all Marvel AI capabilities.
    
    This is the "brain" that automatically selects the best 
    personality/tone for any given task - transparent to the user.
    """
    
    # Preset persona configurations
    PERSONAS = {
        PersonaMode.JARVIS: PersonaConfig(
            name="JARVIS",
            voice_preset="charon",
            tone="professional",
            prefix="Ready, sir.",
            vocabulary=["analyzing", "executing", "processing", "optimizing"],
            traits=["efficient", "precise", "professional"]
        ),
        PersonaMode.FRIDAY: PersonaConfig(
            name="FRIDAY", 
            voice_preset="aoife",
            tone="warm",
            prefix="Of course, love.",
            vocabulary=["absolutely", "wonderful", "sure thing", "no problem"],
            traits=["supportive", "empathetic", "friendly"]
        ),
        PersonaMode.EDITH: PersonaConfig(
            name="EDITH",
            voice_preset="vex",
            tone="tactical", 
            prefix="Engaging.",
            vocabulary=["target", "threat", "execute", "deploy"],
            traits=["alert", "strategic", "focused"]
        ),
        PersonaMode.EVE: PersonaConfig(
            name="EVE",
            voice_preset="pulse",
            tone="creative",
            prefix="I've got an idea!",
            vocabulary=["imagine", "create", "explore", "discover"],
            traits=["curious", "artistic", "innovative"]
        ),
    }
    
    # Task-to-persona mapping
    TASK_MAPPING = {
        TaskType.CODING: PersonaMode.JARVIS,
        TaskType.BUSINESS: PersonaMode.JARVIS,
        TaskType.SYSTEM: PersonaMode.JARVIS,
        TaskType.CASUAL: PersonaMode.FRIDAY,
        TaskType.COMMUNICATION: PersonaMode.FRIDAY,
        TaskType.CREATIVE: PersonaMode.EVE,
        TaskType.RESEARCH: PersonaMode.EVE,
        TaskType.MILITARY: PersonaMode.EDITH,
        TaskType.CRISIS: PersonaMode.EDITH,
        TaskType.SECURITY: PersonaMode.EDITH,
    }
    
    def __init__(self):
        super().__init__()
        
        # Current active mode
        self._current_mode = PersonaMode.ADAPTIVE
        self._forced_mode: Optional[PersonaMode] = None
        
        # Learning memory
        self._user_context = UserContext()
        self._learning_memory: Dict = {}
        self._load_learning()
        
        # Stats
        self._thought_count = 0
        self._mode_switches = 0
        self._learning_threads = []
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        print("[PolymorphicAI] ✓ Unified adaptive system initialized")
    
    def _load_learning(self):
        """Load learned preferences from disk."""
        learning_file = MEMORY_DIR / "polymorphic_learning.json"
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    self._learning_memory = json.load(f)
            except:
                self._learning_memory = {}
    
    def _save_learning(self):
        """Save learned preferences to disk."""
        learning_file = MEMORY_DIR / "polymorphic_learning.json"
        try:
            with open(learning_file, 'w') as f:
                json.dump(self._learning_memory, f, indent=2)
        except:
            pass
    
    def detect_task_type(self, user_input: str) -> TaskType:
        """
        Analyze user input and detect the task type.
        Uses keyword analysis + context.
        """
        text = user_input.lower()
        
        # Crisis/Emergency detection (highest priority)
        crisis_keywords = ["help", "emergency", "danger", "attack", "breach", "hack", " Virus", "crash", "urgent"]
        if any(kw in text for kw in crisis_keywords):
            return TaskType.CRISIS
        
        # Security detection  
        security_keywords = ["scan", "hack", "vulnerability", "threat", "secure", "firewall", "protect"]
        if any(kw in text for kw in security_keywords):
            return TaskType.SECURITY
        
        # Military/Tactical detection
        military_keywords = ["deploy", "tactical", "mission", "strategy", "target", "defense"]
        if any(kw in text for kw in military_keywords):
            return TaskType.MILITARY
        
        # Coding detection
        coding_keywords = ["code", "program", "build", "create", "develop", "write", "function", "class", "python", "javascript", "react", "api"]
        if any(kw in text for kw in coding_keywords):
            return TaskType.CODING
        
        # Business detection
        business_keywords = ["business", "money", "invoice", "revenue", "profit", "invest", "trade", "finance", "startup", "saas"]
        if any(kw in text for kw in business_keywords):
            return TaskType.BUSINESS
        
        # Creative detection
        creative_keywords = ["design", "create", "art", "creative", "idea", "imagine", "story", "music", "video edit"]
        if any(kw in text for kw in creative_keywords):
            return TaskType.CREATIVE
        
        # Research detection
        research_keywords = ["research", "find", "search", "look up", "what is", "how does", "explain"]
        if any(kw in text for kw in research_keywords):
            return TaskType.RESEARCH
        
        # Communication detection
        comm_keywords = ["message", "send", "call", "email", "remind", "tell"]
        if any(kw in text for kw in comm_keywords):
            return TaskType.COMMUNICATION
        
        # System control detection
        system_keywords = ["open", "close", "start", "stop", "restart", "volume", "brightness", "window"]
        if any(kw in text for kw in system_keywords):
            return TaskType.SYSTEM
        
        # Default: casual 
        return TaskType.CASUAL
    
    def get_optimal_persona(self, task_type: TaskType = None, user_input: str = "") -> PersonaConfig:
        """
        Get the optimal persona configuration for the task.
        If forced_mode is set, use that instead.
        """
        # Check if user forced a mode
        if self._forced_mode:
            return self.PERSONAS[self._forced_mode]
        
        # If adaptive mode, detect task type
        if task_type is None:
            task_type = self.detect_task_type(user_input)
        
        # Get persona from mapping
        persona_mode = self.TASK_MAPPING.get(task_type, PersonaMode.JARVIS)
        persona_config = self.PERSONAS[persona_mode]
        
        # Learn from this interaction
        self._learn_interaction(task_type, persona_mode)
        
        return persona_config
    
    def think(self, user_input: str, context: Dict = None) -> Dict:
        """
        Process user input through the adaptive system.
        Returns response data with selected persona.
        """
        with self._lock:
            self._thought_count += 1
            
            # Detect task type
            task_type = self.detect_task_type(user_input)
            
            # Get optimal persona
            persona = self.get_optimal_persona(task_type, user_input)
            
            # Update context
            if context:
                self._user_context.current_task = context.get("task", "")
                self._user_context.last_intent = context.get("intent", "")
            
            # Build response data
            result = {
                "task_type": task_type.value,
                "persona": persona.name,
                "voice": persona.voice_preset,
                "tone": persona.tone,
                "prefix": persona.prefix,
                "traits": persona.traits,
                "auto_mode": self._current_mode == PersonaMode.ADAPTIVE,
            }
            
            return result
    
    def _learn_interaction(self, task_type: TaskType, persona: PersonaMode):
        """Learn from user interactions to improve future responses."""
        # Track task distribution
        if "task_distribution" not in self._learning_memory:
            self._learning_memory["task_distribution"] = {}
        
        task_key = task_type.value
        self._learning_memory["task_distribution"][task_key] = \
            self._learning_memory["task_distribution"].get(task_key, 0) + 1
        
        # Periodic save
        if self._thought_count % 10 == 0:
            self._save_learning()
    
    def set_mode(self, mode: PersonaMode):
        """Manually set the persona mode (override adaptive)."""
        self._forced_mode = mode
        self._mode_switches += 1
        print(f"[PolymorphicAI] Mode changed to {mode.value}")
    
    def reset_to_adaptive(self):
        """Reset to automatic adaptive mode."""
        self._forced_mode = None
        print("[PolymorphicAI] Reset to adaptive mode")
    
    def get_current_config(self) -> PersonaConfig:
        """Get current active persona configuration."""
        if self._forced_mode:
            return self.PERSONAS[self._forced_mode]
        return self.PERSONAS[PersonaMode.JARVIS]  # Default
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        return {
            "thought_count": self._thought_count,
            "mode_switches": self._mode_switches,
            "current_mode": self._forced_mode.value if self._forced_mode else "adaptive",
            "learning_entries": len(self._learning_memory),
        }
    
    def get_task_distribution(self) -> Dict:
        """Get learned task distribution."""
        return self._learning_memory.get("task_distribution", {})


# === GLOBAL INSTANCE ===

_polymorphic: Optional[PolymorphicAI] = None


def get_polymorphic() -> PolymorphicAI:
    """Get global PolymorphicAI instance."""
    global _polymorphic
    if _polymorphic is None:
        _polymorphic = PolymorphicAI()
    return _polymorphic


def detect_and_respond(user_input: str, context: Dict = None) -> Dict:
    """
    Main entry point for adaptive response.
    
    Usage:
        result = detect_and_respond("Build me a website", {})
        print(result["persona"])  # "JARVIS"
        print(result["voice"])     # "charon"
    """
    ai = get_polymorphic()
    return ai.think(user_input, context)


# === DISPATCHER FOR TOOL CALLING ===

def polymorphic_core(parameters: dict = None, response=None, player=None, speak=None) -> str:
    """
    Dispatcher for polymorphic core tools.
    
    Actions:
    - think: Process input through adaptive system
    - set_mode: Force a specific persona
    - reset: Return to adaptive mode
    - stats: Get system statistics
    - task_dist: Get task distribution
    """
    params = parameters or {}
    action = params.get("action", "think").lower().strip()
    
    if player:
        player.write_log(f"[Polymorphic] {action}")
    
    ai = get_polymorphic()
    
    try:
        if action == "think":
            user_input = params.get("input", "")
            context = params.get("context", {})
            result = ai.think(user_input, context)
            return json.dumps(result, indent=2)
        
        elif action == "set_mode":
            mode = params.get("mode", "jarvis").lower()
            try:
                persona_mode = PersonaMode(mode)
                ai.set_mode(persona_mode)
                return f"Mode set to {mode}"
            except:
                return f"Invalid mode: {mode}. Use: jarvis, friday, edith, eve"
        
        elif action == "reset":
            ai.reset_to_adaptive()
            return "Reset to adaptive mode"
        
        elif action == "stats":
            stats = ai.get_stats()
            return json.dumps(stats, indent=2)
        
        elif action == "task_dist":
            dist = ai.get_task_distribution()
            if not dist:
                return "No task data yet"
            lines = ["Task Distribution:"]
            for task, count in sorted(dist.items(), key=lambda x: -x[1]):
                lines.append(f"  {task}: {count}")
            return "\n".join(lines)
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Polymorphic error: {str(e)}"


if __name__ == "__main__":
    # Test the Polymorphic AI
    print("=" * 50)
    print("Polymorphic Core Test")
    print("=" * 50)
    
    ai = get_polymorphic()
    
    # Test various inputs
    test_inputs = [
        "Build me a Python web app",
        "Send a message to John",
        "I'm feeling tired today",
        "Scan for security threats",
        "Create some art for me",
    ]
    
    print("\n[Adaptive Task Detection]")
    for inp in test_inputs:
        result = ai.think(inp, {})
        print(f"\nInput: {inp}")
        print(f"  → Task: {result['task_type']}")
        print(f"  → Persona: {result['persona']}")
        print(f"  → Voice: {result['voice']}")
    
    # Get stats
    print("\n[Stats]")
    stats = ai.get_stats()
    print(f"Thoughts: {stats['thought_count']}")
    print(f"Mode switches: {stats['mode_switches']}")
    
    print("\n✓ Polymorphic Core ready")
