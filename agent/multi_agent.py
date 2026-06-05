# multi_agent.py - Multi-agent coordination system
"""Create and manage specialized sub-agents for complex tasks."""
import json
import threading
import uuid
from pathlib import Path
from typing import Callable, Optional, Any

# Agent registry and active agents
_AGENTS = {}
_AGENT_LOCK = threading.Lock()
_RESULTS = {}

class Agent:
    def __init__(self, name: str, agent_type: str, description: str = "", capabilities: list = None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.type = agent_type
        self.description = description
        self.capabilities = capabilities or []
        self.status = "idle"
        self.task = None
        self.result = None
        
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "task": self.task
        }

def create_agent(name: str, agent_type: str, description: str = "", capabilities: list = None) -> str:
    """Create a new specialized agent."""
    with _AGENT_LOCK:
        agent = Agent(name, agent_type, description, capabilities)
        _AGENTS[agent.id] = agent
        return f"Agent '{name}' created. ID: {agent.id}"

def list_agents() -> str:
    """List all active agents."""
    with _AGENT_LOCK:
        if not _AGENTS:
            return "No active agents."
        
        lines = ["Active Agents:"]
        for a in _AGENTS.values():
            lines.append(f"  [{a.type}] {a.name} - {a.status}")
        return "\n".join(lines)

def get_capabilities(agent_type: str) -> list:
    """Get capabilities by agent type."""
    defaults = {
        "research": ["web_search", "browser_control", "file_controller"],
        "code": ["code_helper", "dev_agent", "file_controller"],
        "file": ["file_controller", "backup_tool", "universal_dir"],
        "system": ["process_manager", "system_info", "network_tools"],
        "network": ["network_tools", "browser_control"],
    }
    return defaults.get(agent_type, ["web_search", "file_controller"])

# Agent type definitions
AGENT_TYPES = {
    "research": {
        "name": "Research Agent",
        "description": "Deep web research, information gathering",
        "capabilities": ["web_search", "browser_control", "file_controller", "summarize"]
    },
    "code": {
        "name": "Code Agent", 
        "description": "Programming, development, code assistance",
        "capabilities": ["code_helper", "dev_agent", "file_controller", "terminal"]
    },
    "file": {
        "name": "File Agent",
        "description": "Complex file operations, organization, backup",
        "capabilities": ["file_controller", "backup_tool", "universal_dir"]
    },
    "system": {
        "name": "System Admin Agent",
        "description": "System management, processes, settings",
        "capabilities": ["process_manager", "system_info", "network_tools", "app_installer"]
    },
    "network": {
        "name": "Network Agent",
        "description": "Network diagnostics, connections",
        "capabilities": ["network_tools", "browser_control", "ping"]
    },
}

def multi_agent(parameters=None, response=None, player=None):
    """Main dispatcher for multi-agent system."""
    params = parameters or {}
    action = params.get("action", "list")
    
    try:
        if action == "create":
            name = params.get("agent_name", "")
            agent_type = params.get("agent_type", "")
            desc = params.get("description", "")
            caps = params.get("capabilities", "")
            
            if not name or not agent_type:
                return "agent_name and agent_type required"
            
            capabilities = caps.split(",") if caps else get_capabilities(agent_type)
            return create_agent(name, agent_type, desc, capabilities)
        
        elif action == "list":
            return list_agents()
        
        elif action == "assign":
            task = params.get("task", "")
            if not task:
                return "Task required"
            
            agent_id = params.get("agent_id", "")
            if agent_id in _AGENTS:
                with _AGENT_LOCK:
                    _AGENTS[agent_id].task = task
                    _AGENTS[agent_id].status = "assigned"
                return f"Task assigned to agent {agent_id}"
            return "Agent not found"
        
        elif action == "status":
            agent_id = params.get("agent_id", "")
            if agent_id in _AGENTS:
                agent = _AGENTS[agent_id]
                return json.dumps(agent.to_dict(), indent=2)
            return "Agent not found"
        
        elif action == "stop":
            agent_id = params.get("agent_id", "")
            if agent_id in _AGENTS:
                with _AGENT_LOCK:
                    _AGENTS[agent_id].status = "stopped"
                return f"Agent {agent_id} stopped"
            return "Agent not found"
        
        elif action == "types":
            lines = ["Available agent types:"]
            for t, info in AGENT_TYPES.items():
                lines.append(f"  {t}: {info['name']} - {info['description']}")
            return "\n".join(lines)
        
        else:
            return list_agents()
    
    except Exception as e:
        return f"Multi-agent error: {e}"
