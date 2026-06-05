# self_updater.py
"""
Self-Updater - JARVIS can update its own code and self-modify.
Enables auto-update capabilities for continuous improvement.
"""

import json
import sys
import shutil
import platform
from pathlib import Path
from datetime import datetime


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
UPDATE_LOG = BASE_DIR / "memory" / "update_log.json"

# Current version
CURRENT_VERSION = "2.0.0"
VERSION_NAME = "MARK XXXIX Enhanced"


def get_version() -> str:
    """Get current JARVIS version info."""
    return f"JARVIS {VERSION_NAME} v{CURRENT_VERSION}"


def get_system_info() -> str:
    """Get detailed system info including code stats."""
    try:
        py_files = list(BASE_DIR.rglob("*.py"))
        total_lines = 0
        for f in py_files:
            try:
                total_lines += len(f.read_text(encoding="utf-8").splitlines())
            except:
                pass
        memory_file = BASE_DIR / "memory" / "long_term.json"
        memory_entries = 0
        if memory_file.exists():
            try:
                data = json.loads(memory_file.read_text(encoding="utf-8"))
                memory_entries = sum(len(v) for v in data.values() if isinstance(v, dict))
            except:
                pass
        return (
            f"System Info:\n"
            f"  Version: {VERSION_NAME} v{CURRENT_VERSION}\n"
            f"  Python Files: {len(py_files)}\n"
            f"  Lines of Code: {total_lines}\n"
            f"  Memory Entries: {memory_entries}\n"
            f"  OS: {platform.system()}\n"
            f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    except Exception as e:
        return f"System info error: {e}"


def read_code_file(path: str) -> str:
    """Read a code file from the system."""
    try:
        target = BASE_DIR / path
        if not target.exists():
            return f"File not found: {path}"
        content = target.read_text(encoding="utf-8")
        return content[:10000]
    except Exception as e:
        return f"Read error: {e}"


def write_code_file(path: str, content: str, backup: bool = True) -> str:
    """Write/update a code file."""
    try:
        target = BASE_DIR / path
        if backup and target.exists():
            backup_path = target.with_suffix(target.suffix + ".bak")
            shutil.copy2(target, backup_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Updated: {path}"
    except Exception as e:
        return f"Write error: {e}"


def restore_backup(path: str) -> str:
    """Restore a file from backup."""
    try:
        target = BASE_DIR / path
        backup_path = target.with_suffix(target.suffix + ".bak")
        if not backup_path.exists():
            return f"No backup found for: {path}"
        shutil.copy2(backup_path, target)
        return f"Restored: {path}"
    except Exception as e:
        return f"Restore error: {e}"


def list_files(pattern: str = "*.py") -> str:
    """List code files."""
    try:
        files = list(BASE_DIR.rglob(pattern))
        files = files[:30]
        if not files:
            return f"No files found: {pattern}"
        lines = [f"Files ({len(files)}):"]
        for f in files:
            rel_path = f.relative_to(BASE_DIR)
            lines.append(f"  {rel_path}")
        return "\n".join(lines)
    except Exception as e:
        return f"List error: {e}"


def search_code(pattern: str, file_pattern: str = "*.py") -> str:
    """Search for a pattern in code."""
    try:
        results = []
        for f in BASE_DIR.rglob(file_pattern):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if pattern.lower() in content.lower():
                    lines = content.splitlines()
                    for i, line in enumerate(lines, 1):
                        if pattern.lower() in line.lower():
                            results.append(f"{f.name}:{i} - {line[:80]}")
            except:
                pass
            if len(results) > 30:
                break
        if not results:
            return f"No matches for: {pattern}"
        return "Matches:\n" + "\n".join(results[:20])
    except Exception as e:
        return f"Search error: {e}"


def create_file(path: str, content: str = "") -> str:
    """Create a new file."""
    try:
        target = BASE_DIR / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Created: {path}"
    except Exception as e:
        return f"Create error: {e}"


def delete_file(path: str) -> str:
    """Delete a file."""
    try:
        target = BASE_DIR / path
        if not target.exists():
            return f"File not found: {path}"
        target.unlink()
        return f"Deleted: {path}"
    except Exception as e:
        return f"Delete error: {e}"


def _log_update(action: str, details: str, status: str = "success") -> None:
    """Log an update action."""
    try:
        UPDATE_LOG.parent.mkdir(parents=True, exist_ok=True)
        if UPDATE_LOG.exists():
            logs = json.loads(UPDATE_LOG.read_text(encoding="utf-8"))
        else:
            logs = []
        logs.append({"action": action, "details": details, "status": status, "timestamp": datetime.now().isoformat()})
        logs = logs[-50:]
        UPDATE_LOG.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding="utf-8")
    except:
        pass


def get_update_log(count: int = 10) -> str:
    """Get recent update logs."""
    try:
        if not UPDATE_LOG.exists():
            return "No update logs yet"
        logs = json.loads(UPDATE_LOG.read_text(encoding="utf-8"))
        lines = ["Recent Updates:"]
        for log in logs[-count:]:
            ts = log.get("timestamp", "")[:16]
            action = log.get("action", "")
            status = log.get("status", "")
            lines.append(f"  [{ts}] {action} - {status}")
        return "\n".join(lines)
    except Exception as e:
        return f"Log error: {e}"


def self_updater(parameters: dict = None, response=None, player=None, session_memory=None) -> str:
    """Main dispatcher for self-updater."""
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    
    if player:
        player.write_log(f"[self_update] {action}")
    
    try:
        if action == "version":
            return get_version()
        elif action == "system_info":
            return get_system_info()
        elif action == "read":
            return read_code_file(params.get("path", ""))
        elif action == "write":
            path = params.get("path", "")
            result = write_code_file(path, params.get("content", ""))
            _log_update("write", path, "success")
            return result
        elif action == "restore":
            path = params.get("path", "")
            result = restore_backup(path)
            _log_update("restore", path, "success")
            return result
        elif action == "list":
            return list_files(params.get("pattern", "*.py"))
        elif action == "search":
            return search_code(params.get("pattern", ""), params.get("file_pattern", "*.py"))
        elif action == "create":
            path = params.get("path", "")
            result = create_file(path, params.get("content", ""))
            _log_update("create", path, "success")
            return result
        elif action == "delete":
            path = params.get("path", "")
            result = delete_file(path)
            _log_update("delete", path, "success")
            return result
        elif action == "logs":
            return get_update_log(int(params.get("count", 10)))
        else:
            return get_version()
    except Exception as e:
        _log_update(action or "error", str(e), "error")
        return f"Self-updater error: {e}"
