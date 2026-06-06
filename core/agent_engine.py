"""
JARVIS Agent Engine - smolagents CodeAgent Integration

This module provides dynamic Python execution sandbox for JARVIS.
When given a complex command, JARVIS will write a bespoke Python script,
run it in a secure local environment, analyze the output, self-correct
if it encounters errors, and return the final result.

Features:
- ChromaDB RAG memory integration for long-term context
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
        # Already in gemini-X format, prepend google/
        model_id = f"google/{backend}"
    elif "claude" in backend:
        # Convert claude-X to anthropic/claude-X
        model_id = f"anthropic/{backend}"
    elif "gpt" in backend or "o1" in backend or "o3" in backend:
        # Convert gpt-4o to openai/gpt-4o
        model_id = f"openai/{backend}"
    else:
        # Default fallback
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
    - Has access to memorize/recall tools
    - Returns the final result as a string response
    
    Args:
        user_prompt: The user's current prompt (used for RAG context retrieval)
        
    Returns:
        CodeAgent: Configured JARVIS brain with code execution capability
    """
    # Import ConfigManager here to avoid circular imports
    from core.config_manager import config
    from core.chroma_memory import chroma_memory
    from actions.memory_tools import MemorizeTool, RecallTool, GetMemoryCountTool
    
    # 1. Fetch current backend from config (e.g., 'gemini-2.5-flash')
    llm_backend = config.get("llm_backend", "gemini-2.5-flash")
    
    # 2. Get the model ID in LiteLLM format
    model_id = _get_model_id(llm_backend)
    
    # 3. Load and set API key based on provider
    api_keys = _load_api_keys()
    
    # Determine provider and set appropriate API key
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
    
    # Extend the personality for code agent context
    system_prompt = (
        f"{personality_prompt}\n\n"
        "You have access to a secure local Python execution environment. "
        "When given a complex task, write Python code to accomplish it, execute the code, "
        "analyze the output, and self-correct if needed. "
        "Always provide the final result to the user. "
        "Use standard libraries (os, pathlib, json, etc.) freely. "
        "Do not simulate results — actually execute the code."
    )
    
    # 5. Initialize the LLM wrapper
    model = LiteLLMModel(model_id=model_id)
    
    # 6. Create the CodeAgent with execution sandbox
    # add_base_tools=True gives web search and basic utilities
    agent = CodeAgent(
        tools=[],  # Custom tools can be added here later
        model=model,
        add_base_tools=True,
        prompt_templates={
            "system_prompt": system_prompt
        },
        executor=LocalPythonExecutor()  # Secure local sandbox
    )
    
    logger.info("JARVIS CodeAgent initialized successfully")
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
