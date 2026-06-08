# MARK LXXX (80) "GOD'S EYE" PROTOCOL - Implementation Plan

## Overview
Transitioning JARVIS from a desktop-bound assistant to a truly Omnipresent (everywhere) and Omniscient (all-knowing) entity through Ambient Computing and Agentic OS Layers.

---

## Phase 1: The Omniscient Core (Knowledge Graph & Memory)

### 1.1 MemU - Three-Layer Memory Model
**Files to create/modify:**
- `core/mem_u.py` - NEW: Three-layer memory (Short-term, Long-term, Procedural)
- `core/synapse_knowledge_graph.py` - UPGRADE: Enhanced entity extraction
- `memory/memory_manager.py` - ENHANCE: Tiered storage

**Implementation:**
- Short-term: Rolling buffer of last 100 interactions
- Long-term: Enhanced JSON storage with embeddings
- Procedural: Task patterns and workflows

### 1.2 Global Data Siphon
**Files to create:**
- `core/data_siphon.py` - NEW: Background data pipeline
- `core/trend_adapter.py` - ENHANCE: Real-time trend monitoring

**Features:**
- GitHub trending monitoring
- NGN/USDT liquidity tracking (mock for now)
- AI paper ArXiv monitoring

### 1.3 Agentic Intent Execution
**Files to modify:**
- `agent/executor.py` - ENHANCE: Auto-execution without confirmation
- `core/agent_engine.py` - ADD: Intent detection

---

## Phase 2: The Omnipresent Mesh (Network Layer)

### 2.1 Tailscale/ZeroTier Mesh Configuration
**Files to create/modify:**
- `core/mesh_network.py` - NEW: Mesh network manager
- `config/settings.json` - ADD: Mesh settings

### 2.2 Ambient Audio Interface
**Files to create:**
- `core/audio_bridge.py` - NEW: Wearable audio bridge
- `actions/wake_word.py` - ENHANCE: Custom wake word

### 2.3 Headless Background Daemon
**Files to create:**
- `jarvis_daemon.py` - NEW: Background service entry point
- `actions/clipboard_manager.py` - ENHANCE: Clipboard daemon

---

## Phase 3: Physical Omnipresence (IoT & Spatial)

### 3.1 mmWave Presence Tracking Interface
**Files to create:**
- `core/spatial_awareness.py` - NEW: Spatial presence manager
- `actions/smart_home.py` - ENHANCE: mmWave integration

### 3.2 Local Edge Fallback
**Files to create:**
- `core/edge_fallback.py` - NEW: Local LLM fallback
- `core/llm_bridge.py` - NEW: Ollama/MLX bridge

### 3.3 Home Assistant MQTT Integration
**Files to modify:**
- `actions/smart_home.py` - ENHANCE: Full MQTT support
- `config/smart_home.json` - CREATE: Configuration

---

## Phase 4: Multi-Persona Swarm

### 4.1 MQTT Message Broker
**Files to create:**
- `core/swarm_coordinator.py` - NEW: Swarm MQTT coordinator
- `core/persona_daemon.py` - NEW: Individual persona daemons

### 4.2 Persona Background Tasks
**Files to modify:**
- `actions/marvel_connector.py` - ENHANCE: Background persona modes
- `agent/multi_agent.py` - ENHANCE: Swarm agent types

---

## Phase 5: Zero-Trust Autonomous Defense

### 5.1 Sandboxed Clones
**Files to modify:**
- `actions/sandbox/shadow_sandbox.py` - ENHANCE: Nano-clone system
- `core/safety_switches.py` - ADD: Biometric switch

### 5.2 Biometric Dead-Man's Switch
**Files to create:**
- `core/biometric_telemetry.py` - NEW: Wearable biometric check
- `core/proximity_check.py` - NEW: Device proximity monitoring

---

## Phase 6: Proactive Digital Sentry

### 6.1 Predictive OS Prefetching
**Files to create:**
- `core/prefetch_engine.py` - NEW: Habit-based prefetch
- `core/context_tracker.py` - ENHANCE: Enhanced tracking

### 6.2 Webhook Interception
**Files to create:**
- `core/webhook_router.py` - NEW: Notification interception
- `core/self_repair.py` - ENHANCE: Auto-remediation

---

## Phase 7: Omni Engine Orchestrator

### 7.1 Central Omni Engine
**Files to create:**
- `core/omni_engine.py` - NEW: Main orchestrator

### 7.2 System Integration
**Files to modify:**
- `main.py` - ADD: Omni engine initialization
- `ui.py` - ADD: Omni UI elements

---

## Implementation Priority

### Priority 1 (Core - Week 1):
1. `core/omni_engine.py` - Central orchestrator
2. `core/mem_u.py` - Three-layer memory
3. `core/data_siphon.py` - Background data pipeline

### Priority 2 (Network - Week 2):
4. `core/mesh_network.py` - Mesh network
5. `jarvis_daemon.py` - Background daemon
6. `core/spatial_awareness.py` - Spatial manager

### Priority 3 (Intelligence - Week 3):
7. `core/edge_fallback.py` - Local LLM
8. `core/swarm_coordinator.py` - MQTT swarm
9. `core/prefetch_engine.py` - Predictive prefetch

### Priority 4 (Security - Week 4):
10. `core/biometric_telemetry.py` - Biometric Dead-Man's
11. `core/webhook_router.py` - Notification routing
12. Integration testing

---

## Dependencies Required

```
# Already in requirements.txt:
- paho-mqtt
- homeassistant
- psutil
- networkx>=3.0

# New dependencies to add:
- openai (for local LLM fallback)
- pyyaml (config)
- requests-oauthlib (webhooks)

# Optional for hardware:
- pyserial (mmWave sensors)
- bluepy (Bluetooth proximity)
```

---

## Success Metrics

- [x] Omni Engine core implemented (`core/omni_engine.py`)
- [x] Three-layer memory implemented (`core/mem_u.py`)
- [x] Data Siphon implemented (`core/data_siphon.py`)
- [ ] Knowledge graph populated with 100+ entities
- [ ] Multi-device mesh connectivity (requires Tailscale/ZeroTier)
- [ ] Local LLM fallback (requires Ollama)
- [ ] Persona swarm responding to MQTT
- [ ] Predictive app prefetching active
- [ ] Biometric dead-man's switch operational

---

## Implementation Status (Complete)

✅ Phase 1 Complete:
- core/omni_engine.py - Central orchestrator with memory integration
- core/mem_u.py - Three-layer memory (Short-term, Long-term, Procedural)
- core/data_siphon.py - Background data pipeline

⏳ Phase 2-7 (Planned):
- core/mesh_network.py - Requires Tailscale/ZeroTier setup
- core/edge_fallback.py - Requires Ollama installation
- core/swarm_coordinator.py - Requires MQTT broker
- core/prefetch_engine.py - Requires habit tracking data
- core/biometric_telemetry.py - Requires wearable device

---

## Quick Start

```python
# Initialize Omni Engine
from core.omni_engine import get_omni_engine

engine = get_omni_engine()
engine.start()

# Test memory
from core.mem_u import get_mem_u
mem = get_mem_u()
mem.add_short_term("user asked about weather", "weather query", "informational")
mem.add_long_term("user_name", "Fatih", "identity")

# Test data siphon
from core.data_siphon import get_data_siphon
siphon = get_data_siphon()
data = siphon.ingest_world_data()
print(siphon.get_morning_briefing())
```
