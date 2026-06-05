# system_info.py
"""
System Information - Get detailed hardware and system information.
Part of enhanced JARVIS system.
"""

import platform
import subprocess
import psutil
from pathlib import Path
from typing import Optional

_OS = platform.system()


def get_cpu_info() -> str:
    """Get detailed CPU information."""
    info = {
        "Processor": platform.processor(),
        "Architecture": platform.machine(),
        "Cores (Physical)": psutil.cpu_count(logical=False),
        "Cores (Logical)": psutil.cpu_count(logical=True),
        "Current Frequency": f"{psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "N/A",
        "Max Frequency": f"{psutil.cpu_freq().max:.0f} MHz" if psutil.cpu_freq() else "N/A",
        "CPU Usage": f"{psutil.cpu_percent(interval=1)}%",
    }
    
    lines = ["CPU Info:"]
    for k, v in info.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def get_memory_info() -> str:
    """Get detailed memory information."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    info = {
        "Total RAM": f"{mem.total / 1024**3:.2f} GB",
        "Available": f"{mem.available / 1024**3:.2f} GB",
        "Used": f"{mem.used / 1024**3:.2f} GB",
        "Free": f"{mem.free / 1024**3:.2f} GB",
        "Usage": f"{mem.percent}%",
        "",
        "Swap Total": f"{swap.total / 1024**3:.2f} GB",
        "Swap Used": f"{swap.used / 1024**3:.2f} GB",
        "Swap Usage": f"{swap.percent}%",
    }
    
    lines = ["Memory Info:"]
    for k, v in info.items():
        if v:
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def get_disk_info() -> str:
    """Get disk usage for all drives."""
    lines = ["Disk Information:"]
    
    try:
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                lines.append(f"  {partition.device}")
                lines.append(f"    Mount: {partition.mountpoint}")
                lines.append(f"    Total: {usage.total / 1024**3:.1f} GB")
                lines.append(f"    Used: {usage.used / 1024**3:.1f} GB ({usage.percent}%)")
                lines.append(f"    Free: {usage.free / 1024**3:.1f} GB")
            except:
                pass
    except:
        # Fallback for single disk
        usage = psutil.disk_usage("/")
        lines.append(f"  Total: {usage.total / 1024**3:.1f} GB")
        lines.append(f"  Used: {usage.used / 1024**3:.1f} GB ({usage.percent}%)")
        lines.append(f"  Free: {usage.free / 1024**3:.1f} GB")
    
    return "\n".join(lines)


def get_network_info() -> str:
    """Get network interfaces and connections."""
    lines = ["Network Information:"]
    
    # Interfaces
    interfaces = psutil.net_if_addrs()
    for name, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == 2:  # AF_INET
                lines.append(f"  {name}: {addr.address}")
    
    # Network stats
    stats = psutil.net_io_counters()
    lines.append("")
    lines.append(f"  Bytes Sent: {stats.bytes_sent / 1024**2:.2f} MB")
    lines.append(f"  Bytes Recv: {stats.bytes_recv / 1024**2:.2f} MB")
    
    return "\n".join(lines)


def get_battery_info() -> str:
    """Get battery status if available."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            power = battery.power_plugged
            time_left = "N/A"
            
            if not power and battery.secsleft:
                mins = int(battery.secsleft / 60)
                time_left = f"{mins // 60}h {mins % 60}m"
            
            status = "Charging" if power else "Discharging"
            return (
                f"Battery: {percent}%\n"
                f"  Status: {status}\n"
                f"  Time Left: {time_left}"
            )
    except:
        pass
    
    return "Battery: Not available"


def get_os_info() -> str:
    """Get OS detailed information."""
    lines = [
        f"System: {platform.system()}",
        f"Release: {platform.release()}",
        f"Version: {platform.version()}",
        f"Machine: {platform.machine()}",
        f"Processor: {platform.processor()}",
    ]
    
    # Try hostname
    try:
        import socket
        lines.append(f"Hostname: {socket.gethostname()}")
    except:
        pass
    
    return "\n".join(lines)


def get_all_info() -> str:
    """Get complete system information."""
    parts = [
        get_os_info(),
        "",
        get_cpu_info(),
        "",
        get_memory_info(),
        "",
        get_disk_info(),
        "",
        get_network_info(),
        "",
        get_battery_info(),
    ]
    return "\n".join(parts)


def system_info(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for system info actions."""
    params = parameters or {}
    action = params.get("action", "all").lower().strip()
    
    if player:
        player.write_log(f"[System] {action}")
    
    try:
        if action == "cpu":
            return get_cpu_info()
        elif action == "memory":
            return get_memory_info()
        elif action == "disk":
            return get_disk_info()
        elif action == "network":
            return get_network_info()
        elif action == "battery":
            return get_battery_info()
        elif action == "os":
            return get_os_info()
        elif action == "all":
            return get_all_info()
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"System info error: {e}"
