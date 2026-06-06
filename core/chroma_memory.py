"""
JARVIS ChromaDB Vector Memory Manager

This module provides infinite RAG (Retrieval-Augmented Generation) memory
for JARVIS using ChromaDB vector database.

Features:
- Persistent local storage (survives restarts)
- Cosine similarity for semantic search
- Category-based memory organization
- Fast retrieval regardless of memory count

Usage:
    from core.chroma_memory import chroma_memory
    
    # Store a fact
    chroma_memory.memorize("User's wife's birthday is October 14th", category="user_preference")
    
    # Retrieve relevant memories
    memories = chroma_memory.recall("birthday")
"""

import logging
import uuid
import datetime
from pathlib import Path
import sys

import chromadb

logger = logging.getLogger(__name__)


def get_base_dir() -> Path:
    """Get the base directory of the application."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


class ChromaMemoryManager:
    """
    Singleton vector memory manager using ChromaDB.
    
    Provides:
    - memorize(): Store facts as vectors
    - recall(): Retrieve semantically similar memories
    - get_all(): Get all stored memories
    - delete(): Remove specific memories
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # Initialize ChromaDB with persistent storage
        memory_path = get_base_dir() / "jarvis_memory"
        memory_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[ChromaMemory] Initializing at: {memory_path}")
        
        try:
            self.client = chromadb.PersistentClient(path=str(memory_path))
        except Exception as e:
            # Fallback for older chromadb versions or in-memory mode
            logger.warning(f"[ChromaMemory] PersistentClient failed: {e}, using ephemeral")
            self.client = chromadb.EphemeralClient()
        
        # Create or load the collection with cosine similarity
        try:
            self.collection = self.client.get_or_create_collection(
                name="jarvis_long_term",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            # Fallback without metadata
            logger.warning(f"[ChromaMemory] Collection creation with metadata failed: {e}")
            self.collection = self.client.get_or_create_collection(name="jarvis_long_term")
        
        logger.info(f"[ChromaMemory] Collection initialized with {self.collection.count()} memories")
    
    def memorize(self, fact: str, category: str = "general") -> str:
        """
        Store a new fact in the vector database.
        
        Args:
            fact: The text to store
            category: Category for organization (user_preference, identity, notes, etc.)
            
        Returns:
            str: Confirmation message
        """
        if not fact or not fact.strip():
            return "Error: Cannot store empty fact"
        
        memory_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        try:
            self.collection.add(
                documents=[fact.strip()],
                metadatas=[{
                    "category": category,
                    "timestamp": timestamp
                }],
                ids=[memory_id]
            )
            logger.info(f"[ChromaMemory] Saved: {fact[:50]}...")
            return f"Memory saved: {fact}"
        except Exception as e:
            logger.error(f"[ChromaMemory] Error saving memory: {e}")
            return f"Error saving memory: {e}"
    
    def recall(self, query: str, n_results: int = 3) -> list:
        """
        Retrieve the most relevant past memories based on semantic similarity.
        
        Args:
            query: The search query
            n_results: Maximum number of results (default 3)
            
        Returns:
            list: List of relevant memory strings
        """
        try:
            count = self.collection.count()
            if count == 0:
                return []
            
            # Limit results to available count
            actual_results = min(n_results, count)
            
            results = self.collection.query(
                query_texts=[query.strip()],
                n_results=actual_results
            )
            
            # Extract and return the documents
            if results and 'documents' in results and results['documents']:
                return results['documents'][0]
            
            return []
        except Exception as e:
            logger.error(f"[ChromaMemory] Error recalling memories: {e}")
            return []
    
    def get_all(self, limit: int = 100) -> list:
        """
        Get all stored memories (for debugging/management).
        
        Args:
            limit: Maximum number to return
            
        Returns:
            list: List of all memory dictionaries
        """
        try:
            count = self.collection.count()
            if count == 0:
                return []
            
            results = self.collection.get(limit=min(limit, count))
            
            memories = []
            if results and 'documents' in results:
                for i, doc in enumerate(results['documents']):
                    meta = results['metadatas'][i] if 'metadatas' in results else {}
                    memories.append({
                        'id': results['ids'][i] if 'ids' in results else '',
                        'fact': doc,
                        'category': meta.get('category', 'unknown') if isinstance(meta, dict) else 'unknown',
                        'timestamp': meta.get('timestamp', '') if isinstance(meta, dict) else ''
                    })
            
            return memories
        except Exception as e:
            logger.error(f"[ChromaMemory] Error getting all memories: {e}")
            return []
    
    def delete(self, memory_id: str) -> str:
        """
        Delete a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            str: Confirmation message
        """
        try:
            self.collection.delete(ids=[memory_id])
            logger.info(f"[ChromaMemory] Deleted: {memory_id}")
            return f"Memory deleted: {memory_id}"
        except Exception as e:
            logger.error(f"[ChromaMemory] Error deleting memory: {e}")
            return f"Error deleting memory: {e}"
    
    def search_by_category(self, category: str, limit: int = 10) -> list:
        """
        Retrieve memories of a specific category.
        
        Args:
            category: The category to filter by
            limit: Maximum number of results
            
        Returns:
            list: List of matching memories
        """
        try:
            results = self.collection.get(
                where={"category": category},
                limit=limit
            )
            
            if results and 'documents' in results:
                return results['documents']
            
            return []
        except Exception as e:
            logger.error(f"[ChromaMemory] Error searching by category: {e}")
            return []
    
    def count(self) -> int:
        """Get total number of stored memories."""
        try:
            return self.collection.count()
        except:
            return 0
    
    def clear_all(self) -> str:
        """
        Clear all memories (use with caution).
        
        Returns:
            str: Confirmation message
        """
        try:
            # Delete all by getting all IDs
            results = self.collection.get()
            if results and 'ids' in results:
                self.collection.delete(ids=results['ids'])
            logger.warning("[ChromaMemory] All memories cleared!")
            return "All memories cleared"
        except Exception as e:
            logger.error(f"[ChromaMemory] Error clearing memories: {e}")
            return f"Error clearing memories: {e}"


# Global singleton instance
chroma_memory = ChromaMemoryManager()


# Convenience functions for easy import
def memorize(fact: str, category: str = "general") -> str:
    """Store a new memory."""
    return chroma_memory.memorize(fact, category)


def recall(query: str, n_results: int = 3) -> list:
    """Retrieve relevant memories."""
    return chroma_memory.recall(query, n_results)


def get_memory_count() -> int:
    """Get total memory count."""
    return chroma_memory.count()


if __name__ == "__main__":
    # Test the ChromaMemory manager
    print("=== JARVIS ChromaDB Memory Test ===")
    
    # Test storing
    print("\n1. Testing memorize...")
    chroma_memory.memorize("User's name is John", category="identity")
    chroma_memory.memorize("User's wife's birthday is October 14th", category="user_preference")
    chroma_memory.memorize("User prefers dark mode theme", category="preferences")
    chroma_memory.memorize("User works as a software engineer", category="identity")
    
    # Test retrieval
    print("\n2. Testing recall...")
    results = chroma_memory.recall("birthday preference")
    print(f"  Found {len(results)} memories:")
    for r in results:
        print(f"    - {r}")
    
    # Test count
    print(f"\n3. Total memories: {chroma_memory.count()}")
    
    # Test category search
    print("\n4. Testing category search...")
    identity_memories = chroma_memory.search_by_category("identity")
    print(f"  Found {len(identity_memories)} identity memories")
    
    print("\n✅ ChromaDB Memory manager ready!")
