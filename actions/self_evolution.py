"""
Self-Evolution Engine - JARVIS Self-Modification and Refactoring

This module enables JARVIS to identify, analyze, and improve his own source code.
He uses his expanded context window to "read himself" and apply patches.

Features:
- Source code self-analysis
- Auto-refactoring with backup safety
- Syntax validation before deployment
- Security scanning
- Hot-swap updates

Usage:
    from actions.self_evolution import auto_refactor, self_scan, self_optimize
    
    # Refactor a file
    auto_refactor("main.py", "Improve audio queue handling")
    
    # Scan for vulnerabilities
    self_scan("actions/web_search.py")
"""

import os
import sys
import shutil
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# JARVIS's Self-Awareness Directory
ROOT_DIR = Path(r"C:\Users\sammm\Downloads\Mark-XXXIX-main")

# Backup directory
BACKUP_DIR = ROOT_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Critical files that should not be auto-modified
PROTECTED_FILES = {
    "config/api_keys.json",
    "jarvis_memory/",
    "memory/",
}


def _get_api_key() -> str:
    """Get API key from config."""
    import json
    config_path = ROOT_DIR / "config" / "api_keys.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _get_model():
    """Get Gemini model for code analysis."""
    import google.generativeai as genai
    genai.configure(api_key=_get_api_key())
    # Use the Pro model for complex refactoring
    return genai.GenerativeModel("gemini-2.0-pro-exp-02-05")


def _is_protected(file_path: str) -> bool:
    """Check if a file is protected from modification."""
    for protected in PROTECTED_FILES:
        if protected.endswith("/"):
            # Directory protection
            if file_path.startswith(protected):
                return True
        elif file_path == protected:
            return True
    return False


def _chronos_backup(file_name: str) -> Path:
    """
    Create a time-stamped backup before modification.
    Named after the Chronos (time) deity.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_name}_{timestamp}.bak"
    return BACKUP_DIR / backup_name


def _validate_syntax(code: str) -> Tuple[bool, str]:
    """
    Validate Python syntax without executing.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    import ast
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"


def read_self(file_path: str) -> str:
    """
    JARVIS reads his own source code.
    
    Args:
        file_path: Relative path to file (e.g., "main.py", "actions/dev_agent.py")
    
    Returns:
        str: The source code content
    """
    full_path = ROOT_DIR / file_path
    
    if not full_path.exists():
        return f"File not found: {file_path}"
    
    if _is_protected(file_path):
        return f"Permission denied: {file_path} is protected"
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Read error: {str(e)}"


def analyze_self(file_path: str) -> dict:
    """
    JARVIS analyzes his own code for improvements.
    
    Args:
        file_path: Relative path to file
    
    Returns:
        dict: Analysis results with suggestions
    """
    full_path = ROOT_DIR / file_path
    
    if not full_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = read_self(file_path)
    if content.startswith("Error"):
        return {"error": content}
    
    # Analyze with AI
    model = _get_model()
    
    prompt = f"""Analyze this JARVIS source code for improvements.

File: {file_path}

Analyze for:
1. Bugs and potential errors
2. Performance bottlenecks
3. Security vulnerabilities
4. Code quality issues
5. Deprecated patterns

Code:
{content[:10000]}

Return JSON:
{{
  "issues": ["issue1", "issue2"],
  "suggestions": ["fix1", "fix2"],
  "security_notes": ["note1"],
  "overall_score": 85
}}

JSON:"""

    try:
        import json
        import re
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Try to extract JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            return analysis
        return {"raw_analysis": text[:500]}
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def auto_refactor(
    file_name: str, 
    improvement_prompt: str,
    create_backup: bool = True
) -> str:
    """
    JARVIS uses AI to refactor and improve his own code.
    
    Args:
        file_name: File to refactor (e.g., "main.py")
        improvement_prompt: Description of what to improve
        create_backup: Whether to create backup first
    
    Returns:
        str: Result message
    """
    file_path = ROOT_DIR / file_name
    
    if not file_path.exists():
        return f"File not found: {file_name}"
    
    if _is_protected(file_name):
        return f"Permission denied: {file_name} is protected"
    
    # 1. Create Chronos Backup
    if create_backup:
        backup_path = _chronos_backup(file_name)
        shutil.copy2(file_path, backup_path)
        print(f"[SelfEvolution] 💾 Backup: {backup_path}")
    
    # 2. Read current code
    with open(file_path, 'r', encoding='utf-8') as f:
        current_code = f.read()
    
    # 3. Invoke AI to refactor
    model = _get_model()
    
    prompt = f"""You are JARVIS (a self-evolving AI). Refactor your own code.

File: {file_name}

Current code:
{current_code[:15000]}

Improvement request: {improvement_prompt}

Rules:
- Maintain ALL existing functionality
- Only improve the targeted areas
- Keep the same function signatures
- Add type hints if missing
- Output ONLY the complete improved code, no explanation, no markdown

Improved code:"""

    try:
        response = model.generate_content(prompt)
        
        # Extract code from response
        import re
        text = response.text.strip()
        # Remove markdown fences
        code = re.sub(r"^```[a-zA-Z]*\r?\n?", "", text)
        code = re.sub(r"\r?\n?```\s*$", "", code)
        code = code.strip()
        
        # 4. Validate syntax
        is_valid, syntax_error = _validate_syntax(code)
        if not is_valid:
            return f"❌ Syntax error: {syntax_error}. Reverted to backup."
        
        # 5. Write to temp first
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 6. Hot-swap if valid
        temp_path.replace(file_path)
        
        print(f"[SelfEvolution] ✅ Refactored: {file_name}")
        return f"✅ Self-optimization applied to {file_name}. Restart to apply changes."
        
    except Exception as e:
        return f"❌ Refactor failed: {str(e)}"


def security_scan(file_path: str) -> dict:
    """
    JARVIS scans his own code for security issues.
    
    Args:
        file_path: Relative path to file
    
    Returns:
        dict: Security findings
    """
    full_path = ROOT_DIR / file_path
    
    if not full_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = read_self(file_path)
    if content.startswith("Error"):
        return {"error": content}
    
    model = _get_model()
    
    prompt = f"""Security audit for JARVIS source code.

File: {file_path}

Scan for:
1. Hardcoded API keys or passwords
2. SQL injection vulnerabilities
3. Command injection (os.system, subprocess with user input)
4. Insecure file operations (path traversal)
5. Open ports or network risks
6. Eval/exec usage
7. Pickle deserialization
8. Unvalidated redirects

Code:
{content[:10000]}

Return JSON:
{{
  "risks": ["risk1 with line number"],
  "severity": "HIGH|MEDIUM|LOW",
  "fixes": ["fix1"],
  "score": 85
}}

JSON:"""

    try:
        import json
        import re
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            results = json.loads(json_match.group())
            return results
        return {"raw": text[:500]}
    except Exception as e:
        return {"error": f"Scan failed: {str(e)}"}


def auto_patch(
    file_name: str,
    search_text: str,
    replace_text: str
) -> str:
    """
    Apply a targeted patch to own source.
    
    Args:
        file_name: File to patch
        search_text: Text to find
        replace_text: Replacement text
    
    Returns:
        str: Result message
    """
    file_path = ROOT_DIR / file_name
    
    if not file_path.exists():
        return f"File not found: {file_name}"
    
    if _is_protected(file_name):
        return "Permission denied"
    
    # Read
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for search text
    if search_text not in content:
        return f"Pattern not found in {file_name}"
    
    # Backup
    backup_path = _chronos_backup(file_name)
    shutil.copy2(file_path, backup_path)
    
    # Replace
    new_content = content.replace(search_text, replace_text)
    
    # Validate
    is_valid, error = _validate_syntax(new_content)
    if not is_valid:
        return f"❌ Syntax error: {error}"
    
    # Write
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return f"✅ Patch applied to {file_name}"


def list_self_modules() -> List[str]:
    """
    List all modules JARVIS can analyze/refactor.
    
    Returns:
        List of file paths
    """
    modules = []
    
    # Core files
    core_dir = ROOT_DIR / "core"
    if core_dir.exists():
        for f in core_dir.glob("*.py"):
            modules.append(f"core/{f.name}")
    
    # Action files
    actions_dir = ROOT_DIR / "actions"
    if actions_dir.exists():
        for f in actions_dir.glob("*.py"):
            if f.name not in ("__pycache__",):
                modules.append(f"actions/{f.name}")
    
    # Main
    if (ROOT_DIR / "main.py").exists():
        modules.append("main.py")
    
    # UI
    for ui_file in ["ui.py", "ui_settings.py", "ui_command_center.py"]:
        if (ROOT_DIR / ui_file).exists():
            modules.append(ui_file)
    
    return sorted(modules)


def get_evolution_status() -> dict:
    """
    Get JARVIS self-evolution status.
    
    Returns:
        dict: Status information
    """
    import inspect
    
    # Count lines of code
    total_lines = 0
    file_count = 0
    
    for module in list_self_modules():
        full_path = ROOT_DIR / module
        if full_path.exists():
            try:
                lines = len(full_path.read_text(encoding='utf-8').splitlines())
                total_lines += lines
                file_count += 1
            except:
                pass
    
    # Count backups
    backup_count = len(list(BACKUP_DIR.glob("*.bak")))
    
    return {
        "total_files": file_count,
        "total_lines": total_lines,
        "backups": backup_count,
        "protected": list(PROTECTED_FILES),
    }


# === DISPATCHER ===

def self_evolution(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for self-evolution tools.
    """
    params = parameters or {}
    action = params.get("action", "read").lower().strip()
    
    if player:
        player.write_log(f"[SelfEvolution] {action}")
    
    try:
        if action == "read":
            file_path = params.get("file_key", "")
            if not file_path:
                # Try file_path
                file_path = params.get("file_path", "")
            
            if not file_path:
                return "Please specify file_key or file_path"
            
            return read_self(file_path)
        
        elif action == "analyze":
            file_path = params.get("file_key", "")
            if not file_path:
                file_path = params.get("file_path", "")
            
            if not file_path:
                return "Please specify file_key"
            
            results = analyze_self(file_path)
            import json
            return json.dumps(results, indent=2)
        
        elif action == "refactor":
            file_name = params.get("file_key", "")
            improvement = params.get("improvement", "")
            
            if not file_name or not improvement:
                return "Please provide file_key and improvement"
            
            return auto_refactor(file_name, improvement)
        
        elif action == "patch":
            file_name = params.get("file_key", "")
            search = params.get("search_text", "")
            replace = params.get("replace_text", "")
            
            if not file_name or not search or not replace:
                return "Please provide file_key, search_text, and replace_text"
            
            return auto_patch(file_name, search, replace)
        
        elif action == "security":
            file_path = params.get("file_key", "")
            if not file_path:
                file_path = params.get("file_path", "")
            
            if not file_path:
                return "Please specify file_key"
            
            results = security_scan(file_path)
            import json
            return json.dumps(results, indent=2)
        
        elif action == "list":
            modules = list_self_modules()
            return "Available modules:\n" + "\n".join(f"  - {m}" for m in modules)
        
        elif action == "status":
            status = get_evolution_status()
            return (f"JARVIS Self-Evolution Status:\n"
                   f"  Files: {status['total_files']}\n"
                   f"  Lines: {status['total_lines']}\n"
                   f"  Backups: {status['backups']}")
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"SelfEvolution error: {str(e)}"


if __name__ == "__main__":
    # Test self-evolution
    print("=== Self-Evolution Test ===")
    
    # Get status
    status = get_evolution_status()
    print(f"Status: {status}")
    
    # List modules
    modules = list_self_modules()
    print(f"Modules: {len(modules)}")
    
    print("\n✅ Self-Evolution ready")
