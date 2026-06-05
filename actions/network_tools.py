# network_tools.py
"""
Network Tools - Network diagnostics and utilities.
Part of enhanced JARVIS system.
"""

import platform
import subprocess
import socket
import requests
from pathlib import Path


_OS = platform.system()


def get_local_ip() -> str:
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unknown"


def get_public_ip() -> str:
    """Get public IP address."""
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception:
        return "Unknown"


def ping_host(host: str = "google.com", count: int = 4) -> str:
    """Ping a host."""
    try:
        if _OS == "Windows":
            result = subprocess.run(
                ["ping", "-n", str(count), host],
                capture_output=True, text=True, timeout=30
            )
        else:
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                capture_output=True, text=True, timeout=30
            )
        
        if result.returncode == 0:
            # Extract timing
            lines = result.stdout.split("\n")
            return "\n".join(lines[:count+1])
        return f"Ping failed: {host}"
    except Exception as e:
        return f"Ping error: {e}"


def check_port(host: str, port: int) -> str:
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return f"Port {port} on {host} is OPEN"
        return f"Port {port} on {host} is CLOSED"
    except Exception as e:
        return f"Port check error: {e}"


def network_tools(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for network tools."""
    params = parameters or {}
    action = params.get("action", "local_ip").lower().strip()
    
    try:
        if action == "local_ip":
            return f"Local IP: {get_local_ip()}"
        
        elif action == "public_ip":
            return f"Public IP: {get_public_ip()}"
        
        elif action == "ping":
            return ping_host(
                params.get("host", "google.com"),
                int(params.get("count", 4))
            )
        
        elif action == "check_port":
            return check_port(
                params.get("host", "localhost"),
                int(params.get("port", 80))
            )
        
        elif action == "all":
            return f"Local: {get_local_ip()} | Public: {get_public_ip()}"
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Network tools error: {e}"
