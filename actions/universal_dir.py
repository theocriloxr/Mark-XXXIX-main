# universal_dir.py - Access any directory on the system
import os
import sys
import platform
from pathlib import Path

_OS = platform.system()

def list_drives() -> str:
    """List all available drives/volumes."""
    if _OS == "Windows":
        try:
            import winreg
            drives = []
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                drive = f"{letter}:\\"
                if Path(drive).exists():
                    drives.append(drive)
            return "Available drives: " + ", ".join(drives)
        except:
            pass
    
    # Unix-like
    volumes = ["/"]
    return "Mount points:\n  /\n  /home\n  /mnt"

def list_directory(path: str = "/", depth: int = 1) -> str:
    """List directory contents with depth control."""
    try:
        target = Path(path).expanduser().resolve()
        
        if not target.exists():
            return f"Path not found: {path}"
        
        if not target.is_dir():
            return f"Not a directory: {path}"
        
        items = []
        for item in sorted(target.iterdir())[:50]:
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name}")
        
        return f"Contents of {target}:\n" + "\n".join(items)
    except PermissionError:
        return "Permission denied"
    except Exception as e:
        return f"Error: {e}"

def get_disk_info() -> str:
    """Get all disk/volume info."""
    if _OS == "Windows":
        try:
            import winreg
            drives = []
            for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
                drive = f"{letter}:\\"
                if Path(drive).exists():
                    try:
                        import psutil
                        usage = psutil.disk_usage(drive)
                        drives.append(f"{drive} {usage.used//(1024**3)}GB/{usage.total//(1024**3)}GB")
                    except:
                        drives.append(drive)
            return "Disks: " + ", ".join(drives)
        except:
            pass
    
    return "Disk info not available"

def universal_dir(parameters: dict = None, response=None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "drives").lower().strip()
    
    if action == "drives":
        return list_drives()
    elif action == "list":
        return list_directory(params.get("path", "/"), int(params.get("depth", 1)))
    elif action == "disks":
        return get_disk_info()
    else:
        return list_drives()
