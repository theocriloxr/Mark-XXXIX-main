"""
Smart Home - Local Environmental Control (IoT Syncing)

JARVIS controls your physical environment to match your digital workflow.
Detects workflow context and automates lights, scenes, and notifications.

Workflow Automation:
- Deep Work (VS Code + Terminal): Dim lights, desk lamp on, notifications pause
- Meeting (Video calling): Quiet room, optimal lighting
- Relax (Media apps): Ambient lighting, mood setting
- Away: All off

Supported Integrations:
- Philips Hue Bridge
- Home Assistant API
- Generic MQTT

Usage:
    from actions.smart_home import SmartHome, execute_automation
    
    # Execute automation
    result = execute_automation("deep_work")
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# Workflow contexts and their automations
WORKFLOW_AUTOMATIONS = {
    "deep_work": {
        "description": "Deep coding work",
        "lights": {"scene": "concentrate", "brightness": 80},
        "desk_lamp": "on",
        "notifications": "dnd",
        "apps": ["vscode", "terminal"]
    },
    "meeting": {
        "description": "Video conference",
        "lights": {"scene": "relax", "brightness": 50},
        "desk_lamp": "on",
        "notifications": "silent",
        "apps": ["zoom", "teams", "slack"]
    },
    "relax": {
        "description": "Relaxing",
        "lights": {"scene": "movie", "brightness": 20},
        "desk_lamp": "off",
        "notifications": "normal",
        "apps": ["spotify", "netflix"]
    },
    "away": {
        "description": "Away from desk",
        "lights": {"scene": "all_off"},
        "desk_lamp": "off",
        "notifications": "normal",
        "apps": []
    },
    "presentation": {
        "description": "Giving a presentation",
        "lights": {"scene": "presentation", "brightness": 100},
        "desk_lamp": "off",
        "notifications": "silent",
        "apps": ["powerpoint", "keynote"]
    }
}


class SmartHome:
    """
    Smart home controller with workflow automation.
    """
    
    def __init__(self):
        self._enabled = False
        self._current_workflow = "normal"
        self._lock = threading.Lock()
        
        # Integration types
        self._hue_bridge = None
        self._home_assistant = None
        self._mqtt_client = None
        
        # Configuration
        self._config = self._load_config()
        
        # Initialize integrations
        self._init_integrations()
    
    def _load_config(self) -> dict:
        """Load smart home configuration."""
        config_path = BASE_DIR / "config" / "smart_home.json"
        
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Smart home config load failed: {e}")
        
        return {
            "enabled": False,
            "integration": "none",  # hue, home_assistant, mqtt
            "hue_ip": "",
            "hue_api_key": "",
            "ha_url": "",
            "ha_token": "",
            "mqtt_broker": "",
            "mqtt_port": 1883
        }
    
    def _init_integrations(self):
        """Initialize smart home integrations."""
        config = self._config
        
        if config.get("integration") == "hue":
            self._init_hue()
        elif config.get("integration") == "home_assistant":
            self._init_home_assistant()
        elif config.get("integration") == "mqtt":
            self._init_mqtt()
    
    def _init_hue(self):
        """Initialize Philips Hue bridge."""
        try:
            from phue import Bridge
            
            ip = self._config.get("hue_ip", "")
            api_key = self._config.get("hue_api_key", "")
            
            if ip and api_key:
                self._hue_bridge = Bridge(ip, api_key)
                logger.info("[SmartHome] Hue bridge connected")
        except Exception as e:
            logger.error(f"[SmartHome] Hue init failed: {e}")
    
    def _init_home_assistant(self):
        """Initialize Home Assistant API."""
        # Store config for later API calls
        self._home_assistant = {
            "url": self._config.get("ha_url", ""),
            "token": self._config.get("ha_token", "")
        }
        logger.info("[SmartHome] Home Assistant configured")
    
    def _init_mqtt(self):
        """Initialize MQTT client."""
        try:
            import paho.mqtt.client as mqtt
            
            broker = self._config.get("mqtt_broker", "localhost")
            port = self._config.get("mqtt_port", 1883)
            
            self._mqtt_client = mqtt.Client()
            self._mqtt_client.connect(broker, port, 60)
            self._mqtt_client.loop_start()
            
            logger.info(f"[SmartHome] MQTT connected to {broker}")
        except Exception as e:
            logger.error(f"[SmartHome] MQTT init failed: {e}")
    
    def set_workflow(self, workflow: str) -> str:
        """
        Set workflow context and apply automation.
        
        Args:
            workflow: Workflow name (deep_work, meeting, relax, away)
            
        Returns:
            str: Result message
        """
        if workflow not in WORKFLOW_AUTOMATIONS:
            return f"Unknown workflow: {workflow}"
        
        automation = WORKFLOW_AUTOMATIONS[workflow]
        
        with self._lock:
            self._current_workflow = workflow
        
        # Apply automation
        try:
            # Lights
            if "lights" in automation:
                self._set_lights(automation["lights"])
            
            # Desk lamp
            if "desk_lamp" in automation:
                self._set_desk_lamp(automation["desk_lamp"])
            
            # Notifications
            if "notifications" in automation:
                self._set_notifications(automation["notifications"])
            
            logger.info(f"[SmartHome] Workflow set: {workflow}")
            return f"Workflow set to: {workflow} - {automation['description']}"
            
        except Exception as e:
            logger.error(f"[SmartHome] Workflow failed: {e}")
            return f"Workflow automation failed: {e}"
    
    def _set_lights(self, config: dict):
        """Set lights based on scene."""
        if self._hue_bridge:
            self._hue_set_scene(config)
        elif self._home_assistant:
            self._ha_set_lights(config)
        elif self._mqtt_client:
            self._mqtt_publish("jarvis/lights", config)
    
    def _hue_set_scene(self, config: dict):
        """Set Hue scene."""
        try:
            scene = config.get("scene", "normal")
            brightness = config.get("brightness", 100)
            
            # In production, map scene names to Hue scene names
            self._hue_bridge.set_light(1, {"bri": int(brightness * 2.54)})
        except Exception as e:
            logger.error(f"[SmartHome] Hue set failed: {e}")
    
    def _ha_set_lights(self, config: dict):
        """Set Home Assistant lights."""
        try:
            import requests
            
            url = f"{self._home_assistant['url']}/api/services/light/turn_on"
            headers = {
                "Authorization": f"Token {self._home_assistant['token']}",
                "Content-Type": "application/json"
            }
            
            brightness = config.get("brightness", 100)
            data = {"brightness_pct": brightness}
            
            requests.post(url, json=data, headers=headers, timeout=5)
        except Exception as e:
            logger.error(f"[SmartHome] HA set failed: {e}")
    
    def _mqtt_publish(self, topic: str, payload: dict):
        """Publish to MQTT."""
        try:
            if self._mqtt_client:
                self._mqtt_client.publish(topic, json.dumps(payload))
        except Exception as e:
            logger.error(f"[SmartHome] MQTT publish failed: {e}")
    
    def _set_desk_lamp(self, state: str):
        """Set desk lamp."""
        if state == "on":
            self._set_single_light(2, True)
        elif state == "off":
            self._set_single_light(2, False)
    
    def _set_single_light(self, light_id: int, on: bool):
        """Set a single light."""
        if self._hue_bridge:
            self._hue_bridge.set_light(light_id, {"on": on})
        elif self._home_assistant:
            try:
                import requests
                
                url = f"{self._home_assistant['url']}/api/services/light/turn_{'on' if on else 'off'}"
                headers = {
                    "Authorization": f"Token {self._home_assistant['token']}",
                    "Content-Type": "application/json"
                }
                data = {"entity_id": f"light.desk_lamp_{light_id}"}
                
                requests.post(url, json=data, headers=headers, timeout=5)
            except:
                pass
    
    def _set_notifications(self, mode: str):
        """Set notification mode (DND, silent, normal)."""
        # In production, integrate with OS notification settings
        logger.info(f"[SmartHome] Notifications: {mode}")
    
    def detect_workflow_from_apps(self, app_list: List[str]) -> str:
        """
        Detect workflow from currently running apps.
        
        Args:
            app_list: List of active app names
            
        Returns:
            str: Detected workflow
        """
        apps_lower = [a.lower() for a in app_list]
        
        for workflow, config in WORKFLOW_AUTOMATIONS.items():
            matching = [a for a in config.get("apps", []) if a.lower() in apps_lower]
            if matching:
                return workflow
        
        return "normal"
    
    def get_current_workflow(self) -> str:
        """Get current workflow."""
        with self._lock:
            return self._current_workflow
    
    def list_workflows(self) -> str:
        """List available workflows."""
        lines = ["Available Workflows:"]
        for name, config in WORKFLOW_AUTOMATIONS.items():
            lines.append(f"  - {name}: {config['description']}")
        return "\n".join(lines)


# === GLOBAL INSTANCE ===

_smart_home: Optional[SmartHome] = None


def get_smart_home() -> SmartHome:
    """Get global SmartHome instance."""
    global _smart_home
    if _smart_home is None:
        _smart_home = SmartHome()
    return _smart_home


# === DISPATCHER ===

def smart_home_dispatch(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """
    Main dispatcher for smart home control.
    
    Parameters:
    - action: workflow | list | status | detect
    - workflow: deep_work, meeting, relax, away, presentation
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[SmartHome] {action}")
    
    smart_home = get_smart_home()
    
    try:
        if action == "workflow":
            workflow = params.get("workflow", "normal")
            return smart_home.set_workflow(workflow)
        
        elif action == "list":
            return smart_home.list_workflows()
        
        elif action == "status":
            return f"Current workflow: {smart_home.get_current_workflow()}"
        
        elif action == "detect":
            # Try to detect from running apps
            try:
                from core.context_tracker import get_window_tracker
                tracker = get_window_tracker()
                
                if tracker:
                    current_window = tracker.get_current_window()
                    if current_window:
                        apps = [current_window]
                        workflow = smart_home.detect_workflow_from_apps(apps)
                        return f"Detected workflow: {workflow}"
            except:
                pass
            
            return "Could not detect workflow"
        
        else:
            return smart_home.list_workflows()
            
    except Exception as e:
        return f"SmartHome error: {e}"


# === CONVENIENCE FUNCTIONS ===

def execute_automation(workflow: str) -> str:
    """Execute a workflow automation."""
    return get_smart_home().set_workflow(workflow)


def detect_and_apply_workflow() -> str:
    """Detect workflow from apps and apply automation."""
    smart_home = get_smart_home()
    
    try:
        from core.context_tracker import get_window_tracker
        
        tracker = get_window_tracker()
        if tracker:
            current = tracker.get_current_window()
            if current:
                workflow = smart_home.detect_workflow_from_apps([current])
                return smart_home.set_workflow(workflow)
    except:
        pass
    
    return "Could not detect workflow"


if __name__ == "__main__":
    print("=== Smart Home Test ===")
    
    smart_home = get_smart_home()
    print(smart_home.list_workflows())
    print(f"\nCurrent: {smart_home.get_current_workflow()}")
    
    print("\n✅ Smart Home ready")
