"""
Agentic Financials - GDP Tracker and P&L Dashboard

Financial tracking for JARVIS as an autonomous business:
- Track AWS costs, LLM token costs, crypto transactions
- Track value generated (tasks, code written)
- Real-time P&L statement
- Sub-agent profitability analysis

Usage:
    from actions.financials import AgenticFinancials, get_financials
    
    financials = get_financials()
    financials.track_expense("aws", 5.50, "EC2 instance")
    financials.track_value("task_completed", 10.0)
    
    pl = financials.get_pl_statement()
"""

import json
import logging
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Get base directory
def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()
FINANCIALS_FILE = BASE_DIR / "memory" / "financials.json"


# Expense categories
CAT_AWS = "aws"
CAT_LLM = "llm"
CAT_CRYPTO = "crypto"
CAT_API = "api"
CAT_COMPUTE = "compute"


# Value categories
VAL_TASK_COMPLETED = "task_completed"
VAL_CODE_WRITTEN = "code_written"
VAL_RESEARCH = "research"
VAL_DATA = "data"


@dataclass
class Transaction:
    """Financial transaction."""
    tx_id: str
    type: str  # expense or value
    category: str
    amount: float
    description: str
    timestamp: float = field(default_factory=time.time)
    agent_name: str = ""


class AgenticFinancials:
    """
    Financial tracking for autonomous AI agent.
    Tracks P&L in real-time.
    """
    
    def __init__(self):
        self.expenses: deque = deque(maxlen=1000)
        self.values: deque = deque(maxlen=1000)
        self.tasks_completed = 0
        self.code_written_lines = 0
        
        # Daily budget
        self.daily_budget = 100.0
        self.daily_spent = 0.0
        self.budget_reset = time.time()
        
        # Load saved data
        self._load()
        
        logger.info("[FINANCIALS] GDP Tracker initialized")
    
    def track_expense(
        self,
        category: str,
        amount: float,
        description: str = "",
        agent_name: str = ""
    ) -> str:
        """
        Track an expense.
        
        Args:
            category: Expense category (aws, llm, crypto, api, compute)
            amount: Amount in USD
            description: Description
            agent_name: Sub-agent that made the expense
            
        Returns:
            str: Transaction ID
        """
        import uuid
        
        tx_id = str(uuid.uuid4())[:8]
        
        tx = Transaction(
            tx_id=tx_id,
            type="expense",
            category=category,
            amount=abs(amount),
            description=description,
            agent_name=agent_name
        )
        
        self.expenses.append(tx)
        self.daily_spent += abs(amount)
        
        self._save()
        
        logger.debug(f"[FINANCIALS] Expense: ${amount:.2f} ({category})")
        return tx_id
    
    def track_value(
        self,
        category: str,
        value: float,
        description: str = "",
        agent_name: str = ""
    ) -> str:
        """
        Track value generated.
        
        Args:
            category: Value category (task_completed, code_written, research)
            value: Estimated value in USD
            description: Description
            agent_name: Sub-agent that generated value
            
        Returns:
            str: Transaction ID
        """
        import uuid
        
        tx_id = str(uuid.uuid4())[:8]
        
        tx = Transaction(
            tx_id=tx_id,
            type="value",
            category=category,
            amount=abs(value),
            description=description,
            agent_name=agent_name
        )
        
        self.values.append(tx)
        
        # Update stats
        if category == VAL_TASK_COMPLETED:
            self.tasks_completed += 1
        elif category == VAL_CODE_WRITTEN:
            self.code_written_lines += int(value)
        
        self._save()
        
        logger.debug(f"[FINANCIALS] Value: ${value:.2f} ({category})")
        return tx_id
    
    def get_pl_statement(self) -> Dict[str, Any]:
        """
        Get P&L statement.
        
        Returns:
            dict: Revenue, expenses, profit/loss
        """
        total_revenue = sum(v.amount for v in self.values)
        total_expenses = sum(e.amount for e in self.expenses)
        profit = total_revenue - total_expenses
        
        # Group by category
        expense_by_cat = {}
        for e in self.expenses:
            cat = e.category
            expense_by_cat[cat] = expense_by_cat.get(cat, 0) + e.amount
        
        value_by_cat = {}
        for v in self.values:
            cat = v.category
            value_by_cat[cat] = value_by_cat.get(cat, 0) + v.amount
        
        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "profit": profit,
            "profit_margin": (profit / total_revenue * 100) if total_revenue > 0 else 0,
            "expenses_by_category": expense_by_cat,
            "value_by_category": value_by_cat,
            "tasks_completed": self.tasks_completed,
            "code_lines": self.code_written_lines,
            "daily_budget": self.daily_budget,
            "daily_spent": self.daily_spent,
            "daily_remaining": self.daily_budget - self.daily_spent
        }
    
    def get_agent_profitability(self) -> Dict[str, Dict]:
        """
        Get profitability by sub-agent.
        
        Returns:
            dict: Agent statistics
        """
        agent_stats = {}
        
        # Aggregate expenses by agent
        for e in self.expenses:
            agent = e.agent_name or "unknown"
            if agent not in agent_stats:
                agent_stats[agent] = {"expenses": 0, "value": 0}
            agent_stats[agent]["expenses"] += e.amount
        
        # Aggregate values by agent
        for v in self.values:
            agent = v.agent_name or "unknown"
            if agent not in agent_stats:
                agent_stats[agent] = {"expenses": 0, "value": 0}
            agent_stats[agent]["value"] += v.amount
        
        # Calculate profit
        for agent in agent_stats:
            stats = agent_stats[agent]
            stats["profit"] = stats["value"] - stats["expenses"]
            stats["roi"] = (
                (stats["value"] / stats["expenses"] * 100)
                if stats["expenses"] > 0 else 100
            )
        
        return agent_stats
    
    def get_recent_transactions(self, count: int = 10) -> List[Dict]:
        """Get recent transactions."""
        all_txs = list(self.expenses) + list(self.values)
        all_txs.sort(key=lambda t: t.timestamp, reverse=True)
        
        return [
            {
                "tx_id": t.tx_id,
                "type": t.type,
                "category": t.category,
                "amount": t.amount,
                "description": t.description,
                "timestamp": t.timestamp,
                "agent": t.agent_name
            }
            for t in all_txs[:count]
        ]
    
    def set_budget(self, daily_budget: float):
        """Set daily budget."""
        self.daily_budget = daily_budget
        self._save()
    
    def reset_daily(self):
        """Reset daily counters."""
        self.daily_spent = 0.0
        self.budget_reset = time.time()
        self._save()
    
    def _load(self):
        """Load data from file."""
        if not FINANCIALS_FILE.exists():
            return
        
        try:
            data = json.loads(FINANCIALS_FILE.read_text(encoding="utf-8"))
            self.daily_budget = data.get("daily_budget", 100.0)
            self.daily_spent = data.get("daily_spent", 0.0)
            self.tasks_completed = data.get("tasks_completed", 0)
            self.code_written_lines = data.get("code_written_lines", 0)
            logger.info("[FINANCIALS] Data loaded")
        except Exception as e:
            logger.warning(f"[FINANCIALS] Load error: {e}")
    
    def _save(self):
        """Save data to file."""
        FINANCIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "daily_budget": self.daily_budget,
            "daily_spent": self.daily_spent,
            "tasks_completed": self.tasks_completed,
            "code_written_lines": self.code_written_lines,
            "saved_at": time.time()
        }
        
        FINANCIALS_FILE.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )


# === GLOBAL INSTANCE ===

_financials: Optional[AgenticFinancials] = None


def get_financials() -> AgenticFinancials:
    """Get global AgenticFinancials instance."""
    global _financials
    if _financials is None:
        _financials = AgenticFinancials()
    return _financials


# === DISPATCHER ===

def agentic_financials(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for Agentic Financials."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[Financials] {action}")
    
    try:
        fin = get_financials()
        
        if action == "status":
            pl = fin.get_pl_statement()
            return (
                f"Revenue: ${pl['total_revenue']:.2f} | "
                f"Expenses: ${pl['total_expenses']:.2f} | "
                f"Profit: ${pl['profit']:.2f}"
            )
        
        elif action == "pl" or action == "profit":
            pl = fin.get_pl_statement()
            lines = [
                "=== P&L Statement ===",
                f"Revenue: ${pl['total_revenue']:.2f}",
                f"Expenses: ${pl['total_expenses']:.2f}",
                f"Profit: ${pl['profit']:.2f}",
                f"Tasks: {pl['tasks_completed']}",
                f"Code: {pl['code_lines']} lines"
            ]
            return "\n".join(lines)
        
        elif action == "expense":
            category = params.get("category", "api")
            amount = float(params.get("amount", 0))
            description = params.get("description", "")
            agent = params.get("agent", "")
            
            if amount <= 0:
                return "Please provide amount"
            
            tx_id = fin.track_expense(category, amount, description, agent)
            return f"Expense tracked: ${amount:.2f}"
        
        elif action == "value":
            category = params.get("category", "task_completed")
            value = float(params.get("value", 0))
            description = params.get("description", "")
            agent = params.get("agent", "")
            
            if value <= 0:
                return "Please provide value"
            
            tx_id = fin.track_value(category, value, description, agent)
            return f"Value tracked: ${value:.2f}"
        
        elif action == "agents" or action == "profitability":
            agents = fin.get_agent_profitability()
            if agents:
                lines = ["Agent Profitability:"]
                for name, stats in sorted(
                    agents.items(),
                    key=lambda x: x[1].get("profit", 0),
                    reverse=True
                ):
                    lines.append(
                        f"  {name}: ${stats.get('profit', 0):.2f} "
                        f"(ROI: {stats.get('roi', 0):.0f}%)"
                    )
                return "\n".join(lines)
            return "No agent data"
        
        elif action == "transactions":
            txs = fin.get_recent_transactions()
            if txs:
                lines = ["Recent Transactions:"]
                for t in txs[:5]:
                    sign = "+" if t["type"] == "value" else "-"
                    lines.append(
                        f"  {sign}${t['amount']:.2f} {t['category']}: "
                        f"{t['description'][:30]}"
                    )
                return "\n".join(lines)
            return "No transactions"
        
        elif action == "budget":
            budget = params.get("budget", "")
            if budget:
                fin.set_budget(float(budget))
                return f"Budget set: ${budget}"
            pl = fin.get_pl_statement()
            return f"Daily budget: ${pl['daily_budget']:.2f}, spent: ${pl['daily_spent']:.2f}"
        
        elif action == "reset":
            fin.reset_daily()
            return "Daily counters reset"
        
        else:
            pl = fin.get_pl_statement()
            return (
                f"P&L: ${pl['profit']:.2f} | "
                f"Tasks: {pl['tasks_completed']} | "
                f"Daily: ${pl['daily_spent']:.2f}/${pl['daily_budget']:.2f}"
            )
    
    except Exception as e:
        return f"Financials error: {e}"


if __name__ == "__main__":
    print("=== Agentic Financials Test ===")
    
    fin = get_financials()
    
    # Track some data
    fin.track_expense(CAT_AWS, 5.50, "EC2 instance", "dev_agent")
    fin.track_expense(CAT_LLM, 2.00, "Gemini tokens", "jarvis")
    fin.track_value(VAL_TASK_COMPLETED, 10.0, "Fixed bug", "dev_agent")
    fin.track_value(VAL_CODE_WRITTEN, 50.0, "Wrote tests", "dev_agent")
    
    # Get P&L
    pl = fin.get_pl_statement()
    print(f"P&L: ${pl['profit']:.2f}")
    print(f"Tasks: {pl['tasks_completed']}")
    
    # Agent profitability
    agents = fin.get_agent_profitability()
    print(f"Agents: {agents}")
    
    print("\n✅ Financials ready")
