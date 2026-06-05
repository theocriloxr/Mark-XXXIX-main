# network_tools.py
"""
Network Tools - Network diagnostics, ping, port check, IP lookup, DNS.
Part of enhanced JARVIS system.
"""

import platform
import subprocess
import socket
import requests
from pathlib import Path
import sys

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()


def ping_host(host: str, count: int = 4) -> str:
    """Ping a host and return results."""
    param = "-n" if platform.system() == "Windows" else "-c"
    timeout_param = "-w" if platform.system() == "Windows" else "-W"
    
    try:
        result = subprocess.run(
            ["ping", param, str(count), timeout_param, "5", host],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            # Parse output for stats
            output = result.stdout
            if "Average" in output:
                import re
                avg_match = re.search(r"Average = (\d+)ms", output)
                if avg_match:
                    return f"Ping to {host}: OK - Avg response: {avg_match.group(1)}ms"
            return f"Ping to {host}: Success\n{output[:300]}"
        return f"Ping to {host}: Failed\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return f"Ping to {host}: Timed out"
    except Exception as e:
        return f"Ping error: {e}"


def check_port(host: str, port: int) -> str:
    """Check if a port is open on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return f"Port {port} on {host}: OPEN"
        return f"Port {port} on {host}: CLOSED"
    except socket.gaierror:
        return f"Could not resolve {host}"
    except Exception as e:
        return f"Port check error: {e}"


def get_local_ip() -> str:
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unknown"


def get_public_ip() -> str:
    """Get public IP address."""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text
    except Exception as e:
        return f"Unable to get public IP: {e}"


def dns_lookup(domain: str) -> str:
    """Perform DNS lookup for a domain."""
    try:
        ip = socket.gethostbyname(domain)
        return f"{domain} -> {ip}"
    except socket.gaierror as e:
        return f"DNS lookup failed: {e}"
    except Exception as e:
        return f"DNS error: {e}"


def get_connections() -> str:
    """Get active network connections."""
    import psutil
    try:
        connections = psutil.net_connections()
        established = [c for c in connections if c.status == "ESTABLISHED"]
        
        lines = [f"Active connections: {len(established)}"]
        for conn in established[:10]:
            try:
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "?"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "?"
                lines.append(f"  {conn.status}: {laddr} -> {raddr}")
            except:
                pass
        
        return "\n".join(lines)
    except Exception as e:
        return f"Connections error: {e}"


def network_tools(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for network tools."""
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    host = params.get("host", "")
    port = params.get("port", 0)
    domain = params.get("domain", "")
    
    if player:
        player.write_log(f"[network] {action}")
    
    try:
        if action == "ping":
            if not host:
                return "Please specify host to ping"
            return ping_host(host)
        elif action == "port":
            if not host or not port:
                return "Please specify host and port"
            return check_port(host, int(port))
        elif action == "ip":
            local = get_local_ip()
            public = get_public_ip()
            return f"Local IP: {local}\nPublic IP: {public}"
        elif action == "dns":
            if not domain:
                return "Please specify domain"
            return dns_lookup(domain)
        elif action == "connections":
            return get_connections()
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Network tools error: {e}"
