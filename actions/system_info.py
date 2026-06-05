# system_info.py
"""
System Information - Detailed system and hardware info.
"""

import platform
import psutil
import sys
from pathlib import Path


_OS = platform.system()


def get_hardware_info() -> str:
    """Get detailed hardware information."""
    try:
        cpu = psutil.cpu_count(logical=True)
        cpu_physical = psutil.cpu_count(logical=False)
        
        mem = psutil.virtual_memory()
        
        lines = [
            "Hardware Info:",
            f"  CPU: {cpu_physical} cores ({cpu} logical)",
            f"  RAM: {mem.total / 1024**3:.1f} GB",
        ]
        
        # Disk info
        try:
            disk = psutil.disk_usage("/")
            lines.append(f"  Disk: {disk.total / 1024**3:.1f} GB total")
        except:
            pass
        
        # GPU (basic)
        if _OS == "windows":
            try:
                import subprocess
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    gpu = result.stdout.strip().split("\n")[-1].strip()
                    if gpu:
                        lines.append(f"  GPU: {gpu}")
            except:
                pass
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def get_os_info() -> str:
    """Get OS information."""
    try:
        import os
        
        lines = [
            "OS Info:",
            f"  System: {_OS}",
            f"  Release: {platform.release()}",
            f"  Version: {platform.version()}",
            f"  Machine: {platform.machine()}",
            f"  Processor: {platform.processor()}",
        ]
        
        # Hostname
        lines.append(f"  Hostname: {platform.node()}")
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def get_battery_info() -> str:
    """Get battery information."""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "No battery detected."
        
        percent = battery.percent
        plugged = "Charging" if battery.power_plugged else "Unplugged"
        time_left = "Unknown"
        if battery.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
            hours = battery.secsleft // 3600
            minutes = (battery.secsleft % 3600) // 60
            time_left = f"{hours}h {minutes}m"
        
        return (
            f"Battery: {percent}%\n"
            f"  Status: {plugged}\n"
            f"  Time left: {time_left}"
        )
    except Exception as e:
        return f"Error: {e}"


def get_network_info() -> str:
    """Get network information."""
    try:
        import socket
        
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        
        lines = [
            "Network:",
            f"  Hostname: {hostname}",
            f"  Local IP: {ip}",
        ]
        
        # Get interfaces
        addrs = psutil.net_if_addrs()
        for interface, addr_list in addrs.items():
            for addr in addr_list:
                if str(addr.family) == "AddressFamily.AF_INET":
                    lines.append(f"  {interface}: {addr.address}")
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def get_all_info() -> str:
    """Get all system information."""
    return "\n\n".join([
        get_hardware_info(),
        get_os_info(),
        get_battery_info(),
        get_network_info(),
    ])


def system_info(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "all").lower().strip()
    
    if player:
        player.write_log(f"[system_info] {action}")
    
    try:
        if action == "hardware":
            return get_hardware_info()
        elif action == "os":
            return get_os_info()
        elif action == "battery":
            return get_battery_info()
        elif action == "network":
            return get_network_info()
        elif action == "all":
            return get_all_info()
        else:
            return get_all_info()
    except Exception as e:
        return f"System info error: {e}"
