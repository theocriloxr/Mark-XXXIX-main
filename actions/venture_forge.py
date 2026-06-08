"""
Venture Forge - JARVIS Full Codebase Generation Tool

This tool allows JARVIS to recursively create folders and files for entire business codebases.
He uses this to scaffold full codebases (React frontend + FastAPI backend + Docker config).

Features:
- Recursive folder/file creation
- Multi-file project generation
- Template-based business scaffolding
- Legal document generation
- Docker/Railway deployment ready

Usage:
    from actions.venture_forge import forge_project_structure, generate_business_venture
    
    # Forge a basic project structure
    forge_project_structure("my_saas", {"main.py": "print('hello')"})
    
    # Generate a full business venture
    generate_business_venture("invoice_processor", "SaaS", "Automated invoice processing")
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

# Base directory
BASE_DIR = Path(r"C:\Users\sammm\Downloads\Mark-XXXIX-main")
PROJECTS_DIR = Path(r"C:\Users\sammm\Downloads\JARVIS_PROJECTS")

# Ensure projects directory exists
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def forge_project_structure(root_name: str, structure: Dict[str, str]) -> str:
    """
    JARVIS uses this to build full business codebases.
    'structure' is a dictionary: {'folder/file.py': 'content'}
    
    Args:
        root_name: Name of the root project folder
        structure: Dict mapping file paths to their content
    
    Returns:
        str: Success message with path
    """
    base_path = PROJECTS_DIR / root_name
    
    for file_path, content in structure.items():
        full_path = base_path / file_path
        # Create directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the comprehensive file content
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    return f"🚀 Venture '{root_name}' forged at {base_path}"


def _get_api_key() -> str:
    """Get API key from config."""
    config_path = BASE_DIR / "config" / "api_keys.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _get_model():
    """Get Gemini model for code generation."""
    import google.generativeai as genai
    genai.configure(api_key=_get_api_key())
    return genai.GenerativeModel("gemini-2.5-flash")


def _strip_code fences(text: str) -> str:
    """Remove markdown code fences from generated code."""
    import re
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\r?\n?", "", text)
    text = re.sub(r"\r?\n?```\s*$", "", text)
    return text.strip()


def generate_business_venture(
    project_name: str,
    venture_type: str,
    description: str,
    framework: str = "auto",
    speak=None,
    player=None
) -> str:
    """
    Generate a complete business venture with full codebase.
    
    Args:
        project_name: Name of the venture
        venture_type: Type (SaaS, E-commerce, Portfolio, etc.)
        description: Business description
        framework: Preferred framework (auto, fastapi, django, react, etc.)
        speak: TTS speak function
        player: UI player
    
    Returns:
        str: Result message
    """
    def log(msg: str):
        print(f"[VentureForge] {msg}")
        if player:
            player.write_log(f"[VentureForge] {msg}")
    
    log(f"Generating {venture_type} venture: {project_name}")
    
    project_dir = PROJECTS_DIR / project_name.lower().replace(" ", "_")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine tech stack based on venture type
    if framework == "auto":
        if venture_type.lower() == "saas":
            tech_stack = "FastAPI + React"
        elif venture_type.lower() == "e-commerce":
            tech_stack = "Django + Vue"
        else:
            tech_stack = "Flask + Vanilla JS"
    else:
        tech_stack = framework
    
    # Generate architecture
    model = _get_model()
    
    prompt = f"""You are a senior software architect. Generate a complete business venture structure.

Project: {project_name}
Type: {venture_type}
Description: {description}
Tech Stack: {tech_stack}

Generate:
1. A tree map showing folder structure
2. Key files with descriptions
3. Core business logic

Follow this JSON format exactly:
{{
  "tree": "project_name/\n  ├── backend/\n  │   ├── main.py\n  │   └── requirements.txt\n  ├── frontend/\n  │   └── index.html",
  "files": [
    {{"path": "README.md", "description": "Project documentation"}},
    {{"path": "requirements.txt", "description": "Python dependencies"}},
    {{"path": "main.py", "description": "Main application entry point"}}
  ],
  "dependencies": ["fastapi", "uvicorn"],
  "run_command": "uvicorn main:app --reload"
}}

JSON:"""
    
    try:
        response = model.generate_content(prompt)
        raw = _strip_code_fences(response.text)
        plan = json.loads(raw)
    except Exception as e:
        log(f"Planning failed: {e}")
        return f"Could not generate venture structure: {e}"
    
    tree = plan.get("tree", "")
    files = plan.get("files", [])
    dependencies = plan.get("dependencies", [])
    run_command = plan.get("run_command", "python main.py")
    
    log(f"Architecture: {tree}")
    
    # Generate each file
    for file_info in files:
        file_path = file_info.get("path", "")
        file_desc = file_info.get("description", "")
        
        if not file_path:
            continue
        
        # Generate file content
        file_prompt = f"""Write complete, working code for: {file_path}
Purpose: {file_desc}
Project: {project_name} ({venture_type})
Tech Stack: {tech_stack}

Output ONLY raw code, no markdown, no explanation."""
        
        try:
            response = model.generate_content(file_prompt)
            code = _strip_code_fences(response.text)
            
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(code, encoding="utf-8")
            
            log(f"✓ {file_path}")
            
        except Exception as e:
            log(f"✗ {file_path}: {e}")
    
    # Create .env file
    env_content = f"""# Environment variables for {project_name}
# Railway Deployment Ready
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/db
"""
    (project_dir / ".env").write_text(env_content, encoding="utf-8")
    
    # Create .gitignore
    gitignore = """__pycache__/
*.pyc
*.pyo
.env
node_modules/
dist/
build/
"""
    (project_dir / ".gitignore").write_text(gitignore, encoding="utf-8")
    
    # Install dependencies
    if dependencies:
        log(f"Installing: {dependencies}")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + dependencies,
                capture_output=True,
                timeout=120,
                cwd=str(project_dir)
            )
        except Exception as e:
            log(f"Install warning: {e}")
    
    # Open in VSCode
    try:
        subprocess.Popen(["code", str(project_dir)], shell=True)
    except:
        pass
    
    result = f"🚀 Venture '{project_name}' ready at {project_dir}\nTree:\n{tree}"
    
    if speak:
        speak(result)
    
    return result


def generate_legal_document(
    document_type: str,
    company_name: str,
    jurisdiction: str = "Nigeria"
) -> str:
    """
    Generate legal documents for ventures.
    
    Args:
        document_type: Type (Terms of Service, Privacy Policy, NDA)
        company_name: Company name
        jurisdiction: Legal jurisdiction
    
    Returns:
        str: Path to generated document
    """
    model = _get_model()
    
    prompt = f"""Write a complete {document_type} for {company_name} under {jurisdiction} law.

Output ONLY raw text, no markdown, no explanation.

{document_type}:"""
    
    try:
        response = model.generate_content(prompt)
        content = _strip_code_fences(response.text)
        
        doc_path = PROJECTS_DIR / company_name.lower().replace(" ", "_") / f"{document_type.lower().replace(' ', '_')}.txt"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(content, encoding="utf-8")
        
        return f"Legal document generated: {doc_path}"
    
    except Exception as e:
        return f"Generation failed: {e}"


# === DISPATCHER ===

def venture_forge(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for Venture Forge tools.
    
    Usage:
        venture_forge(action="forge", structure={"main.py": "print('hello')"})
        venture_forge(action="generate", project_name="invoice_saas", venture_type="SaaS", description="...")
    """
    params = parameters or {}
    action = params.get("action", "forge").lower().strip()
    
    if player:
        player.write_log(f"[VentureForge] {action}")
    
    try:
        if action == "forge":
            root_name = params.get("root_name", "project")
            structure = params.get("structure", {})
            
            if not structure:
                return "Please provide structure dictionary"
            
            return forge_project_structure(root_name, structure)
        
        elif action == "generate":
            project_name = params.get("project_name", "")
            venture_type = params.get("venture_type", "SaaS")
            description = params.get("description", "")
            framework = params.get("framework", "auto")
            
            if not project_name or not description:
                return "Please provide project_name and description"
            
            return generate_business_venture(
                project_name, venture_type, description, framework, speak, player
            )
        
        elif action == "legal":
            document_type = params.get("document_type", "Terms of Service")
            company_name = params.get("company_name", "My Company")
            jurisdiction = params.get("jurisdiction", "Nigeria")
            
            return generate_legal_document(document_type, company_name, jurisdiction)
        
        elif action == "list":
            if not PROJECTS_DIR.exists():
                return "No ventures created yet."
            
            ventures = [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()]
            if not ventures:
                return "No ventures created yet."
            
            return "Ventures:\n" + "\n".join(f"  - {v}" for v in ventures)
        
        else:
            return f"Unknown action: {action}. Available: forge, generate, legal, list"
    
    except Exception as e:
        return f"VentureForge error: {str(e)}"


if __name__ == "__main__":
    # Test venture forge
    print("=== Venture Forge Test ===")
    
    # Test basic forge
    result = forge_project_structure("test_venture", {
        "README.md": "# Test Venture",
        "main.py": "print('Hello from Venture Forge!')"
    })
    print(result)
    
    print("\n✅ Venture Forge ready")
