"""
Ujo Bridge - MARK-XXXIX delegation to Ujo daemon for system-level tasks.

Ujo is the distributed nervous system handling:
- Docker operations
- Cross-platform execution  
- Remote node management
- OS-level hooks

Usage:
    When user requests system tasks, Docker, or cross-device control,
    route to Ujo via this bridge.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Ujo daemon HTTP endpoint (adjust port as needed)
UJO_DAEMON_URL = "http://localhost:8181/api/v1/execute"


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
