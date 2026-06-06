o# TODO: JARVIS Enterprise Features Implementation

## Current Task
Implement two enterprise-grade features:
1. Omnipresent Context Awareness (Active Window Tracker)
2. Multi-Agent Swarms (Delegation via ManagedAgents)

---

## Implementation Steps

### Phase 1: Omnipresent Context Awareness

- [ ] 1.1 Create WindowTracker background thread class
  - File: `core/context_tracker.py` (NEW)
  
- [ ] 1.2 Start window tracker in main.py on boot
  - File: `main.py`
  
- [ ] 1.3 Inject ambient context into agent system prompt
  - File: `core/agent_engine.py`

### Phase 2: Multi-Agent Local Swarms

- [ ] 2.1 Import ManagedAgent from smolagents
  - File: `core/agent_engine.py`
  
- [ ] 2.2 Create research_agent and coder_agent sub-agents
  - File: `core/agent_engine.py`
  
- [ ] 2.3 Wrap sub-agents in ManagedAgent classes
  - File: `core/agent_engine.py`
  
- [ ] 2.4 Configure orchestrator with managed_agents list
  - File: `core/agent_engine.py`

### Phase 3: Integration

- [ ] 3.1 Add web search tools to research_agent
  - File: `core/agent_engine.py`
  
- [ ] 3.2 Test imports and verify everything works
  - All modified files

---

## Dependencies
- pygetwindow (already in requirements.txt) ✓

---

## Notes
- WindowTracker runs as daemon thread, checks active window every 3 seconds
- ManagedAgent wraps CodeAgent for delegation to sub-agents
- Orchestrator is the main JARVIS agent that delegates to swarm
