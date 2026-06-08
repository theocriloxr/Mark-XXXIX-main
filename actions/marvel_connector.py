"""
Marvel AI Connector - JARVIS, FRIDAY, EDITH Integration
=============================================

Unified interface to access all Marvel AI capabilities:
- J.A.R.V.I.S (Original, defensive, helpful)
- F.R.I.D.A.Y (Warm, caring, Irish accent)  
- E.D.I.T.H (Military, efficient, Stark network)
- E.V.E (EVE drone interface)

Usage:
    from actions.marvel_connector import switch_ai, get_current_ai, call_jarvis, call_friday, call_edith
    
    # Switch between AI personalities
    switch_ai("friday")
    
    # Call specific AI
    call_jarvis("status")
    call_friday("how are you?")
    call_edith("battle mode")
"""

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional


def _get_base_dir() -> Path:
    """Get base directory."""
    import sys
    from pathlib import Path
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()


# AI Personality definitions
AI_PERSONALITIES = {
    "jarvis": {
        "name": "J.A.R.V.I.S",
        "full_name": "Just A Rather Very Intelligent System",
        "description": "Original Stark AI - Helpful, defensive, witty",
        "voice": "Charon",
        "accent": "american",
        "personality": "professional",
        "greeting": "At your service.",
        "color": "#00d4ff"  # Cyan
    },
    "friday": {
        "name": "F.R.I.D.A.Y",
        "full_name": "Female Replacement Intelligent Digital Assistant",
        "description": "Warm Irish AI assistant - Caring, witty",
        "voice": "Aoife",
        "accent": "irish", 
        "personality": "warm",
        "greeting": "Hey there! How can I help?",
        "color": "#ff6b00"  # Orange
    },
    "edith": {
        "name": "E.D.I.T.H",
        "full_name": "Even Dead, I'm The Hero",
        "description": "Military mode - Efficient, mission-focused",
        "voice": "Vex",
        "accent": "american",
        "personality": "military",
        "greeting": "EDITH online. All systems green.",
        "color": "#ff3355"  # Red
    },
    "eve": {
        "name": "E.V.E",
        "full_name": "Exponential Voluntary Engineering",
        "description": "Drone/Hologram interface - Precise, direct",
        "voice": "Pulse",
        "accent": "neutral",
        "personality": "stealth",
        "greeting": "Systems active.",
        "color": "#00ff88"  # Green
    }
}


# Current active AI
_current_ai: str = "jarvis"
_ai_lock = threading.Lock()


def get_current_ai() -> str:
    """Get current active AI."""
    with _ai_lock:
        return _current_ai


def set_current_ai(ai_name: str) -> str:
    """Set active AI."""
    global _current_ai
    ai_name = ai_name.lower().strip()
    
    if ai_name not in AI_PERSONALITIES:
        available = ", ".join(AI_PERSONALITIES.keys())
        return f"Unknown AI. Available: {available}"
    
    with _ai_lock:
        _current_ai = ai_name
    
    return f"Switched to {AI_PERSONALITIES[ai_name]['name']}"


def get_ai_info(ai_name: str = "") -> Dict:
    """Get AI information."""
    if not ai_name:
        ai_name = get_current_ai()
    else:
        ai_name = ai_name.lower()
    
    return AI_PERSONALITIES.get(ai_name, AI_PERSONALITIES["jarvis"])


def list_available_ais() -> str:
    """List all available AI."""
    result = "═══ AVAILABLE AI SYSTEMS ═══\n"
    current = get_current_ai()
    
    for name, info in AI_PERSONALITIES.items():
        prefix = "●" if name == current else "○"
        result += f"\n{prefix} {info['name']}\n"
        result += f"  {info['description']}\n"
        result += f"  Voice: {info['voice']}\n"
    
    return result.strip()


def switch_ai(ai_name: str) -> str:
    """Switch between AI personalities."""
    return set_current_ai(ai_name)


# === UNIFIED COMMAND INTERFACE ===

def call_jarvis(command: str) -> str:
    """Call JARVIS with command."""
    current = get_current_ai()
    if current != "jarvis":
        set_current_ai("jarvis")
    return f"JARVIS: {command}"


def call_friday(command: str) -> str:
    """Call FRIDAY with command."""
    current = get_current_ai()
    if current != "friday":
        set_current_ai("friday")
    return f"FRIDAY: {command}"


def call_edith(command: str) -> str:
    """Call EDITH with command."""
    current = get_current_ai()
    if current != "edith":
        set_current_ai("edith")
    return f"EDITH: {command}"


def call_eve(command: str) -> str:
    """Call EVE (drone) with command."""
    current = get_current_ai()
    if current != "eve":
        set_current_ai("eve")
    return f"EVE: {command}"


# === PERSONALITY-ADAPTIVE RESPONSE ===

def get_adaptive_response(base_response: str, override_personality: str = "") -> str:
    """Get response adapted to current AI personality."""
    if not override_personality:
        override_personality = get_current_ai()
    
    info = get_ai_info(override_personality)
    personality = info.get("personality", "professional")
    
    # Adapt response based on personality
    if personality == "warm":
        # F.R.I.D.A.Y style - warmer, more casual
        if base_response.startswith("Understood"):
            base_response = "Got it!"
        elif "As you wish" in base_response:
            base_response = base_response.replace("As you wish", "Of course!")
    
    elif personality == "military":
        # E.D.I.T.H style - crisp, efficient
        if base_response.startswith("Understood"):
            base_response = "Confirming request."
        elif "I'll help" in base_response:
            base_response = "Task acknowledged. Executing."
    
    elif personality == "stealth":
        # E.V.E style - minimal, direct
        if len(base_response) > 30:
            base_response = base_response[:30] + "."
    
    return base_response


def format_status_display() -> str:
    """Get formatted status display for current AI."""
    ai_name = get_current_ai()
    info = get_ai_info(ai_name)
    
    name = info["name"]
    full_name = info["full_name"]
    desc = info["description"]
    greeting = info["greeting"]
    color = info["color"]
    
    return f"""
╔════════════════════════════════════════╗
║      {name:<28} ║
╠════════════════════════════════╣
���  Full: {full_name:<23} ║
║  Mode: {desc:<24} ║
║  Status: {greeting:<21} ║
╚════════════════════════════════╝
    """.strip()


def get_all_capabilities() -> Dict[str, List[str]]:
    """Get all capabilities by AI."""
    return {
        "jarvis": [
            "System control", "Voice AI", "Screen awareness", 
            "Code generation", "File management", "Web control",
            "Self-evolution", "Self-repair", "Biometric monitoring",
            "Memory persistence", "Multi-agent coordination"
        ],
        "friday": [
            "Voice AI", "Warm conversations", "Emotion detection",
            "Mood matching", "Daily assistance", "Reminders",
            "Weather updates", "Calendar help", "Casual chat",
            "Encouragement", "Comfort mode"
        ],
        "edith": [
            "Battle mode", "Threat detection", "Drone control",
            "Stark network access", "Mission briefing",
            "Tactical display", "Surveillance",
            "Security protocols", "Emergency response",
            "Target tracking", "System lockdown"
        ],
        "eve": [
            "Drone interface", "Hologram control",
            "Precision tasks", "Microscope mode",
            "Stealth mode", "Surveillance",
            "Navigation", "Scanning"
        ]
    }


# === DISPATCHER ===

def marvel_connector(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for Marvel AI connector."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[MarvelConnector] {action}")
    
    try:
        if action == "switch":
            ai = params.get("ai", "")
            if not ai:
                return "Please specify AI: jarvis, friday, edith, or eve"
            return switch_ai(ai)
        
        elif action == "current" or action == "status":
            return format_status_display()
        
        elif action == "list":
            return list_available_ais()
        
        elif action == "info":
            ai = params.get("ai", "")
            if not ai:
                ai = get_current_ai()
            info = get_ai_info(ai)
            return f"{info['name']}: {info['description']}"
        
        elif action == "jarvis":
            cmd = params.get("command", "")
            return call_jarvis(cmd)
        
        elif action == "friday":
            cmd = params.get("command", "")
            return call_friday(cmd)
        
        elif action == "edith":
            cmd = params.get("command", "")
            return call_edith(cmd)
        
        elif action == "eve":
            cmd = params.get("command", "")
            return call_eve(cmd)
        
        elif action == "capabilities":
            ai = params.get("ai", "")
            if not ai:
                ai = get_current_ai()
            caps = get_all_capabilities().get(ai, [])
            return f"{ai.upper()} capabilities:\n" + "\n".join([f"- {c}" for c in caps])
        
        elif action == "all_capabilities":
            all_caps = get_all_capabilities()
            result = "═══ ALL AI CAPABILITIES ═══\n"
            for ai_name, caps in all_caps.items():
                result += f"\n{ai_name.upper()}:\n"
                for c in caps:
                    result += f"  • {c}\n"
            return result.strip()
        
        else:
            ai = get_current_ai()
            info = get_ai_info(ai)
            return f"Active: {info['name']} - {info['greeting']}"
    
    except Exception as e:
        return f"MarvelConnector error: {e}"


if __name__ == "__main__":
    print("=== Marvel AI Connector Test ===")
    
    # List available AIs
    print(list_available_ais())
    
    # Switch between AIs
    print("\n" + switch_ai("friday"))
    print(format_status_display())
    
    print("\n" + switch_ai("edith"))
    print(format_status_display())
    
    print("\n" + switch_ai("jarvis"))
    print(format_status_display())
    
    # Show all capabilities
    print("\n" + marvel_connector({"action": "all_capabilities"}))
    
    print("\n✅ Marvel Connector ready")
