"""
Synapse-Sync - P2P Memory Sharing

Enables JARVIS to share memory across multiple devices:
- UDP/TCP listener for memory sync
- Broadcast new memories to peer devices
- Requires Tailscale VPN or same network

Usage:
    from core.synapse_sync import SynapseSync, start_synapse_sync
    
    # Add peer devices (Tailscale IPs)
    synapse = SynapseSync(peer_ips=["100.x.y.z", "100.a.b.c"])
    synapse.start()
    
    # Broadcast memory
    synapse.broadcast_memory("User prefers dark mode")
"""

import json
import logging
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Get base directory
def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


# === SYNAPSE SYNC CLASS ===

class SynapseSync(threading.Thread):
    """
    P2P Memory Sync Daemon.
    Runs as background thread, syncing memories across devices.
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5555,
        peer_ips: List[str] = None
    ):
        """
        Initialize Synapse-Sync.
        
        Args:
            host: Local bind address
            port: Local listen port
            peer_ips: List of peer device IPs (e.g., Tailscale IPs)
        """
        super().__init__(daemon=True)
        
        self.host = host
        self.port = port
        self.peer_ips = peer_ips or []
        
        self.is_running = False
        self.socket = None
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.last_sync = 0
        
        # Lock
        self._lock = threading.Lock()
        
        logger.info(f"[SYNAPSE] Initialized on port {self.port}")
    
    def run(self):
        """Background listener for incoming memories."""
        self.is_running = True
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            
            logger.info(f"[SYNAPSE] Listening on {self.host}:{self.port}")
            
            while self.is_running:
                try:
                    data, addr = self.socket.recvfrom(65535)
                    
                    # Validate source
                    if addr[0] not in self.peer_ips:
                        logger.debug(f"[SYNAPSE] Ignoring unauthorized: {addr[0]}")
                        continue
                    
                    # Process memory
                    payload = json.loads(data.decode("utf-8"))
                    self._process_incoming_memory(payload)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.debug(f"[SYNAPSE] Recv error: {e}")
                    
        except Exception as e:
            logger.error(f"[SYNAPSE] Listener error: {e}")
        finally:
            self.is_running = False
            if self.socket:
                self.socket.close()
    
    def stop(self):
        """Stop the sync daemon."""
        self.is_running = False
        if self.socket:
            self.socket.close()
        logger.info("[SYNAPSE] Stopped")
    
    def _process_incoming_memory(self, payload: Dict[str, Any]):
        """
        Process incoming memory from peer.
        
        Args:
            payload: Memory payload dict
        """
        try:
            source_device = payload.get("source_device", "unknown")
            memory_text = payload.get("text", "")
            timestamp = payload.get("timestamp", 0)
            
            if not memory_text:
                return
            
            with self._lock:
                self.messages_received += 1
                self.last_sync = time.time()
            
            # TODO: Inject into local ChromaDB
            # This connects to existing memory infrastructure
            logger.info(f"[SYNAPSE] Received from {source_device}: {memory_text[:50]}...")
            
            # Import and inject into ChromaDB
            try:
                from core.chroma_memory import chroma_add
                # chroma_add(memory_text, {"source": source_device, "timestamp": timestamp})
            except ImportError:
                pass
            
        except Exception as e:
            logger.error(f"[SYNAPSE] Process error: {e}")
    
    def broadcast_memory(self, memory_text: str, metadata: Dict = None):
        """
        Broadcast memory to all peer devices.
        
        Args:
            memory_text: The memory to sync
            metadata: Additional metadata
        """
        if not self.peer_ips:
            logger.debug("[SYNAPSE] No peers configured")
            return
        
        try:
            payload = {
                "source_device": self._get_device_id(),
                "text": memory_text,
                "timestamp": time.time(),
                "metadata": metadata or {}
            }
            
            data = json.dumps(payload).encode("utf-8")
            
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            for ip in self.peer_ips:
                try:
                    client_sock.sendto(data, (ip, self.port))
                    
                    with self._lock:
                        self.messages_sent += 1
                    
                    logger.debug(f"[SYNAPSE] Synced to {ip}")
                    
                except Exception as e:
                    logger.warning(f"[SYNAPSE] Failed to sync to {ip}: {e}")
            
            client_sock.close()
            
        except Exception as e:
            logger.error(f"[SYNAPSE] Broadcast error: {e}")
    
    def _get_device_id(self) -> str:
        """Get unique device identifier."""
        import platform
        return f"{platform.system()}-{platform.node()}"
    
    def add_peer(self, ip: str):
        """Add a peer device IP."""
        if ip not in self.peer_ips:
            self.peer_ips.append(ip)
            logger.info(f"[SYNAPSE] Added peer: {ip}")
    
    def remove_peer(self, ip: str):
        """Remove a peer device IP."""
        if ip in self.peer_ips:
            self.peer_ips.remove(ip)
            logger.info(f"[SYNAPSE] Removed peer: {ip}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get sync status."""
        with self._lock:
            return {
                "is_running": self.is_running,
                "peer_count": len(self.peer_ips),
                "messages_sent": self.messages_sent,
                "messages_received": self.messages_received,
                "last_sync": self.last_sync
            }


# === GLOBAL INSTANCE ===

_synapse_sync: Optional[SynapseSync] = None


def get_synapse_sync() -> SynapseSync:
    """Get global SynapseSync instance."""
    global _synapse_sync
    if _synapse_sync is None:
        _synapse_sync = SynapseSync()
    return _synapse_sync


def start_synapse_sync(peer_ips: List[str] = None) -> str:
    """Start Synapse-Sync daemon."""
    synapse = get_synapse_sync()
    
    if peer_ips:
        synapse.peer_ips.extend(peer_ips)
    
    if not synapse.is_running:
        synapse.start()
        return f"Synapse-Sync started on port {synapse.port}"
    
    return "Synapse-Sync already running"


def stop_synapse_sync() -> str:
    """Stop Synapse-Sync daemon."""
    synapse = get_synapse_sync()
    synapse.stop()
    return "Synapse-Sync stopped"


def broadcast_memory(memory_text: str, metadata: Dict = None):
    """Broadcast memory to peers."""
    synapse = get_synapse_sync()
    synapse.broadcast_memory(memory_text, metadata)


# === DISPATCHER ===

def synapse_sync(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for Synapse-Sync."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[SynapseSync] {action}")
    
    try:
        synapse = get_synapse_sync()
        
        if action == "start":
            peer_ips_str = params.get("peers", "")
            peer_list = [ip.strip() for ip in peer_ips_str.split(",") if ip.strip()]
            return start_synapse_sync(peer_list)
        
        elif action == "stop":
            return stop_synapse_sync()
        
        elif action == "status":
            status = synapse.get_status()
            return (
                f"Running: {status['is_running']} | "
                f"Peers: {status['peer_count']} | "
                f"Sent: {status['messages_sent']} | "
                f"Recv: {status['messages_received']}"
            )
        
        elif action == "broadcast":
            memory = params.get("memory", "")
            if not memory:
                return "Please provide memory text"
            
            metadata = {
                "category": params.get("category", "general")
            }
            synapse.broadcast_memory(memory, metadata)
            return "Memory broadcasted"
        
        elif action == "add_peer":
            ip = params.get("ip", "")
            if not ip:
                return "Please provide IP address"
            synapse.add_peer(ip)
            return f"Peer added: {ip}"
        
        elif action == "remove_peer":
            ip = params.get("ip", "")
            if not ip:
                return "Please provide IP address"
            synapse.remove_peer(ip)
            return f"Peer removed: {ip}"
        
        elif action == "peers":
            peers = synapse.peer_ips
            if peers:
                return "Peers: " + ", ".join(peers)
            return "No peers configured"
        
        else:
            status = synapse.get_status()
            return f"Synapse-Sync: {status['is_running']}"
    
    except Exception as e:
        return f"SynapseSync error: {e}"


if __name__ == "__main__":
    print("=== Synapse-Sync Test ===")
    
    # Create with test peers
    synapse = SynapseSync(peer_ips=["100.64.1.1", "100.64.1.2"])
    
    print(f"Peers: {synapse.peer_ips}")
    print(f"Device: {synapse._get_device_id()}")
    
    # Test broadcast (won't actually send without real peers)
    # synapse.broadcast_memory("Test memory", {"category": "test"})
    
    print("\n✅ Synapse-Sync ready")
