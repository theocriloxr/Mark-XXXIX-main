# TODO: JARVIS Master-Tier Upgrades - Implementation Plan

## Phase 1: Synapse Knowledge Graph (Relational Memory)

### Objective
Upgrade from pure Vector RAG (ChromaDB) to a Knowledge Graph that understands entity relationships.

### Files to Create:
- [ ] `core/synapse_graph.py` - NetworkX-based knowledge graph for relational memory
- [ ] `core/entity_extractor.py` - NLP-based entity and relation extraction

### Files to Modify:
- [ ] `core/chroma_memory.py` - Integrate with Knowledge Graph for hybrid storage
- [ ] `requirements.txt` - Add networkx dependency

### Implementation Details:
1. Creates NetworkX directed graph for entities and relations
2. Extracts (subject, predicate, object) triples from text
3. Performs multi-hop reasoning queries
4. Supports queries like "Who is the lead dev on the project that Ujo hosts?"

### Dependencies:
- networkx (add to requirements.txt)
- spacy (for entity extraction)

---

## Phase 2: Shadow Sandbox (Virtual OS Layer)

### Objective
Create isolated container environment for testing self-evolving code before deployment.

### Files to Create:
- [ ] `actions/shadow_sandbox.py` - Docker SDK integration for container management
- [ ] `actions/chaos_tests.py` - Safety test suite (memory leaks, socket attempts, etc.)

### Files to Modify:
- [ ] `actions/sandbox/__init__.py` - Enable sandbox integration
- [ ] `core/polymorphic_core.py` - Integrate with sandbox for code verification

### Implementation Details:
1. Uses Docker SDK to spin up isolated containers
2. Runs generated code in sandbox before "ascending" to production
3. Executes chaos tests: memory leak detection, network isolation, resource limits
4. Only verified code reaches main hardware

### Dependencies:
- docker (add to requirements.txt)

---

## Phase 3: Agentic GDP Tracker (Financial Dashboard)

### Objective
Track JARVIS as a sovereign economic actor with real-time P&L statements.

### Files to Create:
- [ ] `actions/financials.py` - Financial tracking module with token cost, AWS, crypto

### Files to Modify:
- [ ] `actions/economic_agent.py` - Integrate with financial tracker
- [ ] `agent/multi_agent.py` - Track sub-agent profitability

### Implementation Details:
1. Tracks all expenses: AWS, Gemini/Claude tokens, crypto transactions
2. Tracks value generated: tasks completed, code written, decisions made
3. Real-time P&L dashboard
4. Sub-agent profitability ranking

### Dependencies:
- Already have necessary libraries

---

## Phase 4: Neural Mirroring (UI Cognitive Adaptation)

### Objective
Bridge BCI neural states to UI for real-time empathic adaptation.

### Files to Modify:
- [ ] `ui.py` - Integrate neural state detection with UI theming
- [ ] `core/neural_decoding.py` - Add state callbacks for UI

### Implementation Details:
1. Maps neural states to UI modes:
   - Focused (Gamma high) → Minimalist Mode, dim non-essential elements
   - Stressed (Beta high) → Enlarge Emergency Stop buttons
   - Relaxed (Alpha high) → Calm deep blue palette
2. Real-time style updates based on brainwave data
3. Color palette shifts automatically

### Dependencies:
- Already integrated in neural_decoding.py

---

## Implementation Order

### Tier 1 (Critical - Start Here):
1. Synapse Knowledge Graph
2. Agentic GDP Tracker

### Tier 2 (Advanced):
3. Shadow Sandbox
4. Neural Mirroring

---

## Testing Strategy

1. **Unit Tests**: Each new module in `tests/`
2. **Integration Tests**: Full workflow testing
3. **Performance**:
   - Knowledge Graph: Multi-hop query latency
   - Sandbox: Container spin time
   - GDP: Tracking accuracy
   - Neural Mirror: State change latency

---

## Success Criteria

- [ ] Knowledge Graph performs multi-hop reasoning
- [ ] Shadow Sandbox isolates untrusted code
- [ ] Financial tracker shows real-time P&L
- [ ] UI adapts to cognitive state in real-time
