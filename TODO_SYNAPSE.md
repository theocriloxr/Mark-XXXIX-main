# Synapse Knowledge Graph Implementation Plan

## Overview
Implement a local Knowledge Graph using NetworkX to give JARVIS relational "human-like" memory with multi-hop reasoning capabilities.

## Files to Create
1. `core/synapse_knowledge_graph.py` - Main knowledge graph module
2. Updated `requirements.txt` - Add networkx dependency

## Files to Modify
1. `core/chroma_memory.py` - Integrate with Knowledge Graph
2. `memory/memory_manager.py` - Integrate entity extraction
3. `config/api_keys.json` - Not needed (local only)

## Implementation Details

### 1. SynapseKnowledgeGraph Class
- **Storage**: NetworkX MultiDiGraph for relationships
- **Persistence**: Save/load graph as JSON (GEXF or node-link format)
- **Entities**: People, Projects, Tools, Locations, Concepts
- **Relations**: "works_on", "hosts", "owns", "depends_on", "manages", "uses", "created_by"

### 2. Entity Extraction
- Simple regex-based extraction for known entity types:
  - @mentions (people like @Alice, @Ujo)
  - #hashtags (projects like #SignalRank)
  - Capitalized phrases (potential entities)
- Pattern matching for relations:
  - "[Person] manages [Project]"
  - "[Project] runs on [Host]"
  - "[Tool] created by [Person]"

### 3. Multi-Hop Reasoning Queries
- `query_relation(subject, relation, target)` - Single hop
- `query_path(start_entity, end_entity)` - Multi-hop path finding
- `query_by_entity(entity)` - Get all relationships for an entity

### 4. Integration with ChromaDB
- When memorizing: Extract entities/relations → Store in Graph
- When recalling: Can query graph first → then use vector similarity

## Dependencies
- networkx>=3.0 (for graph operations)

## Follow-up Steps After Implementation
1. Install networkx: `pip install networkx`
2. Test the Knowledge Graph with sample data
3. Verify multi-hop queries work ("Who is lead dev on project Ujo hosts?")
