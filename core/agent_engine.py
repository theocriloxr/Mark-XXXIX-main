"""
JARVIS Agent Engine - smolagents CodeAgent Integration

This module provides dynamic Python execution sandbox for JARVIS.
When given a complex command, JARVIS will write a bespoke Python script,
run it in a secure local environment, analyze the output, self-correct
if it encounters errors, and return the final result.

Features:
- ChromaDB RAG memory integration for long-term context
- Omnipresent Context Awareness (window tracking)
- Multi-Agent Swarms (ManagedAgent delegation)
- Dynamic tool loading
- personality-based system prompts

Usage:
    from core.agent_engine import get_jarvis_agent
    
    # Instantiate the agent dynamically (respects config changes)
    jarvis_brain = get_jarvis_agent(user_prompt="What did I tell you about my wife?")
    
    # Execute a complex command
    response = jarvis_brain.run("Look at my downloads directory, group all files by extension...")
"""

import logging
import os
import sys
from pathlib import Path
from smolagents import CodeAgent, LiteLLMModel, LocalPythonExecutor

# Try to import ManagedAgent - it may not be available in newer smolagents versions
try:
    from smolagents import ManagedAgent
except ImportError:
    ManagedAgent = None

logger = logging.getLogger(__name__)


def get_base_dir() -> Path:
    """Get the base directory of the application."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


def _load_api_keys() -> dict:
    """Load API keys from config file."""
    import json
    api_config_path = BASE_DIR / "config" / "api_keys.json"
    if api_config_path.exists():
        with open(api_config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _get_model_id(llm_backend: str) -> str:
    """
    Convert ConfigManager backend to smolagents LiteLLM model ID format.
    
    LiteLLM uses provider/model format:
    - google/gemini-2.5-flash
    - anthropic/claude-3-5-sonnet-20241022
    - openai/gpt-4o
    """
    backend = llm_backend.lower()
    
    if "gemini" in backend:
        model_id = f"google/{backend}"
    elif "claude" in backend:
        model_id = f"anthropic/{backend}"
    elif "gpt" in backend or "o1" in backend or "o3" in backend:
        model_id = f"openai/{backend}"
    else:
        model_id = "google/gemini-2.5-flash"
    
    logger.info(f"Model ID for LiteLLM: {model_id}")
    return model_id


def get_jarvis_agent(user_prompt: str = ""):
    """
    Dynamically builds and returns a smolagents CodeAgent based on 
    the active backend and personality configuration.
    
    This agent:
    - Writes Python code on the fly to accomplish tasks
    - Executes code in a secure LocalPythonExecutor sandbox
    - Self-corrects if it encounters syntax or runtime errors
    - Retrieves relevant long-term memories via RAG
    - Has ambient OS context from window tracking
    - Can delegate to sub-agents for complex tasks
    - Has access to memorize/recall tools
    - Returns the final result as a string response
    
    Args:
        user_prompt: The user's current prompt (used for RAG context retrieval)
        
    Returns:
        CodeAgent: Configured JARVIS brain with code execution capability
    """
    if ManagedAgent is None:
        logger.warning("ManagedAgent not available in smolagents - sub-agent delegation disabled")
    
    # Import ConfigManager here to avoid circular imports
    from core.config_manager import config
    from core.chroma_memory import chroma_memory
    from core.context_tracker import get_window_tracker, is_tracker_running
    from actions.memory_tools import MemorizeTool, RecallTool, GetMemoryCountTool
    from actions.vision_tools import InspectScreenTool, DesktopClickTool
    
    # 1. Fetch current backend from config (e.g., 'gemini-2.5-flash')
    llm_backend = config.get("llm_backend", "gemini-2.5-flash")
    
    # 2. Get the model ID in LiteLLM format
    model_id = _get_model_id(llm_backend)
    
    # 3. Load and set API key based on provider
    api_keys = _load_api_keys()
    
    if "google" in model_id:
        api_key = api_keys.get("gemini_api_key", os.environ.get("GOOGLE_API_KEY", ""))
        os.environ["GOOGLE_API_KEY"] = api_key
    elif "anthropic" in model_id:
        api_key = api_keys.get("anthropic_api_key", os.environ.get("ANTHROPIC_API_KEY", ""))
        os.environ["ANTHROPIC_API_KEY"] = api_key
    elif "openai" in model_id:
        api_key = api_keys.get("openai_api_key", os.environ.get("OPENAI_API_KEY", ""))
        os.environ["OPENAI_API_KEY"] = api_key
    
    logger.info(f"Initializing Jarvis CodeAgent with model: {model_id}")
    
    # 4. Get personality prompt from config
    personality_prompt = config.get_personality_prompt()
    
    # 5a. Get ambient window context (Omnipresent Context Awareness)
    ambient_context = ""
    try:
        if is_tracker_running():
            tracker = get_window_tracker()
            ambient_context = tracker.get_context_string()
            logger.info(f"[Context] Active window: {tracker.current_window}")
    except Exception as e:
        logger.warning(f"[Context] Tracker unavailable: {e}")
    
    # 5b. RAG: Fetch relevant memories based on user prompt
    memory_context = ""
    if user_prompt and user_prompt.strip():
        try:
            relevant_memories = chroma_memory.recall(user_prompt, n_results=3)
            if relevant_memories:
                memory_context = "\n".join(relevant_memories)
                logger.info(f"[RAG] Retrieved {len(relevant_memories)} relevant memories")
        except Exception as e:
            logger.warning(f"[RAG] Memory recall failed: {e}")
    
    # ========== BUILD ENHANCED SYSTEM PROMPT ==========
    prompt_parts = [personality_prompt]
    
    # Add ambient OS context (what user is looking at right now)
    if ambient_context:
        prompt_parts.append(
            f"\n## AMBIENT OS CONTEXT (What You're Looking At Right Now)\n"
            f"{ambient_context}\n"
            f"This context is automatically tracked. Use it to provide relevant assistance."
        )
    
    # Add long-term memory context
    if memory_context:
        prompt_parts.append(
            f"\n## LONG-TERM MEMORY (Relevant Past Context)\n"
            f"{memory_context}\n"
            f"You have access to the above memories from past conversations. "
            f"Use them to provide personalized responses."
        )
    
    # Add execution and delegation capabilities
    if ManagedAgent is not None:
        prompt_parts.append(
            f"\n## CAPABILITIES\n"
            f"You have access to a secure local Python execution environment. "
            f"When given a complex task, write Python code to accomplish it, execute the code, "
            f"analyze the output, and self-correct if needed.\n"
            f"If the task requires research or complex multi-step work, delegate to your sub-agents:\n"
            f"  - web_researcher: For web searches, documentation, and information gathering\n"
            f"  - senior_engineer: For complex code writing, testing, and execution\n"
            f"Always provide the final result to the user. "
            f"Do not simulate results - actually execute the code."
        )
    else:
        prompt_parts.append(
            f"\n## CAPABILITIES\n"
            f"You have access to a secure local Python execution environment. "
            f"When given a complex task, write Python code to accomplish it, execute the code, "
            f"analyze the output, and self-correct if needed.\n"
            f"Always provide the final result to the user. "
            f"Do not simulate results - actually execute the code."
        )
    
    system_prompt = "\n\n".join(prompt_parts)
    
    # 6. Initialize the LLM wrapper
    model = LiteLLMModel(model_id=model_id)
    
    # 7. Create memory tools for the agent
    memory_tools = [
        MemorizeTool(),
        RecallTool(),
        GetMemoryCountTool(),
    ]
    
    # 7b. Create vision tools for screen inspection and desktop control
    vision_tools = [
        InspectScreenTool(),
        DesktopClickTool(),
    ]
    
    # Combine all tools
    all_tools = memory_tools + vision_tools
    
    # Check if ManagedAgent is available
    if ManagedAgent is not None:
        # 8a. Create sub-agents for multi-agent swarm
        # Research Agent - for web searches and information gathering
        research_agent = CodeAgent(
            tools=[],
            model=model,
            add_base_tools=True,
            prompt_templates={
                "system_prompt": "You are a meticulous researcher. Find data, search the web, "
                "read documentation, and summarize information accurately."
            }
        )
        
        # Coder Agent - for complex code writing and execution
        coder_agent = CodeAgent(
            tools=[],
            model=model,
            add_base_tools=True,
            executor=LocalPythonExecutor(),
            prompt_templates={
                "system_prompt": "You are a senior Python developer. Write flawless code, "
                "test it thoroughly, and ensure it runs without errors."
            }
        )
        
        # 8b. Wrap sub-agents in ManagedAgent classes
        managed_researcher = ManagedAgent(
            agent=research_agent,
            name="web_researcher",
            description="Call this agent when you need to search the internet, read documentation, or gather facts."
        )
        
        managed_coder = ManagedAgent(
            agent=coder_agent,
            name="senior_engineer",
            description="Call this agent when you need complex python scripts written, tested, or executed."
        )
        
        # 9. Create the Orchestrator (JARVIS) with managed sub-agents
        # add_base_tools=True gives web search and basic utilities
        agent = CodeAgent(
            tools=all_tools,
            model=model,
            add_base_tools=True,
            managed_agents=[managed_researcher, managed_coder],
            prompt_templates={
                "system_prompt": system_prompt
            },
            executor=LocalPythonExecutor()  # Secure local sandbox
        )
    else:
        # ManagedAgent not available - create agent without sub-agents
        logger.info("Creating CodeAgent without managed sub-agents")
        agent = CodeAgent(
            tools=all_tools,
            model=model,
            add_base_tools=True,
            prompt_templates={
                "system_prompt": system_prompt
            },
            executor=LocalPythonExecutor()  # Secure local sandbox
        )
    
    # Log memory count
    try:
        mem_count = chroma_memory.count()
        logger.info(f"JARVIS CodeAgent initialized with {mem_count} memories")
    except:
        logger.info("JARVIS CodeAgent initialized")
    
    return agent


def execute_agent_command(user_text: str) -> str:
    """
    Convenience function to execute a command through the JARVIS agent.
    
    Args:
        user_text: The user's command or question
        
    Returns:
        str: The agent's response
    """
    jarvis_brain = get_jarvis_agent()
    
    try:
        response = jarvis_brain.run(user_text)
        return response
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        return f"Agent encountered an error: {str(e)}"


if __name__ == "__main__":
    # Test the agent engine
    print("=== JARVIS Agent Engine Test ===")
    print("Initializing agent...")
    
    try:
        agent = get_jarvis_agent()
        print(f"Agent type: {type(agent)}")
        print("✅ Agent engine ready")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
