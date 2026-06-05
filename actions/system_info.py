# system_info.py
"""
System Information Tool - Get detailed system hardware and software info.
"""
import platform
import subprocess
import sys
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

_OS = platform.system()

def get_full_system_info() -> str:
    """Get comprehensive system information."""
    info = []
    info.append("=== SYSTEM INFO ===")
    info.append(f"OS: {platform.system()} {platform.release()}")
    info.append(f"Version: {platform.version()}")
    info.append(f"Machine: {platform.machine()}")
    info.append(f"Processor: {platform.processor()}")
    info.append(f"Hostname: {platform.node()}")
    
    # Hardware info
    try:
        import psutil
        info.append(f"\n=== HARDWARE ===")
        info.append(f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
        
        mem = psutil.virtual_memory()
        info.append(f"RAM: {mem.total / (1024**3):.1f} GB total, {mem.available / (1024**3):.1f} GB available")
        
        disk = psutil.disk_usage('/')
        info.append(f"Disk: {disk.total / (1024**3):.1f} GB total, {disk.free / (1024**3):.1f} GB free")
    except:
        pass
    
    # Network
    try:
        import socket
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        info.append(f"\n=== NETWORK ===")
        info.append(f"Hostname: {hostname}")
        info.append(f"IP Address: {ip}")
    except:
        pass
    
    return "\n".join(info)


def get_hardware_info() -> str:
    """Get detailed hardware info."""
    try:
        import psutil
        lines = ["=== HARDWARE ==="]
        
        # CPU
        cpu = psutil.cpu_freq()
        lines.append(f"CPU: {psutil.cpu_count(logical=True)} cores")
        if cpu:
            lines.append(f"CPU Freq: {cpu.current:.0f} MHz")
        
        # Memory
        mem = psutil.virtual_memory()
        lines.append(f"RAM: {mem.total / (1024**3):.1f} GB ({mem.percent}% used)")
        
        # Disk
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                lines.append(f"Disk {part.device}: {usage.total / (1024**3):.1f} GB")
            except:
                pass
        
        # Battery
        try:
            battery = psutil.sensors_battery()
            if battery:
                lines.append(f"Battery: {battery.percent}% ({'charging' if battery.power_plugged else 'discharging'})")
        except:
            pass
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error getting hardware: {e}"


def get_network_info() -> str:
    """Get network information."""
    try:
        import socket
        import psutil
        
        lines = ["=== NETWORK ==="]
        lines.append(f"Hostname: {socket.gethostname()}")
        
        # Get IP addresses
        interfaces = psutil.net_if_addrs()
        for name, addrs in interfaces.items():
            for addr in addrs:
                if str(addr.family) == 'AddressFamily.AF_INET':
                    lines.append(f"{name}: {addr.address}")
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def system_info(parameters: dict = None, response=None, player=None) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "info").lower().strip()
    
    if action == "full":
        return get_full_system_info()
    elif action == "hardware":
        return get_hardware_info()
    elif action == "network":
        return get_network_info()
    else:
        return get_full_system_info()
