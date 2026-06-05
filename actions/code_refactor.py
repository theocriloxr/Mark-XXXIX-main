# code_refactor.py
"""
Self-Code Editor - JARVIS can edit and update its own code.
"""

import os
import sys
from pathlib import Path


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()


def read_code_file(relative_path: str) -> str:
    """Read a code file from JARVIS codebase."""
    try:
        target = BASE_DIR / relative_path
        if not target.exists():
            return f"File not found: {relative_path}"
        
        content = target.read_text(encoding="utf-8")
        if len(content) > 5000:
            content = content[:5000] + "\n\n[Truncated]"
        return content
    except Exception as e:
        return f"Error reading: {e}"


def write_code_file(relative_path: str, content: str) -> str:
    """Write to a code file in JARVIS codebase."""
    try:
        target = BASE_DIR / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Updated: {relative_path}"
    except Exception as e:
        return f"Error writing: {e}"


def list_code_files() -> str:
    """List all Python files in codebase."""
    try:
        files = list(BASE_DIR.rglob("*.py"))
        lines = ["JARVIS Codebase:"]
        for f in sorted(files)[:30]:
            rel = f.relative_to(BASE_DIR)
            lines.append(f"  {rel}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def get_code_stats() -> str:
    """Get code statistics."""
    try:
        files = list(BASE_DIR.rglob("*.py"))
        total_lines = 0
        total_files = len(files)
        
        for f in files:
            try:
                lines = len(f.read_text(encoding="utf-8").splitlines())
                total_lines += lines
            except:
                pass
        
        return (
            f"Codebase Stats:\n"
            f"  Files: {total_files}\n"
            f"  Lines: {total_lines}"
        )
    except Exception as e:
        return f"Error: {e}"


def search_code(pattern: str) -> str:
    """Search code for pattern."""
    try:
        files = list(BASE_DIR.rglob("*.py"))
        results = []
        
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                if pattern.lower() in content.lower():
                    results.append(str(f.relative_to(BASE_DIR)))
            except:
                pass
        
        if not results:
            return f"No matches for: {pattern}"
        
        return f"Found in {len(results)} file(s):\n" + "\n".join(results[:20])
    except Exception as e:
        return f"Error: {e}"


def code_refactor(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    
    if player:
        player.write_log(f"[code_refactor] {action}")
    
    try:
        if action == "read":
            return read_code_file(params.get("path", "main.py"))
        elif action == "write":
            return write_code_file(
                params.get("path", ""),
                params.get("content", "")
            )
        elif action == "list":
            return list_code_files()
        elif action == "stats":
            return get_code_stats()
        elif action == "search":
            return search_code(params.get("pattern", ""))
        else:
            return list_code_files()
    except Exception as e:
        return f"Code refactor error: {e}"
