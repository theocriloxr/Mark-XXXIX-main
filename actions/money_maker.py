# money_maker.py
"""
Money Maker - Financial tracking and income generation assistant.
Helps track income, expenses, invoicing, and job searching.
"""

import json
import os
import sys
import platform
from pathlib import Path
from datetime import datetime
from threading import Lock


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
FINANCE_FILE = BASE_DIR / "memory" / "finance.json"
_lock = Lock()


def _load_finance() -> dict:
    """Load finance data."""
    if not FINANCE_FILE.exists():
        return {"income": [], "expenses": [], "invoices": []}
    try:
        return json.loads(FINANCE_FILE.read_text(encoding="utf-8"))
    except:
        return {"income": [], "expenses": [], "invoices": []}


def _save_finance(data: dict) -> None:
    """Save finance data."""
    FINANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        FINANCE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def track_income(source: str, amount: float, description: str = "") -> str:
    """Track income/earnings."""
    data = _load_finance()
    entry = {
        "source": source,
        "amount": amount,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat()
    }
    data["income"].append(entry)
    _save_finance(data)
    return f"Income tracked: {source} +${amount}"


def track_expense(amount: float, description: str, category: str = "other") -> str:
    """Track expenses."""
    data = _load_finance()
    entry = {
        "amount": amount,
        "description": description,
        "category": category,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat()
    }
    data["expenses"].append(entry)
    _save_finance(data)
    return f"Expense tracked: ${amount} - {description}"


def get_summary(period: str = "month") -> str:
    """Get financial summary."""
    data = _load_finance()
    
    now = datetime.now()
    if period == "month":
        month = now.month
        year = now.year
    else:
        month = None
        year = now.year
    
    total_income = 0
    for inc in data.get("income", []):
        if month and year:
            d = inc.get("date", "")
            if d:
                try:
                    y, m, _ = d.split("-")
                    if int(m) == month and int(y) == year:
                        total_income += inc.get("amount", 0)
                except:
                    pass
        else:
            total_income += inc.get("amount", 0)
    
    total_expenses = 0
    for exp in data.get("expenses", []):
        if month and year:
            d = exp.get("date", "")
            if d:
                try:
                    y, m, _ = d.split("-")
                    if int(m) == month and int(y) == year:
                        total_expenses += exp.get("amount", 0)
                except:
                    pass
        else:
            total_expenses += exp.get("amount", 0)
    
    net = total_income - total_expenses
    
    return (
        f"Financial Summary ({period}):\n"
        f"  Income: ${total_income:.2f}\n"
        f"  Expenses: ${total_expenses:.2f}\n"
        f"  Net: ${net:.2f}"
    )


def create_invoice(client: str, items: list, total: float) -> str:
    """Create an invoice."""
    data = _load_finance()
    invoice = {
        "invoice_id": f"INV-{len(data.get('invoices', [])) + 1:04d}",
        "client": client,
        "items": items,
        "total": total,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "pending"
    }
    data["invoices"].append(invoice)
    _save_finance(data)
    return f"Invoice {invoice['invoice_id']} created for {client}: ${total}"


def search_jobs(keywords: str, platform: str = "all") -> str:
    """Search for jobs (web search wrapper)."""
    # This would use web_search internally
    query = f"{keywords} jobs {platform} freelance"
    return f"Job search ready. Use web_search with query: {query}"


def money_maker(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher."""
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    
    if player:
        player.write_log(f"[money] {action}")
    
    try:
        if action == "track_income":
            return track_income(
                params.get("source", "other"),
                float(params.get("amount", 0)),
                params.get("description", "")
            )
        elif action == "track_expense":
            return track_expense(
                float(params.get("amount", 0)),
                params.get("description", ""),
                params.get("category", "other")
            )
        elif action == "summary":
            return get_summary(params.get("period", "month"))
        elif action == "invoice":
            return create_invoice(
                params.get("client", "Client"),
                params.get("items", []),
                float(params.get("amount", 0))
            )
        elif action == "jobs":
            return search_jobs(
                params.get("keywords", ""),
                params.get("platform", "all")
            )
        elif action == "analyze":
            return get_summary("month")
        else:
            return get_summary("month")
    
    except Exception as e:
        return f"Money maker error: {e}"
