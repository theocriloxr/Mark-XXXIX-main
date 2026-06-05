# network_tools.py
"""
Network Tools - IP, Ping, Connections, etc.
"""

import platform
import socket
import subprocess
import time
from datetime import datetime


_OS = platform.system()


def get_ip() -> str:
    """Get local IP address."""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return f"Local IP: {ip}"
    except Exception as e:
        return f"Error: {e}"


def get_external_ip() -> str:
    """Get external/public IP."""
    try:
        import requests
        ip = requests.get("https://api.ipify.org", timeout=5).text
        return f"External IP: {ip}"
    except Exception as e:
        return f"Error getting external IP: {e}"


def ping_host(host: str = "8.8.8.8", count: int = 4) -> str:
    """Ping a host."""
    try:
        if _OS == "windows":
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
            # Parse the output
            lines = result.stdout.split("\n")
            for line in lines:
                if "time=" in line.lower():
                    return f"Ping to {host}: {line.strip()}"
            return f"Ping to {host}: OK"
        return f"Ping failed: {host}"
    except Exception as e:
        return f"Error: {e}"


def get_connections() -> str:
    """Get active network connections."""
    try:
        import psutil
        connections = psutil.net_connections()
        
        # Group by status
        established = []
        listening = []
        
        for conn in connections:
            try:
                if conn.status == "ESTABLISHED":
                    established.append(conn)
                elif conn.status == "LISTEN":
                    listening.append(conn)
            except:
                pass
        
        lines = [
            f"Connections: {len(established)} established, {len(listening)} listening",
        ]
        
        # Show some established
        if established[:5]:
            lines.append("\nEstablished:")
            for conn in established[:5]:
                try:
                    lines.append(f"  {conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip if conn.raddr else '?'}:{conn.raddr.port if conn.raddr else '?'}")
                except:
                    pass
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def check_port(host: str, port: int) -> str:
    """Check if a port is open."""
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return f"Port {port} on {host}: OPEN"
        return f"Port {port} on {host}: CLOSED"
    except Exception as e:
        return f"Error checking port: {e}"
    finally:
        sock.close()


def network_tools(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "ip").lower().strip()
    
    if player:
        player.write_log(f"[network] {action}")
    
    try:
        if action == "ip":
            return get_ip()
        elif action == "external_ip":
            return get_external_ip()
        elif action == "ping":
            return ping_host(
                params.get("host", "8.8.8.8"),
                int(params.get("count", 4))
            )
        elif action == "connections":
            return get_connections()
        elif action == "check_port":
            return check_port(
                params.get("host", "localhost"),
                int(params.get("port", 80))
            )
        else:
            return get_ip()
    except Exception as e:
        return f"Network error: {e}"
