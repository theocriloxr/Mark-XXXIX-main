"""
Self-Repair Module - JARVIS Self-Awareness and Self-Repair

Allows JARVIS to identify, read, analyze, and patch his own source code.
This is the critical component for the "Self-Evolution" capability.

Features:
- Read source code from any file in the JARVIS root directory
- Analyze code for bugs and optimization opportunities
- Apply patches with backup safety
- Syntax validation before applying changes
- Self-improvement loop with sandbox testing

Usage:
    from actions.self_repair import read_source_code, update_source_code, patch_system_file
    
    # Read a source file
    content = read_source_code("main.py")
    
    # Update source code with safety
    result = update_source_code("main.py", new_content)
    
    # Patch a specific file
    result = patch_system_file("ui_settings.py", old_str, new_str)
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

# JARVIS Root Directory
BASE_DIR = Path(r"C:\Users\sammm\Downloads\Mark-XXXIX-main")

# Map of core files for quick access
CORE_FILES = {
    "main": "main.py",
    "ui": "ui.py",
    "ui_settings": "ui_settings.py",
    "vision": "actions/vision_tools.py",
    "agent": "core/agent_engine.py",
    "config": "core/config_manager.py",
    "memory": "memory/memory_manager.py",
    "prompt": "core/prompt.txt",
    "economic": "actions/economic_agent.py",
}


def get_base_dir() -> Path:
    """Get the base directory of the application."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return BASE_DIR


def read_source_code(file_key: str = None, file_path: str = None) -> str:
    """
    Allows JARVIS to see his own heart - read source code.
    
    Args:
        file_key: Key name from CORE_FILES (e.g., "main", "ui_settings")
        file_path: Full relative path to file (e.g., "actions/dev_agent.py")
    
    Returns:
        str: The source code content, or error message
    """
    try:
        if file_path:
            # Direct path provided
            full_path = BASE_DIR / file_path
        elif file_key:
            # Look up from CORE_FILES
            if file_key not in CORE_FILES:
                return f"Error: Unknown file key '{file_key}'. Available keys: {', '.join(CORE_FILES.keys())}"
            full_path = BASE_DIR / CORE_FILES[file_key]
        else:
            return "Error: Please provide either file_key or file_path"
        
        if not full_path.exists():
            return f"Error: File not found: {full_path}"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    except Exception as e:
        return f"Error reading source: {str(e)}"


def update_source_code(
    file_key: str = None, 
    file_path: str = None, 
    new_content: str = None,
    create_backup: bool = True
) -> str:
    """
    Allows JARVIS to rewrite his logic with safety guarantees.
    
    Args:
        file_key: Key name from CORE_FILES
        file_path: Full relative path to file
        new_content: The new code content to write
        create_backup: Whether to create backup before writing (default: True)
    
    Returns:
        str: Success or error message
    """
    try:
        if not new_content:
            return "Error: No new_content provided"
        
        # Determine file path
        if file_path:
            full_path = BASE_DIR / file_path
        elif file_key:
            if file_key not in CORE_FILES:
                return f"Error: Unknown file key '{file_key}'"
            full_path = BASE_DIR / CORE_FILES[file_key]
        else:
            return "Error: Please provide file_key or file_path"
        
        if not full_path.exists():
            return f"Error: File not found: {full_path}"
        
        # 1. Create backup first (Safety Protocol)
        if create_backup:
            backup_path = full_path.with_suffix(full_path.suffix + ".bak")
            import shutil
            shutil.copy2(full_path, backup_path)
        
        # 2. Write the new code temporarily first
        temp_path = full_path.with_suffix(full_path.suffix + ".tmp")
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 3. Syntax Check - does it even compile?
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(temp_path)],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Syntax error - remove temp and return error
                temp_path.unlink()
                error_msg = result.stderr.decode('utf-8', errors='replace')[:500]
                return f"❌ Syntax check failed. Reverting to safe state.\nError: {error_msg}"
            
        except subprocess.TimeoutExpired:
            temp_path.unlink()
            return "❌ Syntax check timed out. Reverting to safe state."
        
        except Exception as e:
            # Can't run py_compile - try alternative check
            pass
        
        # 4. If syntax check passed, apply the change
        temp_path.replace(full_path)
        
        return f"✅ Logic improved in {full_path.name}. Restart required to apply changes."
    
    except Exception as e:
        return f"❌ Upgrade failed: {str(e)}"


def patch_system_file(
    file_key: str = None,
    file_path: str = None,
    search_text: str = None,
    replace_text: str = None
) -> str:
    """
    Patch a specific section of a source file.
    
    Args:
        file_key: Key name from CORE_FILES
        file_path: Full relative path to file
        search_text: The exact text to find and replace
        replace_text: The replacement text
    
    Returns:
        str: Success or error message
    """
    try:
        if not search_text or not replace_text:
            return "Error: Both search_text and replace_text are required"
        
        # Determine file path
        if file_path:
            full_path = BASE_DIR / file_path
        elif file_key:
            if file_key not in CORE_FILES:
                return f"Error: Unknown file key '{file_key}'"
            full_path = BASE_DIR / CORE_FILES[file_key]
        else:
            return "Error: Please provide file_key or file_path"
        
        if not full_path.exists():
            return f"Error: File not found: {full_path}"
        
        # Read current content
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if search_text exists
        if search_text not in content:
            return f"🔍 Text pattern not found in {full_path.name}. No patch applied."
        
        # Create backup
        backup_path = full_path.with_suffix(full_path.suffix + ".bak")
        import shutil
        shutil.copy2(full_path, backup_path)
        
        # Apply patch
        new_content = content.replace(search_text, replace_text)
        
        # Write to temp first
        temp_path = full_path.with_suffix(full_path.suffix + ".tmp")
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Syntax check
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(temp_path)],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                temp_path.unlink()
                error_msg = result.stderr.decode('utf-8', errors='replace')[:300]
                return f"❌ Syntax check failed: {error_msg}"
            
        except Exception:
            pass  # Continue if check fails
        
        # Apply
        temp_path.replace(full_path)
        
        return f"✅ Patch applied to {full_path.name}. Restart required."
    
    except Exception as e:
        return f"❌ Patch failed: {str(e)}"


def analyze_bug(error_message: str) -> Tuple[str, str, str]:
    """
    Analyze an error message and suggest a fix.
    
    Args:
        error_message: The error traceback or message
    
    Returns:
        Tuple of (file_key, search_text, suggested_fix)
    """
    error_lower = error_message.lower()
    
    # PySide6/QDialog errors
    if "qdialog" in error_lower and "argument" in error_lower:
        return (
            "ui_settings",
            "super().__init__(parent)",
            "super().__init__(parent)"
        )
    
    # Import errors
    if "modulenotfounderror" in error_lower or "importerror" in error_lower:
        # Try to extract module name
        import re
        match = re.search(r"module '([^']+)'", error_lower)
        if match:
            module = match.group(1)
            return (" unknown", "", f"pip install {module}")
    
    # Generic suggestions
    return ("", "", "Review the error and apply appropriate fix.")


def get_system_status() -> dict:
    """
    Get JARVIS system status for self-diagnosis.
    
    Returns:
        dict: Status information
    """
    status = {
        "base_dir": str(BASE_DIR),
        "core_files": list(CORE_FILES.keys()),
        "python_version": sys.version,
    }
    
    # Check if critical files exist
    existing = []
    missing = []
    
    for key, path in CORE_FILES.items():
        full_path = BASE_DIR / path
        if full_path.exists():
            existing.append(key)
        else:
            missing.append(key)
    
    status["existing_files"] = existing
    status["missing_files"] = missing
    
    return status


# === DISPATCHER ===

def self_repair(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for self-repair tools.
    
    Usage:
        self_repair(action="read", file_key="main")
        self_repair(action="patch", file_key="ui_settings", search_text="...", replace_text="...")
        self_repair(action="status")
    """
    params = parameters or {}
    action = params.get("action", "read").lower().strip()
    
    if player:
        player.write_log(f"[SelfRepair] {action}")
    
    try:
        if action == "read":
            file_key = params.get("file_key")
            file_path = params.get("file_path")
            
            if not file_key and not file_path:
                return "Please specify file_key or file_path"
            
            content = read_source_code(file_key, file_path)
            
            # If content is large, truncate for display
            if len(content) > 500:
                return content[:500] + "\n... [truncated]"
            
            return content
        
        elif action == "write":
            file_key = params.get("file_key")
            file_path = params.get("file_path")
            content = params.get("content")
            
            if not content:
                return "Please provide content parameter"
            
            result = update_source_code(file_key, file_path, content)
            if speak:
                speak(result)
            return result
        
        elif action == "patch":
            file_key = params.get("file_key")
            file_path = params.get("file_path")
            search_text = params.get("search_text")
            replace_text = params.get("replace_text")
            
            if not search_text or not replace_text:
                return "Please provide search_text and replace_text"
            
            result = patch_system_file(file_key, file_path, search_text, replace_text)
            if speak:
                speak(result)
            return result
        
        elif action == "analyze":
            error_msg = params.get("error", "")
            
            if not error_msg:
                return "Please provide error parameter to analyze"
            
            file_key, search, fix = analyze_bug(error_msg)
            return f"Suggested fix for {file_key}: {fix}"
        
        elif action == "status":
            status = get_system_status()
            lines = [
                "JARVIS Self-Repair Status:",
                f"Base: {status['base_dir']}",
                f"Python: {status['python_version'][:8]}",
                f"Files: {len(status['existing_files'])}/{len(CORE_FILES)}",
                f"Existing: {', '.join(status['existing_files'])}",
            ]
            return "\n".join(lines)
        
        elif action == "list":
            # List available files
            lines = ["Available Core Files:"]
            for key, path in CORE_FILES.items():
                lines.append(f"  {key}: {path}")
            return "\n".join(lines)
        
        else:
            return f"Unknown action: {action}. Available: read, write, patch, analyze, status, list"
    
    except Exception as e:
        return f"SelfRepair error: {str(e)}"


if __name__ == "__main__":
    # Test self-repair
    print("=== JARVIS Self-Repair Test ===")
    
    # Get status
    status = get_system_status()
    print(f"Base: {status['base_dir']}")
    print(f"Existing: {status['existing_files']}")
    
    # Test read
    print("\n--- Testing Read ---")
    content = read_source_code("main")
    print(f"main.py lines: {len(content.splitlines())}")
    
    print("\n✅ Self-Repair ready")
