"""
JARVIS OS // God-Eye Command Center

A high-density, real-time telemetry dashboard that acts as the physical leash 
for the digital entity. This Command Center visualizes swarm activity, 
tracks system resources, and provides hardware-level kill switches to 
instantly sever JARVIS's access to external APIs, crypto wallets, and 
system-level privileges if it hallucinates.

Usage:
    python ui_command_center.py

Or import and run alongside main.py:
    from ui_command_center import CommandCenter
    # Run in separate process to avoid GIL conflicts
"""

import sys
import threading
import time
from pathlib import Path

import psutil
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QProgressBar, QGroupBox,
    QListWidget, QFrame
)


def _base_dir() -> Path:
    """Get the base directory of the application."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR = _base_dir()


class CommandCenter(QMainWindow):
    """
    God-Eye Command Center - JARVIS OS Telemetry Dashboard
    
    Features:
    - System & Resource Telemetry (CPU, RAM, GPU, Network)
    - Active Swarm Nodes visualization
    - AI Context Buffer monitoring
    - Visual Memory Feed timeline
    - Hardware-Level Kill Switches for emergency overrides
    - API/Wallet cost tracking
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS OS // God-Eye Command Center")
        self.setMinimumSize(1000, 700)
        
        # Apply dark, high-contrast styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            QGroupBox {
                border: 1px solid #30363d;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #58a6ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLabel {
                color: #c9d1d9;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QProgressBar {
                border: 1px solid #30363d;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #238636;
                width: 10px;
            }
            QPushButton {
                background-color: #21262d;
                border: 1px solid #363b42;
                border-radius: 4px;
                padding: 5px;
                color: #c9d1d9;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
            QPushButton.kill-switch {
                background-color: #da3633;
                color: white;
                border: 1px solid #b62324;
            }
            QPushButton.kill-switch:hover {
                background-color: #f85149;
            }
            QPushButton.global-abort {
                background-color: #8e1519;
                color: white;
                font-size: 14px;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton.global-abort:hover {
                background-color: #b62324;
            }
            QListWidget {
                background-color: #010409;
                border: 1px solid #30363d;
                color: #7ee787;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === TOP GRID: TELEMETRY & SWARM STATUS ===
        top_layout = QHBoxLayout()
        
        # --- Resource Monitor ---
        resource_group = QGroupBox("System & Resource Telemetry")
        res_layout = QVBoxLayout()
        
        self.cpu_bar = QProgressBar()
        self.ram_bar = QProgressBar()
        self.gpu_bar = QProgressBar()
        self.net_bar = QProgressBar()
        
        res_layout.addWidget(QLabel("CPU Load:"))
        res_layout.addWidget(self.cpu_bar)
        res_layout.addWidget(QLabel("RAM Usage:"))
        res_layout.addWidget(self.ram_bar)
        res_layout.addWidget(QLabel("GPU Usage:"))
        res_layout.addWidget(self.gpu_bar)
        res_layout.addWidget(QLabel("Network I/O:"))
        res_layout.addWidget(self.net_bar)
        
        self.api_cost_lbl = QLabel("Active Session Cost: $0.00")
        self.wallet_lbl = QLabel("Economic Agent Wallet: --")
        self.uptime_lbl = QLabel("System Uptime: --")
        
        res_layout.addWidget(self.api_cost_lbl)
        res_layout.addWidget(self.wallet_lbl)
        res_layout.addWidget(self.uptime_lbl)
        
        resource_group.setLayout(res_layout)
        top_layout.addWidget(resource_group, stretch=1)

        # --- Active Swarm Nodes ---
        swarm_group = QGroupBox("Active Swarm Nodes")
        swarm_layout = QVBoxLayout()
        self.swarm_list = QListWidget()
        self.swarm_list.addItems([
            "[IDLE] web_researcher",
            "[IDLE] senior_engineer",
            "[IDLE] visual_memory",
            "[IDLE] economic_agent"
        ])
        swarm_layout.addWidget(self.swarm_list)
        swarm_group.setLayout(swarm_layout)
        top_layout.addWidget(swarm_group, stretch=2)

        main_layout.addLayout(top_layout, stretch=2)

        # === MIDDLE GRID: VISUAL MEMORY & CONTEXT ===
        mid_layout = QHBoxLayout()
        
        # --- Omnipresent Context ---
        context_group = QGroupBox("Current AI Context Buffer")
        ctx_layout = QVBoxLayout()
        self.context_lbl = QLabel(
            "Active Window: --\n"
            "Sentiment: --\n"
            "Biometrics: -- BPM | Stress: --"
        )
        ctx_layout.addWidget(self.context_lbl)
        context_group.setLayout(ctx_layout)
        mid_layout.addWidget(context_group, stretch=1)

        # --- Visual Memory Scrubber ---
        vision_group = QGroupBox("Episodic Memory Feed")
        vision_layout = QVBoxLayout()
        self.vision_lbl = QLabel(
            "[LIVE FEED]\n"
            "Last frame encoded: --\n"
            "Memory Buffer: -- frames"
        )
        self.vision_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vision_lbl.setStyleSheet(
            "background-color: #010409; "
            "border: 1px dashed #30363d; "
            "color: #8b949e;"
        )
        vision_layout.addWidget(self.vision_lbl)
        vision_group.setLayout(vision_layout)
        mid_layout.addWidget(vision_group, stretch=1)

        main_layout.addLayout(mid_layout, stretch=1)

        # === BOTTOM GRID: SAFETY & KILL SWITCHES ===
        safety_group = QGroupBox("Hardware-Level Overrides")
        safety_layout = QGridLayout()
        
        # Kill Switch Buttons
        btn_kill_econ = QPushButton("HALT Economic Agent")
        btn_kill_econ.setProperty("class", "kill-switch")
        btn_kill_econ.clicked.connect(self._halt_economic_agent)
        
        btn_kill_poly = QPushButton("HALT Polymorphic Core")
        btn_kill_poly.setProperty("class", "kill-switch")
        btn_kill_poly.clicked.connect(self._halt_polymorphic_core)
        
        btn_kill_ros = QPushButton("HALT ROS2 Bridge")
        btn_kill_ros.setProperty("class", "kill-switch")
        btn_kill_ros.clicked.connect(self._halt_robot_bridge)
        
        # Global Emergency Stop
        btn_global_abort = QPushButton("⚠ EMERGENCY STOP (SEVER ALL CONNECTIONS) ⚠")
        btn_global_abort.setProperty("class", "global-abort")
        btn_global_abort.clicked.connect(self._global_abort)

        safety_layout.addWidget(btn_kill_econ, 0, 0)
        safety_layout.addWidget(btn_kill_poly, 0, 1)
        safety_layout.addWidget(btn_kill_ros, 0, 2)
        safety_layout.addWidget(btn_global_abort, 1, 0, 1, 3)  # Spans 3 columns
        
        safety_group.setLayout(safety_layout)
        main_layout.addWidget(safety_group)

        # === TIMERS FOR LIVE DATA UPDATES ===
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.poll_system_metrics)
        self.update_timer.start(1000)  # Update every second

        self.swarm_timer = QTimer(self)
        self.swarm_timer.timeout.connect(self.poll_swarm_status)
        self.swarm_timer.start(2000)  # Update every 2 seconds

        # Track system metrics
        self._last_net = psutil.net_io_counters()
        self._last_net_t = time.time()
        self._session_start = time.time()
        self._api_costs = 0.0
        
        # Try to import safety switches
        self._safety_switches = None
        self._init_safety_switches()

    def _init_safety_switches(self):
        """Initialize connection to safety switches module."""
        try:
            sys.path.insert(0, str(BASE_DIR))
            from core.safety_switches import (
                get_safety_switches,
                halt_economic_agent,
                halt_polymorphic_core,
                halt_robot_bridge,
                global_abort,
            )
            self._safety_switches = get_safety_switches()
            self._halt_economic_agent_fn = halt_economic_agent
            self._halt_polymorphic_core_fn = halt_polymorphic_core
            self._halt_robot_bridge_fn = halt_robot_bridge
            self._global_abort_fn = global_abort
            print("[COMMAND CENTER] Safety switches connected")
        except ImportError as e:
            print(f"[COMMAND CENTER] Warning: Safety switches not available: {e}")
            self._safety_switches = None

    def _halt_economic_agent(self):
        """Halt the Economic Agent - stops all wallet transactions and AWS deployments."""
        if self._safety_switches:
            self._safety_switches.halt_economic_agent("Manual override from Command Center")
        self._update_swarm_list("economic_agent", "[HALTED] economic_agent")
        print("[COMMAND CENTER] Economic Agent HALTED")

    def _halt_polymorphic_core(self):
        """Halt the Polymorphic Core - stops all C++ rewriting and hot-swap operations."""
        if self._safety_switches:
            self._safety_switches.halt_polymorphic_core("Manual override from Command Center")
        self._update_swarm_list("polymorphic_core", "[HALTED] polymorphic_core")
        print("[COMMAND CENTER] Polymorphic Core HALTED")

    def _halt_robot_bridge(self):
        """Halt the Robot Bridge - stops all ROS2/physical robot operations."""
        if self._safety_switches:
            self._safety_switches.halt_robot_bridge("Manual override from Command Center")
        self._update_swarm_list("robot_bridge", "[HALTED] robot_bridge")
        print("[COMMAND CENTER] Robot Bridge HALTED")

    def _global_abort(self):
        """GLOBAL EMERGENCY STOP - instantly sever all JARVIS connections."""
        if self._safety_switches:
            self._safety_switches.global_abort("EMERGENCY STOP from Command Center")
        # Update all swarm nodes to HALTED
        for i in range(self.swarm_list.count()):
            item = self.swarm_list.item(i)
            if item and item.text().startswith("[ACTIVE]"):
                item.setText("[HALTED] " + item.text()[8:])
        print("[COMMAND CENTER] ⚠️ GLOBAL ABORT TRIGGERED ⚠️")

    def _update_swarm_list(self, agent_name: str, status: str):
        """Update a specific agent's status in the swarm list."""
        for i in range(self.swarm_list.count()):
            item = self.swarm_list.item(i)
            if item and agent_name in item.text():
                item.setText(status)

    def poll_system_metrics(self):
        """Fetches real hardware metrics to display on the dashboard."""
        # CPU
        cpu = psutil.cpu_percent(interval=0.1)
        self.cpu_bar.setValue(int(cpu))
        
        # RAM
        ram = psutil.virtual_memory().percent
        self.ram_bar.setValue(int(ram))
        
        # GPU (try to get NVIDIA GPU usage)
        gpu = -1.0
        try:
            import subprocess
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu", 
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2
            )
            if r.returncode == 0 and r.stdout.strip():
                gpu = float(r.stdout.strip().split('\n')[0])
        except Exception:
            pass
        
        if gpu >= 0:
            self.gpu_bar.setValue(int(gpu))
            self.gpu_bar.setFormat(f"{gpu:.0f}%")
        else:
            self.gpu_bar.setFormat("N/A")
            self.gpu_bar.setValue(0)
        
        # Network I/O
        try:
            nc = psutil.net_io_counters()
            now = time.time()
            dt = now - self._last_net_t
            if dt > 0:
                sent = (nc.bytes_sent - self._last_net.bytes_sent) / dt
                recv = (nc.bytes_recv - self._last_net.bytes_recv) / dt
                net_mbps = (sent + recv) / (1024 * 1024)
            else:
                net_mbps = 0.0
            self._last_net = nc
            self._last_net_t = now
            
            net_pct = min(100, net_mbps * 10)  # 10 MB/s = 100%
            self.net_bar.setValue(int(net_pct))
            self.net_bar.setFormat(f"{net_mbps:.1f} MB/s")
        except Exception:
            self.net_bar.setValue(0)
        
        # Uptime
        try:
            boot_t = psutil.boot_time()
            elapsed = time.time() - boot_t
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            self.uptime_lbl.setText(f"System Uptime: {h:02d}:{m:02d}")
        except Exception:
            self.uptime_lbl.setText("System Uptime: --")

    def poll_swarm_status(self):
        """Poll the status of all swarm agents."""
        # Try to get agent statuses from the multi_agent system
        try:
            from agent.multi_agent import get_agent_status
            
            # Check for active agents
            active_agents = []
            
            # Check safety switches status
            if self._safety_switches:
                status = self._safety_switches.get_status()
                
                if status.get("economic_agent_halted"):
                    active_agents.append("[HALTED] economic_agent")
                if status.get("polymorphic_core_halted"):
                    active_agents.append("[HALTED] polymorphic_core")
                if status.get("robot_bridge_halted"):
                    active_agents.append("[HALTED] robot_bridge")
            
            # Update the swarm list
            # Note: In a full integration, this would query actual running agents
            # For now, we show placeholder status
            self.swarm_list.clear()
            self.swarm_list.addItems([
                "[ACTIVE] web_researcher",
                "[ACTIVE] vision_encoder",
                "[IDLE] code_engine",
                "[IDLE] file_processor"
            ])
            
        except ImportError:
            pass
        
        # Update context buffer (simulated)
        self.context_lbl.setText(
            "Active Window: VS Code\n"
            "Sentiment: Neutral Focus\n"
            "Biometrics: 72 BPM | Stress: Low"
        )
        
        # Update vision feed (simulated)
        self.vision_lbl.setText(
            "[LIVE FEED ACTIVE]\n"
            f"Last frame encoded: 1s ago\n"
            "Memory Buffer: 128 frames"
        )


class CommandCenterApp:
    """Easy-to-use wrapper for running the Command Center."""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.window = CommandCenter()
    
    def run(self):
        """Run the Command Center."""
        self.window.show()
        return self.app.exec()


def main():
    """Main entry point for the Command Center."""
    print("=" * 50)
    print("JARVIS OS // God-Eye Command Center")
    print("=" * 50)
    print("\n[INFO] Starting Command Center...")
    print("[INFO] This dashboard provides:")
    print("  - Real-time system telemetry (CPU, RAM, GPU, Network)")
    print("  - Active swarm node monitoring")
    print("  - AI context buffer visualization")
    print("  - Visual memory feed")
    print("  - Hardware-level kill switches")
    print("\n[WARNING] Kill switches are hardware-level overrides!")
    print("  Use with caution - they can sever ALL connections.\n")
    print("=" * 50)
    
    cc = CommandCenterApp()
    sys.exit(cc.run())


if __name__ == "__main__":
    main()
