# money_maker.py
"""
Money Maker - Income tracking and financial helper tools.
Part of enhanced JARVIS system to help user make money.
"""

import os
import json
import platform
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta

try:
    import requests
    _REQUESTS = True
except ImportError:
    _REQUESTS = False


_OS = platform.system()


def _base_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _base_dir()
MONEY_DATA_PATH = BASE_DIR / "memory" / "money.json"


def _load_money_data() -> dict:
    """Load financial data."""
    if MONEY_DATA_PATH.exists():
        try:
            return json.loads(MONEY_DATA_PATH.read_text())
        except:
            pass
    return {"income": [], "expenses": [], "invoices": []}


def _save_money_data(data: dict):
    """Save financial data."""
    MONEY_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    MONEY_DATA_PATH.write_text(json.dumps(data, indent=2))


def track_income(source: str, amount: float, desc: str = "") -> str:
    """Track income."""
    data = _load_money_data()
    entry = {
        "source": source,
        "amount": amount,
        "description": desc,
        "date": datetime.now().isoformat()
    }
    data["income"].append(entry)
    _save_money_data(data)
    return f" income tracked: {amount} from {source}"


def track_expense(description: str, category: str, amount: float) -> str:
    """Track expense."""
    data = _load_money_data()
    entry = {
        "description": description,
        "category": category,
        "amount": amount,
        "date": datetime.now().isoformat()
    }
    data["expenses"].append(entry)
    _save_money_data(data)
    return f"Expense tracked: {amount} for {description}"


def get_summary(days: int = 30) -> str:
    """Get financial summary."""
    data = _load_money_data()
    since = datetime.now() - timedelta(days=days)
    
    total_income = 0
    for entry in data.get("income", []):
        entry_date = datetime.fromisoformat(entry["date"])
        if entry_date >= since:
            total_income += entry["amount"]
    
    total_expenses = 0
    for entry in data.get("expenses", []):
        entry_date = datetime.fromisoformat(entry["date"])
        if entry_date >= since:
            total_expenses += entry["amount"]
    
    profit = total_income - total_expenses
    
    return (
        f"Financial Summary ({days} days):\n"
        f"  Income: {total_income:,.2f}\n"
        f"  Expenses: {total_expenses:,.2f}\n"
        f"  Profit: {profit:,.2f}"
    )


def search_jobs(keywords: str, platform: str = "all") -> str:
    """Search for freelance jobs."""
    if not _REQUESTS:
        return "requests library not available"
    
    # Common freelance platforms
    sites = []
    
    if platform in ("all", "upwork"):
        sites.append("https://www.upwork.com/ab/jobs/search/?q=")
    if platform in ("all", "fiverr"):
        sites.append("https://www.fiverr.com/search_gigs?query=")
    if platform in ("all", "freelancer"):
        sites.append("https://www.freelancer.com/jobs/")
    
    if not sites:
        return f"Unknown platform: {platform}"
    
    return "Job search URLs:\n" + "\n".join(sites + keywords.replace(" ", "%20"))


def money_maker(
    parameters: dict = None,
    response=None,
    player=None,
) -> str:
    """Main dispatcher for money maker."""
    params = parameters or {}
    action = params.get("action", "summary").lower().strip()
    
    try:
        if action == "track_income":
            return track_income(
                params.get("source", ""),
                float(params.get("amount", 0)),
                params.get("description", "")
            )
        
        elif action == "track_expense":
            return track_expense(
                params.get("description", ""),
                params.get("category", ""),
                float(params.get("amount", 0)))
            )
        
        elif action == "summary":
            return get_summary(int(params.get("days", 30)))
        
        elif action == "jobs":
            return search_jobs(
                params.get("keywords", ""),
                params.get("platform", "all"))
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Money maker error: {e}"
