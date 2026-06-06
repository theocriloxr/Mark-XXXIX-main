"""
Economic Agent - Self-Paying Autonomous Agent

JARVIS manages its own economic resources:
- Crypto wallet for API costs
- AWS EC2 auto-scaling for heavy tasks
- Bug bounty payments to developers
- Self-sustaining operation

Usage:
    from actions.economic_agent import EconomicAgent, get_wallet_balance
    
    # Check balance
    balance = get_wallet_balance()
    
    # Execute paid task
    result = execute_paid_task("heavy_computation", budget=10)
"""

import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Supported blockchains
ETHEREUM = "ethereum"
SOLANA = "solana"
STRIPE = "stripe"

# Max budget per task (USD)
DEFAULT_BUDGET = 100  # USD


@dataclass
class Transaction:
    """Wallet transaction."""
    tx_id: str
    amount: float
    currency: str = "USD"
    description: str = ""
    timestamp: float = 0
    status: str = "pending"  # pending, confirmed, failed


class EconomicAgent:
    """
    Self-paying economic agent.
    Manages crypto wallet and paid services.
    """
    
    def __init__(self):
        self._enabled = False
        
        # Wallet configs
        self._wallet_config: Dict[str, Any] = {}
        
        # AWS config
        self._aws_config: Dict[str, Any] = {}
        
        # Budget tracking
        self._daily_budget = DEFAULT_BUDGET
        self._daily_spent = 0
        self._budget_reset = 0
        
        # Transaction history
        self._transactions: deque = deque(maxlen=100)
        
        # Lock
        self._lock = None
        
        # Statistics
        self._total_spent = 0
        self._tasks_executed = 0
        
        # Initialize
        self._init_wallet()
    
    def _init_wallet(self):
        """Initialize wallet."""
        # Stub - in production, use web3.py or solders for Solana
        self._wallet_config = {
            "provider": "solana",
            "address": "",
            "enabled": False
        }
        
        # AWS config
        self._aws_config = {
            "enabled": False,
            "instance_type": "t3.medium",
            "max_instances": 5
        }
        
        logger.info("[EconomicAgent] Initialized")
    
    def get_wallet_balance(self) -> float:
        """Get wallet balance."""
        # In production, query blockchain
        if self._wallet_config.get("enabled"):
            # Return actual balance
            return 0.0
        
        # Demo balance
        return 100.0
    
    def get_daily_budget(self) -> float:
        """Get remaining daily budget."""
        current_time = time.time()
        
        # Reset daily budget if new day
        if current_time - self._budget_reset > 86400:
            self._daily_spent = 0
            self._budget_reset = current_time
        
        return self._daily_budget - self._daily_spent
    
    def can_afford(self, amount: float) -> bool:
        """Check if can afford amount."""
        return self.get_wallet_balance() >= amount and self.get_daily_budget() >= amount
    
    def execute_paid_task(
        self,
        task_type: str,
        budget: float = None,
        parameters: Dict = None
    ) -> str:
        """
        Execute a paid task.
        
        Args:
            task_type: heavy_computation, aws_deploy, bounty
            budget: Max budget in USD
            parameters: Task parameters
            
        Returns:
            str: Result
        """
        if not self._enabled:
            return "Economic agent disabled"
        
        budget = budget or DEFAULT_BUDGET
        
        if not self.can_afford(budget):
            return f"Insufficient funds. Budget: ${self.get_daily_budget():.2f}"
        
        try:
            if task_type == "heavy_computation":
                return self._execute_aws_task(budget, parameters)
            elif task_type == "aws_deploy":
                return self._execute_aws_task(budget, parameters)
            elif task_type == "bounty":
                return self._post_bounty(budget, parameters)
            else:
                return f"Unknown task type: {task_type}"
        
        except Exception as e:
            return f"Task failed: {e}"
    
    def _execute_aws_task(self, budget: float, parameters: Dict = None) -> str:
        """Execute AWS task."""
        if not self._aws_config.get("enabled"):
            # Simulate for demo
            self._daily_spent += budget
            self._total_spent += budget
            self._tasks_executed += 1
            
            return f"Task executed on remote (simulated). Cost: ${budget:.2f}"
        
        # In production:
        # 1. Start EC2 instance
        # 2. Run task
        # 3. Stop instance
        
        instance_type = self._aws_config.get("instance_type", "t3.medium")
        
        logger.info(f"[EconomicAgent] Starting AWS {instance_type} for ${budget}")
        
        # Simulated cost
        self._daily_spent += budget
        self._total_spent += budget
        self._tasks_executed += 1
        
        return f"AWS task completed. Cost: ${budget:.2f}"
    
    def _post_bounty(self, budget: float, parameters: Dict = None) -> str:
        """Post bug bounty."""
        description = parameters.get("description", "Bug fix") if parameters else "Bug fix"
        
        # In production, post to GitHub Issues with bounty label
        logger.info(f"[EconomicAgent] Posting bounty: ${budget} for {description}")
        
        self._daily_spent += budget
        self._total_spent += budget
        
        return f"Bounty posted: ${budget} for {description}"
    
    def fund_wallet(self, amount: float, source: str = "stripe") -> str:
        """Add funds to wallet."""
        tx_id = str(uuid.uuid4())[:8]
        
        tx = Transaction(
            tx_id=tx_id,
            amount=amount,
            description=f"Deposit from {source}",
            timestamp=time.time(),
            status="confirmed"
        )
        
        self._transactions.append(tx)
        
        return f"Wallet funded: ${amount}"
    
    def get_transaction_history(self, count: int = 10) -> List[Dict]:
        """Get transaction history."""
        txs = list(self._transactions)[-count:]
        
        return [
            {
                "tx_id": t.tx_id,
                "amount": t.amount,
                "description": t.description,
                "timestamp": t.timestamp,
                "status": t.status
            }
            for t in txs
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "wallet_enabled": self._wallet_config.get("enabled", False),
            "aws_enabled": self._aws_config.get("enabled", False),
            "total_spent": self._total_spent,
            "tasks_executed": self._tasks_executed,
            "daily_budget": self._daily_budget,
            "daily_spent": self._daily_spent,
            "balance": self.get_wallet_balance()
        }
    
    def configure_wallet(self, provider: str, address: str, private_key: str = None) -> str:
        """Configure crypto wallet."""
        self._wallet_config = {
            "provider": provider,
            "address": address,
            "enabled": True
        }
        return f"Wallet configured: {provider}"
    
    def configure_aws(
        self,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1"
    ) -> str:
        """Configure AWS."""
        self._aws_config = {
            "enabled": True,
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
            "instance_type": "t3.medium"
        }
        return "AWS configured"
    
    def set_budget(self, daily_budget: float):
        """Set daily budget."""
        self._daily_budget = daily_budget
    
    def enable(self):
        """Enable economic agent."""
        self._enabled = True
    
    def disable(self):
        """Disable economic agent."""
        self._enabled = False


# === GLOBAL INSTANCE ===

_economic_agent: Optional[EconomicAgent] = None


def get_economic_agent() -> EconomicAgent:
    """Get global economic agent."""
    global _economic_agent
    if _economic_agent is None:
        _economic_agent = EconomicAgent()
    return _economic_agent


def get_wallet_balance() -> float:
    """Get wallet balance."""
    return get_economic_agent().get_wallet_balance()


def execute_paid_task(task_type: str, budget: float = None) -> str:
    """Execute a paid task."""
    return get_economic_agent().execute_paid_task(task_type, budget)


# === DISPATCHER ===

def economic_agent(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for economic agent."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[EconomicAgent] {action}")
    
    agent = get_economic_agent()
    
    try:
        if action == "status":
            stats = agent.get_statistics()
            return (
                f"Balance: ${stats['balance']:.2f} | "
                f"Daily: ${stats['daily_spent']:.2f}/${stats['daily_budget']:.2f} | "
                f"Tasks: {stats['tasks_executed']}"
            )
        
        elif action == "balance":
            return f"Wallet balance: ${agent.get_wallet_balance():.2f}"
        
        elif action == "budget":
            return f"Daily budget: ${agent.get_daily_budget():.2f}"
        
        elif action == "execute":
            task_type = params.get("task_type", "")
            budget = params.get("budget", DEFAULT_BUDGET)
            
            if not task_type:
                return "Please specify task_type"
            
            result = agent.execute_paid_task(task_type, budget, params)
            if speak:
                speak(result)
            return result
        
        elif action == "fund":
            amount = params.get("amount", 100)
            source = params.get("source", "stripe")
            return agent.fund_wallet(amount, source)
        
        elif action == "transactions":
            txs = agent.get_transaction_history()
            if txs:
                lines = ["Transactions:"]
                for t in txs[:5]:
                    lines.append(f"- ${t['amount']:.2f}: {t['description']}")
                return "\n".join(lines)
            return "No transactions"
        
        elif action == "configure":
            what = params.get("what", "").lower()
            
            if what == "wallet":
                provider = params.get("provider", "solana")
                address = params.get("address", "")
                return agent.configure_wallet(provider, address)
            elif what == "aws":
                return agent.configure_aws("", "")
            
            return "Specify what: wallet, aws"
        
        elif action == "enable":
            agent.enable()
            return "Economic agent enabled."
        
        elif action == "disable":
            agent.disable()
            return "Economic agent disabled."
        
        else:
            stats = agent.get_statistics()
            return f"EconomicAgent: ${stats['balance']:.2f} balance, {stats['tasks_executed']} tasks"
    
    except Exception as e:
        return f"EconomicAgent error: {e}"


if __name__ == "__main__":
    print("=== Economic Agent Test ===")
    
    agent = get_economic_agent()
    print(agent.get_statistics())
    
    print("\n✅ Economic Agent ready")
