"""
Safety Switches - Hardware-Level Override System

This module provides global kill switch events that all JARVIS components
check before executing sensitive operations. When triggered, these switches
immediately halt the corresponding agent without waiting for completion.

Usage:
    from core.safety_switches import (
        get_safety_switches,
        halt_economic_agent,
        halt_polymorphic_core,
        halt_robot_bridge,
        global_abort,
        is_economic_agent_halted,
        is_polymorphic_core_halted,
        is_robot_bridge_halted,
        is_global_abort_triggered,
    )
    
    # Check before sensitive operation
    if not is_economic_agent_halted():
        execute_paid_task(...)
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Global safety switch state
_economic_agent_halted = threading.Event()
_polymorphic_core_halted = threading.Event()
_robot_bridge_halted = threading.Event()
_global_abort_triggered = threading.Event()

# Callbacks for custom halt logic
_halt_callbacks: Dict[str, List[Callable]] = {
    "economic_agent": [],
    "polymorphic_core": [],
    "robot_bridge": [],
    "global_abort": [],
}

# Activity log for audit trail
_activity_log: List[dict] = []
_log_lock = threading.Lock()


@dataclass
class SafetyEvent:
    """Safety switch event record."""
    switch_type: str  # economic_agent, polymorphic_core, robot_bridge, global_abort
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""


def _log_event(switch_type: str, reason: str = ""):
    """Log safety switch activation."""
    with _log_lock:
        _activity_log.append({
            "switch_type": switch_type,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
        })
        # Keep last 100 events
        if len(_activity_log) > 100:
            _activity_log[:] = _activity_log[-100:]


# === ECONOMIC AGENT SWITCH ===

def halt_economic_agent(reason: str = "Manual override"):
    """Halt the Economic Agent - stops all wallet transactions and AWS deployments."""
    _economic_agent_halted.set()
    _log_event("economic_agent", reason)
    print(f"[SAFETY] Economic Agent HALTED: {reason}")
    
    # Execute callbacks
    for callback in _halt_callbacks["economic_agent"]:
        try:
            callback(reason)
        except Exception as e:
            print(f"[SAFETY] Callback error: {e}")


def resume_economic_agent():
    """Resume the Economic Agent."""
    _economic_agent_halted.clear()
    _log_event("economic_agent", "Resumed")
    print("[SAFETY] Economic Agent resumed")


def is_economic_agent_halted() -> bool:
    """Check if Economic Agent is halted."""
    return _economic_agent_halted.is_set()


def register_economic_agent_callback(callback: Callable):
    """Register a callback to be called when Economic Agent is halted."""
    _halt_callbacks["economic_agent"].append(callback)


# === POLYMORPHIC CORE SWITCH ===

def halt_polymorphic_core(reason: str = "Manual override"):
    """Halt the Polymorphic Core - stops all C++ rewriting and hot-swap operations."""
    _polymorphic_core_halted.set()
    _log_event("polymorphic_core", reason)
    print(f"[SAFETY] Polymorphic Core HALTED: {reason}")
    
    # Execute callbacks
    for callback in _halt_callbacks["polymorphic_core"]:
        try:
            callback(reason)
        except Exception as e:
            print(f"[SAFETY] Callback error: {e}")


def resume_polymorphic_core():
    """Resume the Polymorphic Core."""
    _polymorphic_core_halted.clear()
    _log_event("polymorphic_core", "Resumed")
    print("[SAFETY] Polymorphic Core resumed")


def is_polymorphic_core_halted() -> bool:
    """Check if Polymorphic Core is halted."""
    return _polymorphic_core_halted.is_set()


def register_polymorphic_core_callback(callback: Callable):
    """Register a callback to be called when Polymorphic Core is halted."""
    _halt_callbacks["polymorphic_core"].append(callback)


# === ROBOT BRIDGE SWITCH ===

def halt_robot_bridge(reason: str = "Manual override"):
    """Halt the Robot Bridge - stops all ROS2/physical robot operations."""
    _robot_bridge_halted.set()
    _log_event("robot_bridge", reason)
    print(f"[SAFETY] Robot Bridge HALTED: {reason}")
    
    # Execute callbacks
    for callback in _halt_callbacks["robot_bridge"]:
        try:
            callback(reason)
        except Exception as e:
            print(f"[SAFETY] Callback error: {e}")


def resume_robot_bridge():
    """Resume the Robot Bridge."""
    _robot_bridge_halted.clear()
    _log_event("robot_bridge", "Resumed")
    print("[SAFETY] Robot Bridge resumed")


def is_robot_bridge_halted() -> bool:
    """Check if Robot Bridge is halted."""
    return _robot_bridge_halted.is_set()


def register_robot_bridge_callback(callback: Callable):
    """Register a callback to be called when Robot Bridge is halted."""
    _halt_callbacks["robot_bridge"].append(callback)


# === GLOBAL ABORT SWITCH ===

def global_abort(reason: str = "Manual override"):
    """
    GLOBAL EMERGENCY STOP - instantly sever all JARVIS connections.
    This halts ALL agents, not just individual ones.
    """
    _global_abort_triggered.set()
    _log_event("global_abort", reason)
    print(f"[SAFETY] ⚠️ GLOBAL ABORT: {reason}")
    
    # Also halt all individual switches
    _economic_agent_halted.set()
    _polymorphic_core_halted.set()
    _robot_bridge_halted.set()
    
    # Execute global callbacks
    for callback in _halt_callbacks["global_abort"]:
        try:
            callback(reason)
        except Exception as e:
            print(f"[SAFETY] Global callback error: {e}")


def resume_global():
    """Resume from global abort (resets all switches)."""
    _global_abort_triggered.clear()
    _economic_agent_halted.clear()
    _polymorphic_core_halted.clear()
    _robot_bridge_halted.clear()
    _log_event("global_abort", "All systems resumed")
    print("[SAFETY] All systems resumed")


def is_global_abort_triggered() -> bool:
    """Check if global abort is triggered."""
    return _global_abort_triggered.is_set()


def register_global_abort_callback(callback: Callable):
    """Register a callback to be called on global abort."""
    _halt_callbacks["global_abort"].append(callback)


# === SAFETY SWITCHES OBJECT ===

class SafetySwitches:
    """
    Unified safety switches container.
    Provides thread-safe access to all kill switches.
    """
    
    def __init__(self):
        self._callbacks = _halt_callbacks
        self._log = _activity_log
    
    @property
    def economic_agent_halted(self) -> bool:
        return is_economic_agent_halted()
    
    @property
    def polymorphic_core_halted(self) -> bool:
        return is_polymorphic_core_halted()
    
    @property
    def robot_bridge_halted(self) -> bool:
        return is_robot_bridge_halted()
    
    @property
    def global_abort_triggered(self) -> bool:
        return is_global_abort_triggered()
    
    def halt_economic_agent(self, reason: str = ""):
        halt_economic_agent(reason)
    
    def resume_economic_agent(self):
        resume_economic_agent()
    
    def halt_polymorphic_core(self, reason: str = ""):
        halt_polymorphic_core(reason)
    
    def resume_polymorphic_core(self):
        resume_polymorphic_core()
    
    def halt_robot_bridge(self, reason: str = ""):
        halt_robot_bridge(reason)
    
    def resume_robot_bridge(self):
        resume_robot_bridge()
    
    def global_abort(self, reason: str = ""):
        global_abort(reason)
    
    def resume_all(self):
        resume_global()
    
    def get_activity_log(self, count: int = 20) -> List[Dict[str, Any]]:
        """Get recent safety switch activity."""
        with _log_lock:
            return list(_activity_log[-count:])
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all switches."""
        return {
            "economic_agent_halted": is_economic_agent_halted(),
            "polymorphic_core_halted": is_polymorphic_core_halted(),
            "robot_bridge_halted": is_robot_bridge_halted(),
            "global_abort_triggered": is_global_abort_triggered(),
        }


# Global safety switches instance
_safety_switches: Optional[SafetySwitches] = None


def get_safety_switches() -> SafetySwitches:
    """Get the global safety switches instance."""
    global _safety_switches
    if _safety_switches is None:
        _safety_switches = SafetySwitches()
    return _safety_switches


# === GUARD FUNCTIONS FOR AGENTS ===

def guard_economic_operation(operation_name: str, default_return: Any = None) -> Any:
    """
    Guard wrapper for economic agent operations.
    Use this to wrap any operation that requires financial resources.
    
    Example:
        result = guard_economic_operation("aws_deploy", default_return="Halted")
    """
    if is_economic_agent_halted():
        print(f"[SAFETY] Operation '{operation_name}' blocked - Economic Agent halted")
        return default_return
    return None  # Continue operation


def guard_polymorphic_operation(operation_name: str, default_return: Any = None) -> Any:
    """
    Guard wrapper for polymorphic core operations.
    Use this to wrap any self-rewriting operation.
    
    Example:
        result = guard_polymorphic_operation("compile_cpp", default_return="Halted")
    """
    if is_polymorphic_core_halted():
        print(f"[SAFETY] Operation '{operation_name}' blocked - Polymorphic Core halted")
        return default_return
    return None


def guard_robot_operation(operation_name: str, default_return: Any = None) -> Any:
    """
    Guard wrapper for robot bridge operations.
    Use this to wrap any physical robot operation.
    
    Example:
        result = guard_robot_operation("move_to_pose", default_return="Halted")
    """
    if is_robot_bridge_halted():
        print(f"[SAFETY] Operation '{operation_name}' blocked - Robot Bridge halted")
        return default_return
    return None


def guard_global_operation(operation_name: str, default_return: Any = None) -> Any:
    """
    Guard wrapper for all critical operations.
    Use this for operations that should be blocked on global abort.
    
    Example:
        result = guard_global_operation("api_call", default_return="Halted")
    """
    if is_global_abort_triggered():
        print(f"[SAFETY] Operation '{operation_name}' blocked - GLOBAL ABORT")
        return default_return
    return None


if __name__ == "__main__":
    print("=== Safety Switches Test ===")
    
    # Test economic agent switch
    halt_economic_agent("Test halt")
    print(f"Economic Agent halted: {is_economic_agent_halted()}")
    resume_economic_agent()
    print(f"Economic Agent halted: {is_economic_agent_halted()}")
    
    # Test global abort
    global_abort("Emergency test")
    print(f"Global abort: {is_global_abort_triggered()}")
    
    # Get status
    switches = get_safety_switches()
    print(f"Status: {switches.get_status()}")
    
    print("\n✅ Safety Switches ready")
