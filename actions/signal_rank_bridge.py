"""
SignalRankAI Bridge - MARK-XXXIX delegation to trading brain.

SignalRankAI is the institutional-grade algorithmic trading engine.
Route financial queries here instead of calculating directly.

Usage:
    When user asks about markets, portfolio, or trading actions,
    query SignalRankAI via this bridge.
"""

import json
import logging
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# SignalRankAI FastAPI endpoint (adjust port as needed)
SIGNAL_RANK_API_URL = "http://localhost:8000/api"


def signal_rank_bridge(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    Query SignalRankAI for trading intelligence.
    
    Parameters:
    - query: portfolio_status | market_analysis | active_signals | risk_check
    - symbols: List of ticker symbols (e.g., "AAPL,MSFT")
    - timeframe: 1h | 1d | 1w | 1m
    """
    p = parameters or {}
    query = p.get("query", "portfolio_status")
    symbols = p.get("symbols", "")
    timeframe = p.get("timeframe", "1d")
    
    logger.info(f"[SIGNAL RANK] Query: {query}")
    
    if player:
        player.write_log(f"[SignalRank] Fetching {query}...")
    
    # Map query types to API endpoints
    endpoint_map = {
        "portfolio_status": "/portfolio/summary",
        "market_analysis": "/ml/analysis",
        "active_signals": "/signals/active",
        "risk_check": "/risk/assessment",
        "health": "/health"
    }
    
    endpoint = endpoint_map.get(query, "/health")
    url = f"{SIGNAL_RANK_API_URL}{endpoint}"
    
    # Add query parameters
    params = {}
    if symbols:
        params["symbols"] = symbols
    if timeframe:
        params["timeframe"] = timeframe
    
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"
    
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            
            # Format for speech/display
            if query == "portfolio_status":
                total = result.get("total_value", 0)
                pnl = result.get("daily_pnl", 0)
                msg = f"Portfolio value: ${total:,.2f}. Daily P&L: ${pnl:,.2f}"
            elif query == "active_signals":
                signals = result.get("signals", [])
                msg = f"Active signals: {len(signals)} positions"
            elif query == "market_analysis":
                sentiment = result.get("sentiment", "neutral")
                msg = f"Market sentiment: {sentiment}"
            else:
                msg = f"SignalRank data: {json.dumps(result)[:200]}"
            
            if speak:
                speak(msg)
            return msg
            
    except urllib.error.URLError as e:
        error_msg = f"Cannot connect to SignalRankAI. Is the API running? {e}"
        logger.error(f"[SIGNAL RANK] {error_msg}")
        if speak:
            speak("I cannot connect to the trading system.")
        return error_msg
    except Exception as e:
        error_msg = f"SignalRank bridge error: {e}"
        logger.error(f"[SIGNAL RANK] {error_msg}")
        if speak:
            speak(f"Trading query failed: {str(e)[:100]}")
        return error_msg


# Standalone function for direct calls  
def get_trading_status(
    query_type: str,
    parameters: Dict[str, Any] = None
) -> str:
    """Query SignalRankAI for trading data."""
    return signal_rank_bridge(parameters={
        "query": query_type,
        **(parameters or {})
    })


if __name__ == "__main__":
    # Test
    print("[SignalRank] Testing connection...")
    result = signal_rank_bridge({"query": "health"})
    print(result)
