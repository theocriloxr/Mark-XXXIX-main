# TODO - smolagents CodeAgent Engine Implementation

## Plan Overview
Implement Upgrade #2: The smolagents CodeAgent Engine to give JARVIS dynamic Python execution sandbox.

## Steps

### Step 1: Install Dependencies
- [ ] Add smolagents to requirements.txt

### Step 2: Create Agent Engine
- [ ] Create core/agent_engine.py with CodeAgent orchestration
- [ ] Bind to ConfigManager for dynamic backend and personality
- [ ] Implement get_jarvis_agent() function

### Step 3: Integrate with main.py
- [ ] Import agent_engine in main.py
- [ ] Add agent routing for complex commands
- [ ] Keep existing tool system for backward compatibility

### Step 4: Test
- [ ] Test agent initialization
- [ ] Verify ConfigManager binding when llm_backend changes
- [ ] Test command execution flow
