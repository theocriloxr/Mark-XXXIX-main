# os_integration.py
"""
OS Integration - Makes JARVIS work as a system-level assistant
Always listening, starts with OS, system tray, proactive assistance
Based on best practices from Siri, Cortana, Google Assistant
"""

import os
import sys
import platform
import subprocess
import json
import time
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime

_OS = platform.system()

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
CONFIG_DIR = BASE_DIR / "config"
OS_CONFIG = CONFIG_DIR / "os_integration.json"


def _load_config() -> dict:
    """Load OS integration configuration."""
    if OS_CONFIG.exists():
        try:
            return json.loads(OS_CONFIG.read_text(encoding="utf-8"))
        except:
            pass
    return _default_config()


def _default_config() -> dict:
    """Default OS integration settings."""
    return {
        "always_listen": True,
        "wake_word": "JARVIS",
        "start_with_os": True,
        "system_tray": True,
        "proactive_mode": True,
        "learning_enabled": True,
        "background_monitoring": True,
        "notifications": True,
        "response_style": "natural",  # natural | concise | detailed
        "language": "en",
    }


def _save_config(config: dict) -> None:
    """Save OS integration configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    OS_CONFIG.write_text(json.dumps(config, indent=2), encoding="utf-8")


def _get_os() -> str:
    return _OS.lower()


def get_status() -> str:
    """Get current OS integration status."""
    config = _load_config()
    
    status_lines = [
        "OS Integration Status:",
        f"  Always Listen: {'✓' if config.get('always_listen') else '✗'}",
        f"  Wake Word: '{config.get('wake_word', 'JARVIS')}'",
        f"  Start with OS: {'✓' if config.get('start_with_os') else '✗'}",
        f"  System Tray: {'✓' if config.get('system_tray') else '✗'}",
        f"  Proactive Mode: {'✓' if config.get('proactive_mode') else '✗'}",
        f"  Learning: {'✓' if config.get('learning_enabled') else '✗'}",
    ]
    
    # Check if running
    if _is_service_running():
        status_lines.append("  Service Status: RUNNING")
    else:
        status_lines.append("  Service Status: NOT RUNNING")
    
    return "\n".join(status_lines)


def _is_service_running() -> bool:
    """Check if JARVIS service is running."""
    if _get_os() == "windows":
        try:
            result = subprocess.run(
                ["tasklist"], capture_output=True, text=True, timeout=5
            )
            return "jarvis" in result.stdout.lower() or "main.py" in result.stdout.lower()
        except:
            pass
    else:
        try:
            result = subprocess.run(
                ["pgrep", "-f", "jarvis"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            pass
    return False


def install_service(action: str = "install") -> str:
    """Install/uninstall JARVIS as system service."""
    try:
        if _get_os() == "windows":
            return _install_windows_service(action)
        elif _get_os() == "darwin":
            return _install_macos_service(action)
        else:
            return _install_linux_service(action)
    except Exception as e:
        return f"Service {action} failed: {e}"


def _install_windows_service(action: str) -> str:
    """Install JARVIS as Windows service/auto-start."""
    if action == "install":
        # Create startup entry
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            exe_path = sys.executable or sys.executable
            winreg.SetValueEx(
                key, "JARVIS",
                0,
                winreg.REG_SZ,
                f'"{exe_path}" "{BASE_DIR / "main.py"}"'
            )
            winreg.CloseKey(key)
            return "JARVIS installed to Windows startup."
        except Exception as e:
            return f"Install failed: {e}"
    
    elif action == "uninstall":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            winreg.DeleteValue(key, "JARVIS")
            winreg.CloseKey(key)
            return "JARVIS removed from Windows startup."
        except:
            return "JARVIS not in startup (or already removed)."
    
    elif action == "status":
        running = _is_service_running()
        return f"JARVIS service: {'Running' if running else 'Not running'}"


def _install_macos_service(action: str) -> str:
    """Install as macOS LaunchAgent."""
    plist_path = Path.home() / "Library" / "LaunchAgents" / "com.jarvis.launcher.plist"
    
    if action == "install":
        exe_path = sys.executable or "python3"
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jarvis.launcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
        <string>{BASE_DIR / "main.py"}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        plist_path.write_text(plist)
        
        # Load the agent
        subprocess.run(["launchctl", "load", str(plist_path)], check=False)
        return "JARVIS installed as macOS LaunchAgent."
    
    elif action == "uninstall":
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
            plist_path.unlink()
        return "JARVIS removed from macOS startup."
    
    elif action == "status":
        running = _is_service_running()
        return f"JARVIS: {'Running' if running else 'Not running'}"


def _install_linux_service(action: str) -> str:
    """Install as Linux systemd service."""
    service_path = Path("/etc/systemd/system/jarvis.service")
    
    if action == "install":
        exe_path = sys.executable or "python3"
        service = f"""[Unit]
Description=JARVIS AI Assistant
After=network.target

[Service]
Type=simple
ExecStart={exe_path} {BASE_DIR / "main.py"}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        try:
            service_path.write_text(service)
            subprocess.run(["systemctl", "daemon-reload"], check=False)
            subprocess.run(["systemctl", "enable", "jarvis"], check=False)
            return "JARVIS installed as systemd service."
        except PermissionError:
            return "Need sudo to install systemd service."
    
    elif action == "uninstall":
        try:
            subprocess.run(["systemctl", "stop", "jarvis"], check=False)
            subprocess.run(["systemctl", "disable", "jarvis"], check=False)
            if service_path.exists():
                service_path.unlink()
            return "JARVIS removed from systemd."
        except:
            return "Remove failed (need sudo)."
    
    elif action == "status":
        result = subprocess.run(
            ["systemctl", "is-active", "jarvis"],
            capture_output=True
        )
        return f"JARVIS: {result.stdout.decode().strip()}"


def set_config(key: str, value) -> str:
    """Update OS integration setting."""
    config = _load_config()
    config[key] = value
    _save_config(config)
    return f"Setting updated: {key} = {value}"


def get_learning_data() -> dict:
    """Get learned user patterns and preferences."""
    learning_file = BASE_DIR / "memory" / "learnedPatterns.json"
    if learning_file.exists():
        try:
            return json.loads(learning_file.read_text())
        except:
            pass
    return {
        "common_commands": {},
        "preferred_times": {},
        "habits": [],
        "feedback_history": [],
    }


def save_learned(pattern: str, command_type: str = "general") -> None:
    """Save learned pattern from user interaction."""
    data = get_learning_data()
    
    # Track common commands
    cmds = data.get("common_commands", {})
    cmds[pattern] = cmds.get(pattern, 0) + 1
    data["common_commands"] = cmds
    
    # Track time patterns
    hour = datetime.now().hour
    times = data.get("preferred_times", {})
    times[str(hour)] = times.get(str(hour), 0) + 1
    data["preferred_times"] = times
    
    learning_file = BASE_DIR / "memory" / "learnedPatterns.json"
    learning_file.parent.mkdir(parents=True, exist_ok=True)
    learning_file.write_text(json.dumps(data, indent=2))


def get_insights() -> str:
    """Get learned insights about the user."""
    data = get_learning_data()
    
    lines = ["Learned Insights:"]
    
    # Top commands
    cmds = data.get("common_commands", {})
    if cmds:
        top = sorted(cmds.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append("  Most Used Commands:")
        for cmd, count in top:
            lines.append(f"    - {cmd}: {count}x")
    
    # Preferred times
    times = data.get("preferred_times", {})
    if times:
        peak_hour = max(times.items(), key=lambda x: x[1])[0]
        lines.append(f"  Most Active Around: {peak_hour}:00")
    
    return "\n".join(lines)


def os_integration(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """Main dispatcher for OS integration features."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    try:
        if action == "status":
            return get_status()
        
        elif action == "install":
            return install_service("install")
        
        elif action == "uninstall":
            return install_service("uninstall")
        
        elif action == "start":
            return install_service("install")
        
        elif action == "stop":
            return install_service("uninstall")
        
        elif action in ("enable", "disable"):
            enable = (action == "enable")
            key = params.get("setting", "always_listen")
            return set_config(key, enable)
        
        elif action == "set":
            key = params.get("key", "")
            value = params.get("value", True)
            if value == "true":
                value = True
            elif value == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            return set_config(key, value)
        
        elif action == "insights":
            return get_insights()
        
        elif action == "config":
            return json.dumps(_load_config(), indent=2)
        
        elif action == "learn":
            # Learn from interaction
            pattern = params.get("pattern", "")
            cmd_type = params.get("type", "general")
            if pattern:
                save_learned(pattern, cmd_type)
                return f"Learned: {pattern}"
            return "Specify pattern to learn."
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"OS integration error: {e}"
