"""
JARVIS Memory Tools - Smolagents Tools for RAG Memory

These tools allow JARVIS to actively memorize and recall facts 
using the ChromaDB vector database.

Usage:
    from actions.memory_tools import MemorizeTool, RecallTool
    
    # Add to agent tools
    tools = [MemorizeTool(), RecallTool()]
"""

from smolagents import Tool
from core.chroma_memory import chroma_memory


class MemorizeTool(Tool):
    """
    Tool for saving important facts to JARVIS's long-term memory.
    
    Use this when:
    - User provides personal information (name, birthday, etc.)
    - User expresses a preference
    - User mentions something important to remember
    - User asks JARVIS to remember something
    
    Example: "Remember that my wife's birthday is October 14th"
    """
    
    name = "memorize_fact"
    description = (
        "Saves important facts, preferences, personal information, or data "
        "to JARVIS's long-term memory database. Use this whenever the user "
        "asks you to remember something or provides important information "
        "that should be stored for future reference."
    )
    
    inputs = {
        "fact": {
            "type": "string",
            "description": (
                "The exact fact or information to remember. "
                "Be specific and include all relevant details. "
                "Examples: 'User's name is John Smith', "
                "'User prefers dark mode theme', "
                "'User's wife's birthday is October 14th'"
            )
        },
        "category": {
            "type": "string",
            "description": (
                "Category for organizing the memory. "
                "Options: 'identity' (personal info), 'preferences' (likes/dislikes), "
                "'relationships' (people), 'general' (other info). "
                "Default: 'general'"
            ),
            "default": "general"
        }
    }
    output_type = "string"
    
    def forward(self, fact: str, category: str = "general") -> str:
        """
        Save a fact to long-term memory.
        
        Args:
            fact: The information to remember
            category: Category for organization
            
        Returns:
            str: Confirmation message
        """
        if not fact or not fact.strip():
            return "Error: Cannot store empty fact"
        
        result = chroma_memory.memorize(fact.strip(), category)
        return result


class RecallTool(Tool):
    """
    Tool for retrieving relevant memories from JARVIS's long-term memory.
    
    Use this when:
    - User asks about past conversations
    - User references something they've told JARVIS before
    - You need context from previous interactions
    - User asks "do you remember...?"
    
    Example: "Do you remember my wife's birthday?"
    """
    
    name = "recall_memories"
    description = (
        "Retrieves relevant past memories from JARVIS's long-term memory "
        "based on semantic similarity. Use this whenever the user asks about "
        "something they've told you before, or when you need context from "
        "previous conversations. Returns the most relevant memories."
    )
    
    inputs = {
        "query": {
            "type": "string",
            "description": (
                "The search query describing what to look for. "
                "Use natural language describing the memory. "
                "Examples: 'birthday', 'name', 'preferences', 'wife'"
            )
        },
        "n_results": {
            "type": "number",
            "description": (
                "Maximum number of memories to retrieve. "
                "Default: 3"
            ),
            "default": 3
        }
    }
    output_type = "string"
    
    def forward(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant memories.
        
        Args:
            query: Search query
            n_results: Number of results
            
        Returns:
            str: Formatted memory results
        """
        if not query or not query.strip():
            return "Error: Empty query"
        
        results = chroma_memory.recall(query.strip(), n_results)
        
        if not results:
            return "No relevant memories found."
        
        # Format results
        formatted = []
        for i, memory in enumerate(results, 1):
            formatted.append(f"{i}. {memory}")
        
        return "Relevant past memories:\n" + "\n".join(formatted)


class ClearMemoryTool(Tool):
    """
    Tool for clearing all memories (admin use only).
    
    Use with caution - this deletes all stored memories.
    """
    
    name = "clear_all_memories"
    description = (
        "WARNING: Clears ALL memories from JARVIS's long-term memory. "
        "Use only when explicitly requested by the user. "
        "This action cannot be undone."
    )
    
    inputs = {}
    output_type = "string"
    
    def forward(self) -> str:
        """Clear all memories."""
        return chroma_memory.clear_all()


class GetMemoryCountTool(Tool):
    """
    Tool for checking how many memories are stored.
    
    Useful for debugging or when user asks "how much do you remember?"
    """
    
    name = "memory_count"
    description = (
        "Returns the total number of memories stored in JARVIS's "
        "long-term memory database."
    )
    
    inputs = {}
    output_type = "string"
    
    def forward(self) -> str:
        """Get memory count."""
        count = chroma_memory.count()
        return f"JARVIS has {count} memories stored."


# Export tools for easy import
MEMORY_TOOLS = [
    MemorizeTool(),
    RecallTool(),
    GetMemoryCountTool(),
    ClearMemoryTool(),
]


if __name__ == "__main__":
    # Test the memory tools
    print("=== JARVIS Memory Tools Test ===")
    
    # Test memorize
    print("\n1. Testing MemorizeTool...")
    tool = MemorizeTool()
    result = tool.forward("User's name is John", category="identity")
    print(f"  Result: {result}")
    
    # Test recall
    print("\n2. Testing RecallTool...")
    tool = RecallTool()
    result = tool.forward("name")
    print(f"  Result: {result}")
    
    # Test count
    print("\n3. Testing GetMemoryCountTool...")
    tool = GetMemoryCountTool()
    result = tool.forward()
    print(f"  Result: {result}")
    
    print("\n✅ Memory tools ready!")
