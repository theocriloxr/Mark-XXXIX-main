# universal_dir.py
"""
Universal Directory - Access ANY folder/drive on the system.
Part of enhanced JARVIS system with full filesystem access.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

_OS = platform.system()


def get_drives() -> str:
    """Get all available drives on the system."""
    if _OS == "Windows":
        return _get_drives_windows()
    elif _OS == "Darwin":
        return _get_drives_macos()
    else:
        return _get_drives_linux()


def _get_drives_windows() -> str:
    """Get Windows drives."""
    try:
        import winreg
        drives = []
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\Scsi")
        i = 0
        while True:
            try:
                name = winreg.EnumValue(key, i)[0]
                if "Scsi" in name:
                    break
                i += 1
            except:
                break
        
        # Get logical drives
        import win32api
        drives = win32api.GetLogicalDrives()
        result = []
        for i in range(26):
            if drives & (1 << i):
                letter = chr(65 + i)
                result.append(f"{letter}:\\")
        
        if result:
            return "Available drives: " + " ".join(result)
        return "Could not detect drives."
    except Exception as e:
        return f"Error: {e}"


def _get_drives_macos() -> str:
    """Get macOS volumes."""
    volumes = ["/"]
    try:
        # Get mounted volumes
        result = subprocess.run(
            ["ls", "/Volumes"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                volumes.append(f"/Volumes/{line}")
    except:
        pass
    
    return "Available: " + " ".join(volumes)


def _get_drives_linux() -> str:
    """Get Linux mount points."""
    mounts = ["/"]
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    mp = parts[1]
                    if mp.startswith("/media") or mp.startswith("/mnt"):
                        mounts.append(mp)
    except:
        pass
    
    return "Available: " + " ".join(set(mounts))


def list_directory(path: str = "", show_hidden: bool = False) -> str:
    """List contents of any directory."""
    try:
        target = Path(path) if path else Path.home()
        
        if not target.exists():
            return f"Path not found: {path}"
        
        if not target.is_dir():
            return f"Not a directory: {path}"
        
        items = []
        for item in sorted(target.iterdir()):
            if not show_hidden and item.name.startswith("."):
                continue
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({_format_size(size)})")
        
        if not items:
            return f"Directory is empty: {target}"
        
        return f"{target}:\n" + "\n".join(items)
    
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error: {e}"


def _format_size(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def get_path_info(path: str = "") -> str:
    """Get detailed info about a path."""
    try:
        target = Path(path)
        
        if not target.exists():
            return f"Path not found: {path}"
        
        stat = target.stat()
        parts = {
            "Path": str(target),
            "Exists": "Yes",
            "Type": "Directory" if target.is_dir() else "File",
        }
        
        if target.is_file():
            parts["Size"] = _format_size(stat.st_size)
        
        parts["Parent"] = str(target.parent)
        parts["Name"] = target.name
        
        lines = [f"Info for {path}:"]
        for k, v in parts.items():
            lines.append(f"  {k}: {v}")
        
        return "\n".join(lines)
    
    except Exception as e:
        return f"Error: {e}"


def navigate_to(path: str = "") -> str:
    """Navigate to and describe a path."""
    try:
        target = Path(path)
        
        if not target.exists():
            return f"Path not found: {path}"
        
        if target.is_file():
            return f"File: {target.name}\nLocation: {target.parent}\nSize: {_format_size(target.stat().st_size)}"
        
        # It's a directory
        contents = list(target.iterdir())[:10]
        count = sum(1 for _ in target.iterdir())
        
        lines = [
            f"Directory: {target.name}",
            f"Items: {count}",
            f"Path: {target}",
        ]
        
        if contents:
            lines.append("Contents:")
            for item in contents:
                marker = "📁" if item.is_dir() else "📄"
                lines.append(f"  {marker} {item.name}")
        
        return "\n".join(lines)
    
    except Exception as e:
        return f"Error: {e}"


def find_files(path: str = "", pattern: str = "", max_results: int = 20) -> str:
    """Search for files anywhere on the system."""
    try:
        search_path = Path(path) if path else Path.home()
        
        if not search_path.exists():
            return f"Path not found: {path}"
        
        results = []
        try:
            for item in search_path.rglob(pattern + "*"):
                if len(results) >= max_results:
                    break
                if item.is_file():
                    results.append(f"📄 {item.name} — {item.parent}")
        except Exception:
            pass
        
        if not results:
            return f"No files matching '{pattern}' found."
        
        return "\n".join(results[:max_results])
    
    except Exception as e:
        return f"Search error: {e}"


def universal_dir(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for universal directory."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    path = params.get("path", "")
    
    try:
        if action == "drives":
            return get_drives()
        
        elif action == "list":
            return list_directory(
                path,
                show_hidden=params.get("show_hidden", False)
            )
        
        elif action == "info":
            return get_path_info(path)
        
        elif action == "navigate":
            return navigate_to(path)
        
        elif action == "find":
            return find_files(
                path,
                params.get("pattern", ""),
                int(params.get("max_results", 20))
            )
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Universal dir error: {e}"
