# multi_agent.py - Multi-agent coordination system
"""
Coordinator for multiple specialized sub-agents that can work together
to handle complex tasks requiring different capabilities.
"""

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class AgentType(Enum):
    RESEARCH = "research"
    CODE = "code"
    FILE = "file"
    SYSTEM = "system"
    NETWORK = "network"
    CUSTOM = "custom"


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SubAgent:
    agent_id: str
    name: str
    agent_type: AgentType
    description: str
    capabilities: list
    status: AgentStatus = AgentStatus.IDLE
    result: str = ""
    created_at: float = field(default_factory=time.time)


class MultiAgentCoordinator:
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
        self._agents: dict[str, SubAgent] = {}
        self._lock = threading.Lock()
        self._create_default_agents()
        self._initialized = True
    
    def _create_default_agents(self):
        defaults = [
            SubAgent(
                agent_id="research_1",
                name="Research Agent",
                agent_type=AgentType.RESEARCH,
                description="Web research and information gathering",
                capabilities=["web_search", "browser_control", "file_write"]
            ),
            SubAgent(
                agent_id="code_1",
                name="Code Agent",
                agent_type=AgentType.CODE,
                description="Programming assistance and code generation",
                capabilities=["code_helper", "dev_agent", "file_write"]
            ),
            SubAgent(
                agent_id="file_1",
                name="File Agent",
                agent_type=AgentType.FILE,
                description="File operations and management",
                capabilities=["file_controller", "universal_dir"]
            ),
            SubAgent(
                agent_id="system_1",
                name="System Agent",
                agent_type=AgentType.SYSTEM,
                description="System management and monitoring",
                capabilities=["process_manager", "system_info", "computer_settings"]
            ),
        ]
        for agent in defaults:
            self._agents[agent.agent_id] = agent
    
    def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        description: str = "",
        capabilities: list = None
    ) -> str:
        agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
        agent = SubAgent(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            description=description,
            capabilities=capabilities or []
        )
        self._agents[agent_id] = agent
        return agent_id
    
    def list_agents(self) -> str:
        lines = ["Active Agents:"]
        for a in self._agents.values():
            lines.append(f"  - {a.name} ({a.agent_type.value}): {a.status.value}")
        return "\n".join(lines)
    
    def get_agent_status(self, agent_id: str) -> str:
        agent = self._agents.get(agent_id)
        if not agent:
            return f"Agent not found: {agent_id}"
        return f"{agent.name}: {agent.status.value} | {agent.description}"
    
    def assign_task(self, agent_id: str, task: str) -> str:
        agent = self._agents.get(agent_id)
        if not agent:
            return f"Agent not found: {agent_id}"
        
        agent.status = AgentStatus.RUNNING
        # In a full implementation, this would queue the task
        # For now, simulate task assignment
        agent.result = f"Task assigned: {task}"
        return f"Task assigned to {agent.name}"
    
    def stop_agent(self, agent_id: str) -> str:
        agent = self._agents.get(agent_id)
        if not agent:
            return f"Agent not found: {agent_id}"
        agent.status = AgentStatus.IDLE
        return f"Agent {agent.name} stopped"


# Global coordinator instance
_coordinator = None


def get_coordinator() -> MultiAgentCoordinator:
    global _coordinator
    if _coordinator is None:
        _coordinator = MultiAgentCoordinator()
    return _coordinator


def multi_agent(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    coord = get_coordinator()
    
    if action == "create":
        agent_type = AgentType(params.get("agent_type", "custom"))
        name = params.get("agent_name", f"Agent_{uuid.uuid4().hex[:4]}")
        desc = params.get("description", "")
        caps = params.get("capabilities", "").split(",") if params.get("capabilities") else []
        
        agent_id = coord.create_agent(
            name=name,
            agent_type=agent_type,
            description=desc,
            capabilities=caps
        )
        return f"Agent created: {name} ({agent_id})"
    
    elif action == "list":
        return coord.list_agents()
    
    elif action == "status":
        return coord.get_agent_status(params.get("agent_id", ""))
    
    elif action == "assign":
        return coord.assign_task(
            params.get("agent_id", ""),
            params.get("task", "")
        )
    
    elif action == "stop":
        return coord.stop_agent(params.get("agent_id", ""))
    
    else:
        return coord.list_agents()
