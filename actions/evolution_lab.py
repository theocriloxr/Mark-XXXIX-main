"""
Evolution Lab - Self-Coding & Auto-Installing Skills

Main controller for JARVIS's ability to learn new skills permanently.
When JARVIS encounters a task it doesn't know how to do, it can:
1. Analyze if the task is reusable
2. Delegate to the tool_maker agent
3. Create, test, and validate the new tool
4. Hot-reload into its own brain without restart

Usage:
    from actions.evolution_lab import EvolutionLab
    lab = EvolutionLab()
    result = lab.learn_skill("pdf_formatter", "Convert CSV to clean PDF invoice")
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SANDBOX_DIR = BASE_DIR / "actions" / "sandbox"


class EvolutionLab:
    """
    Orchestrator for JARVIS's self-learning capability.
    
    Workflow:
    1. User requests task
    2. analyze() - Determine if reusable
    3. delegate() - Send to tool_maker
    4. validate() - Run tests
    5. deploy() - Hot-reload into production
    """
    
    def __init__(self):
        self.sandbox_dir = SANDBOX_DIR
        self.tool_maker = None
        self.learned_skills: dict = {}
        self.learning_enabled = True
        
        # Initialize tool maker
        self._init_tool_maker()
    
    def _init_tool_maker(self):
        """Lazy import and initialize tool maker."""
        try:
            from actions.tool_maker import get_tool_maker
            self.tool_maker = get_tool_maker()
            logger.info("[EvolutionLab] ToolMaker initialized")
        except Exception as e:
            logger.error(f"[EvolutionLab] ToolMaker init failed: {e}")
            self.tool_maker = None
    
    def is_reusable_task(self, task_description: str) -> bool:
        """
        Analyze if a task should be learned permanently.
        
        Uses the tool_maker's analysis.
        """
        if not self.tool_maker:
            return False
        return self.tool_maker.is_reusable_task(task_description)
    
    def analyze_task(self, task_description: str) -> dict:
        """
        Deep analysis of a task to determine learning requirements.
        
        Returns:
            dict: Analysis with recommendation
        """
        analysis = {
            "task": task_description,
            "is_reusable": False,
            "complexity": "simple",
            "estimated_effort": "low",
            "reason": ""
        }
        
        if not self.tool_maker:
            analysis["reason"] = "ToolMaker not available"
            return analysis
        
        # Use tool maker analysis
        analysis["is_reusable"] = self.tool_maker.is_reusable_task(task_description)
        
        # Complexity analysis
        words = len(task_description.split())
        
        if words > 20:
            analysis["complexity"] = "complex"
            analysis["estimated_effort"] = "high"
        elif words > 10:
            analysis["complexity"] = "medium"
            analysis["estimated_effort"] = "medium"
        else:
            analysis["complexity"] = "simple"
            analysis["estimated_effort"] = "low"
        
        # Recommendation
        if analysis["is_reusable"]:
            analysis["reason"] = "Task involves reusable transformation"
        else:
            analysis["reason"] = "Task is one-time query"
        
        return analysis
    
    def learn_skill(
        self,
        skill_name: str,
        description: str,
        parameters: dict = None,
        force: bool = False
    ) -> dict:
        """
        Complete workflow to learn a new skill.
        
        Args:
            skill_name: Name for the new tool
            description: What the tool should do
            parameters: Expected parameters schema
            force: Force learning even for one-time tasks
            
        Returns:
            dict: Complete result
        """
        result = {
            "skill_name": skill_name,
            "description": description,
            "status": "pending",
            "phase": "analysis",
            "tool_created": False,
            "test_passed": False,
            "deployed": False,
            "hot_reloaded": False,
            "message": ""
        }
        
        if not self.learning_enabled:
            result["status"] = "disabled"
            result["message"] = "Evolution Lab is disabled"
            return result
        
        if not self.tool_maker:
            result["status"] = "error"
            result["message"] = "ToolMaker not available"
            return result
        
        start_time = time.time()
        
        try:
            # Phase 1: Analysis
            analysis = self.analyze_task(description)
            result["phase"] = "analysis"
            
            if not analysis["is_reusable"] and not force:
                result["status"] = "skipped"
                result["message"] = "Task not reusable, not learning"
                return result
            
            # Phase 2: Delegate to tool_maker
            result["phase"] = "creation"
            create_result = self.tool_maker.create_tool(
                skill_name,
                description,
                parameters
            )
            
            result["tool_created"] = create_result.get("test_passed", False)
            
            if create_result.get("test_passed"):
                # Phase 3: Validation passed
                result["test_passed"] = True
                result["phase"] = "validation"
                
                # Phase 4: Deploy to production
                if create_result.get("deployed"):
                    result["deployed"] = True
                    
                    if create_result.get("hot_reloaded"):
                        result["hot_reloaded"] = True
                
                result["status"] = "success"
                elapsed = time.time() - start_time
                result["message"] = f"Skill '{skill_name}' learned in {elapsed:.1f}s"
                
                # Track learned skill
                self.learned_skills[skill_name] = {
                    "description": description,
                    "learned_at": time.time(),
                    "parameters": parameters
                }
                
            else:
                result["status"] = "failed"
                result["message"] = create_result.get("message", "Tests failed")
        
        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            logger.error(f"[EvolutionLab] Learn skill failed: {e}")
        
        return result
    
    def list_learned_skills(self) -> str:
        """List all skills learned by JARVIS."""
        if not self.learned_skills:
            return "No skills learned yet."
        
        lines = ["Learned Skills:"]
        for name, info in self.learned_skills.items():
            timestamp = info.get("learned_at", 0)
            time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
            lines.append(f"  - {name}: {info.get('description', '')[:50]} ({time_str})")
        
        return "\n".join(lines)
    
    def forget_skill(self, skill_name: str) -> bool:
        """
        Remove a learned skill from production.
        
        Args:
            skill_name: Name of skill to forget
            
        Returns:
            bool: Success status
        """
        try:
            # Remove from production
            prod_file = BASE_DIR / "actions" / f"{skill_name}.py"
            if prod_file.exists():
                prod_file.unlink()
            
            # Remove from sandbox
            sandbox_file = self.sandbox_dir / "tools" / f"{skill_name}.py"
            if sandbox_file.exists():
                sandbox_file.unlink()
            
            # Remove from memory
            if skill_name in self.learned_skills:
                del self.learned_skills[skill_name]
            
            logger.info(f"[EvolutionLab] Forgot skill: {skill_name}")
            return True
            
        except Exception as e:
            logger.error(f"[EvolutionLab] Forget failed: {e}")
            return False
    
    def enable(self) -> str:
        """Enable evolution learning."""
        self.learning_enabled = True
        return "Evolution Lab enabled."
    
    def disable(self) -> str:
        """Disable evolution learning."""
        self.learning_enabled = False
        return "Evolution Lab disabled."
    
    def get_status(self) -> str:
        """Get evolution lab status."""
        status = [
            f"Evolution Lab: {'Enabled' if self.learning_enabled else 'Disabled'}",
            f"Skills Learned: {len(self.learned_skills)}",
        ]
        
        if self.learned_skills:
            status.append(f"Latest: {list(self.learned_skills.keys())[-1]}")
        
        return "\n".join(status)


# === DISPATCHER ===

def evolution_lab(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for Evolution Lab.
    
    Parameters:
    - action: learn | analyze | list | forget | enable | disable | status
    - skill_name: Name of skill to create/learn
    - description: What the skill should do
    - parameters: Expected parameters as JSON
    - force: Force learning (true/false)
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[EvolutionLab] {action}")
    
    try:
        lab = EvolutionLab()
        
        if action == "learn":
            skill_name = params.get("skill_name", "")
            description = params.get("description", "")
            
            if not skill_name or not description:
                return "Please provide skill_name and description."
            
            # Parse parameters if provided
            parameters = None
            if params.get("parameters"):
                try:
                    parameters = json.loads(params["parameters"])
                except:
                    pass
            
            force = params.get("force", "").lower() == "true"
            
            result = lab.learn_skill(
                skill_name,
                description,
                parameters,
                force
            )
            
            if result.get("status") == "success":
                msg = f"Skill '{skill_name}' learned successfully."
                if speak:
                    speak(msg)
                return msg
            else:
                return f"Failed: {result.get('message', 'Unknown error')}"
        
        elif action == "analyze":
            description = params.get("description", "")
            
            if not description:
                return "Please provide description to analyze."
            
            analysis = lab.analyze_task(description)
            
            lines = [
                f"Task: {analysis['task']}",
                f"Reusable: {analysis['is_reusable']}",
                f"Complexity: {analysis['complexity']}",
                f"Reason: {analysis['reason']}"
            ]
            return "\n".join(lines)
        
        elif action == "list":
            return lab.list_learned_skills()
        
        elif action == "forget":
            skill_name = params.get("skill_name", "")
            
            if not skill_name:
                return "Please provide skill_name to forget."
            
            if lab.forget_skill(skill_name):
                return f"Skill '{skill_name}' forgotten."
            else:
                return f"Failed to forget skill '{skill_name}'."
        
        elif action == "enable":
            return lab.enable()
        
        elif action == "disable":
            return lab.disable()
        
        elif action == "status":
            return lab.get_status()
        
        else:
            return lab.get_status()
            
    except Exception as e:
        error_msg = f"Evolution Lab error: {e}"
        logger.error(error_msg)
        return error_msg


# === GLOBAL INSTANCE ===

_lab_instance: Optional[EvolutionLab] = None


def get_evolution_lab() -> EvolutionLab:
    """Get global EvolutionLab instance."""
    global _lab_instance
    if _lab_instance is None:
        _lab_instance = EvolutionLab()
    return _lab_instance


if __name__ == "__main__":
    # Test
    print("=== Evolution Lab Test ===")
    lab = get_evolution_lab()
    
    print(lab.get_status())
    
    # Test analysis
    print("\n--- Analysis Test ---")
    analysis = lab.analyze_task("Convert this CSV to a clean PDF invoice")
    print(f"Analysis: {analysis}")
    
    print("\n✅ Evolution Lab ready")
