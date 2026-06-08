"""
MemU - Three-Layer Memory Model
==============================

Enhanced memory system with three distinct layers:
1. Short-term: Rolling buffer of recent interactions
2. Long-term: Persistent facts and relationships  
3. Procedural: Task patterns and workflows

Usage:
    from core.mem_u import MemU, get_mem_u
    
    mem = get_mem_u()
    mem.add_short_term("user asked about weather")
    mem.add_long_term("user_likes", "pizza", "food")
    patterns = mem.get_procedural("research_task")
"""

import json
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def get_base_dir() -> Path:
    """Get base directory."""
    import sys
    from pathlib import Path
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


@dataclass
class ShortTermEntry:
    """Short-term memory entry."""
    content: str
    timestamp: float = field(default_factory=time.time)
    context: str = ""
    intent: str = ""


class MemU:
    """
    Three-layer memory model.
    Provides enhanced memory capabilities beyond simple JSON storage.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._lock = threading.Lock()
        
        # Short-term: Rolling buffer (last 100 items)
        self._short_term: deque = deque(maxlen=100)
        
        # Long-term: Persistent memory
        self._long_term: Dict[str, Dict] = {}
        
        # Procedural: Task patterns
        self._procedural: Dict[str, List[Dict]] = {}
        
        # Load existing data
        self._load()
        
        self._initialized = True
        logger.info("[MemU] Initialized")
    
    def _load(self):
        """Load memory from disk."""
        memory_file = BASE_DIR / "memory" / "mem_u.json"
        
        if not memory_file.exists():
            return
        
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self._long_term = data.get("long_term", {})
            self._procedural = data.get("procedural", {})
            
            logger.info(f"[MemU] Loaded: {len(self._long_term)} long-term, {len(self._procedural)} procedural")
        except Exception as e:
            logger.warning(f"[MemU] Load error: {e}")
    
    def save(self):
        """Save memory to disk."""
        memory_file = BASE_DIR / "memory" / "mem_u.json"
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        with self._lock:
            data = {
                "long_term": self._long_term,
                "procedural": self._procedural,
                "saved_at": time.time()
            }
        
        try:
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.debug("[MemU] Saved")
        except Exception as e:
            logger.warning(f"[MemU] Save error: {e}")
    
    # === SHORT-TERM MEMORY ===
    
    def add_short_term(self, content: str, context: str = "", intent: str = ""):
        """Add to short-term memory."""
        entry = ShortTermEntry(
            content=content,
            context=context,
            intent=intent
        )
        with self._lock:
            self._short_term.append(entry)
    
    def get_short_term(self, count: int = 10) -> List[ShortTermEntry]:
        """Get recent short-term memories."""
        with self._lock:
            entries = list(self._short_term)[-count:]
        return entries
    
    def get_short_term_text(self, count: int = 10) -> str:
        """Get short-term memories as text."""
        entries = self.get_short_term(count)
        if not entries:
            return ""
        
        lines = ["Recent context:"]
        for entry in entries:
            lines.append(f"  - {entry.content}")
        return "\n".join(lines)
    
    # === LONG-TERM MEMORY ===
    
    def add_long_term(self, key: str, value: str, category: str = "notes"):
        """Add to long-term memory."""
        with self._lock:
            if category not in self._long_term:
                self._long_term[category] = {}
            
            self._long_term[category][key] = {
                "value": value,
                "updated": datetime.now().isoformat()
            }
        
        self.save()
    
    def get_long_term(self, key: str, category: str = "notes") -> Optional[str]:
        """Get long-term memory."""
        with self._lock:
            cat = self._long_term.get(category, {})
            entry = cat.get(key, {})
        
        return entry.get("value") if entry else None
    
    def get_all_long_term(self, category: str = "") -> Dict[str, Any]:
        """Get all long-term memories."""
        with self._lock:
            if category:
                return self._long_term.get(category, {})
            return dict(self._long_term)
    
    def format_long_term_for_prompt(self) -> str:
        """Format long-term memory for LLM prompt."""
        with self._lock:
            lines = []
            
            for category, items in self._long_term.items():
                if not isinstance(items, dict):
                    continue
                
                lines.append(f"\n{category.upper()}:")
                
                for key, entry in list(items.items())[:10]:
                    value = entry.get("value", "") if isinstance(entry, dict) else entry
                    lines.append(f"  {key}: {value}")
            
            if not lines:
                return ""
            
            return "\n".join(lines)
    
    # === PROCEDURAL MEMORY ===
    
    def add_procedural(self, task_type: str, steps: List[Dict]):
        """Add procedural memory (task workflow)."""
        with self._lock:
            if task_type not in self._procedural:
                self._procedural[task_type] = []
            
            self._procedural[task_type].append({
                "steps": steps,
                "timestamp": time.time(),
                "count": len(steps)
            })
        
        self.save()
    
    def get_procedural(self, task_type: str) -> Optional[List[Dict]]:
        """Get procedural memory for a task type."""
        with self._lock:
            procedures = self._procedural.get(task_type, [])
        
        if procedures:
            # Return most recent
            return procedures[-1].get("steps", [])
        return None
    
    def get_procedural_summary(self) -> str:
        """Get summary of all procedural memories."""
        with self._lock:
            if not self._procedural:
                return "No procedural memories"
            
            lines = ["Procedural memories:"]
            for task_type, procedures in self._procedural.items():
                count = len(procedures)
                lines.append(f"  - {task_type}: {count} patterns")
            
            return "\n".join(lines)
    
    # === QUERY METHODS ===
    
    def query(self, query: str) -> str:
        """Query all memory layers."""
        query_lower = query.lower()
        
        results = []
        
        # Search short-term
        short_entries = self.get_short_term(20)
        for entry in short_entries:
            if query_lower in entry.content.lower():
                results.append(f"Short-term: {entry.content}")
        
        # Search long-term
        for category, items in self._long_term.items():
            for key, entry in items.items():
                if query_lower in key.lower():
                    value = entry.get("value", "") if isinstance(entry, dict) else entry
                    results.append(f"Long-term[{category}]: {key} = {value}")
        
        # Search procedural
        for task_type in self._procedural:
            if query_lower in task_type.lower():
                results.append(f"Procedural: {task_type}")
        
        if results:
            return "\n".join(results[:10])
        return "No matching memories"
    
    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics."""
        with self._lock:
            long_term_count = sum(
                len(items) for items in self._long_term.values()
                if isinstance(items, dict)
            )
            procedural_count = len(self._procedural)
        
        return {
            "short_term": len(self._short_term),
            "long_term": long_term_count,
            "procedural": procedural_count
        }


# === GLOBAL INSTANCE ===

_mem_u: Optional[MemU] = None


def get_mem_u() -> MemU:
    """Get global MemU instance."""
    global _mem_u
    if _mem_u is None:
        _mem_u = MemU()
    return _mem_u


# === DISPATCHER ===

def mem_u_dispatch(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for MemU."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[MemU] {action}")
    
    try:
        mem = get_mem_u()
        
        if action == "status":
            stats = mem.get_stats()
            return (
                f"Short-term: {stats['short_term']} | "
                f"Long-term: {stats['long_term']} | "
                f"Procedural: {stats['procedural']}"
            )
        
        elif action == "add_short":
            content = params.get("content", "")
            context = params.get("context", "")
            intent = params.get("intent", "")
            
            if not content:
                return "Please provide content"
            
            mem.add_short_term(content, context, intent)
            return "Short-term memory added"
        
        elif action == "get_short":
            count = int(params.get("count", 10))
            text = mem.get_short_term_text(count)
            return text or "No short-term memories"
        
        elif action == "add_long":
            key = params.get("key", "")
            value = params.get("value", "")
            category = params.get("category", "notes")
            
            if not key or not value:
                return "Please provide key and value"
            
            mem.add_long_term(key, value, category)
            return f"Long-term memory added: {category}/{key}"
        
        elif action == "get_long":
            key = params.get("key", "")
            category = params.get("category", "notes")
            
            if not key:
                return "Please provide key"
            
            value = mem.get_long_term(key, category)
            if value:
                return f"{key}: {value}"
            return "Not found"
        
        elif action == "format":
            return mem.format_long_term_for_prompt()
        
        elif action == "query":
            query = params.get("query", "")
            if not query:
                return "Please provide query"
            return mem.query(query)
        
        elif action == "procedural":
            return mem.get_procedural_summary()
        
        else:
            stats = mem.get_stats()
            return f"MemU: {stats['short_term']} short, {stats['long_term']} long, {stats['procedural']} procedural"
    
    except Exception as e:
        return f"MemU error: {e}"


if __name__ == "__main__":
    print("=== MemU Test ===")
    
    mem = get_mem_u()
    print(mem.get_stats())
    
    # Add short-term
    mem.add_short_term("User asked about weather in Lagos", "weather", "query")
    print("\n" + mem.get_short_term_text(5))
    
    # Add long-term
    mem.add_long_term("location", "Lagos, Nigeria", "identity")
    print("\n" + mem.format_long_term_for_prompt())
    
    print("\n✅ MemU ready")
