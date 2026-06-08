"""
Cyber Sentinel - JARVIS Local Cybersecurity Defense

This module allows JARVIS to monitor for unauthorized access, suspicious processes,
and network vulnerabilities locally on the user's machine.

Features:
- Port vulnerability scanning
- Process monitoring for malware indicators
- Network traffic analysis
- Automatic threat response
- Security audit logging

Usage:
    from actions.cyber_sentinel import run_local_audit, secure_local_env
    
    # Run security audit
    audit = run_local_audit()
    
    # Secure environment
    secure_local_env()
"""

import psutil
import socket
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# High-risk ports that may indicate backdoors
RISKY_PORTS = [4444, 1337, 31337, 6667, 8080, 4444, 5555, 9000, 9001]

# Suspicious process patterns
SUSPICIOUS_PATTERNS = [
    "miner", "cryptominer", "xmrig", "nicehash",
    "keylogger", "stealer", " RAT", "远程管理",
    "njrat", "ncrat", "prat",
]

# JARVIS Base Directory
BASE_DIR = Path(r"C:\Users\sammm\Downloads\Mark-XXXIX-main")


def get_local_ip() -> str:
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"


def get_public_ip() -> str:
    """Get public IP address."""
    try:
        import requests
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text
    except:
        return "Unknown"


def scan_open_ports() -> List[Dict]:
    """
    Scan for suspicious open ports.
    
    Returns:
        List of suspicious port findings
    """
    findings = []
    
    try:
        for conn in psutil.net_connections():
            try:
                if conn.status == 'LISTEN':
                    port = conn.laddr.port
                    if port in RISKY_PORTS:
                        findings.append({
                            "port": port,
                            "address": f"{conn.laddr.ip}:{port}",
                            "process": _get_process_name(conn.pid),
                            "pid": conn.pid,
                            "severity": "HIGH" if port in [4444, 1337] else "MEDIUM"
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        findings.append({"error": str(e)})
    
    return findings


def _get_process_name(pid: int) -> str:
    """Get process name from PID."""
    try:
        process = psutil.Process(pid)
        return process.name()
    except:
        return "unknown"


def scan_suspicious_processes() -> List[Dict]:
    """
    Scan for suspicious processes (potential malware).
    
    Returns:
        List of suspicious process findings
    """
    findings = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                name_lower = proc.info['name'].lower()
                
                # Check for suspicious patterns
                for pattern in SUSPICIOUS_PATTERNS:
                    if pattern.lower() in name_lower:
                        findings.append({
                            "name": proc.info['name'],
                            "pid": proc.info['pid'],
                            "cpu": proc.info['cpu_percent'],
                            "memory": proc.info['memory_percent'],
                            "pattern": pattern,
                            "severity": "HIGH"
                        })
                        break
                
                # Check for excessive CPU (>90% sustained)
                if proc.info['cpu_percent'] > 90:
                    findings.append({
                        "name": proc.info['name'],
                        "pid": proc.info['pid'],
                        "cpu": proc.info['cpu_percent'],
                        "memory": proc.info['memory_percent'],
                        "issue": "High CPU usage",
                        "severity": "MEDIUM"
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        findings.append({"error": str(e)})
    
    return findings


def check_network_connections() -> List[Dict]:
    """
    Analyze active network connections.
    
    Returns:
        List of network connection info
    """
    connections = []
    
    try:
        for conn in psutil.net_connections():
            try:
                if conn.status and conn.status != 'LISTEN':
                    connections.append({
                        "local": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                        "remote": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        "status": conn.status,
                        "process": _get_process_name(conn.pid),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        connections.append({"error": str(e)})
    
    return connections[:50]  # Limit to 50


def check_system_resources() -> Dict:
    """
    Check system resource usage.
    
    Returns:
        System resource info
    """
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "disk_percent": psutil.disk_usage('/').percent,
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else "N/A",
    }


def run_local_audit() -> Dict:
    """
    Run comprehensive security audit.
    
    Returns:
        Audit report with all findings
    """
    report = {
        "timestamp": str(psutil.time),
        "local_ip": get_local_ip(),
        "public_ip": get_public_ip(),
        "vulnerabilities": [],
        "suspicious_processes": [],
        "network_connections": [],
        "system_resources": {},
    }
    
    # 1. Scan for suspicious ports
    port_findings = scan_open_ports()
    for finding in port_findings:
        report["vulnerabilities"].append(
            f"Warning: Risky port {finding.get('port')} is open ({finding.get('process')})"
        )
    
    # 2. Scan for suspicious processes
    proc_findings = scan_suspicious_processes()
    for finding in proc_findings:
        report["suspicious_processes"].append(
            f"Suspicious: {finding.get('name')} (PID: {finding.get('pid')}) - {finding.get('pattern', finding.get('issue'))}"
        )
    
    # 3. Check network connections
    report["network_connections"] = check_network_connections()
    
    # 4. System resources
    report["system_resources"] = check_system_resources()
    
    return report


def generate_audit_report(audit: Dict) -> str:
    """
    Generate human-readable audit report.
    
    Args:
        audit: Audit results
    
    Returns:
        Formatted report string
    """
    lines = ["🛡️ CYBER SENTINEL AUDIT REPORT", "=" * 40]
    
    lines.append(f"\n🌐 Network:")
    lines.append(f"  Local IP: {audit.get('local_ip')}")
    lines.append(f"  Public IP: {audit.get('public_ip')}")
    
    lines.append(f"\n⚠️ Vulnerabilities:")
    if audit.get("vulnerabilities"):
        for v in audit.get("vulnerabilities", []):
            lines.append(f"  • {v}")
    else:
        lines.append("  ✓ No suspicious ports detected")
    
    lines.append(f"\n🔍 Suspicious Processes:")
    if audit.get("suspicious_processes"):
        for p in audit.get("suspicious_processes", []):
            lines.append(f"  • {p}")
    else:
        lines.append("  ✓ No suspicious processes detected")
    
    lines.append(f"\n💻 System Resources:")
    res = audit.get("system_resources", {})
    lines.append(f"  CPU: {res.get('cpu_percent')}%")
    lines.append(f"  Memory: {res.get('memory_percent')}%")
    lines.append(f"  Disk: {res.get('disk_percent')}%")
    
    return "\n".join(lines)


def secure_local_env(block_mode: bool = False) -> str:
    """
    Secure local environment by closing risky ports or killing suspicious processes.
    
    Args:
        block_mode: If True, actually kill processes (USE WITH CAUTION)
    
    Returns:
        Result message
    """
    audit = run_local_audit()
    
    actions_taken = []
    
    # Scan for suspicious ports
    for finding in scan_open_ports():
        port = finding.get("port")
        if port in [4444, 1337]:  # Critical risks
            actions_taken.append(f"⚠️ CRITICAL: Port {port} detected - manual investigation required")
    
    # Scan for suspicious processes
    for finding in scan_suspicious_processes():
        if finding.get("severity") == "HIGH":
            if block_mode and finding.get("pid"):
                try:
                    proc = psutil.Process(finding["pid"])
                    proc.terminate()
                    actions_taken.append(f"Terminated suspicious process: {finding['name']}")
                except:
                    actions_taken.append(f"Could not terminate: {finding['name']}")
            else:
                actions_taken.append(f"Alert: Suspicious process {finding['name']} - review recommended")
    
    if not actions_taken:
        return "🛡️ Environment secure. No threats detected."
    
    return "\n".join(actions_taken)


def get_network_defense_status() -> Dict:
    """
    Get network defense status.
    
    Returns:
        Status dictionary
    """
    return {
        "local_ip": get_local_ip(),
        "public_ip": get_public_ip(),
        "risky_ports": RISKY_PORTS,
        "suspicious_patterns": SUSPICIOUS_PATTERNS,
        "last_audit": run_local_audit(),
    }


# === DISPATCHER ===

def cyber_sentinel(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for Cyber Sentinel tools.
    """
    params = parameters or {}
    action = params.get("action", "audit").lower().strip()
    
    if player:
        player.write_log(f"[CyberSentinel] {action}")
    
    try:
        if action == "audit":
            audit = run_local_audit()
            return generate_audit_report(audit)
        
        elif action == "secure":
            block = params.get("block", False)
            return secure_local_env(block)
        
        elif action == "ports":
            findings = scan_open_ports()
            if not findings:
                return "No suspicious ports detected."
            
            lines = ["Suspicious Ports:"]
            for f in findings:
                lines.append(f"  • Port {f['port']} - {f['process']} ({f['severity']})")
            return "\n".join(lines)
        
        elif action == "processes":
            findings = scan_suspicious_processes()
            if not findings:
                return "No suspicious processes detected."
            
            lines = ["Suspicious Processes:"]
            for f in findings:
                lines.append(f"  • {f['name']} (PID: {f['pid']}) - {f.get('pattern', f.get('issue'))}")
            return "\n".join(lines)
        
        elif action == "network":
            connections = check_network_connections()
            lines = ["Active Network Connections:"]
            for c in connections[:10]:
                lines.append(f"  • {c.get('local')} -> {c.get('remote')} ({c.get('status')})")
            return "\n".join(lines)
        
        elif action == "resources":
            res = check_system_resources()
            return (f"System Resources:\n"
                    f"  CPU: {res['cpu_percent']}%\n"
                    f"  Memory: {res['memory_percent']}%\n"
                    f"  Disk: {res['disk_percent']}%")
        
        elif action == "status":
            status = get_network_defense_status()
            return (f"🛡️ Cyber Sentinel Status:\n"
                    f"  Local IP: {status['local_ip']}\n"
                    f"  Public IP: {status['public_ip']}\n"
                    f"  Monitoring: {len(status['risky_ports'])} risky ports")
        
        else:
            return f"Unknown action: {action}. Available: audit, secure, ports, processes, network, resources, status"
    
    except Exception as e:
        return f"CyberSentinel error: {str(e)}"


if __name__ == "__main__":
    # Test Cyber Sentinel
    print("=== Cyber Sentinel Test ===")
    
    # Run audit
    audit = run_local_audit()
    print(f"Vulnerabilities: {len(audit['vulnerabilities'])}")
    print(f"Suspicious Processes: {len(audit['suspicious_processes'])}")
    
    print("\n✅ Cyber Sentinel ready")
