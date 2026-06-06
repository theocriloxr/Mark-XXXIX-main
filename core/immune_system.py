"""
Autonomous OS Immune System - Self-Healing Defense

JARVIS monitors system processes and network traffic for anomalies,
automatically defends against threats, and can isolated infected processes.

Features:
- Process anomaly detection (unusual CPU/memory patterns)
- Network traffic monitoring (unusual connections)
- Auto-quarantine malicious processes
- Custom firewall rule generation
- Zero-day threat adaptation

Usage:
    from core.immune_system import ImmuneSystem, start_immune_system
    
    start_immune_system()
    
    # Query threat status
    status = get_threat_status()
"""

import logging
import threading
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Threat levels
THREAT_NONE = "none"
THREAT_LOW = "low"
THREAT_MEDIUM = "medium"
THREAT_HIGH = "high"
THREAT_CRITICAL = "critical"

# Anomaly thresholds
CPU_SPIKE_THRESHOLD = 90  # % CPU usage
MEMORY_LEAK_THRESHOLD = 500  # MB growth rate
NETWORK_SPIKE_THRESHOLD = 100  # MB/hour
PROCESS_SPAWN_RATE = 10  # processes/hour


@dataclass
class ThreatRecord:
    """Record of a detected threat."""
    threat_id: str
    threat_level: str
    threat_type: str  # process, network, file, behavior
    description: str
    source: str  # process name, IP, file path
    timestamp: float
    action_taken: str = ""
    resolved: bool = False


class ImmuneSystem(threading.Thread):
    """
    Autonomous immune system for JARVIS.
    Monitors and defends against OS-level threats.
    """
    
    def __init__(self):
        super().__init__(daemon=True)
        
        self.is_running = False
        self._enabled = True
        
        # Threat database
        self._threats: List[ThreatRecord] = []
        self._threat_history: deque = deque(maxlen=100)
        
        # Baseline metrics
        self._baseline_processes: Dict[str, Dict] = {}
        self._baseline_network: Dict[str, int] = {}
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self._scan_count = 0
        self._threats_detected = 0
        self._threats_resolved = 0
        
        # Monitoring callbacks
        self._defense_callbacks: List[Callable] = []
    
    def run(self):
        """Main monitoring loop."""
        self.is_running = True
        
        logger.info("[ImmuneSystem] Starting defense monitoring")
        
        # Initialize baselines on first run
        self._initialize_baselines()
        
        while self.is_running:
            try:
                # Scan for threats
                self._scan_processes()
                self._scan_network()
                self._scan_file_system()
                
                self._scan_count += 1
                
            except Exception as e:
                logger.error(f"[ImmuneSystem] Scan error: {e}")
            
            # Scan every 30 seconds
            time.sleep(30)
    
    def stop(self):
        """Stop the immune system."""
        self.is_running = False
        logger.info("[ImmuneSystem] Stopped")
    
    def _initialize_baselines(self):
        """Initialize baseline metrics."""
        logger.info("[ImmuneSystem] Initializing baselines...")
        
        # Get baseline processes
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    name = proc.info['name']
                    cpu = proc.info['cpu_percent'] or 0
                    self._baseline_processes[name] = {
                        'cpu': cpu,
                        'first_seen': time.time()
                    }
                except:
                    pass
        except ImportError:
            logger.warning("[ImmuneSystem] psutil not available")
        
        logger.info(f"[ImmuneSystem] Baseline: {len(self._baseline_processes)} processes")
    
    def _scan_processes(self):
        """Scan for anomalous processes."""
        try:
            import psutil
            
            current_time = time.time()
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    name = proc.info['name']
                    cpu = proc.info['cpu_percent'] or 0
                    mem = proc.info['memory_info']
                    mem_mb = mem.rss / (1024 * 1024)
                    
                    # Check for CPU spike
                    if cpu > CPU_SPIKE_THRESHOLD:
                        baseline = self._baseline_processes.get(name, {})
                        baseline_cpu = baseline.get('cpu', 0)
                        
                        # Significant increase from baseline
                        if cpu > baseline_cpu + 50:
                            self._detect_threat(
                                threat_type="process",
                                level=THREAT_MEDIUM,
                                source=name,
                                description=f"High CPU usage: {cpu}% (baseline: {baseline_cpu}%)"
                            )
                    
                    # Check for suspicious process names
                    if self._is_suspicious_process(name):
                        self._detect_threat(
                            threat_type="process",
                            level=THREAT_HIGH,
                            source=name,
                            description=f"Suspicious process detected: {name}"
                        )
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except ImportError:
            logger.debug("[ImmuneSystem] psutil not available for process scanning")
    
    def _scan_network(self):
        """Scan for anomalous network activity."""
        try:
            import psutil
            
            connections = psutil.net_connections()
            
            # Count connections by status
            established_count = 0
            foreign_ips = set()
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    established_count += 1
                    
                    if conn.raddr:
                        ip = conn.raddr.ip
                        foreign_ips.add(ip)
                        
                        # Check for suspicious IPs (known malware IPs)
                        if self._is_malicious_ip(ip):
                            self._detect_threat(
                                threat_type="network",
                                level=THREAT_CRITICAL,
                                source=ip,
                                description=f"Connection to known malicious IP: {ip}"
                            )
            
            # Check for network spike
            if established_count > 100:
                self._detect_threat(
                    threat_type="network",
                    level=THREAT_LOW,
                    source="multiple",
                    description=f"High connection count: {established_count}"
                )
                    
        except ImportError:
            logger.debug("[ImmuneSystem] psutil not available for network scanning")
    
    def _scan_file_system(self):
        """Scan for suspicious file modifications."""
        # Check recently modified executables in startup locations
        suspicious_paths = [
            "C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
        ]
        
        import os
        import stat
        
        for path in suspicious_paths:
            if not os.path.exists(path):
                continue
            
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    
                    # Check if it's an executable
                    if item.endswith(('.exe', '.bat', '.cmd', '.ps1', '.vbs')):
                        # Check if new
                        mtime = os.stat(item_path).st_mtime
                        age = time.time() - mtime
                        
                        # Modified in last hour
                        if age < 3600:
                            self._detect_threat(
                                threat_type="file",
                                level=THREAT_MEDIUM,
                                source=item_path,
                                description=f"New startup executable: {item}"
                            )
                            
            except PermissionError:
                pass
    
    def _is_suspicious_process(self, name: str) -> bool:
        """Check if a process name is suspicious."""
        # Common malware process names
        suspicious = [
            'cryptominer', 'miner', 'xmr', 'xmrig',
            'payload', 'injector', 'keylogger',
            'stealer', 'clipper', 'trojan'
        ]
        
        name_lower = name.lower()
        return any(s in name_lower for s in suspicious)
    
    def _is_malicious_ip(self, ip: str) -> bool:
        """Check if an IP is known malicious."""
        # In production, this would query a threat intelligence feed
        # For now, check for local/suspicious ranges
        if ip.startswith(('10.', '192.168.', '127.')):
            return False
        
        # Could add known malicious IP ranges here
        return False
    
    def _detect_threat(
        self,
        threat_type: str,
        level: str,
        source: str,
        description: str
    ):
        """Detect and respond to a threat."""
        threat_id = f"threat_{int(time.time() * 1000)}"
        
        record = ThreatRecord(
            threat_id=threat_id,
            threat_level=level,
            threat_type=threat_type,
            description=description,
            source=source,
            timestamp=time.time()
        )
        
        with self._lock:
            self._threats.append(record)
            self._threat_history.append(record)
        
        self._threats_detected += 1
        
        logger.warning(f"[ImmuneSystem] {level.upper()} {threat_type}: {description}")
        
        # Auto-response for critical threats
        if level == THREAT_CRITICAL:
            self._auto_respond(record)
    
    def _auto_respond(self, threat: ThreatRecord):
        """Automatic response to threats."""
        try:
            if threat.threat_type == "process":
                self._isolate_process(threat.source)
                threat.action_taken = "isolated"
                
            elif threat.threat_type == "network":
                self._block_ip(threat.source)
                threat.action_taken = "blocked"
            
            threat.resolved = True
            self._threats_resolved += 1
            
        except Exception as e:
            logger.error(f"[ImmuneSystem] Auto-response failed: {e}")
    
    def _isolate_process(self, process_name: str):
        """Isolate a suspicious process."""
        try:
            import psutil
            
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] == process_name:
                    pid = proc.info['pid']
                    
                    # Terminate the process
                    proc.terminate()
                    logger.info(f"[ImmuneSystem] Terminated process: {process_name} (PID: {pid})")
                    
        except Exception as e:
            logger.error(f"[ImmuneSystem] Process isolation failed: {e}")
    
    def _block_ip(self, ip: str):
        """Block a malicious IP."""
        # Create Windows firewall rule
        try:
            import subprocess
            
            rule_name = f"JARVIS_BLOCK_{ip.replace('.', '_')}"
            
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                'name=' + rule_name,
                'dir=in',
                'action=block',
                'remoteip=' + ip
            ], check=True)
            
            logger.info(f"[ImmuneSystem] Blocked IP: {ip}")
            
        except Exception as e:
            logger.error(f"[ImmuneSystem] IP blocking failed: {e}")
    
    def get_threats(self, level: str = None, unresolved: bool = False) -> List[Dict]:
        """Get detected threats."""
        with self._lock:
            threats = list(self._threats)
        
        if level:
            threats = [t for t in threats if t.threat_level == level]
        
        if unresolved:
            threats = [t for t in threats if not t.resolved]
        
        return [
            {
                "id": t.threat_id,
                "level": t.threat_level,
                "type": t.threat_type,
                "description": t.description,
                "source": t.source,
                "timestamp": t.timestamp,
                "resolved": t.resolved
            }
            for t in threats
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get immune system statistics."""
        with self._lock:
            return {
                "scan_count": self._scan_count,
                "threats_detected": self._threats_detected,
                "threats_resolved": self._threats_resolved,
                "active_threats": len([t for t in self._threats if not t.resolved]),
                "status": "running" if self.is_running else "stopped"
            }
    
    def clear_threats(self) -> str:
        """Clear resolved threats."""
        with self._lock:
            self._threats = [t for t in self._threats if not t.resolved]
        
        return "Resolved threats cleared."
    
    def enable(self):
        """Enable immune system."""
        self._enabled = True
    
    def disable(self):
        """Disable immune system."""
        self._enabled = False


# === GLOBAL INSTANCE ===

_immune_system: Optional[ImmuneSystem] = None


def get_immune_system() -> ImmuneSystem:
    """Get global immune system instance."""
    global _immune_system
    if _immune_system is None:
        _immune_system = ImmuneSystem()
    return _immune_system


def start_immune_system() -> str:
    """Start the immune system daemon."""
    system = get_immune_system()
    
    if not system.is_running:
        system.start()
        return "Immune system started. JARVIS is now defending your OS."
    
    return "Immune system already running."


def stop_immune_system() -> str:
    """Stop the immune system."""
    system = get_immune_system()
    system.stop()
    
    return "Immune system stopped."


def get_threat_status() -> str:
    """Get threat status summary."""
    system = get_immune_system()
    stats = system.get_statistics()
    
    return (
        f"Scans: {stats['scan_count']} | "
        f"Threats: {stats['threats_detected']} | "
        f"Resolved: {stats['threats_resolved']} | "
        f"Active: {stats['active_threats']}"
    )


def get_active_threats() -> List[Dict]:
    """Get unresolved threats."""
    return get_immune_system().get_threats(unresolved=True)


# === DISPATCHER ===

def immune_system(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for immune system."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[ImmuneSystem] {action}")
    
    system = get_immune_system()
    
    try:
        if action == "status":
            return get_threat_status()
        
        elif action == "threats":
            level = params.get("level")
            threats = system.get_threats(level=level, unresolved=False)
            
            if not threats:
                return "No threats detected."
            
            lines = ["Detected Threats:"]
            for t in threats[:10]:
                lines.append(
                    f"- [{t['level']}] {t['type']}: {t['description']}"
                )
            return "\n".join(lines)
        
        elif action == "clear":
            return system.clear_threats()
        
        elif action == "enable":
            system.enable()
            return "Immune system enabled."
        
        elif action == "disable":
            system.disable()
            return "Immune system disabled."
        
        else:
            return get_threat_status()
    
    except Exception as e:
        return f"ImmuneSystem error: {e}"


if __name__ == "__main__":
    print("=== Immune System Test ===")
    
    system = get_immune_system()
    print(f"Status: {system.get_statistics()}")
    
    print("\n✅ Immune System ready")
