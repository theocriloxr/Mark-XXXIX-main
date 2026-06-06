"""
Ujo Bridge - MARK-XXXIX delegation to Ujo daemon for system-level tasks.

Ujo is the distributed nervous system handling:
- Docker operations
- Cross-platform execution  
- Remote node management
- OS-level hooks
- Distributed Agent Swarm Execution

Usage:
    When user requests system tasks, Docker, or cross-device control,
    route to Ujo via this bridge.
    
    For distributed agents: Pass the agent payload and target node, 
    Ujo will execute the agent remotely and stream results back.
"""

import json
import logging
import urllib.request
import urllib.error
import uuid
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Ujo daemon HTTP endpoint (adjust port as needed)
UJO_DAEMON_URL = "http://localhost:8181/api/v1/execute"


# === DISTRIBUTED EXECUTION TYPES ===

@dataclass
class AgentPayload:
    """Payload for distributed agent execution."""
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    agent_type: str = "code"  # code, research, file, system
    task: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 60
    callback_url: str = ""


@dataclass
class ExecutionResult:
    """Result from distributed execution."""
    task_id: str
    status: str  # pending, running, completed, failed
    output: str = ""
    error: str = ""
    node: str = "local"
    started_at: float = 0
    completed_at: float = 0


def ujo_network(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    Execute system-level tasks via Ujo daemon.
    
    Parameters:
    - action: docker_deploy | fs_manipulation | remote_exec | status
    - target: local | macbook-pro | aws-server | <node_id>
    - command: The command to execute
    - payload: Additional parameters
    """
    p = parameters or {}
    action = p.get("action", "status")
    target = p.get("target", "local")
    command = p.get("command", "")
    payload = p.get("payload", {})
    
    logger.info(f"[UJO BRIDGE] {action} -> {target}: {command}")
    
    if player:
        player.write_log(f"[UJO] Routing {action} to {target}...")
    
    # Build request data
    request_data = {
        "action": action,
        "target_node": target,
        "command": command,
        "parameters": payload
    }
    
    data = json.dumps(request_data).encode('utf-8')
    req = urllib.request.Request(
        UJO_DAEMON_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            
            if result.get("status") == "success":
                output = result.get("output", "Executed successfully")
                msg = f"Ujo completed {action} on {target}: {output}"
                if speak:
                    speak(msg)
                return msg
            else:
                error = result.get("error", "Unknown error")
                msg = f"Ujo error: {error}"
                if speak:
                    speak(msg)
                return msg
                
    except urllib.error.URLError as e:
        error_msg = f"Cannot reach Ujo daemon. Is ujo-os.service running? {e}"
        logger.error(f"[UJO] {error_msg}")
        if speak:
            speak("I cannot connect to the Ujo daemon. Please ensure it's running.")
        return error_msg
    except Exception as e:
        error_msg = f"Ujo bridge error: {e}"
        logger.error(f"[UJO] {error_msg}")
        if speak:
            speak(f"Ujo task failed: {str(e)[:100]}")
        return error_msg


# === DISTRIBUTED AGENT EXECUTION ===

def execute_distributed_agent(
    task: str,
    agent_type: str = "code",
    target: str = "local",
    parameters: Dict[str, Any] = None,
    timeout: int = 60
) -> str:
    """
    Execute a JARVIS agent on a remote machine via Ujo network.
    
    This offloads heavy tasks (code compilation, data analysis) to remote
    machines, keeping local compute free.
    
    Args:
        task: Task description for the agent
        agent_type: code, research, file, system
        target: Target node (local, macbook-pro, aws-server)
        parameters: Additional parameters
        timeout: Execution timeout in seconds
        
    Returns:
        str: Execution result or task ID for streaming
    """
    # Create payload
    payload_obj = AgentPayload(
        task_id=uuid.uuid4().hex[:8],
        agent_type=agent_type,
        task=task,
        parameters=parameters or {},
        timeout=timeout
    )
    
    request_data = {
        "action": "agent_execute",
        "target_node": target,
        "agent_payload": {
            "task_id": payload_obj.task_id,
            "agent_type": payload_obj.agent_type,
            "task": payload_obj.task,
            "parameters": payload_obj.parameters,
            "timeout": payload_obj.timeout
        }
    }
    
    logger.info(f"[UJO DISTRIBUTED] Executing {agent_type} agent on {target}")
    
    # Send to Ujo daemon
    data = json.dumps(request_data).encode('utf-8')
    req = urllib.request.Request(
        UJO_DAEMON_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout + 10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            
            if result.get("status") == "success":
                return result.get("output", f"Task {payload_obj.task_id} executed on {target}")
            else:
                return f"Remote execution failed: {result.get('error', 'Unknown')}"
                
    except Exception as e:
        logger.error(f"[UJO DISTRIBUTED] Execution failed: {e}")
        return f"Cannot execute remotely: {e}"


def get_execution_status(task_id: str) -> str:
    """
    Get status of a distributed execution.
    
    Args:
        task_id: Task ID from execute_distributed_agent
        
    Returns:
        str: Status (pending, running, completed, failed)
    """
    request_data = {
        "action": "execution_status",
        "task_id": task_id
    }
    
    data = json.dumps(request_data).encode('utf-8')
    req = urllib.request.Request(
        UJO_DAEMON_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result.get("status", "unknown")
    except:
        return "unavailable"


def list_remote_nodes() -> str:
    """List available remote nodes."""
    request_data = {"action": "list_nodes"}
    
    data = json.dumps(request_data).encode('utf-8')
    req = urllib.request.Request(
        UJO_DAEMON_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            nodes = result.get("nodes", [])
            if nodes:
                return "Available nodes: " + ", ".join(nodes)
            return "No remote nodes available"
    except Exception as e:
        return f"Cannot list nodes: {e}"


# === AGENT SWARM EXECUTION ===

def execute_agent_swarm(
    tasks: list,
    agent_type: str = "code",
    target: str = "aws-server"
) -> str:
    """
    Execute multiple tasks as a swarm on remote machine.
    
    Args:
        tasks: List of task descriptions
        agent_type: Type of agent
        target: Target node
        
    Returns:
        str: Summary of swarm execution
    """
    request_data = {
        "action": "agent_swarm",
        "target_node": target,
        "agent_type": agent_type,
        "tasks": tasks
    }
    
    data = json.dumps(request_data).encode('utf-8')
    req = urllib.request.Request(
        UJO_DAEMON_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("status") == "success":
                return f"Swarm executed {len(tasks)} tasks on {target}"
            return f"Swarm failed: {result.get('error')}"
    except Exception as e:
        return f"Swarm execution failed: {e}"


# Standalone function for direct calls
def execute_system_task(
    task_type: str,
    target_system: str,
    payload: Dict[str, Any] = None
) -> str:
    """Delegate system task to Ujo daemon."""
    return ujo_network(parameters={
        "action": task_type,
        "target": target_system,
        "payload": payload or {}
    })


if __name__ == "__main__":
    # Test
    print("[UJO] Testing connection...")
    result = ujo_network({"action": "status", "target": "local"})
    print(result)
