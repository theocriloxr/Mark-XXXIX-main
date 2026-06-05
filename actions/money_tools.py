# money_tools.py
"""
Money & Income Tools - Tools to help make money, track finances, trade crypto, stocks.
Part of enhanced JARVIS system for income generation.
"""

import json
import requests
import platform
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
FINANCE_FILE = BASE_DIR / "memory" / "finances.json"


def get_crypto_price(symbol: str = "BTC") -> str:
    """Get cryptocurrency price."""
    try:
        # Use CoinGecko API (free, no key needed)
        symbol_upper = symbol.upper()
        
        # Map common symbols to CoinGecko IDs
        coin_ids = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "LINK": "chainlink",
            "AVAX": "avalanche-2",
        }
        
        coin_id = coin_ids.get(symbol_upper, symbol_lower.lower())
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = data[coin_id]["usd"]
            return f"{symbol_upper}: ${price:,.2f} USD"
        
        return f"Unable to fetch {symbol} price"
    except Exception as e:
        return f"Price error: {e}"


def get_crypto_prices(symbols: str = "BTC,ETH,SOL") -> str:
    """Get multiple crypto prices."""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        coin_ids = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "LINK": "chainlink",
            "AVAX": "avalanche-2",
        }
        
        ids = [coin_ids.get(s, s.lower()) for s in symbol_list if s in coin_ids]
        ids_str = ",".join(ids)
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            lines = ["Crypto Prices:"]
            for sym in symbol_list:
                coin_id = coin_ids.get(sym, sym.lower())
                if coin_id in data:
                    price = data[coin_id]["usd"]
                    lines.append(f"  {sym}: ${price:,.2f}")
            return "\n".join(lines)
        
        return "Unable to fetch prices"
    except Exception as e:
        return f"Price error: {e}"


def search_crypto_news(symbol: str = "BTC") -> str:
    """Search for crypto news."""
    try:
        # Use CryptoCompare news API
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data["Data"][:5]
            
            lines = [f"Latest crypto news:"]
            for i, article in enumerate(articles, 1):
                title = article.get("title", "")[:60]
                source = article.get("source", "")
                lines.append(f"{i}. {title}... ({source})")
            
            return "\n".join(lines)
        
        return "Unable to fetch news"
    except Exception as e:
        return f"News error: {e}"


def track_expense(description: str, amount: float, category: str = "other") -> str:
    """Track an expense."""
    try:
        FINANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        if FINANCE_FILE.exists():
            data = json.loads(FINANCE_FILE.read_text(encoding="utf-8"))
        else:
            data = {"expenses": [], "income": [], "investments": []}
        
        # Add expense
        expense = {
            "description": description,
            "amount": abs(float(amount)),
            "category": category,
            "date": datetime.now().isoformat()
        }
        
        data["expenses"].append(expense)
        
        # Save
        FINANCE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return f"Expense tracked: {description} - ${abs(amount):.2f}"
    except Exception as e:
        return f"Track error: {e}"


def track_income(description: str, amount: float, source: str = " salary ") -> str:
    """Track income."""
    try:
        FINANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        if FINANCE_FILE.exists():
            data = json.loads(FINANCE_FILE.read_text(encoding="utf-8"))
        else:
            data = {"expenses": [], "income": [], "investments": []}
        
        income = {
            "description": description,
            "amount": abs(float(amount)),
            "source": source,
            "date": datetime.now().isoformat()
        }
        
        data["income"].append(income)
        
        FINANCE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return f"Income tracked: {description} - ${abs(amount):.2f}"
    except Exception as e:
        return f"Track error: {e}"


def get_finance_summary() -> str:
    """Get finance summary."""
    try:
        if not FINANCE_FILE.exists():
            return "No finance data tracked yet"
        
        data = json.loads(FINANCE_FILE.read_text(encoding="utf-8"))
        
        total_expenses = sum(e.get("amount", 0) for e in data.get("expenses", []))
        total_income = sum(i.get("amount", 0) for i in data.get("income", []))
        
        balance = total_income - total_expenses
        
        lines = [
            "Finance Summary:",
            f"  Total Income: ${total_income:,.2f}",
            f"  Total Expenses: ${total_expenses:,.2f}",
            f"  Balance: ${balance:,.2f}"
        ]
        
        return "\n".join(lines)
    except Exception as e:
        return f"Summary error: {e}"


def search_jobs(query: str = "python developer remote") -> str:
    """Search for jobs."""
    try:
        # Use Jooble API (free tier)
        url = "https://jooble.org/api/"
        payload = {
            "keywords": query,
            "location": "Remote",
            "page": 1
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            jobs = result.get("jobs", [])[:5]
            
            lines = [f"Jobs for '{query}':"]
            for job in jobs:
                title = job.get("title", "")[:50]
                company = job.get("company", "")
                lines.append(f"  • {title} @ {company}")
            
            return "\n".join(lines)
        
        return "Unable to search jobs"
    except Exception as e:
        return f"Job search error: {e}"


def money_tools(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for money tools."""
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    
    if player:
        player.write_log(f"[money] {action}")
    
    try:
        if action == "crypto_price":
            return get_crypto_price(params.get("symbol", "BTC"))
        elif action == "crypto_prices":
            return get_crypto_prices(params.get("symbols", "BTC,ETH,SOL"))
        elif action == "crypto_news":
            return search_crypto_news(params.get("symbol", "BTC"))
        elif action == "track_expense":
            return track_expense(
                params.get("description", ""),
                float(params.get("amount", 0)),
                params.get("category", "other")
            )
        elif action == "track_income":
            return track_income(
                params.get("description", ""),
                float(params.get("amount", 0)),
                params.get("source", "salary")
            )
        elif action == "summary":
            return get_finance_summary()
        elif action == "jobs":
            return search_jobs(params.get("query", "python developer remote"))
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Money tools error: {e}"
