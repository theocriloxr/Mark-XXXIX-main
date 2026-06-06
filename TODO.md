# JARVIS ChromaDB RAG Memory Implementation

## Overview
Implementing infinite RAG memory via ChromaDB for persistent, ultra-fast long-term memory.

## Tasks

### Step 1: Add ChromaDB to requirements.txt
- [ ] Add chromadb to requirements.txt dependencies

### Step 2: Create ChromaDB Memory Manager (core/chroma_memory.py)
- [ ] Create new core/chroma_memory.py with:
  - ChromaDB PersistentClient setup
  - Collection with cosine similarity
  - memorize() function
  - recall() function
  - Global singleton instance

### Step 3: Create Memory Tools (actions/memory_tools.py)
- [ ] Create MemorizeTool for saving facts
- [ ] Create RecallTool for retrieving memories  
- [ ] Export tools for agent integration

### Step 4: Wire RAG into Agent (core/agent_engine.py)
- [ ] Import chroma_memory and memory_tools
- [ ] Add RAG system prompt injection in get_jarvis_agent()
- [ ] Add memorize/recall tools to agent tools list

### Step 5: Install dependencies and test
- [ ] Run pip install chromadb
- [ ] Test memory functionality

## Follow-up (Future Enhancements)
- Auto-memorize important details from conversations
- Memory consolidation/cleanup
- Export/import memory backup
