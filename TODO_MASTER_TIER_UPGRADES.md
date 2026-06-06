# MASTER-TIER UPGRADES IMPLEMENTATION PLAN

## Overview
Implementing four major upgrades to finalize the JARVIS ecosystem:
1. **Synapse Knowledge Graph** - Relational memory with multi-hop reasoning
2. **Shadow Sandbox** - Isolated container testing for self-evolving code
3. **Agentic GDP Tracker** - Financial tracking dashboard for AI P&L
4. **Neural Mirroring** - UI cognitive adaptation to brain states

---

## UPGRADE 1: SYNAPSE KNOWLEDGE GRAPH

### Purpose
Give JARVIS human-like relational memory that can perform multi-hop reasoning. Instead of just storing text chunks (Vector RAG), JARVIS will extract Entities and Relations to answer complex queries like "Who is the lead dev on the project that Ujo is currently hosting?"

### Files to Create
| File | Purpose |
|------|---------|
| `core/synapse_knowledge_graph.py` | NetworkX-based knowledge graph with entity extraction |

### Files to Modify
| File | Changes |
|------|---------|
| `requirements.txt` | Add `networkx>=3.0` |
| `memory/memory_manager.py` | Integrate entity extraction when saving memories |

### Implementation Details
```python
# Storage: NetworkX MultiDiGraph for directed relationships
# Persistence: Save/load graph as JSON

# Entity Types:
- PERSON: Alice, Bob, Developer names
- PROJECT: SignalRank, Ujo, Jarvis
- TOOL: code_helper, dev_agent
- LOCATION: server, laptop, cloud

# Relation Types:
- "works_on": person → project
- "hosts": location → project
- "owns": person → tool
- "depends_on": tool → tool
- "manages": person → project
- "uses": project → tool
- "created_by": project → person

# Key Methods:
- add_entity(name, entity_type, properties)
- add_relation(source, relation, target)
- find_path(start_entity, end_entity)  # Multi-hop reasoning
- query_natural(question)  # e.g., "Who manages the project that Ujo hosts?"
- save_graph() / load_graph()
```

---

## UPGRADE 2: SHADOW SANDBOX

### Purpose
Create an isolated virtual OS layer (Docker container) to test self-evolving code before it runs on physical hardware. This prevents crashes from Polymorphic Core or Evolution Lab generated code.

### Files to Create
| File | Purpose |
|------|---------|
| `actions/sandbox/shadow_sandbox.py` | Docker SDK integration for container deployment |
| `actions/sandbox/chaos_tests.py` | Safety test suite for code verification |

### Files to Modify
| File | Changes |
|------|---------|
| `requirements.txt` | Add `docker>=7.0` |
| `actions/sandbox/__init__.py` | Update sandbox config, add auto-deploy options |

### Implementation Details
```python
# Shadow Sandbox Features:
- Spin up headless Docker container on demand
- Deploy generated code / evolved modules
- Run "Chaos Tests":
  * Memory leak detection (tracemalloc)
  * Unauthorized socket attempts
  * File system access audit
  * CPU infinite loop detection
- Return verification report
- "Ascend" only verified safe code

# Container Config:
- Image: python:3.11-slim (headless)
- Network: isolated (no external access)
- Memory limit: 512MB
- CPU limit: 1 core
- Timeout: 60 seconds per test

# Key Methods:
- deploy_to_sandbox(code, language)
- run_chaos_tests(container_id)
- verify_ascension(test_results)
- cleanup_container(container_id)
```

---

## UPGRADE 3: AGENTIC GDP TRACKER

### Purpose
Track JARVIS as a sovereign economic actor. Monitor every cent spent (AWS, tokens, crypto) against value generated (tasks completed, code written). Real-time P&L statement for AI sub-agents.

### Files to Create
| File | Purpose |
|------|---------|
| `actions/financials.py` | AgenticFinancials module for P&L tracking |

### Files to Modify
| File | Changes |
|------|---------|
| `actions/economic_agent.py` | Extend with GDP tracking integration |
| `main.py` | Add financials tool declaration |
| `ui_command_center.py` | Add P&L panel to Command Center |

### Implementation Details
```python
# Cost Tracking:
- AWS: API calls, EC2 instances
- LLM Tokens: Gemini/Claude usage
- Crypto: Wallet transactions

# Value Generated:
- Tasks completed (count)
- Code written (lines)
- Files processed
- Research queries answered

# P&L Statement:
daily_revenue    - daily_costs    = daily_profit
total_revenue   - total_costs   = total_profit

# Sub-agent Profitability:
- track per sub-agent (researcher, engineer, vision)
- profit_per_agent = value_by_agent / cost_by_agent

# Key Methods:
- track_cost(category, amount, description)
- track_value(category, amount, description)
- get_pl_statement()  # Daily + Total P&L
- get_agent_profitability()
- get_daily_report()
- get_cost_breakdown()
```

---

## UPGRADE 4: NEURAL MIRRORING

### Purpose
Bridge the final gap between JARVIS's biological user and the PySide6 UI. The interface physically adapts based on real-time brain states (BCI input).

### Files to Create
| File | Purpose |
|------|---------|
| `core/neural_mirror.py` | UI cognitive adaptation based on neural states |

### Files to Modify
| File | Changes |
|------|---------|
| `core/neural_decoding.py` | Add trigger support for UI callbacks |
| `ui_command_center.py` | Implement dynamic styling based on brain state |

### Implementation Details
```python
# Brain State → UI Adaptation:
- Focused (Beta high):
  * Minimalist Mode
  * Hide all notifications
  * Dim non-essential elements
  * Color palette: calm deep blue (#0a1628)
  
- Stressed (Beta high + Theta):
  * Enlarge Emergency Stop buttons
  * Offer to simplify current task
  * Reduce complexity
  * Reduce notifications
  
- Relaxed (Alpha high):
  * Standard Dashboard Mode
  * Show all features
  * Full color palette
  
- Confused (Theta high):
  * Highlight issues
  * Offer help proactively
  * Show simplified view
  * Increase element spacing

# Key Methods:
- set_ui_mode(state)
- adapt_to_brainwaves(wave_data)
- update_command_center_styling(cognitive_state)
- trigger_neural_action(state, action)
```

---

## DEPENDENCIES TO ADD

```
# Add to requirements.txt
networkx>=3.0       # For Knowledge Graph
docker>=7.0         # For Shadow Sandbox
```

---

## IMPLEMENTATION ORDER

1. **Synapse Knowledge Graph** (Foundation - relational memory)
2. **Shadow Sandbox** (Safety - test before deployment)
3. **Agentic GDP Tracker** (Financial tracking)
4. **Neural Mirroring** (UI adaptation)

---

## INTEGRATION STEPS

### Step 1: Dependencies
```bash
pip install networkx docker
```

### Step 2: Each Module
- Create module file
- Test independently
- Add to tool declarations in main.py if needed

### Step 3: Command Center Integration
- Add P&L panel to ui_command_center.py
- Add Neural Mirror callback support

### Step 4: End-to-End Testing
- Verify all modules work together
- Test multi-hop reasoning
- Test sandbox deployment
- Test financial tracking
- Test UI adaptation

---

## TODOS

- [ ] UPGRADE 1: Synapse Knowledge Graph
  - [ ] Create core/synapse_knowledge_graph.py
  - [ ] Modify requirements.txt
  - [ ] Integrate with memory_manager.py
  - [ ] Test multi-hop reasoning

- [ ] UPGRADE 2: Shadow Sandbox
  - [ ] Create actions/sandbox/shadow_sandbox.py
  - [ ] Create actions/sandbox/chaos_tests.py
  - [ ] Modify actions/sandbox/__init__.py
  - [ ] Test container deployment

- [ ] UPGRADE 3: Agentic GDP Tracker
  - [ ] Create actions/financials.py
  - [ ] Integrate with economic_agent.py
  - [ ] Add tool declaration to main.py
  - [ ] Add P&L panel to Command Center

- [ ] UPGRADE 4: Neural Mirroring
  - [ ] Create core/neural_mirror.py
  - [ ] Integrate with neural_decoding.py
  - [ ] Update ui_command_center.py with dynamic styling
  - [ ] Test brain state UI adaptation

---

## FOLLOW-UP STEPS

1. Install dependencies:
   ```bash
   pip install networkx>=3.0 docker>=7.0
   ```

2. Test each module independently before integration

3. Integrate into main.py tool declarations
   
4. Verify Command Center integration

5. Run end-to-end tests for all four upgrades
