"""
JARVIS Sandbox - Self-Coding & Auto-Installing Skills

Directory for experimental tools being developed by the Evolution Lab.
Tools here are tested before being moved to production actions/ directory.

Structure:
    sandbox/
    ├── tools/     # Experimental tool Python files
    ├── tests/     # Pytest test files
    └── logs/      # Execution logs
"""

__version__ = "1.0.0"

# Sandbox configuration
SANDBOX_ENABLED = True
AUTO_DEPLOY_THRESHOLD = 0.95  # 95% test success required
