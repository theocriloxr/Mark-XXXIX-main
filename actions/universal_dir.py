# universal_dir.py
"""
Universal Directory Access - Full filesystem access beyond home directory.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from datetime import datetime


_OS = platform.system()


def get_drives() -> str:
    """List all available drives/mount points."""
    if _OS == "windows":
        try:
            output = []
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                drive = f"{letter}:\\"
                if Path(drive).exists():
                    try:
                        stat = os.stat(drive)
                        output.append(f"{letter}:")
                    except:
                        output.append(f"{letter}:")
            return f"Available drives: {', '.join(output)}"
        except Exception as e:
            return f"Error: {e}"
    elif _OS == "darwin":
        volumes = "/Volumes"
        try:
            if Path(volumes).exists():
                drives = [p.name for p in Path(volumes).iterdir() if p.is_dir()]
                return f"Volumes: {', '.join(drives) if drives else 'Main disk only'}"
        except:
            pass
        return "Available: Root and /Volumes"
    else:
        return "Available: / (root)"


def list_directory(path: str, show_hidden: bool = False) -> str:
    """List contents of any directory."""
    try:
        target = Path(path)
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
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                elif size < 1024 * 1024 * 1024:
                    size_str = f"{size/1024/1024:.1f} MB"
                else:
                    size_str = f"{size/1024/1024/1024:.1f} GB"
                items.append(f"📄 {item.name} ({size_str})")
        
        if not items:
            return f"Directory is empty: {path}"
        
        return f"Contents of {path} ({len(items)} items):\n" + "\n".join(items)
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error: {e}"


def get_info(path: str) -> str:
    """Get directory info."""
    try:
        target = Path(path)
        if not target.exists():
            return f"Path not found: {path}"
        
        stat = target.stat()
        info = {
            "Path": str(target),
            "Type": "Directory" if target.is_dir() else "File",
            "Size": stat.st_size,
            "Created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
            "Modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "Accessed": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M"),
        }
        
        lines = [f"Info for {path}:"]
        for k, v in info.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def find_files(path: str, pattern: str, max_results: int = 20) -> str:
    """Find files matching pattern."""
    try:
        search_path = Path(path)
        if not search_path.exists():
            return f"Path not found: {path}"
        
        results = []
        try:
            for item in search_path.rglob(f"*{pattern}*"):
                if item.is_file():
                    results.append(str(item))
                    if len(results) >= max_results:
                        break
        except Exception:
            pass
        
        if not results:
            return f"No files matching '{pattern}' found in {path}"
        
        return f"Found {len(results)} file(s):\n" + "\n".join(results[:max_results])
    except Exception as e:
        return f"Error: {e}"


def universal_dir(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    path = params.get("path", "C:\\" if _OS == "windows" else "/")
    
    if player:
        player.write_log(f"[universal_dir] {action} {path}")
    
    try:
        if action == "drives" or action == "list_drives":
            return get_drives()
        elif action == "list":
            return list_directory(
                path,
                show_hidden=params.get("show_hidden", False)
            )
        elif action == "info":
            return get_info(path)
        elif action == "navigate":
            return list_directory(path)
        elif action == "find":
            return find_files(
                path,
                params.get("pattern", ""),
                int(params.get("max_results", 20))
            )
        else:
            return get_drives()
    except Exception as e:
        return f"Universal dir error: {e}"
