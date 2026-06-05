# universal_dir.py
"""
Universal Directory Access - Access any folder/drive on the system.
Part of enhanced JARVIS system for comprehensive file access.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List

_OS = platform.system()


def get_drives() -> List[str]:
    """Get all available drives on the system."""
    drives = []
    
    if _OS == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\MountedDevices")
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if name.startswith("\\DosDevices\\") and value:
                        drive = name.replace("\\DosDevices\\", "")[:2]
                        if drive not in drives and len(drive) == 2:
                            drives.append(drive)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except:
            # Fallback
            for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
                if Path(f"{letter}:\\").exists():
                    drives.append(f"{letter}:")
        # Always include C:
        if "C:" not in drives:
            drives.insert(0, "C:")
    else:
        # Unix-like
        drives = ["/"]
        # Try common mount points
        for mp in ["/media", "/mnt", "/Volumes"]:
            if Path(mp).exists():
                drives.append(mp)
    
    return drives


def list_root_dirs(path: str = "") -> str:
    """List root level directories."""
    try:
        if not path:
            return "\n".join(f"📁 {d}" for d in get_drives())
        
        target = Path(path)
        if not target.exists():
            return f"Path not found: {path}"
        
        items = []
        for item in sorted(target.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                sz = item.stat().st_size
                items.append(f"📄 {item.name}")
        
        if not items:
            return "Empty directory"
        
        return f"{path}:\n" + "\n".join(items)
    except Exception as e:
        return f"Error: {e}"


def get_disk_info(path: str = "") -> str:
    """Get disk/partition info."""
    try:
        if _OS == "Windows":
            result = subprocess.run(
                ["wmic", "logicaldisk", "get", "caption,size,freespace,drivetype"],
                capture_output=True, text=True
            )
            return result.stdout
        else:
            result = subprocess.run(
                ["df", "-h"],
                capture_output=True, text=True
            )
            return result.stdout
    except Exception as e:
        return f"Error: {e}"


def universal_dir(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for universal directory actions."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
    try:
        if action == "list" or action == "ls":
            return list_root_dirs(params.get("path", ""))
        
        elif action == "drives":
            return "\n".join(f"📁 {d}" for d in get_drives())
        
        elif action == "disk_info":
            return get_disk_info(params.get("path", ""))
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Universal dir error: {e}"
