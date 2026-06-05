# tool_schemas.py
"""
Strict JSON/Pydantic Schemas for JARVIS Bridge Tools

These schemas define exactly what the LLM (Gemini) is allowed to send to bridge tools.
They eliminate hallucinations by specifying exact parameter constraints.

Usage:
    Import these schemas when configuring Gemini's function calling.
    Pass them directly into your tools definition.
"""

# === UJO NETWORK SCHEMA ===
# Routes system-level tasks to the Ujo daemon (distributed nervous system)

UJO_NETWORK_SCHEMA = {
    "name": "ujo_network",
    "description": (
        "Delegates system-level tasks, OS-level file manipulations, remote execution, "
        "and Docker deployments to the background Ujo daemon. "
        "Use for Docker operations, cross-device control, or OS hooks."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "The category of operation to execute. "
                    "Allowed values: docker_deploy | fs_manipulation | remote_exec | status"
                ),
                "enum": ["docker_deploy", "fs_manipulation", "remote_exec", "status"]
            },
            "target": {
                "type": "STRING",
                "description": (
                    "The target node identifier. "
                    "Use 'local' for current machine, or node name (e.g., 'macbook-pro', 'aws-server')"
                ),
                "default": "local"
            },
            "command": {
                "type": "STRING",
                "description": "The command to execute on the target system"
            },
            "payload": {
                "type": "STRING",
                "description": (
                    "Additional parameters as JSON string. "
                    "Examples: {'container': 'nginx', 'image': 'nginx:latest'} or {'path': '/home/user'}"
                )
            }
        },
        "required": ["action"]
    }
}


# === SIGNAL RANK BRIDGE SCHEMA ===
# Queries the institutional trading brain (SignalRankAI) for market data

SIGNAL_RANK_SCHEMA = {
    "name": "signal_rank_bridge",
    "description": (
        "Queries the institutional trading brain (SignalRankAI) for live market data, "
        "portfolio performance, active signals, or risk checks. "
        "Use for any financial/trading queries."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": (
                    "The exact type of trading data requested. "
                    "Allowed values: portfolio_status | market_analysis | active_signals | risk_check"
                ),
                "enum": ["portfolio_status", "market_analysis", "active_signals", "risk_check"]
            },
            "symbols": {
                "type": "STRING",
                "description": (
                    "Comma-separated ticker symbols. "
                    "Examples: 'AAPL,MSFT' or 'BTC,ETH'"
                )
            },
            "timeframe": {
                "type": "STRING",
                "description": "Time frame for data. Allowed values: 1h | 1d | 1w | 1m",
                "enum": ["1h", "1d", "1w", "1m"],
                "default": "1d"
            }
        },
        "required": ["query"]
    }
}


# === COMBINED TOOL SCHEMAS ===
# For easy import into Gemini configuration

BRIDGE_TOOL_SCHEMAS = [UJO_NETWORK_SCHEMA, SIGNAL_RANK_SCHEMA]


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    # Test printing schemas
    import json
    
    print("=== UJO NETWORK SCHEMA ===")
    print(json.dumps(UJO_NETWORK_SCHEMA, indent=2))
    print("\n=== SIGNAL RANK SCHEMA ===")
    print(json.dumps(SIGNAL_RANK_SCHEMA, indent=2))
    
    print("\n✅ Schemas loaded successfully.")
    print("Pass these to Gemini's function_declarations for strict tool calling.")
