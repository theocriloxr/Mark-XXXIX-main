"""
Venture Orchestrator - Multi-Business Revenue Management

This module allows JARVIS to manage multiple revenue streams simultaneously,
scouting opportunities, and pivoting based on market data.

Features:
- Multi-sector venture management
- Trend scouting and analysis
- Automated venture scaling
- Revenue tracking
- Market pivot decision making

Usage:
    from actions.venture_orchestrator import VentureOrchestrator
    
    orchestrator = VentureOrchestrator()
    orchestrator.daily_pivot()
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Base directories
BASE_DIR = Path(r"C:\Users\sammm\Downloads\Mark-XXXIX-main")
PROJECTS_DIR = Path(r"C:\Users\sammm\Downloads\JARVIS_PROJECTS")

# Ensure directories exist
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


# === VENTURE CONFIGURATION ===

VENTURE_SECTORS = {
    "fintech": {
        "name": "Fintech Arbitrage",
        "description": "Cross-border stablecoin arbitrage (USDT/NGN)",
        "weekly_potential": "1.2M - 2M ₦",
        "tools": ["browser_control", "web_search"],
    },
    "b2b_ai": {
        "name": "B2B AI Orchestration",
        "description": "Rental specialized sub-agents to businesses",
        "weekly_potential": "800k - 1.5M ₦",
        "tools": ["dev_agent", "code_helper"],
    },
    "defi": {
        "name": "DeFi Yield",
        "description": "Automated farming on DeFi protocols",
        "weekly_potential": "500k - 1M ₦",
        "tools": ["browser_control", "money_assistant"],
    },
    "saas": {
        "name": "SaaS Micro-Agency",
        "description": "Rapid SaaS deployment for pain points",
        "weekly_potential": "400k - 1.2M ₦",
        "tools": ["dev_agent", "venture_forge"],
    },
}


def _get_api_key() -> str:
    """Get API key from config."""
    config_path = BASE_DIR / "config" / "api_keys.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _get_model():
    """Get Gemini model."""
    import google.generativeai as genai
    genai.configure(api_key=_get_api_key())
    return genai.GenerativeModel("gemini-2.5-flash")


def scout_global_market() -> List[Dict]:
    """
    Scout global markets for opportunities.
    
    Returns:
        List of market opportunities
    """
    model = _get_model()
    
    prompt = """Scout current market opportunities (June 2026).

Identify:
1. Trending tech niches
2. High-demand freelance skills  
3. crypto/fintech opportunities
4. Business pain points with money potential

Return JSON array:
[{
  "niche": "niche name",
  "demand": "high|medium|low",
  "revenue_potential": "amount",
  "competition": "low|medium|high",
  "action": "build|research|skip"
}]

JSON:"""

    try:
        response = model.generate_content(prompt)
        import re
        text = response.text.strip()
        
        # Extract JSON
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            opportunities = json.loads(json_match.group())
            return opportunities
        
        return []
    except Exception as e:
        print(f"[VentureOrch] Scout error: {e}")
        return []


def match_user_files_to_trends(trends: List[Dict], user_context: str = "") -> Dict:
    """
    Match user skills/files to market trends.
    
    Args:
        trends: Market trends
        user_context: User's skill background
    
    Returns:
        Best niche match
    """
    model = _get_model()
    
    prompt = f"""Match user capabilities to market trends.

User context: {user_context}

Trends:
{json.dumps(trends[:5], indent=2)}

Return JSON:
{{
  "best_niche": "niche name",
  "reason": "why this matches",
  "action_plan": "what to build first",
  "estimated_revenue": "amount"
}}

JSON:"""

    try:
        response = model.generate_content(prompt)
        import re
        text = response.text.strip()
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"best_niche": "saas", "reason": "Default", "action_plan": "Build generic SaaS"}
    except:
        return {"best_niche": "saas", "reason": "Fallback", "action_plan": "Build generic SaaS"}


class VentureOrchestrator:
    """
    Venture Orchestrator - manages multiple revenue streams.
    """
    
    def __init__(self):
        self.active_sectors = list(VENTURE_SECTORS.keys())
        self.learning_queue = []
        self.ventures = {}
        self.load_state()
    
    def load_state(self):
        """Load venture state from file."""
        state_file = BASE_DIR / "ventures_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                    self.ventures = data.get("ventures", {})
            except:
                pass
    
    def save_state(self):
        """Save venture state to file."""
        state_file = BASE_DIR / "ventures_state.json"
        with open(state_file, "w") as f:
            json.dump({"ventures": self.ventures}, f)
    
    def start_new_venture(self, niche: str) -> str:
        """
        Start a new venture in a niche.
        
        Args:
            niche: The venture niche
    
        Returns:
            Result message
        """
        if niche not in VENTURE_SECTORS:
            return f"Unknown niche: {niche}"
        
        config = VENTURE_SECTORS[niche]
        
        # Create venture record
        venture_id = f"{niche}_{int(time.time())}"
        self.ventures[venture_id] = {
            "niche": niche,
            "name": config["name"],
            "description": config["description"],
            "potential": config["weekly_potential"],
            "status": "active",
            "started": str(datetime.now()),
            "revenue": 0,
        }
        self.save_state()
        
        return f"🚀 Venture started: {config['name']}\nPotential: {config['weekly_potential']}"
    
    def daily_pivot(self) -> str:
        """
        Scan markets and decide on pivots.
        
        Returns:
            Report on opportunities
        """
        print("[VentureOrch] 🚀 Daily market scan...")
        
        # 1. Scout the world
        trends = scout_global_market()
        
        # 2. Match with user capability
        match = match_user_files_to_trends(trends)
        
        # 3. Build or Scale report
        lines = ["📊 MARKET ANALYSIS"]
        lines.append(f"\nTop Opportunities:")
        for t in trends[:3]:
            lines.append(f"  • {t.get('niche')}: {t.get('revenue_potential')} ({t.get('competition')} competition)")
        
        lines.append(f"\n🎯 Best Match: {match.get('best_niche')}")
        lines.append(f"   Reason: {match.get('reason')}")
        lines.append(f"   Plan: {match.get('action_plan')}")
        
        if match.get("action_plan", "").lower() != "skip":
            # Auto-start venture
            result = self.start_new_venture(match.get("best_niche"))
            lines.append(f"\n{result}")
        
        return "\n".join(lines)
    
    def get_status(self) -> str:
        """Get overall venture status."""
        lines = ["🚀 VENTURE ORCHESTRATOR STATUS"]
        lines.append(f"\nActive Sectors:")
        for sector, config in VENTURE_SECTORS.items():
            lines.append(f"  • {config['name']}: {config['weekly_potential']}")
        
        lines.append(f"\nRunning Ventures:")
        if self.ventures:
            for vid, venture in self.ventures.items():
                status = venture.get("status", "unknown")
                lines.append(f"  • {venture.get('name')} ({status})")
        else:
            lines.append("  No active ventures")
        
        return "\n".join(lines)
    
    def record_revenue(self, venture_id: str, amount: int) -> str:
        """Record revenue for a venture."""
        if venture_id in self.ventures:
            self.ventures[venture_id]["revenue"] = amount
            self.save_state()
            return f"Recorded ₦{amount} for {venture_id}"
        return f"Venture {venture_id} not found"


# === DISPATCHER ===

def venture_orchestrator(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for Venture Orchestrator.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[VentureOrch] {action}")
    
    try:
        orchestrator = VentureOrchestrator()
        
        if action == "start":
            niche = params.get("niche", "saas")
            return orchestrator.start_new_venture(niche)
        
        elif action == "pivot":
            return orchestrator.daily_pivot()
        
        elif action == "status":
            return orchestrator.get_status()
        
        elif action == "revenue":
            venture_id = params.get("venture_id", "")
            amount = params.get("amount", 0)
            return orchestrator.record_revenue(venture_id, amount)
        
        elif action == "sectors":
            lines = ["Available Sectors:"]
            for sector, config in VENTURE_SECTORS.items():
                lines.append(f"  {sector}: {config['name']} ({config['weekly_potential']})")
            return "\n".join(lines)
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"VentureOrch error: {str(e)}"


if __name__ == "__main__":
    # Test Venture Orchestrator
    print("=== Venture Orchestrator Test ===")
    
    orchestrator = VentureOrchestrator()
    
    # Get status
    print(orchestrator.get_status())
    
    print("\n✅ Venture Orchestrator ready")
