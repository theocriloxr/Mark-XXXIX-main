# process_manager.py
"""
Process Manager - View and manage running processes on the system.
Part of enhanced JARVIS system for comprehensive system control.
"""

import os
import sys
import platform
import subprocess
import time
from pathlib import Path
from typing import Optional

_OS = platform.system()

def _get_os() -> str:
    return _OS.lower()


def list_processes(max_count: int = 50, search: str = "") -> str:
    """List running processes, optionally filtered by name."""
    try:
        if _get_os() == "windows":
            return _list_processes_windows(max_count, search)
        elif _get_os() == "darwin":
            return _list_processes_macos(max_count, search)
        else:
            return _list_processes_linux(max_count, search)
    except Exception as e:
        return f"Error listing processes: {e}"


def _list_processes_windows(max_count: int, search: str) -> str:
    try:
        import psutil
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                name = info.get('name', '')
                if search and search.lower() not in name.lower():
                    continue
                processes.append({
                    'pid': info.get('pid'),
                    'name': name,
                    'cpu': info.get('cpu_percent', 0),
                    'mem': info.get('memory_percent', 0)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        processes = processes[:max_count]
        
        if not processes:
            return f"No processes found matching: {search}"
        
        lines = [f"Top {len(processes)} processes:"]
        for p in processes:
            lines.append(f"  PID {p['pid']:>6} | {p['name']:<30} | CPU {p['cpu']:>5.1f}% | MEM {p['mem']:>5.1f}%")
        return "\n".join(lines)
    except Exception as e:
        return f"Windows process error: {e}"


def _list_processes_macos(max_count: int, search: str) -> str:
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,pcpu,pmem,comm"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split("\n")[1:max_count+1]
        
        if search:
            lines = [l for l in lines if search.lower() in l.lower()]
        
        if not lines:
            return f"No processes found: {search}"
        
        output = ["Running processes:"]
        for line in lines[:max_count]:
            parts = line.split(None, 3)
            if len(parts) >= 4:
                output.append(f"  PID {parts[0]:>6} | {parts[3]:<30} | CPU {parts[1]}% | MEM {parts[2]}%")
        return "\n".join(output)
    except Exception as e:
        return f"macOS process error: {e}"


def _list_processes_linux(max_count: int, search: str) -> str:
    return _list_processes_macos(max_count, search)


def kill_process(pid: int, force: bool = False) -> str:
    """Kill a process by PID."""
    try:
        if _get_os() == "windows":
            signal = "/F" if force else ""
            result = subprocess.run(
                ["taskkill", signal, "/PID", str(pid)],
                capture_output=True, text=True
            )
        else:
            sig = "-9" if force else "-15"
            result = subprocess.run(
                ["kill", sig, str(pid)],
                capture_output=True, text=True
            )
        
        if result.returncode == 0:
            return f"Process {pid} terminated."
        return f"Failed to kill {pid}: {result.stderr}"
    except Exception as e:
        return f"Error killing process: {e}"


def kill_by_name(name: str, all_instances: bool = True) -> str:
    """Kill all processes matching a name."""
    try:
        if _get_os() == "windows":
            flag = "/IM" if all_instances else "/IM"
            result = subprocess.run(
                ["taskkill", "/F", "/IM", name],
                capture_output=True, text=True
            )
        else:
            result = subprocess.run(
                ["pkill", "-9" if all_instances else "-15", name],
                capture_output=True, text=True
            )
        
        if result.returncode == 0:
            return f"Killed all '{name}' processes."
        return f"Failed to kill '{name}': {result.stderr}"
    except Exception as e:
        return f"Error: {e}"


def get_process_info(pid: int) -> str:
    """Get detailed info about a specific process."""
    try:
        import psutil
        p = psutil.Process(pid)
        
        info = {
            'PID': p.pid,
            'Name': p.name(),
            'Status': p.status(),
            'CPU %': f"{p.cpu_percent(interval=0.1):.1f}",
            'Memory': f"{p.memory_info().rss / 1024 / 1024:.1f} MB",
            'Threads': p.num_threads(),
            'Created': time.ctime(p.create_time()),
            'User': p.username(),
        }
        
        # Try to get command line
        try:
            info['Command'] = " ".join(p.cmdline())
        except:
            pass
        
        lines = [f"Process {pid}:"]
        for k, v in info.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    except psutil.NoSuchProcess:
        return f"Process {pid} not found."
    except Exception as e:
        return f"Error: {e}"


def get_system_stats() -> str:
    """Get overall system process stats."""
    try:
        import psutil
        
        total = len(psutil.p_processes())
        running = sum(1 for p in psutil.process_iter() if p.status() == psutil.STATUS_RUNNING)
        
        cpu_count = psutil.cpu_count()
        mem = psutil.virtual_memory()
        
        return (
            f"System Processes:\n"
            f"  Total: {total}\n"
            f"  Running: {running}\n"
            f"  CPU Cores: {cpu_count}\n"
            f"  Memory: {mem.percent}% used"
        )
    except Exception as e:
        return f"Error: {e}"


def process_manager(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for process manager actions."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
    try:
        if action == "list":
            return list_processes(
                max_count=int(params.get("max_count", 50)),
                search=params.get("search", "")
            )
        
        elif action == "kill":
            pid = params.get("pid")
            name = params.get("name")
            
            if pid:
                return kill_process(
                    int(pid),
                    force=params.get("force", False)
                )
            elif name:
                return kill_by_name(name)
            return "Specify pid or name to kill."
        
        elif action == "info":
            return get_process_info(int(params.get("pid", 0)))
        
        elif action == "stats":
            return get_system_stats()
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Process manager error: {e}"
