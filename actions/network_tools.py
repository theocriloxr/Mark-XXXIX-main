# network_tools.py - Network diagnostic and utility tools
import subprocess
import socket
import platform
import requests
import json
import sys
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

_OS = platform.system().lower()

def check_ping(host: str = "google.com", count: int = 4) -> str:
    """Ping a host."""
    try:
        p = "-n" if _OS == "windows" else "-c"
        result = subprocess.run(
            ["ping", p, str(count), host],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return f"Ping to {host}: Success\n{result.stdout[:500]}"
        return f"Ping failed: {result.stderr[:200]}"
    except Exception as e:
        return f"Ping error: {e}"

def get_ip_info() -> str:
    """Get public and local IP info."""
    lines = ["=== NETWORK INFO ==="]
    
    # Local IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        lines.append(f"Local IP: {local_ip}")
        lines.append(f"Hostname: {hostname}")
    except:
        lines.append("Local IP: Unable to determine")
    
    # Public IP
    try:
        public_ip = requests.get("https://api.ipify.org?format=txt", timeout=5).text.strip()
        lines.append(f"Public IP: {public_ip}")
    except:
        lines.append("Public IP: Unable to determine")
    
    return "\n".join(lines)

def check_port(host: str, port: int) -> str:
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return f"Port {port} on {host}: OPEN"
        return f"Port {port} on {host}: CLOSED"
    except Exception as e:
        return f"Port check error: {e}"

def get_connections() -> str:
    """List active network connections."""
    try:
        import psutil
        lines = ["=== ACTIVE CONNECTIONS ==="]
        
        for conn in psutil.net_connections(kind='inet')[:20]:
            if conn.status == 'ESTABLISHED':
                lines.append(f"{conn.laddr.ip}:{conn.laddr.port} <-> {conn.raddr.ip}:{conn.raddr.port} [{conn.status}]")
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"

def network_tools(parameters: dict = None, response=None, player=None) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "info").lower().strip()
    
    if action == "ping":
        return check_ping(params.get("host", "google.com"), int(params.get("count", 4)))
    elif action == "ip":
        return get_ip_info()
    elif action == "port":
        return check_port(params.get("host", "google.com"), int(params.get("port", 80)))
    elif action == "connections":
        return get_connections()
    else:
        return get_ip_info()
