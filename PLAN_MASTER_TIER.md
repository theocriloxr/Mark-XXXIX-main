# Master-Tier Upgrades Implementation Plan

## Overview
Implementing four major upgrades + OS bridge to finalize the JARVIS ecosystem:

1. **Synapse Knowledge Graph** - Relational memory with multi-hop reasoning
2. **Shadow Sandbox** - Isolated container testing for self-evolving code  
3. **Agentic GDP Tracker** - Financial tracking dashboard for AI P&L
4. **Neural Mirroring** - UI cognitive adaptation to brain states

## Additional Requirements:
5. **Universal OS Bridge** - Cross-platform abstraction
6. **Synapse-Sync** - P2P memory sharing

---

## Upgrade 1: Synapse Knowledge Graph

### File: `core/synapse_knowledge_graph.py` (NEW)

**Purpose**: NetworkX-based knowledge graph for relational memory

**Features**:
- Entity extraction from any memory
- Relations: works_on, hosts, owns, depends_on, manages, uses, created_by
- Multi-hop queries: Find paths between entities
- Persistent storage as JSON

**Implementation**:
```python
import networkx as nx
import json
from pathlib import Path

class SynapseKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._entities = {}  # entity_id -> {name, type, properties}
        self._load()
    
    def add_entity(self, entity_id: str, name: str, entity_type: str, properties: dict = None):
        """Add entity to graph"""
        
    def add_relation(self, from_id: str, relation: str, to_id: str, properties: dict = None):
        """Add relation between entities"""
        
    def query_path(self, start_entity: str, end_entity: str) -> list:
        """Multi-hop reasoning: find path between entities"""
        
    def save(self):
        """Persist graph to JSON"""
        
    def load(self):
        """Load graph from JSON"""
```

### Integration:
- Modify `memory/memory_manager.py` to extract entities before saving
- Add to tool declarations in `main.py`

---

## Upgrade 2: Shadow Sandbox  

### File: `actions/sandbox/shadow_sandbox.py` (NEW)

**Purpose**: Docker-based isolated testing environment

**Features**:
- Spin up headless Docker container
- Chaos tests: memory leak, unauthorized socket detection
- Safe code execution before deployment
- Result verification before "ascension"

**Implementation**:
```python
import docker

class ShadowSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.container = None
    
    def deploy(self, code: str, language: str = "python") -> str:
        """Deploy code to sandbox container"""
        
    def run_chaos_tests(self, code: str) -> dict:
        """Run safety tests"""
        
    def verify_and_ascend(self, code: str) -> bool:
        """Verify safe -> deploy to production"""
```

### File: `actions/sandbox/chaos_tests.py` (NEW)

**Chaos Tests**:
- Memory leak detection
- Unauthorized socket attempts
- Infinite loop detection
- Resource exhaustion prevention

---

## Upgrade 3: Agentic GDP Tracker  

### File: `actions/financials.py` (NEW)

**Purpose**: Track JARVIS's P&L as autonomous business

**Features**:
- Track AWS costs, LLM token costs, crypto transactions
- Value Generated metrics: tasks completed, code written
- Real-time P&L statement
- Sub-agent profitability analysis

**Implementation**:
```python
class AgenticFinancials:
    def __init__(self):
        self.expenses = []
        self.revenue = []
        self.tasks_completed = 0
    
    def track_expense(self, category: str, amount: float, description: str):
        """Track any expense"""
        
    def track_value(self, task_type: str, value: float):
        """Track value generated"""
        
    def get_pl_statement(self) -> dict:
        """Get P&L statement"""
        
    def get_agent_profitability(self) -> dict:
        """Which sub-agents are profitable"""
```

### Integration:
- Extend `actions/economic_agent.py`
- Add to `main.py` tool declarations

---

## Upgrade 4: Neural Mirroring  

### File: `core/neural_mirror.py` (NEW)

**Purpose**: Adapt UI based on brain states

**Features**:
- Listen to cognitive state from neural_decoding
- UI modes: Focused (minimalist), Stressed (enlarged buttons), Relaxed (standard), Confused (help offered)
- Color palette shifts based on state

**Implementation**:
```python
class NeuralMirror:
    def __init__(self):
        self.current_mode = "standard"
        
    def adapt_ui(self, cognitive_state: str):
        """Adapt UI based on brain state"""
        
    def enable_minimalist_mode(self):
        """Hide notifications, dim dashboard"""
        
    def enable_focus_mode(self):
        """Calm deep blue, hide non-essential"""
        
    def enable_help_mode(self):
        """Enlarge help options"""
```

### Integration:
- Link to `core/neural_decoding.py`
- Link to `ui_command_center.py` styling

---

## Upgrade 5: Universal OS Bridge  

### File: `core/bridge.py` (NEW)

**Purpose**: Cross-platform abstraction

**Features**:
- Detect OS: Windows, macOS, Linux
- Unified API for: get_active_window, notify, get_resource_usage
- Platform-specific backends

**Implementation**:
```python
import platform
import subprocess

class OSBridge:
    def __init__(self):
        self.os_type = platform.system()
        
    def get_active_window_title(self):
        if self.os_type == "Windows":
            # pygetwindow / ctypes
        elif self.os_type == "Darwin":
            # AppleScript
        elif self.os_type == "Linux":
            # xprop
            
    def notify(self, title: str, message: str):
        """Cross-platform notifications"""
```

### Integration:
- Replace `core/context_tracker.py` imports
- Update `main.py` imports

---

## Upgrade 6: Synapse-Sync (P2P Memory)

### File: `core/synapse_sync.py` (NEW)

**Purpose**: Share memory across devices

**Features**:
- UDP/TCP listener for memory sync
- Broadcast new memories to peer devices
- Requires Tailscale VPN for same network

**Implementation**:
```python
class SynapseSync(threading.Thread):
    def __init__(self, peer_ips: list = None):
        self.peer_ips = peer_ips or []
        
    def broadcast_memory(self, memory_text: str):
        """Send to all peers"""
        
    def process_incoming_memory(self, payload: dict):
        """Inject synced memory into local ChromaDB"""
```

---

## Implementation Order

| # | Module | File | Dependency | Priority |
|---|--------|------|------------|-----------|
| 1 | OS Bridge | core/bridge.py | None | HIGH |
| 2 | Synapse KG | core/synapse_knowledge_graph.py | bridge.py | HIGH |
| 3 | Shadow Sandbox | actions/sandbox/shadow_sandbox.py | bridge.py | MEDIUM |
| 4 | GDP Tracker | actions/financials.py | None | MEDIUM | 
| 5 | Neural Mirror | core/neural_mirror.py | neural_decoding.py | LOW |
| 6 | Synapse-Sync | core/synapse_sync.py | synapse_kg.py | LOW |

---

## Files to Modify

| File | Changes |
|------|--------|
| main.py | Add tool declarations, integrate bridge |
| memory/memory_manager.py | Add entity extraction hooks |
| core/agent_engine.py | Import bridge for context |
| ui_command_center.py | Add neural mirror styling |
| requirements.txt | Add networkx (already added), docker |

---

## Dependencies (Already in requirements.txt)
- networkx>=3.0 ✓
- docker>=7.0 ✓ (needs addition)

---

## Follow-up Steps

1. Install: `pip install networkx docker`
2. Create core/synapse_knowledge_graph.py
3. Create core/bridge.py
4. Create actions/sandbox/shadow_sandbox.py  
5. Create actions/financials.py
6. Create core/neural_mirror.py
7. Integrate into main.py
8. Test each module
9. Verify Command Center integration
