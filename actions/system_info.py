# system_info.py
"""
System Information - Get detailed system hardware and software information.
Part of enhanced JARVIS system.
"""
import platform
import subprocess
import psutil
from pathlib import Path
import sys
import os

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()

def get_os_info() -> str:
    """Get detailed OS information."""
    os_name = platform.system()
    version = platform.version()
    release = platform.release()
    machine = platform.machine()
    processor = platform.processor()
    
    try:
        if os_name == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "os", "get", "Caption,Version,BuildNumber"],
                    capture_output=True, text=True, timeout=5
                )
                os_version = result.stdout.strip()
            except:
                os_version = f"{os_name} {release}"
        elif os_name == "Darwin":
            result = subprocess.run(
                ["sw_vers"],
                capture_output=True, text=True, timeout=5
            )
            os_version = result.stdout.strip()
        else:
            os_version = f"{os_name} {release}"
    except:
        os_version = f"{os_name} {release}"
    
    return (
        f"Operating System: {os_name}\n"
        f"Version: {version}\n"
        f"Release: {release}\n"
        f"Machine: {machine}\n"
        f"Processor: {processor}\n"
        f"Details:\n{os_version}"
    )


def get_hardware_info() -> str:
    """Get detailed hardware information."""
    cpu = platform.processor()
    cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)
    mem = psutil.virtual_memory()
    mem_total = mem.total / (1024**3)
    mem_available = mem.available / (1024**3)
    
    # Get disk info
    disks = []
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["wmic", "logicaldisk", "get", "Caption,Size,FreeSpace"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split("\n")[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        disks.append(f"  {parts[0]}: {int(parts[1])/(1024**3):.1f}GB total")
        else:
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append(f"  {part.device}: {usage.total/(1024**3):.1f}GB")
                except:
                    pass
    except:
        pass
    
    disk_info = "\n".join(disks) if disks else "  Unable to get disk info"
    
    return (
        f"CPU: {cpu}\n"
        f"Cores: {physical_cores} physical, {cores} logical\n"
        f"Memory: {mem_total:.1f}GB total, {mem_available:.1f}GB available\n"
        f"Disks:\n{disk_info}"
    )


def get_battery_info() -> str:
    """Get battery information."""
    try:
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "Charging" if battery.power_plugged else "Not Charging"
                time_left = "N/A"
                if battery.secsleft != -1:
                    hrs = battery.secsleft // 3600
                    mins = (battery.secsleft % 3600) // 60
                    time_left = f"{hrs}h {mins}m"
                
                return (
                    f"Battery: {percent}%\n"
                    f"Status: {plugged}\n"
                    f"Time Remaining: {time_left}"
                )
        return "No battery detected"
    except Exception as e:
        return f"Battery info unavailable: {e}"


def get_network_info() -> str:
    """Get network information."""
    try:
        nets = psutil.net_io_counters()
        interfaces = psutil.net_if_stats()
        
        info = f"Total Data: {nets.bytesSent/(1024**2):.1f}MB sent, {nets.bytesRecv/(1024**2):.1f}MB received\n"
        info += "Network Interfaces:\n"
        
        for name, stats in interfaces.items():
            if stats.isup:
                info += f"  {name}: {stats.speed}Mbps, {stats.mtu}MTU\n"
        
        return info
    except Exception as e:
        return f"Network info unavailable: {e}"


def get_all_info() -> str:
    """Get all system information."""
    return (
        "=" * 40 + "\n"
        "SYSTEM INFORMATION\n"
        "=" * 40 + "\n\n"
        + get_os_info() + "\n\n"
        + get_hardware_info() + "\n\n"
        + get_battery_info() + "\n\n"
        + get_network_info()
    )


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
        player.write_log(f"[system_info] {action}")
    
    try:
        if action == "os":
            return get_os_info()
        elif action == "hardware":
            return get_hardware_info()
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
