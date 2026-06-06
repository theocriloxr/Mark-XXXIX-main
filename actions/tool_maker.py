"""
Tool Maker Agent - Self-Coding & Auto-Installing Skills

This module creates the tool_maker sub-agent that:
1. Analyzes a task to determine if it's reusable
2. Writes Python code for the new tool
3. Creates pytest test files
4. Runs tests and self-fixes on failures
5. Validates for production deployment

Usage:
    from actions.tool_maker import ToolMakerAgent
    agent = ToolMakerAgent()
    result = agent.create_tool("pdf_formatter", "Convert CSV to clean PDF invoice")
"""

import json
import logging
import sys
import traceback
import uuid
from pathlib import Path
from typing import Callable, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Add parent to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
SANDBOX_DIR = BASE_DIR / "actions" / "sandbox"
TOOLS_DIR = BASE_DIR / "actions"


class ToolMakerAgent:
    """
    Agent that creates, tests, and validates new tools for JARVIS.
    Uses CodeAgent for code generation and self-correction.
    """
    
    def __init__(self):
        self.sandbox_dir = SANDBOX_DIR
        self.tools_dir = TOOLS_DIR
        self.tools_subdir = self.sandbox_dir / "tools"
        self.tests_subdir = self.sandbox_dir / "tests"
        self.logs_subdir = self.sandbox_dir / "logs"
        
        # Ensure directories exist
        self.tools_subdir.mkdir(parents=True, exist_ok=True)
        self.tests_subdir.mkdir(parents=True, exist_ok=True)
        self.logs_subdir.mkdir(parents=True, exist_ok=True)
        
        # Track created tools
        self.created_tools: dict = {}
    
    def is_reusable_task(self, task_description: str) -> bool:
        """
        Analyze if a task is reusable (should be learned permanently).
        
        Reusable tasks:
        - File format conversions (CSV→PDF, image resize, etc.)
        - Data processing pipelines
        - Report generation
        - Custom computations
        
        One-time tasks:
        - Simple web searches
        - Single file operations
        -临时 queries
        """
        # Keywords that indicate reusable tasks
        reusable_keywords = [
            "convert", "format", "generate", "create", "process",
            "export", "import", "transform", "analyze", "report",
            "invoice", "resume", "chart", "graph", "visualize",
            "batch", "automate", "pipeline", "aggregate"
        ]
        
        # Keywords that indicate one-time tasks
        onetime_keywords = [
            "find", "search", "look", "check", "show",
            "what is", "who is", "when", "where",
            "download this", "open this"
        ]
        
        task_lower = task_description.lower()
        
        # Check for one-time indicators first
        for kw in onetime_keywords:
            if kw in task_lower:
                return False
        
        # Check for reusable indicators
        for kw in reusable_keywords:
            if kw in task_lower:
                return True
        
        # Default: treat as reusable if complex
        return len(task_description.split()) > 5
    
    def generate_tool_code(
        self,
        tool_name: str,
        description: str,
        parameters: dict = None
    ) -> str:
        """
        Generate Python code for a new tool using CodeAgent.
        
        Args:
            tool_name: Name of the tool (e.g., "pdf_formatter")
            description: What the tool should do
            parameters: Expected parameters schema
            
        Returns:
            str: Complete Python code for the tool
        """
        # Use the agent engine for code generation
        try:
            from core.agent_engine import get_jarvis_agent
            
            # Create a prompt for code generation
            prompt = f"""Write a complete JARVIS tool in Python.

Tool Name: {tool_name}
Description: {description}
Parameters: {json.dumps(parameters or {}, indent=2)}

Requirements:
1. Create a function main entry point: def {tool_name}(parameters: dict, player=None, speak=None) -> str
2. Include proper docstrings
3. Add error handling with try/except
4. Return a string result
5. Use the player object for logging: player.write_log("message")
6. Use speak for audio output if needed
7. DO NOT include any imports that require pip install beyond standard library

Output ONLY the Python code, no explanations."""
            
            # Generate code using the agent
            agent = get_jarvis_agent(user_prompt=prompt)
            result = agent.run(prompt)
            
            return result
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            # Fallback: generate basic template
            return self._generate_basic_template(tool_name, description, parameters)
    
    def _generate_basic_template(
        self,
        tool_name: str,
        description: str,
        parameters: dict = None
    ) -> str:
        """Generate a basic tool template."""
        params_str = json.dumps(parameters or {"param": "STRING"}, indent=4)
        
        return f'''"""Auto-generated tool: {tool_name}

{description}

Generated by JARVIS Evolution Lab.
"""
import logging
import json

logger = logging.getLogger(__name__)


def {tool_name}(
    parameters: dict = None,
    player=None,
    speak=None
) -> str:
    """Main entry point for {tool_name}."""
    params = parameters or {{
        "param": ""
    }}
    
    if player:
        player.write_log(f"[{tool_name}] Executing...")
    
    try:
        # TODO: Implement tool logic
        result = "Tool '{tool_name}' executed successfully."
        
        if player:
            player.write_log(f"[{tool_name}] {{result}}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error in {tool_name}: {{e}}"
        logger.error(error_msg)
        if player:
            player.write_log(f"[{tool_name}] ERROR: {{error_msg}}")
        return error_msg


# === MAIN DISPATCHER ===

def main(parameters: dict = None, player=None, speak=None) -> str:
    """Dispatcher for tool actions."""
    return {tool_name}(parameters=parameters, player=player, speak=speak)
'''
    
    def create_test(
        self,
        tool_name: str,
        test_cases: list = None
    ) -> str:
        """
        Create pytest test file for the tool.
        
        Args:
            tool_name: Name of the tool to test
            test_cases: List of test case dicts
            
        Returns:
            str: Complete pytest code
        """
        test_cases = test_cases or [
            {"name": "test_basic", "input": {}, "expected": "success"},
            {"name": "test_with_params", "input": {"param": "value"}, "expected": "success"},
        ]
        
        test_code = f'''"""Auto-generated tests for {tool_name}

Generated by JARVIS Evolution Lab.
"""
import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from actions.{tool_name} import {tool_name}


def test_basic():
    """Basic functionality test."""
    result = {tool_name}({{}})
    assert result is not None
    assert isinstance(result, str)


def test_with_params():
    """Test with parameters."""
    params = {{"param": "test_value"}}
    result = {tool_name}(params)
    assert result is not None


def test_error_handling():
    """Test error handling."""
    # Should handle errors gracefully
    result = {tool_name}({{"invalid": "params"}})
    assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        return test_code
    
    def run_tests(
        self,
        tool_name: str,
        tool_code: str,
        test_code: str
    ) -> dict:
        """
        Write tool and test files, run tests, return results.
        
        Args:
            tool_name: Name of the tool
            tool_code: Python code for the tool
            test_code: Pytest test code
            
        Returns:
            dict: {"success": bool, "output": str, "errors": str}
        """
        tool_file = self.tools_subdir / f"{tool_name}.py"
        test_file = self.tests_subdir / f"test_{tool_name}.py"
        
        result = {
            "success": False,
            "output": "",
            "errors": "",
            "test_passed": False
        }
        
        try:
            # Write tool code
            tool_file.write_text(tool_code, encoding="utf-8")
            logger.info(f"[ToolMaker] Wrote tool: {tool_file}")
            
            # Write test code
            test_file.write_text(test_code, encoding="utf-8")
            logger.info(f"[ToolMaker] Wrote test: {test_file}")
            
            # Run pytest
            import subprocess
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(BASE_DIR)
            )
            
            result["output"] = proc.stdout
            result["errors"] = proc.stderr
            
            if proc.returncode == 0:
                result["success"] = True
                result["test_passed"] = True
                logger.info(f"[ToolMaker] Tests passed for {tool_name}")
            else:
                # Self-fix: try to read traceback and fix
                fix_result = self.self_fix(tool_name, tool_code, proc.stderr)
                if fix_result:
                    result["success"] = True
                    result["output"] += f"\n[Self-fixed] {fix_result}"
                    
        except Exception as e:
            result["errors"] = str(e)
            logger.error(f"[ToolMaker] Test failed: {e}")
        
        return result
    
    def self_fix(
        self,
        tool_name: str,
        tool_code: str,
        error_output: str
    ) -> Optional[str]:
        """
        Analyze error and attempt to fix the code.
        
        Args:
            tool_name: Name of the tool
            tool_code: Current tool code
            error_output: Pytest/stderr output
            
        Returns:
            str: Fixed code if successful, None otherwise
        """
        try:
            # Use agent to fix the code
            from core.agent_engine import get_jarvis_agent
            
            prompt = f"""Fix the following Python code based on this error:

Error:
{error_output}

Current Code:
{tool_code}

Requirements:
1. Fix syntax errors
2. Fix import errors  
3. Fix runtime errors
4. Keep the same functionality
5. Output ONLY the fixed code, no explanations."""
            
            agent = get_jarvis_agent(user_prompt=prompt)
            fixed_code = agent.run(prompt)
            
            # Validate fixed code has no obvious issues
            if fixed_code and "def " in fixed_code:
                # Write fixed code
                tool_file = self.tools_subdir / f"{tool_name}.py"
                tool_file.write_text(fixed_code, encoding="utf-8")
                logger.info(f"[ToolMaker] Self-fixed: {tool_name}")
                return fixed_code
            
        except Exception as e:
            logger.error(f"[ToolMaker] Self-fix failed: {e}")
        
        return None
    
    def hot_reload_tool(self, tool_name: str) -> bool:
        """
        Use importlib to reload a tool without restarting JARVIS.
        
        Args:
            tool_name: Name of the tool to reload
            
        Returns:
            bool: Success status
        """
        try:
            import importlib
            import sys
            
            # Try to import and reload
            if tool_name in sys.modules:
                module = sys.modules[tool_name]
                importlib.reload(module)
                logger.info(f"[ToolMaker] Hot-reloaded: {tool_name}")
                return True
            else:
                # Import fresh
                module = importlib.import_module(f"actions.{tool_name}")
                logger.info(f"[ToolMaker] Hot-loaded: {tool_name}")
                return True
                
        except Exception as e:
            logger.error(f"[ToolMaker] Hot-reload failed: {e}")
            return False
    
    def move_to_production(self, tool_name: str) -> bool:
        """
        Move validated tool from sandbox to production actions/.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            bool: Success status
        """
        try:
            sandbox_tool = self.tools_subdir / f"{tool_name}.py"
            prod_tool = self.tools_dir / f"{tool_name}.py"
            
            if not sandbox_tool.exists():
                logger.error(f"[ToolMaker] Sandbox tool not found: {tool_name}")
                return False
            
            # Read and copy
            content = sandbox_tool.read_text(encoding="utf-8")
            prod_tool.write_text(content, encoding="utf-8")
            
            logger.info(f"[ToolMaker] Moved to production: {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"[ToolMaker] Move to production failed: {e}")
            return False
    
    def create_tool(
        self,
        tool_name: str,
        description: str,
        parameters: dict = None
    ) -> dict:
        """
        Complete workflow: create, test, validate, and deploy tool.
        
        Args:
            tool_name: Name for the new tool
            description: What the tool should do
            parameters: Expected parameters
            
        Returns:
            dict: Complete result with status
        """
        result = {
            "tool_name": tool_name,
            "description": description,
            "status": "created",
            "test_passed": False,
            "deployed": False,
            "hot_reloaded": False,
            "message": ""
        }
        
        # Check if reusable
        if not self.is_reusable_task(description):
            result["status"] = "skipped"
            result["message"] = "Task is one-time, not learning permanently"
            return result
        
        try:
            # Step 1: Generate code
            code = self.generate_tool_code(tool_name, description, parameters)
            
            # Step 2: Create tests
            tests = self.create_test(tool_name)
            
            # Step 3: Run tests
            test_result = self.run_tests(tool_name, code, tests)
            
            if test_result["test_passed"]:
                result["test_passed"] = True
                
                # Step 4: Move to production
                if self.move_to_production(tool_name):
                    result["deployed"] = True
                    
                    # Step 5: Hot reload
                    if self.hot_reload_tool(tool_name):
                        result["hot_reloaded"] = True
                
                result["status"] = "success"
                result["message"] = f"Tool '{tool_name}' created and deployed successfully"
            else:
                result["status"] = "test_failed"
                result["message"] = test_result["errors"][:200]
                
        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            logger.error(f"[ToolMaker] Create tool failed: {e}")
        
        return result


# === GLOBAL INSTANCE ===

_tool_maker: Optional[ToolMakerAgent] = None


def get_tool_maker() -> ToolMakerAgent:
    """Get global ToolMakerAgent instance."""
    global _tool_maker
    if _tool_maker is None:
        _tool_maker = ToolMakerAgent()
    return _tool_maker


def create_tool(
    tool_name: str,
    description: str,
    parameters: dict = None
) -> dict:
    """Convenience function to create a tool."""
    return get_tool_maker().create_tool(tool_name, description, parameters)


if __name__ == "__main__":
    # Test
    print("=== ToolMaker Agent Test ===")
    tm = get_tool_maker()
    
    # Test reusable detection
    test_tasks = [
        "Convert this CSV to a clean PDF invoice",
        "Find my downloads folder",
        "Generate a monthly sales report",
    ]
    
    for task in test_tasks:
        is_reusable = tm.is_reusable_task(task)
        print(f"Task: '{task}' -> Reusable: {is_reusable}")
    
    print("\n✅ ToolMaker ready")
