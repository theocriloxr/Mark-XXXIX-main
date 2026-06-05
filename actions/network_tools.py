# network_tools.py
"""
Network Tools - IP, ping, connections, network diagnostics
"""

import subprocess
import socket
import platform
import sys
from pathlib import Path
import json

_OS = platform.system()

def _run_cmd(cmd: list) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except Exception as e:
        return str(e)

def get_ip_address(internal: bool = True) -> str:
    try:
        if internal:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return f"Internal IP: {ip}"
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"External IP: {ip}"
    except Exception as e:
        return f"Error: {e}"

def ping_host(host: str = "google.com", count: int = 4) -> str:
    cmd = ["ping", "-c", str(count), host] if _OS != "Windows" else ["ping", "-n", str(count), host]
    return _run_cmd(cmd)

def check_port(host: str, port: int) -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return f"Port {port} on {host} is OPEN"
        return f"Port {port} on {host} is CLOSED"
    except Exception as e:
        return f"Error: {e}"

def get_connections() -> str:
    if _OS == "Windows":
        result = _run_cmd(["netstat", "-ano"])
        lines = result.split("\n")[:30]
        return "Active connections:\n" + "\n".join(lines)
    
    elif _OS == "Darwin":
        result = _run_cmd(["netstat", "-an"])
        lines = result.split("\n")[:30]
        return "Active connections:\n" + "\n".join(lines)
    
    else:
        result = _run_cmd(["ss", "-tunap"])
        lines = result.split("\n")[:30]
        return "Active connections:\n" + "\n".join(lines)

def get_dns() -> str:
    if _OS == "Windows":
        result = _run_cmd(["ipconfig", "/all"])
        for line in result.split("\n"):
            if "DNS" in line:
                return line.strip()
        return "DNS servers not found"
    
    elif _OS == "Darwin":
        result = _run_cmd(["scutil", "--dns"])
        return result[:500]
    
    else:
        result = _run_cmd(["cat", "/etc/resolv.conf"])
        return result[:300]

def get_gateway() -> str:
    if _OS == "Windows":
        result = _run_cmd(["ipconfig"])
        for line in result.split("\n"):
            if "Default Gateway" in line:
                return line.strip()
        return "Gateway not found"
    
    elif _OS == "Darwin":
        result = _run_cmd(["netstat", "-nr"])
        for line in result.split("\n"):
            if "default" in line.lower():
                return line.strip()
        return "Gateway not found"
    
    else:
        result = _run_cmd(["ip", "route"])
        for line in result.split("\n"):
            if "default" in line:
                return line.strip()
        return "Gateway not found"

def network_tools(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "ip").lower().strip()
    host = params.get("host", "").strip()
    port = params.get("port", 80)
    
    try:
        if action == "ip":
            return get_ip_address(internal=params.get("internal", True))
        
        elif action == "ping":
            if not host:
                host = "google.com"
            return ping_host(host, int(params.get("count", 4)))
        
        elif action == "check_port":
            if not host:
                return "Specify host."
            return check_port(host, int(port))
        
        elif action == "connections":
            return get_connections()
        
        elif action == "dns":
            return get_dns()
        
        elif action == "gateway":
            return get_gateway()
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Error: {e}"
