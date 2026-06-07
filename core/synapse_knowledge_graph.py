"""
Synapse Knowledge Graph - Relational Memory with Multi-Hop Reasoning

NetworkX-based knowledge graph for JARVIS that enables:
- Entity extraction from memories
- Complex relationship mapping (e.g., "Who manages the project hosted on Ujo?")
- Multi-hop reasoning across thousands of memories

Usage:
    from core.synapse_knowledge_graph import SynapseKG, get_synapse_kg
    
    kg = get_synapse_kg()
    kg.add_entity("alice", "Alice", "person", {"role": "developer"})
    kg.add_entity("signalrank", "SignalRank", "project", {"status": "active"})
    kg.add_relation("alice", "manages", "signalrank")
    
    # Multi-hop query
    path = kg.query_path("alice", "active")
"""

import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Get base directory
def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()
GRAPH_FILE = BASE_DIR / "memory" / "synapse_graph.json"


# Entity types
ENTITY_PERSON = "person"
ENTITY_PROJECT = "project"
ENTITY_TOOL = "tool"
ENTITY_LOCATION = "location"
ENTITY_DEVICE = "device"


# Relation types
REL_WORKS_ON = "works_on"
REL_HOSTS = "hosts"
REL_OWNS = "owns"
REL_DEPENDS_ON = "depends_on"
REL_MANAGES = "manages"
REL_USES = "uses"
REL_CREATED_BY = "created_by"
REL_MEMBER_OF = "member_of"


class SynapseKG:
    """
    Knowledge Graph for relational memory.
    Uses NetworkX MultiDiGraph for complex relationship queries.
    """
    
    def __init__(self):
        try:
            import networkx as nx
            self.nx = nx
        except ImportError:
            logger.warning("[SYNAPSE] NetworkX not available, using in-memory dict")
            self.nx = None
        
        # Graph structure
        self.entities: Dict[str, Dict] = {}
        self.relations: List[Dict] = []
        
        # Load existing graph
        self._load()
        
        logger.info(f"[SYNAPSE] Knowledge Graph initialized with {len(self.entities)} entities")
    
    def _get_graph(self):
        """Get NetworkX graph or create fallback."""
        if self.nx:
            return self.nx.MultiDiGraph()
        return None
    
    def add_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        properties: Dict[str, Any] = None
    ) -> bool:
        """
        Add an entity to the knowledge graph.
        
        Args:
            entity_id: Unique identifier (e.g., "alice", "signalrank")
            name: Display name (e.g., "Alice", "SignalRank")
            entity_type: Type (person, project, tool, location, device)
            properties: Optional properties dict
            
        Returns:
            bool: Success
        """
        properties = properties or {}
        properties["added_at"] = time.time()
        
        self.entities[entity_id] = {
            "id": entity_id,
            "name": name,
            "type": entity_type,
            "properties": properties
        }
        
        logger.debug(f"[SYNAPSE] Added entity: {entity_id} ({entity_type})")
        return True
    
    def add_relation(
        self,
        from_id: str,
        relation: str,
        to_id: str,
        properties: Dict[str, Any] = None
    ) -> bool:
        """
        Add a relation between entities.
        
        Args:
            from_id: Source entity ID
            relation: Relation type (works_on, hosts, owns, etc.)
            to_id: Target entity ID
            properties: Optional properties
            
        Returns:
            bool: Success
        """
        if from_id not in self.entities:
            logger.warning(f"[SYNAPSE] Unknown entity: {from_id}")
            return False
        
        if to_id not in self.entities:
            logger.warning(f"[SYNAPSE] Unknown entity: {to_id}")
            return False
        
        properties = properties or {}
        properties["created_at"] = time.time()
        
        self.relations.append({
            "from": from_id,
            "relation": relation,
            "to": to_id,
            "properties": properties
        })
        
        logger.debug(f"[SYNAPSE] {from_id} --{relation}--> {to_id}")
        return True
    
    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get entity by ID."""
        return self.entities.get(entity_id)
    
    def find_entity(self, name: str) -> Optional[str]:
        """Find entity ID by name."""
        for eid, ent in self.entities.items():
            if ent.get("name", "").lower() == name.lower():
                return eid
            if ent.get("id", "").lower() == name.lower():
                return eid
        return None
    
    def get_relations(self, entity_id: str) -> List[Dict]:
        """Get all relations for an entity."""
        return [
            r for r in self.relations
            if r["from"] == entity_id or r["to"] == entity_id
        ]
    
    def query_path(self, start_id: str, end_id: str, max_hops: int = 3) -> List[List[str]]:
        """
        Multi-hop reasoning: find path between entities.
        
        Args:
            start_id: Starting entity ID
            end_id: Target entity ID
            max_hops: Maximum hops to search
            
        Returns:
            list: List of paths (each path is list of entity IDs)
        """
        if start_id not in self.entities or end_id not in self.entities:
            return []
        
        # BFS for shortest path
        paths = []
        visited = {start_id}
        queue = [(start_id, [start_id])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_hops:
                continue
            
            if current == end_id:
                paths.append(path)
                continue
            
            # Find neighbors
            for rel in self.relations:
                neighbor = None
                if rel["from"] == current:
                    neighbor = rel["to"]
                elif rel["to"] == current:
                    neighbor = rel["from"]
                
                if neighbor and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return paths
    
    def query_relations(
        self,
        entity_id: str = None,
        relation: str = None,
        target_type: str = None
    ) -> List[Dict]:
        """
        Query relations with filters.
        
        Args:
            entity_id: Filter by entity
            relation: Filter by relation type
            target_type: Filter by target entity type
            
        Returns:
            list: Matching relations
        """
        results = self.relations
        
        if entity_id:
            results = [r for r in results if r["from"] == entity_id or r["to"] == entity_id]
        
        if relation:
            results = [r for r in results if r["relation"] == relation]
        
        if target_type:
            results = [
                r for r in results
                if self.entities.get(r["to"], {}).get("type") == target_type
            ]
        
        return results
    
    def search(self, query: str) -> List[Dict]:
        """
        Search entities and relations.
        
        Args:
            query: Search query
            
        Returns:
            list: Matching entities/relations
        """
        query = query.lower()
        results = []
        
        # Search entities
        for eid, ent in self.entities.items():
            if query in ent.get("name", "").lower():
                results.append({"type": "entity", "data": ent})
            elif query in ent.get("type", "").lower():
                results.append({"type": "entity", "data": ent})
        
        # Search relations
        for rel in self.relations:
            if query in rel.get("relation", "").lower():
                results.append({
                    "type": "relation",
                    "data": {
                        "from": self.entities.get(rel["from"], {}).get("name"),
                        "relation": rel["relation"],
                        "to": self.entities.get(rel["to"], {}).get("name")
                    }
                })
        
        return results
    
    def extract_from_text(self, text: str) -> List[Dict]:
        """
        Extract entities and relations from text.
        Simple pattern-based extraction.
        
        Args:
            text: Text to analyze
            
        Returns:
            list: Extracted entities/relations
        """
        extracted = []
        
        # Simple patterns for common entities
        # Pattern: "X is a Y" or "X is the Y"
        patterns = [
            (r"(\w+)\s+is\s+(?:a|an|the)\s+(\w+)", "type"),
            (r"(\w+)\s+works\s+on\s+(\w+)", "works_on"),
            (r"(\w+)\s+hosts\s+(\w+)", "hosts"),
            (r"(\w+)\s+manages\s+(\w+)", "manages"),
            (r"(\w+)\s+owns\s+(\w+)", "owns"),
            (r"(\w+)\s+depends\s+on\s+(\w+)", "depends_on"),
            (r"(\w+)\s+created\s+by\s+(\w+)", "created_by"),
        ]
        
        for pattern, rel_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    extracted.append({
                        "from": match[0].lower(),
                        "to": match[1].lower(),
                        "relation": rel_type
                    })
        
        return extracted
    
    def _load(self) -> None:
        """Load graph from file."""
        if not GRAPH_FILE.exists():
            return
        
        try:
            data = json.loads(GRAPH_FILE.read_text(encoding="utf-8"))
            self.entities = data.get("entities", {})
            self.relations = data.get("relations", [])
            logger.info(f"[SYNAPSE] Graph loaded: {len(self.entities)} entities")
        except Exception as e:
            logger.warning(f"[SYNAPSE] Load error: {e}")
    
    def _save(self) -> None:
        """Save graph to file."""
        GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "entities": self.entities,
            "relations": self.relations,
            "saved_at": time.time()
        }
        
        GRAPH_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"[SYNAPSE] Graph saved: {len(self.entities)} entities")
    
    def save(self) -> None:
        """Public save method."""
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "entities": len(self.entities),
            "relations": len(self.relations),
            "entity_types": list(set(e.get("type") for e in self.entities.values())),
            "relation_types": list(set(r.get("relation") for r in self.relations))
        }
    
    def clear(self) -> None:
        """Clear all data."""
        self.entities = {}
        self.relations = []
        self._save()


# === GLOBAL INSTANCE ===

_synapse_kg: Optional[SynapseKG] = None


def get_synapse_kg() -> SynapseKG:
    """Get global SynapseKG instance."""
    global _synapse_kg
    if _synapse_kg is None:
        _synapse_kg = SynapseKG()
    return _synapse_kg


# === DISPATCHER ===

def synapse_kg(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for Synapse Knowledge Graph."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[SynapseKG] {action}")
    
    try:
        kg = get_synapse_kg()
        
        if action == "status":
            stats = kg.get_stats()
            return (
                f"Entities: {stats['entities']} | "
                f"Relations: {stats['relations']}"
            )
        
        elif action == "add_entity":
            entity_id = params.get("entity_id", "")
            name = params.get("name", "")
            entity_type = params.get("entity_type", "unknown")
            
            if not entity_id or not name:
                return "Please provide entity_id and name"
            
            kg.add_entity(entity_id, name, entity_type, params.get("properties"))
            kg.save()
            return f"Entity added: {name}"
        
        elif action == "add_relation":
            from_id = params.get("from_id", "")
            relation = params.get("relation", "")
            to_id = params.get("to_id", "")
            
            if not from_id or not relation or not to_id:
                return "Please provide from_id, relation, and to_id"
            
            if kg.add_relation(from_id, relation, to_id, params.get("properties")):
                kg.save()
                return f"Relation added: {from_id} --{relation}--> {to_id}"
            return "Failed to add relation"
        
        elif action == "get":
            entity_id = params.get("entity_id", "")
            entity = kg.get_entity(entity_id)
            if entity:
                return f"{entity['name']} ({entity['type']})"
            return "Entity not found"
        
        elif action == "relations":
            entity_id = params.get("entity_id", "")
            rels = kg.get_relations(entity_id)
            if rels:
                lines = ["Relations:"]
                for r in rels[:10]:
                    direction = "->" if r["from"] == entity_id else "<-"
                    lines.append(f"  {r['from']} {direction} {r['relation']} {r['to']}")
                return "\n".join(lines)
            return "No relations found"
        
        elif action == "path":
            start_id = params.get("start_id", "")
            end_id = params.get("end_id", "")
            max_hops = int(params.get("max_hops", 3))
            
            if not start_id or not end_id:
                return "Please provide start_id and end_id"
            
            paths = kg.query_path(start_id, end_id, max_hops)
            if paths:
                lines = ["Paths found:"]
                for path in paths[:5]:
                    path_names = [
                        kg.entities.get(p, {}).get("name", p)
                        for p in path
                    ]
                    lines.append(" -> ".join(path_names))
                return "\n".join(lines)
            return "No path found"
        
        elif action == "search":
            query = params.get("query", "")
            if not query:
                return "Please provide query"
            
            results = kg.search(query)
            if results:
                lines = ["Results:"]
                for r in results[:10]:
                    if r["type"] == "entity":
                        lines.append(f"  Entity: {r['data']['name']} ({r['data']['type']})")
                    else:
                        lines.append(f"  {r['data']['from']} {r['data']['relation']} {r['data']['to']}")
                return "\n".join(lines)
            return "No results"
        
        elif action == "extract":
            text = params.get("text", "")
            if not text:
                return "Please provide text"
            
            extracted = kg.extract_from_text(text)
            if extracted:
                lines = ["Extracted:"]
                for e in extracted:
                    lines.append(f"  {e['from']} --{e['relation']}--> {e['to']}")
                return "\n".join(lines)
            return "Nothing extracted"
        
        elif action == "clear":
            kg.clear()
            return "Graph cleared"
        
        else:
            stats = kg.get_stats()
            return f"SynapseKG: {stats['entities']} entities, {stats['relations']} relations"
    
    except Exception as e:
        return f"SynapseKG error: {e}"


if __name__ == "__main__":
    # Test
    print("=== Synapse Knowledge Graph Test ===")
    
    kg = get_synapse_kg()
    
    # Add entities
    kg.add_entity("alice", "Alice", "person", {"role": "lead developer"})
    kg.add_entity("bob", "Bob", "person", {"role": "designer"})
    kg.add_entity("signalrank", "SignalRank", "project", {"status": "active"})
    kg.add_entity("ujo", "Ujo", "device", {"type": "server"})
    
    # Add relations
    kg.add_relation("alice", "works_on", "signalrank")
    kg.add_relation("bob", "works_on", "signalrank")
    kg.add_relation("signalrank", "hosts", "ujo")
    kg.add_relation("alice", "manages", "signalrank")
    
    kg.save()
    
    # Query
    stats = kg.get_stats()
    print(f"Stats: {stats}")
    
    # Path query
    paths = kg.query_path("alice", "ujo")
    print(f"Alice -> Ujo paths: {paths}")
    
    print("\n✅ Synapse Knowledge Graph ready")
