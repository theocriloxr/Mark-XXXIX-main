# JARVIS Master-Tier Architecture Upgrade Plan

Based on comprehensive code analysis, here is the detailed implementation plan for the final frontier upgrades.

---

## Information Gathered

### Current Architecture Summary:
- **Main System**: `main.py` - WebSocket-based live audio conversation with Gemini 2.5 Flash
- **Agent Engine**: `core/agent_engine.py` - smolagents CodeAgent with multi-agent delegation
- **Multi-Agent**: `agent/multi_agent.py` - Sub-agent coordination system (research, code, file, system agents)
- **Context Tracker**: `core/context_tracker.py` - Active window tracking every 3 seconds
- **Wake Word**: `actions/wake_word.py` - openWakeWord integration for always-listening
- **Ujo Bridge**: `actions/ujo_network.py` - HTTP-based daemon for remote execution
- **30+ Tools**: File processing, web search, computer control, vision, etc.

### Current Limitations (that these upgrades will fix):
1. **Turn-based communication**: 3-8 second latency (speak → transcribe → generate → TTS → play)
2. **No permanent learning**: Each dev_agent task is one-time only
3. **No speculative context**: Responds only after user speaks
4. **No emotion detection**: Same persona regardless of user mood
5. **No real-time file indexing**: Uses search-based file lookup

---

## Implementation Plan

### Phase 1: Evolution Lab (Self-Coding & Auto-Installing Skills)
**Goal**: JARVIS learns new skills permanently instead of one-time execution

**Files to create/modify:**
1. `actions/evolution_lab.py` - NEW: Tool maker orchestration
2. `actions/sandbox/` - NEW: Directory for experimental tools
3. `actions/tool_maker.py` - NEW: Agent that writes, tests, and validates new tools

**Workflow:**
```
User request → analyze for reusability → delegate to tool_maker agent
  → write tool.py + test_tool.py in sandbox
  → run pytest, self-fix on failure
  → hot-reload into main actions/ directory
  → use importlib.reload() to inject without restart
```

**Implementation:**
- Create `actions/sandbox/` directory structure
- Create `actions/evolution_lab.py` main controller
- Create `actions/tool_maker.py` with CodeAgent for code generation
- Add tool schema for the Evolution Lab in `actions/tool_schemas.py`

### Phase 2: Zero-Latency Streaming Voice Pipeline
**Goal**: Sub-800ms latency for real-time Iron Man experience

**Files to modify:**
1. `main.py` - Upgrade from turn-based to streaming pipeline
2. `actions/wake_word.py` - Enhanced with streaming STT integration

**Architecture Changes:**
- **Streaming STT**: Feed audio chunks directly to faster-whisper or Deepgram
- **Streaming LLM**: Enable `stream=True` in LiteLLMModel
- **Streaming TTS WebSocket**: Connect to Cartesia/ElevenLabs WebSocket API
- **Parallel Pipeline**: Begin speaking while still generating

**Implementation:**
- Modify `JarvisLive` class to use async audio streaming
- Add WebSocket connection for real-time TTS
- Implement audio chunk prefetching

### Phase 3: Ujo-Distributed Swarms
**Goal**: Offload heavy tasks to remote machines via Ujo network

**Files to modify:**
1. `actions/ujo_network.py` - Extend for agent swarm execution
2. `actions/tool_schemas.py` - Add distributed execution schema
3. `agent/multi_agent.py` - Integrate with remote execution

**Implementation:**
- Add `distributed_exec` action to Ujo bridge
- Create `execute_remote_agent()` function
- Add streaming result callback

### Phase 4: Omniceptive File System (Real-Time Indexing)
**Goal**: JARVIS knows every file change in real-time without searching

**Files to create:**
1. `core/file_watcher.py` - NEW: watchdog-based file system monitor
2. `core/file_index.db` - NEW: SQLite graph for file metadata

**Implementation:**
```
OS file event → watchdog observer → update SQLite index
  → "Where did I save that invoice?" → instant answer from index
```

- Use `watchdog` library to monitor file system events
- Create SQLite database for file metadata (path, timestamp, size, hash)
- Add file index query tool

### Phase 5: Speculative Pre-Computation (Mind Reader)
**Goal**: Anticipate user needs before they speak

**Files to modify:**
1. `core/context_tracker.py` - Add prediction logic
2. `actions/signal_rank_bridge.py` - Integrate with SignalRank for trading

**Implementation:**
- Track window patterns (e.g., opens crypto chart → pre-fetch trading signals)
- Create prediction queue based on context
- Pre-compute responses before user asks

### Phase 6: Acoustic Sentiment Adaptation
**Goal**: Detect user emotion and adapt JARVIS personality

**Files to create:**
1. `core/sentiment_analyzer.py` - NEW: Voice emotion detection

**Implementation:**
- Pipe live audio to lightweight sentiment classifier
- Adapt system prompt based on detected emotion:
  - Calm → conversational, detailed
  - Frustrated → urgent, concise, no pleasantries

### Phase 7: Local Environmental Control (IoT Syncing)
**Goal**: Control physical environment (lights, etc.) based on workflow

**Files to create:**
1. `actions/smart_home.py` - NEW: Smart home integration

**Implementation:**
- Connect to Home Assistant API, MQTT, or Philips Hue
- Detect workflow context (VS Code + Terminal = "Deep Work")
- Automate: dim lights, desk lamp on, notifications pause

---

## Dependent Files to be Edited

### Creation (NEW):
1. `core/file_watcher.py`
2. `core/sentiment_analyzer.py`
3. `actions/evolution_lab.py`
4. `actions/tool_maker.py`
5. `actions/smart_home.py`
6. `core/prediction_engine.py`

### Modification (EXISTING):
1. `main.py` - Streaming pipeline, sentiment analysis
2. `core/context_tracker.py` - Speculative pre-computation
3. `actions/wake_word.py` - Streaming STT
4. `actions/tool_schemas.py` - Add new tool schemas
5. `actions/ujo_network.py` - Distributed agent execution
6. `agent/multi_agent.py` - Remote agent support

---

## Testing & Follow-up

1. **Unit Tests**: Each new module needs test files
2. **Integration Tests**: Full workflow testing
3. **Performance Benchmarks**:
   - Voice latency: measure ms from wake to first audio
   - File indexing: measure ms for file queries
   - Prediction accuracy: track pre-computation hits
4. **User Testing**: Subjective quality assessment of personality adaptation

---

## Implementation Priority (Recommended)

**Tier 1 (Critical for "Iron Man" experience):**
1. Evolution Lab (Phase 1)
2. Zero-Latency Streaming (Phase 2)

**Tier 2 (Advanced features):**
3. Ujo-Distributed Swarms (Phase 3)
4. Omniceptive File System (Phase 4)

**Tier 3 (Bleeding-edge):**
5. Speculative Pre-Computation (Phase 5)
6. Acoustic Sentiment Adaptation (Phase 6)
7. Local Environmental Control (Phase 7)

---

## Next Steps

Please review and confirm which phases you'd like to implement first:
- **Option A**: Implement Tier 1 first (Evolution Lab + Streaming Pipeline)
- **Option B**: Full implementation in order
- **Option C**: Specific phase(s) only

I will then proceed with creating the TODO.md and implementing the files.
