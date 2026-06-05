# multi_agent.py
"""
Multi-Agent Coordinator - Manages multiple specialized agents working together.
Part of enhanced JARVIS system.
"""

import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


def get_base_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


class AgentType(Enum):
    RESEARCH = "research"
    CODE = "code"
    FILE = "file"
    SYSTEM = "system"
    NETWORK = "network"
    GENERAL = "general"


@dataclass
class Agent:
    name: str
    type: AgentType
    description: str
    capabilities: list[str] = field(default_factory=list)
    active: bool = False
    last_used: float = 0
    task_count: int = 0


class MultiAgentCoordinator:
    """Coordinates multiple specialized agents."""
    
    def __init__(self):
        self._agents: dict[str, Agent] = {}
        self._active_tasks: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize default agents."""
        default_agents = [
            Agent(
                name="Research Agent",
                type=AgentType.RESEARCH,
                description="Web research, information gathering, comparisons",
                capabilities=["web_search", "browser_control", "research"]
            ),
            Agent(
                name="Code Agent", 
                type=AgentType.CODE,
                description="Programming, code writing, debugging",
                capabilities=["code_helper", "dev_agent", "run_code"]
            ),
            Agent(
                name="File Agent",
                type=AgentType.FILE,
                description="File operations, organizing, searching",
                capabilities=["file_controller", "organize", "backup"]
            ),
            Agent(
                name="System Agent",
                type=AgentType.SYSTEM,
                description="System control, settings, process management",
                capabilities=["computer_settings", "process_manager", "system_info"]
            ),
            Agent(
                name="Network Agent",
                type=AgentType.NETWORK,
                description="Network tools, connectivity checks",
                capabilities=["network_tools", "ping", "ports"]
            ),
            Agent(
                name="General Agent",
                type=AgentType.GENERAL,
                description="General tasks and queries",
                capabilities=["all"]
            ),
        ]
        
        for agent in default_agents:
            self._agents[agent.type.value] = agent
    
    def list_agents(self) -> str:
        """List all available agents."""
        lines = ["Available Agents:"]
        for key, agent in self._agents.items():
            status = "🟢" if agent.active else "⚪"
            lines.append(f"  {status} {agent.name} - {agent.description}")
        return "\n".join(lines)
    
    def get_agent_for_task(self, task_type: str) -> Optional[Agent]:
        """Get best agent for a task type."""
        task_lower = task_type.lower()
        
        # Map task keywords to agents
        if any(kw in task_lower for kw in ["search", "research", "find info", "look up"]):
            return self._agents.get(AgentType.RESEARCH.value)
        
        if any(kw in task_lower for kw in ["code", "program", "write", "debug", "fix"]):
            return self._agents.get(AgentType.CODE.value)
        
        if any(kw in task_lower for kw in ["file", "folder", "organize", "copy", "move"]):
            return self._agents.get(AgentType.FILE.value)
        
        if any(kw in task_lower for kw in ["system", "process", "install", "update"]):
            return self._agents.get(AgentType.SYSTEM.value)
        
        if any(kw in task_lower for kw in ["network", "ping", "ip", "connection"]):
            return self._agents.get(AgentType.NETWORK.value)
        
        return self._agents.get(AgentType.GENERAL.value)
    
    def assign_task(self, task: str, agent_type: str = "") -> str:
        """Assign a task to an agent."""
        if agent_type:
            agent = self._agents.get(agent_type.lower())
        else:
            agent = self.get_agent_for_task(task)
        
        if not agent:
            return "No suitable agent found for this task."
        
        with self._lock:
            agent.active = True
            agent.last_used = time.time()
            agent.task_count += 1
        
        return f"Task assigned to: {agent.name}"
    
    def complete_task(self, agent_type: str) -> str:
        """Mark task as complete."""
        agent = self._agents.get(agent_type.lower())
        if agent:
            agent.active = False
            return f"Task completed for: {agent.name}"
        return "Agent not found."
    
    def get_agent_status(self, agent_type: str = "") -> str:
        """Get status of an agent."""
        if agent_type:
            agent = self._agents.get(agent_type.lower())
            if not agent:
                return "Agent not found."
            return (
                f"{agent.name}\n"
                f"  Active: {agent.active}\n"
                f"  Tasks: {agent.task_count}\n"
                f"  Last used: {time.ctime(agent.last_used)}"
            )
        
        return self.list_agents()
    
    def create_specialized_agent(
        self,
        name: str,
        description: str,
        capabilities: list[str]
    ) -> str:
        """Create a new specialized agent."""
        agent_type = AgentType.GENERAL
        
        # Try to find matching type
        for at in AgentType:
            if at.value in capabilities[0].lower() if capabilities else "":
                agent_type = at
                break
        
        new_agent = Agent(
            name=name,
            type=agent_type,
            description=description,
            capabilities=capabilities
        )
        
        self._agents[name.lower().replace(" ", "_")] = new_agent
        return f"Created agent: {name}"


# Global coordinator instance
_coordinator = MultiAgentCoordinator()


def get_coordinator() -> MultiAgentCoordinator:
    """Get the global coordinator."""
    return _coordinator


def multi_agent(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for multi-agent."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
    if player:
        player.write_log(f"[MultiAgent] {action}")
    
    try:
        if action == "list":
            return get_coordinator().list_agents()
        
        elif action == "assign":
            return get_coordinator().assign_task(
                params.get("task", ""),
                params.get("agent", "")
            )
        
        elif action == "complete":
            return get_coordinator().complete_task(
                params.get("agent", "")
            )
        
        elif action == "status":
            return get_coordinator().get_agent_status(
                params.get("agent", "")
            )
        
        elif action == "create":
            return get_coordinator().create_specialized_agent(
                params.get("name", ""),
                params.get("description", ""),
                params.get("capabilities", "").split(",")
            )
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Multi-agent error: {e}"
