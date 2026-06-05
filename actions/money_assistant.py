# money_assistant.py
"""
Money Making Assistant - Helps with income generation, freelancing, investments
"""

import json
import random
import sys
from pathlib import Path
import re
from datetime import datetime
import subprocess

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
MONEY_DATA = BASE_DIR / "memory" / "money.json"

def _load_money_data() -> dict:
    if MONEY_DATA.exists():
        try:
            return json.loads(MONEY_DATA.read_text(encoding="utf-8"))
        except:
            pass
    return {"incomes": [], "expenses": [], "goals": [], "skills": []}

def _save_money_data(data: dict) -> None:
    MONEY_DATA.parent.mkdir(parents=True, exist_ok=True)
    MONEY_DATA.write_text(json.dumps(data, indent=2), encoding="utf-8")

def add_income(amount: float, source: str, note: str = "") -> str:
    data = _load_money_data()
    data["incomes"].append({
        "amount": amount,
        "source": source,
        "note": note,
        "date": datetime.now().isoformat()
    })
    _save_money_data(data)
    return f" income recorded: ${amount} from {source}"

def add_expense(amount: float, category: str, note: str = "") -> str:
    data = _load_money_data()
    data["expenses"].append({
        "amount": amount,
        "category": category,
        "note": note,
        "date": datetime.now().isoformat()
    })
    _save_money_data(data)
    return f" expense recorded: ${amount} for {category}"

def add_skill(skill: str, hourly_rate: float = 0) -> str:
    data = _load_money_data()
    data["skills"].append({
        "skill": skill,
        "hourly_rate": hourly_rate,
        "date_added": datetime.now().isoformat()
    })
    _save_money_data(data)
    return f" skill added: {skill}"

def get_financial_summary() -> str:
    data = _load_money_data()
    
    total_income = sum(i.get("amount", 0) for i in data.get("incomes", []))
    total_expense = sum(e.get("amount", 0) for e in data.get("expenses", []))
    net = total_income - total_expense
    
    skills = data.get("skills", [])
    potential = sum(s.get("hourly_rate", 0) * 40 * 52 for s in skills)
    
    return (
        f"Financial Summary:\n"
        f"  Total Income: ${total_income:.2f}\n"
        f"  Total Expenses: ${total_expense:.2f}\n"
        f"  Net: ${net:.2f}\n"
        f"  Skills: {len(skills)}\n"
        f"  Annual Potential: ${potential:.2f}"
    )

def suggest_freelance_gigs() -> str:
    gigs = [
        {"title": "Python Developer", "rate": "$50-150/hr", "platforms": "Upwork, Toptal, Fiverr"},
        {"title": "Web Scraper", "rate": "$30-100/hr", "platforms": "Fiverr, Upwork"},
        {"title": "AI Prompt Engineer", "rate": "$60-200/hr", "platforms": "PromptBase, Upwork"},
        {"title": "Video Editor", "rate": "$25-75/hr", "platforms": "Fiverr, PremierePro"},
        {"title": "Voice Over", "rate": "$25-100/hr", "platforms": "Voices.com, Fiverr"},
        {"title": "Content Writer", "rate": "$30-80/hr", "platforms": "Contently, Upwork"},
        {"title": "Virtual Assistant", "rate": "$20-50/hr", "platforms": "Belay, Fancy"},
        {"title": "Data Analyst", "rate": "$50-120/hr", "platforms": "Upwork, Toptal"},
    ]
    return "Freelance Opportunities:\n" + "\n".join([
        f"  - {g['title']}: {g['rate']} ({g['platforms']})"
        for g in gigs[:5]
    ])

def calculate_passive_income(principal: float, rate: float, years: int) -> str:
    monthly_rate = rate / 100 / 12
    months = years * 12
    
    future_value = principal * ((1 + monthly_rate) ** months)
    monthly_income = (future_value * monthly_rate) / 1.05
    
    return (
        f"Passive Income Calculator:\n"
        f"  Principal: ${principal:,.2f}\n"
        f"  Rate: {rate}%\n"
        f"  Years: {years}\n"
        f"  Future Value: ${future_value:,.2f}\n"
        f"  Monthly Income: ${monthly_income:,.2f}"
    )

def calculate_tax(income: float) -> str:
    brackets = [(0, 11000, 0.10), (11000, 44725, 0.12), (44725, 95375, 0.22),
             (95375, 170050, 0.24), (170050, 215950, 0.32), (215950, 539900, 0.35)]
    
    tax = 0
    remaining = income
    
    for i, (min_income, max_income, rate) in enumerate(brackets):
        if remaining <= 0:
            break
        taxable = min(remaining, max_income - min_income)
        tax += taxable * rate
        remaining -= taxable
    
    effective_rate = (tax / income * 100) if income > 0 else 0
    
    return (
        f"Tax Calculation:\n"
        f"  Income: ${income:,.2f}\n"
        f"  Estimated Tax: ${tax:,.2f}\n"
        f"  Effective Rate: {effective_rate:.1f}%"
    )

def money_assistant(parameters: dict = None, player=None) -> str:
    params = parameters or {}
    action = params.get("action", "summary").lower().strip()
    
    try:
        if action == "add_income":
            return add_income(
                float(params.get("amount", 0)),
                params.get("source", ""),
                params.get("note", "")
            )
        
        elif action == "add_expense":
            return add_expense(
                float(params.get("amount", 0)),
                params.get("category", ""),
                params.get("note", "")
            )
        
        elif action == "add_skill":
            return add_skill(
                params.get("skill", ""),
                float(params.get("hourly_rate", 0))
            )
        
        elif action == "summary":
            return get_financial_summary()
        
        elif action == "gigs":
            return suggest_freelance_gigs()
        
        elif action == "passive":
            return calculate_passive_income(
                float(params.get("principal", 10000)),
                float(params.get("rate", 7)),
                int(params.get("years", 10))
            )
        
        elif action == "tax":
            return calculate_tax(float(params.get("income", 50000)))
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Error: {e}"
