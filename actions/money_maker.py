# money_maker.py - Tools to help make money through automation and intelligence
import json
import os
import sys
import subprocess
import platform
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
_OS = platform.system().lower()

# Money-making tool configurations
CONFIG_PATH = BASE_DIR / "config" / "money_config.json"

def _load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"skills": [], "income_streams": [], "opportunities": []}

def _save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")

def analyze_market_trends(topics: list) -> str:
    """Analyze market trends for given topics."""
    try:
        import requests
        # Simulated market analysis - in production would use real APIs
        trends = []
        for topic in topics[:5]:
            trends.append(f"  - {topic}: High demand in freelance market")
        return "Market Analysis:\n" + "\n".join(trends)
    except Exception as e:
        return f"Analysis error: {e}"

def find_freelance_opportunities(skills: list) -> str:
    """Find freelance opportunities based on skills."""
    platforms = [
        "Upwork", "Fiverr", "Toptal", "Freelancer.com", "PeoplePerHour"
    ]
    results = ["Freelance Platforms:"]
    for p in platforms:
        results.append(f"  - {p}: Active for {len(skills)} skill areas")
    return "\n".join(results)

def create_upwork_proposal(project_type: str, rate: str = "$50/hr") -> str:
    """Create Upwork proposal template."""
    templates = {
        "web_dev": f"""Hi,

I'm a full-stack web developer with 5+ years of experience. I specialize in {project_type}.

My rate: {rate}

Why choose me:
- 100% client satisfaction
- Fast turnaround
- Clean, maintainable code

Let's discuss your project!""",
        "data": f"""Data analysis expert here. I can help you extract insights from {project_type}.

Rate: {rate}

Ready to start!"""
    }
    template = templates.get(project_type.lower().replace(" ", "_"), templates["web_dev"])
    return template

def find_startup_ideas(user_skills: list) -> str:
    """Suggest startup ideas based on skills."""
    ideas = []
    skills_str = ", ".join(user_skills[:3])
    
    ideas.append(f"=== STARTUP IDEAS based on: {skills_str} ===\n")
    ideas.append("1. SaaS Tool")
    ideas.append("   - Build automation tool for repetitive tasks")
    ideas.append("   - Target: Small businesses")
    ideas.append("\n2. Consulting Service")  
    ideas.append("   - Specialized knowledge service")
    ideas.append("   - High hourly rate potential")
    ideas.append("\n3. Digital Product")
    ideas.append("   - Online course or template bundle")
    ideas.append("   - Passive income potential")
    
    return "\n".join(ideas)

def track_income(amount: float, source: str, note: str = "") -> str:
    """Track income entry."""
    config = _load_config()
    entry = {
        "date": datetime.now().isoformat(),
        "amount": amount,
        "source": source,
        "note": note
    }
    
    if "income_streams" not in config:
        config["income_streams"] = []
    config["income_streams"].append(entry)
    _save_config(config)
    
    return f"Income tracked: ${amount} from {source}"

def get_income_summary() -> str:
    """Get income summary."""
    config = _load_config()
    streams = config.get("income_streams", [])
    
    if not streams:
        return "No income tracked yet. Start earning, sir!"
    
    total = sum(s.get("amount", 0) for s in streams)
    return f"Income Summary:\n  Total: ${total:.2f}\n  Entries: {len(streams)}"

def automate_cold_outreach(client_names: list, service: str) -> str:
    """Generate cold outreach messages."""
    messages = []
    for client in client_names:
        msg = f"""Hi {client},

I noticed you're looking for {service} expertise. I specialize in helping businesses like yours.

Quick question: What's your biggest challenge with {service} right now?

Best,"""
        messages.append(f"\n=== {client} ===\n{msg}")
    
    return "\n".join(messages)

def money_maker(parameters: dict = None, response=None, player=None) -> str:
    """Main dispatcher for money-making tools."""
    params = parameters or {}
    action = params.get("action", "ideas").lower().strip()
    
    if action == "market":
        return analyze_market_trends(params.get("topics", ["web development", "data entry"]))
    elif action == "freelance":
        return find_freelance_opportunities(params.get("skills", []))
    elif action == "proposal":
        return create_upwork_proposal(
            params.get("project_type", "web development"),
            params.get("rate", "$50/hr")
        )
    elif action == "ideas":
        return find_startup_ideas(params.get("skills", []))
    elif action == "track":
        return track_income(
            float(params.get("amount", 0)),
            params.get("source", "freelance"),
            params.get("note", "")
        )
    elif action == "income":
        return get_income_summary()
    elif action == "outreach":
        return automate_cold_outreach(
            params.get("clients", []),
            params.get("service", "web development")
        )
    else:
        return find_startup_ideas(params.get("skills", []))
