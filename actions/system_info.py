# system_info.py
"""
System Info - Detailed system and hardware information.
Part of enhanced JARVIS system.
"""

import platform
import subprocess
import psutil
from pathlib import Path


_OS = platform.system()


def get_basic_info() -> str:
    """Get basic system information."""
    try:
        info = {
            "System": platform.system(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "hostname": platform.node(),
        }
        
        # CPU
        info["CPU Cores"] = f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical"
        
        # Memory
        mem = psutil.virtual_memory()
        info["RAM"] = f"{mem.total / (1024**3):.1f} GB ({mem.percent}% used)"
        
        # Boot time
        boot = psutil.boot_time()
        import time
        info["Boot Time"] = time.ctime(boot)
        
        lines = ["System Information:"]
        for k, v in info.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def get_hardware_info() -> str:
    """Get detailed hardware information."""
    lines = ["Hardware Details:"]
    
    try:
        if _OS == "Windows":
            # GPU info via wmic
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"]
            )
            if result.returncode == 0:
                lines.append(f"  GPU: {result.stdout.strip()}")
        elif _OS == "Darwin":
            # macOS hardware
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                lines.append(result.stdout)
    except:
        pass
    
    # Try GPU temperature
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            lines.append(f"  Temperature: {temps}")
    except:
        pass
    
    return "\n".join(lines)


def get_network_info() -> str:
    """Get network configuration."""
    lines = ["Network:"]
    
    try:
        # IP addresses
        addrs = psutil.net_if_addrs()
        for iface, addr_list in addrs.items():
            for addr in addr_list:
                if addr.family == 2:  # AF_INET
                    lines.append(f"  {iface}: {addr.address}")
    except Exception as e:
        lines.append(f"  Error: {e}")
    
    return "\n".join(lines)


def system_info(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for system info actions."""
    params = parameters or {}
    action = params.get("action", "basic").lower().strip()
    
    try:
        if action == "basic":
            return get_basic_info()
        elif action == "hardware":
            return get_hardware_info()
        elif action == "network":
            return get_network_info()
        elif action == "all":
            return get_basic_info() + "\n\n" + get_network_info()
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"System info error: {e}"
