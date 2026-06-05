# service_manager.py
"""
Service Manager - Windows Services / macOS LaunchD / Linux Systemd
"""

import subprocess
import platform
import sys
from pathlib import Path

_OS = platform.system()

def get_services() -> str:
    if _OS == "Windows":
        try:
            result = subprocess.run(
                ["sc", "query", "state=all"],
                capture_output=True, text=True, timeout=30
            )
            lines = result.stdout.strip().split("\n")
            services = []
            for line in lines:
                if "SERVICE_NAME" in line:
                    name = line.split(":", 1)[1].strip()
                    services.append(name)
            return f"Windows Services ({len(services)}):\n" + "\n".join(services[:30])
        except Exception as e:
            return f"Error: {e}"
    
    elif _OS == "Darwin":
        try:
            result = subprocess.run(
                ["launchctl", "list"],
                capture_output=True, text=True, timeout=10
            )
            return f"macOS Services:\n{result.stdout[:2000]}"
        except Exception as e:
            return f"Error: {e}"
    
    else:
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service"],
                capture_output=True, text=True, timeout=10
            )
            return f"Linux Services:\n{result.stdout[:2000]}"
        except Exception as e:
            return f"Error: {e}"

def start_service(name: str) -> str:
    if _OS == "Windows":
        result = subprocess.run(
            ["sc", "start", name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return f"Started: {name}"
        return f"Failed: {result.stderr[:100]}"
    
    elif _OS == "Darwin":
        result = subprocess.run(
            ["launchctl", "load", f"/Library/LaunchDaemons/{name}.plist"],
            capture_output=True, text=True
        )
        return f"Started: {name}"
    
    else:
        result = subprocess.run(
            ["sudo", "systemctl", "start", name],
            capture_output=True, text=True
        )
        return f"Started: {name}"

def stop_service(name: str) -> str:
    if _OS == "Windows":
        result = subprocess.run(
            ["sc", "stop", name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return f"Stopped: {name}"
        return f"Failed: {result.stderr[:100]}"
    
    elif _OS == "Darwin":
        result = subprocess.run(
            ["launchctl", "unload", f"/Library/LaunchDaemons/{name}.plist"],
            capture_output=True, text=True
        )
        return f"Stopped: {name}"
    
    else:
        result = subprocess.run(
            ["sudo", "systemctl", "stop", name],
            capture_output=True, text=True
        )
        return f"Stopped: {name}"

def check_service(name: str) -> str:
    if _OS == "Windows":
        result = subprocess.run(
            ["sc", "query", name],
            capture_output=True, text=True
        )
        return result.stdout[:500]
    
    elif _OS == "Darwin":
        result = subprocess.run(
            ["launchctl", "list", name],
            capture_output=True, text=True
        )
        return result.stdout[:500]
    
    else:
        result = subprocess.run(
            ["systemctl", "status", name],
            capture_output=True, text=True
        )
        return result.stdout[:500]

def service_manager(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    name = params.get("name", "").strip()
    
    try:
        if action == "list":
            return get_services()
        
        elif action == "start":
            if not name:
                return "Specify service name."
            return start_service(name)
        
        elif action == "stop":
            if not name:
                return "Specify service name."
            return stop_service(name)
        
        elif action == "check":
            if not name:
                return "Specify service name."
            return check_service(name)
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Error: {e}"
