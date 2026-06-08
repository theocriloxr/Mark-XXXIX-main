"""
Omni Engine - Central orchestrator for Mark LXXX (80) "God's Eye" Protocol
===================================================================

The Omni Engine serves as the central brain for JARVIS's omnipresence.
It coordinates all background services, memory systems, and agentic workflows.

Key Capabilities:
- 24/7 ambient loop for continuous world monitoring
- Multi-persona swarm coordination via MQTT
- Knowledge graph integration with MemU memory
- Edge fallback for offline operation
- Biometric dead-man's switch
- Predictive prefetching

Usage:
    from core.omni_engine import OmniPresenceEngine, get_omni_engine
    
    engine = get_omni_engine()
    engine.start()
"""

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


def get_base_dir() -> Path:
    """Get base directory."""
    import sys
    from pathlib import Path
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


class OmniState(Enum):
    """Omni Engine states."""
    INITIALIZING = "initializing"
    ONLINE = "online"
    AMBIENT = "ambient"
    HIGH_PERFORMANCE = "high_performance"
    DEGRADED = "degraded"
    OFFLINE = "offline"


@dataclass
class OmniMetrics:
    """System metrics for Omni Engine."""
    uptime: float = 0
    cycles_completed: int = 0
    context_ingested: int = 0
    intents_executed: int = 0
    memory_entities: int = 0
    active_personas: int = 0
    swarm_messages: int = 0
    edge_fallbacks: int = 0
    prefetch_hits: int = 0


class OmniPresenceEngine:
    """
    Central orchestrator for JARVIS's omnipresence.
    Manages all background services and coordinates intelligence.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._state = OmniState.INITIALIZING
        self._start_time = time.time()
        self._metrics = OmniMetrics()
        
        # Threading
        self._ambient_loop_thread: Optional[threading.Thread] = None
        self._is_running = False
        self._lock = threading.Lock()
        
        # Subsystems
        self._knowledge_graph = None
        self._mem_u = None
        self._data_siphon = None
        self._swarm_coordinator = None
        self._edge_fallback = None
        self._spatial_awareness = None
        self._prefetch_engine = None
        self._biometric_telemetry = None
        self._webhook_router = None
        
        # Persona daemons
        self._persona_daemons: Dict[str, threading.Thread] = {}
        
        # Callbacks
        self._on_state_change: List[Callable] = []
        self._on_intent_detected: List[Callable] = []
        
        # Initialize subsystems
        self._init_subsystems()
        
        self._initialized = True
        logger.info("[OMNI] Omni Engine initialized")
    
    def _init_subsystems(self):
        """Initialize all subsystems."""
        # Knowledge Graph (Synapse)
        try:
            from core.synapse_knowledge_graph import get_synapse_kg
            self._knowledge_graph = get_synapse_kg()
            self._metrics.memory_entities = len(self._knowledge_graph.entities)
        except Exception as e:
            logger.warning(f"[OMNI] Knowledge graph init failed: {e}")
        
        # MemU Memory (if available)
        try:
            from core.mem_u import get_mem_u
            self._mem_u = get_mem_u()
        except ImportError:
            logger.info("[OMNI] MemU not available, using legacy memory")
        
        # Data Siphon (background data pipeline)
        try:
            from core.data_siphon import get_data_siphon
            self._data_siphon = get_data_siphon()
        except ImportError:
            logger.info("[OMNI] Data Siphon not available, skipping")
        
        # Swarm Coordinator (MQTT)
        try:
            from core.swarm_coordinator import get_swarm_coordinator
            self._swarm_coordinator = get_swarm_coordinator()
        except ImportError:
            logger.info("[OMNI] Swarm Coordinator not available, skipping")
        
        # Edge Fallback (local LLM)
        try:
            from core.edge_fallback import get_edge_fallback
            self._edge_fallback = get_edge_fallback()
        except ImportError:
            logger.info("[OMNI] Edge Fallback not available, skipping")
        
        # Spatial Awareness (mmWave)
        try:
            from core.spatial_awareness import get_spatial_awareness
            self._spatial_awareness = get_spatial_awareness()
        except ImportError:
            logger.info("[OMNI] Spatial Awareness not available, skipping")
        
        # Prefetch Engine
        try:
            from core.prefetch_engine import get_prefetch_engine
            self._prefetch_engine = get_prefetch_engine()
        except ImportError:
            logger.info("[OMNI] Prefetch Engine not available, skipping")
        
        # Biometric Telemetry (Dead-Man's Switch)
        try:
            from core.biometric_telemetry import get_biometric_telemetry
            self._biometric_telemetry = get_biometric_telemetry()
        except ImportError:
            logger.info("[OMNI] Biometric Telemetry not available, skipping")
        
        # Webhook Router
        try:
            from core.webhook_router import get_webhook_router
            self._webhook_router = get_webhook_router()
        except ImportError:
            logger.info("[OMNI] Webhook Router not available, skipping")
    
    def start(self):
        """Start the Omni Engine."""
        if self._is_running:
            return "[OMNI] Already running"
        
        self._is_running = True
        self._state = OmniState.ONLINE
        
        # Start ambient loop
        self._ambient_loop_thread = threading.Thread(
            target=self._ambient_loop,
            daemon=True
        )
        self._ambient_loop_thread.start()
        
        logger.info("[OMNI] Omni Engine started")
        return "[OMNI] God's Eye online"
    
    def stop(self):
        """Stop the Omni Engine."""
        self._is_running = False
        self._state = OmniState.OFFLINE
        
        # Stop all persona daemons
        for name, thread in self._persona_daemons.items():
            if thread.is_alive():
                thread.join(timeout=2)
        
        logger.info("[OMNI] Omni Engine stopped")
        return "[OMNI] God's Eye offline"
    
    def _ambient_loop(self):
        """Main ambient loop - runs 24/7 in background."""
        self._state = OmniState.AMBIENT
        
        cycle_count = 0
        while self._is_running:
            try:
                cycle_start = time.time()
                cycle_count += 1
                self._metrics.cycles_completed = cycle_count
                
                # 1. Ingest world data
                if self._data_siphon:
                    try:
                        context = self._data_siphon.ingest_world_data()
                        if context:
                            self._metrics.context_ingested += 1
                    except Exception as e:
                        logger.debug(f"[OMNI] Data siphon error: {e}")
                
                # 2. Check for user intent
                if self.detect_user_intent():
                    self._metrics.intents_executed += 1
                    for callback in self._on_intent_detected:
                        try:
                            callback()
                        except Exception:
                            pass
                
                # 3. Update knowledge graph
                if self._knowledge_graph:
                    self._metrics.memory_entities = len(self._knowledge_graph.entities)
                
                # 4. Check biometric status
                if self._biometric_telemetry:
                    if not self._biometric_telemetry.is_user_present():
                        # User may be away - reduce activity
                        self._state = OmniState.DEGRADED
                
                # 5. Spatial awareness
                if self._spatial_awareness:
                    self._spatial_awareness.check_presence()
                
                # 6. Swarm coordination
                if self._swarm_coordinator:
                    self._metrics.active_personas = self._swarm_coordinator.get_active_count()
                    self._metrics.swarm_messages = self._swarm_coordinator.get_message_count()
                
                # Update uptime
                self._metrics.uptime = time.time() - self._start_time
                
                # Sleep for next cycle (default 10 seconds)
                cycle_time = time.time() - cycle_start
                sleep_time = max(1, 10 - cycle_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"[OMNI] Ambient loop error: {e}")
                time.sleep(10)
    
    def detect_user_intent(self) -> bool:
        """Detect user intent from context."""
        try:
            # Check window tracker for active app patterns
            from core.context_tracker import get_window_tracker
            tracker = get_window_tracker()
            
            if tracker and tracker.is_running:
                current_window = tracker.get_current_window()
                
                # Check prefetch engine
                if self._prefetch_engine:
                    if self._prefetch_engine.should_prefetch(current_window):
                        self._metrics.prefetch_hits += 1
                        return True
                
                # Check for intent patterns
                if current_window:
                    # Simple pattern matching
                    intent_keywords = ["meeting", "call", "email", "pay", "transfer"]
                    for keyword in intent_keywords:
                        if keyword in current_window.lower():
                            return True
            
            return False
        except Exception:
            return False
    
    def execute_agentic_workflow(self, intent: str) -> str:
        """Execute an agentic workflow based on detected intent."""
        logger.info(f"[OMNI] Executing intent: {intent}")
        
        # This would integrate with the agent system
        # For now, return the intent for processing
        return f"Intent detected: {intent}"
    
    def get_state(self) -> OmniState:
        """Get current Omni state."""
        return self._state
    
    def get_metrics(self) -> OmniMetrics:
        """Get system metrics."""
        return self._metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status."""
        return {
            "state": self._state.value,
            "uptime": self._metrics.uptime,
            "cycles": self._metrics.cycles_completed,
            "contexts": self._metrics.context_ingested,
            "intents": self._metrics.intents_executed,
            "entities": self._metrics.memory_entities,
            "personas": self._metrics.active_personas,
            "swarm_msgs": self._metrics.swarm_messages,
            "edge_fallbacks": self._metrics.edge_fallbacks,
            "prefetch_hits": self._metrics.prefetch_hits,
            "knowledge_graph": self._knowledge_graph is not None,
            "data_siphon": self._data_siphon is not None,
            "swarm_coordinator": self._swarm_coordinator is not None,
            "edge_fallback": self._edge_fallback is not None,
            "spatial_awareness": self._spatial_awareness is not None,
            "prefetch_engine": self._prefetch_engine is not None,
            "biometric": self._biometric_telemetry is not None,
            "webhook_router": self._webhook_router is not None,
        }
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for Omni events."""
        if event == "state_change":
            self._on_state_change.append(callback)
        elif event == "intent_detected":
            self._on_intent_detected.append(callback)
    
    def switch_persona(self, persona: str) -> str:
        """Switch active persona."""
        try:
            from actions.marvel_connector import switch_ai
            return switch_ai(persona)
        except Exception as e:
            return f"Persona switch failed: {e}"
    
    def broadcast_to_swarm(self, message: Dict[str, Any]) -> str:
        """Broadcast message to persona swarm."""
        if self._swarm_coordinator:
            self._swarm_coordinator.broadcast(message)
            return "Broadcast sent to swarm"
        return "Swarm coordinator not available"
    
    def query_knowledge_graph(self, query: str) -> str:
        """Query the knowledge graph."""
        if self._knowledge_graph:
            results = self._knowledge_graph.search(query)
            if results:
                lines = ["Knowledge Graph Results:"]
                for r in results[:5]:
                    lines.append(f"  - {r}")
                return "\n".join(lines)
            return "No results found"
        return "Knowledge graph not available"
    
    def enable_edge_fallback(self) -> bool:
        """Enable local LLM edge fallback."""
        if self._edge_fallback:
            return self._edge_fallback.enable()
        return False
    
    def disable_edge_fallback(self) -> bool:
        """Disable local LLM edge fallback."""
        if self._edge_fallback:
            return self._edge_fallback.disable()
        return False
    
    def is_edge_fallback_active(self) -> bool:
        """Check if edge fallback is active."""
        if self._edge_fallback:
            return self._edge_fallback.is_active()
        return False


# === GLOBAL INSTANCE ===

_omni_engine: Optional[OmniPresenceEngine] = None


def get_omni_engine() -> OmniPresenceEngine:
    """Get global Omni Engine instance."""
    global _omni_engine
    if _omni_engine is None:
        _omni_engine = OmniPresenceEngine()
    return _omni_engine


# === DISPATCHER ===

def omni_engine(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for Omni Engine."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[OmniEngine] {action}")
    
    try:
        engine = get_omni_engine()
        
        if action == "start":
            return engine.start()
        
        elif action == "stop":
            return engine.stop()
        
        elif action == "status":
            status = engine.get_status()
            lines = [
                f"State: {status['state']}",
                f"Uptime: {status['uptime']:.0f}s",
                f"Cycles: {status['cycles']}",
                f"Entities: {status['entities']}",
                f"Personas: {status['personas']}",
            ]
            
            subsystems = []
            if status.get("knowledge_graph"):
                subsystems.append("KG")
            if status.get("data_siphon"):
                subsystems.append("Data")
            if status.get("swarm_coordinator"):
                subsystems.append("Swarm")
            if status.get("edge_fallback"):
                subsystems.append("Edge")
            if status.get("spatial_awareness"):
                subsystems.append("Spatial")
            if status.get("prefetch_engine"):
                subsystems.append("Prefetch")
            if status.get("biometric"):
                subsystems.append("Bio")
            
            if subsystems:
                lines.append(f"Subsystems: {', '.join(subsystems)}")
            
            return " | ".join(lines)
        
        elif action == "metrics":
            metrics = engine.get_metrics()
            return (
                f"Cycles: {metrics.cycles_completed} | "
                f"Context: {metrics.context_ingested} | "
                f"Intents: {metrics.intents_executed} | "
                f"Prefetch: {metrics.prefetch_hits}"
            )
        
        elif action == "persona":
            persona = params.get("persona", "jarvis")
            return engine.switch_persona(persona)
        
        elif action == "broadcast":
            message = params.get("message", "")
            return engine.broadcast_to_swarm({"message": message})
        
        elif action == "query":
            query = params.get("query", "")
            return engine.query_knowledge_graph(query)
        
        elif action == "edge_on":
            if engine.enable_edge_fallback():
                return "Edge fallback enabled"
            return "Edge fallback not available"
        
        elif action == "edge_off":
            if engine.disable_edge_fallback():
                return "Edge fallback disabled"
            return "Edge fallback not available"
        
        elif action == "edge_status":
            if engine.is_edge_fallback_active():
                return "Edge fallback: ACTIVE"
            return "Edge fallback: INACTIVE"
        
        else:
            return engine.get_status()["state"]
    
    except Exception as e:
        return f"OmniEngine error: {e}"


if __name__ == "__main__":
    print("=== Omni Engine Test ===")
    
    engine = get_omni_engine()
    print(engine.get_status())
    
    # Start engine
    print("\n" + engine.start())
    time.sleep(2)
    
    print("\n" + omni_engine({"action": "status"}))
    
    # Stop engine
    print("\n" + engine.stop())
    
    print("\n✅ Omni Engine ready")
