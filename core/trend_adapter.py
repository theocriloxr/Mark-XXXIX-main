"""
Trend Adapter - JARVIS Technology Trend Monitoring
==================================================

Keeps JARVIS current with:
- Tech trends and updates
- New API capabilities
- UI changes adaptation
- Knowledge base updates
- Framework version tracking

Usage:
    from core.trend_adapter import check_trends, update_knowledge, get_trend_status
    
    # Check for new trends
    check_trends()
    
    # Update knowledge base
    update_knowledge("gemini-2.0")
    
    # Get status
    get_trend_status()
"""

import datetime
import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def _get_base_dir() -> Path:
    """Get base directory."""
    import sys
    from pathlib import Path
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
TREND_CONFIG = BASE_DIR / "config" / "trends.json"


# Known tech categories to monitor
TECH_CATEGORIES = [
    "ai_models",
    "frameworks", 
    "apis",
    "libraries",
    "platforms",
    "tools",
    " languages"
]


@dataclass
class TrendEntry:
    """A trend entry."""
    name: str
    category: str
    version: str
    last_checked: str
    status: str  # current, outdated, deprecated
    notes: str = ""


class TrendDatabase:
    """Trend tracking database."""
    
    def __init__(self):
        self._trends: Dict[str, TrendEntry] = {}
        self._last_full_scan = ""
        self._auto_update = True
        self._load()
    
    def _load(self):
        """Load from config."""
        if not TREND_CONFIG.exists():
            self._init_defaults()
            return
        
        try:
            with open(TREND_CONFIG, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for key, entry in data.get("trends", {}).items():
                self._trends[key] = TrendEntry(
                    name=entry["name"],
                    category=entry["category"],
                    version=entry["version"],
                    last_checked=entry["last_checked"],
                    status=entry["status"],
                    notes=entry.get("notes", "")
                )
            
            self._last_full_scan = data.get("last_full_scan", "")
            self._auto_update = data.get("auto_update", True)
        except Exception:
            self._init_defaults()
    
    def _save(self):
        """Save to config."""
        try:
            TREND_CONFIG.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "trends": {
                    key: {
                        "name": entry.name,
                        "category": entry.category,
                        "version": entry.version,
                        "last_checked": entry.last_checked,
                        "status": entry.status,
                        "notes": entry.notes
                    }
                    for key, entry in self._trends.items()
                },
                "last_full_scan": self._last_full_scan,
                "auto_update": self._auto_update
            }
            with open(TREND_CONFIG, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[TrendAdapter] Save error: {e}")
    
    def _init_defaults(self):
        """Initialize default trends."""
        defaults = {
            "gemini-pro": TrendEntry("Gemini Pro", "ai_models", "1.0", 
                                 datetime.datetime.now().isoformat(), "current"),
            "python": TrendEntry("Python", "languages", "3.12",
                              datetime.datetime.now().isoformat(), "current"),
            "react": TrendEntry("React", "frameworks", "18.x",
                            datetime.datetime.now().isoformat(), "current"),
            "fastapi": TrendEntry("FastAPI", "frameworks", "0.100+",
                               datetime.datetime.now().isoformat(), "current"),
        }
        self._trends = defaults
        self._save()
    
    def get_trend(self, name: str) -> Optional[TrendEntry]:
        """Get a trend."""
        return self._trends.get(name.lower())
    
    def add_trend(self, name: str, category: str, version: str, notes: str = "") -> str:
        """Add a new trend."""
        key = name.lower()
        if key in self._trends:
            return f"Trend '{name}' already exists"
        
        self._trends[key] = TrendEntry(
            name=name,
            category=category,
            version=version,
            last_checked=datetime.datetime.now().isoformat(),
            status="current",
            notes=notes
        )
        self._save()
        return f"Added trend: {name} {version}"
    
    def update_trend(self, name: str, version: str, status: str = "current") -> str:
        """Update a trend."""
        key = name.lower()
        if key not in self._trends:
            return f"Trend '{name}' not found"
        
        trend = self._trends[key]
        trend.version = version
        trend.status = status
        trend.last_checked = datetime.datetime.now().isoformat()
        self._save()
        return f"Updated {name} to {version} ({status})"
    
    def check_outdated(self) -> List[TrendEntry]:
        """Get outdated trends."""
        return [t for t in self._trends.values() if t.status == "outdated"]
    
    def check_deprecated(self) -> List[TrendEntry]:
        """Get deprecated trends."""
        return [t for t in self._trends.values() if t.status == "deprecated"]
    
    def get_all_trends(self) -> List[TrendEntry]:
        """Get all trends."""
        return list(self._trends.values())
    
    def set_auto_update(self, enabled: bool):
        """Set auto-update."""
        self._auto_update = enabled
        self._save()
    
    def get_status(self) -> dict:
        """Get status summary."""
        current = sum(1 for t in self._trends.values() if t.status == "current")
        outdated = sum(1 for t in self._trends.values() if t.status == "outdated")
        deprecated = sum(1 for t in self._trends.values() if t.status == "deprecated")
        
        return {
            "total_trends": len(self._trends),
            "current": current,
            "outdated": outdated,
            "deprecated": deprecated,
            "last_scan": self._last_full_scan,
            "auto_update": self._auto_update
        }


# Global instance
_trend_lock = threading.Lock()
_trend_db: Optional[TrendDatabase] = None


def _get_trend_db() -> TrendDatabase:
    """Get trend database."""
    global _trend_db
    with _trend_lock:
        if _trend_db is None:
            _trend_db = TrendDatabase()
        return _trend_db


# === TREND OPERATIONS ===

def check_trends() -> str:
    """
    Check for trending technologies.
    
    Returns:
        str: Summary of trends
    """
    db = _get_trend_db()
    status = db.get_status()
    
    outdated = db.check_outdated()
    deprecated = db.check_deprecated()
    
    result = f"""
═══ TREND ANALYSIS ═══
Total: {status['total_trends']}
Current: {status['current']}
Outdated: {status['outdated']}
Deprecated: {status['deprecated']}
"""
    
    if outdated:
        result += f"\n⚠️ Outdated: {', '.join([t.name for t in outdated])}"
    
    if deprecated:
        result += f"\n❌ Deprecated: {', '.join([t.name for t in deprecated])}"
    
    return result.strip()


def add_trend(name: str, category: str, version: str, notes: str = "") -> str:
    """Add a new technology trend."""
    return _get_trend_db().add_trend(name, category, version, notes)


def update_knowledge(item_name: str, version: str = "") -> str:
    """Update knowledge base with new information."""
    db = _get_trend_db()
    
    if version:
        return db.update_trend(item_name, version)
    
    # If no version, just update last_checked
    return db.update_trend(item_name, "current")


def mark_outdated(item_name: str) -> str:
    """Mark an item as outdated."""
    return _get_trend_db().update_trend(item_name, "outdated", "outdated")


def mark_deprecated(item_name: str) -> str:
    """Mark an item as deprecated."""
    return _get_trend_db().update_trend(item_name, "deprecated", "deprecated")


def remove_trend(item_name: str) -> str:
    """Remove a trend."""
    db = _get_trend_db()
    key = item_name.lower()
    
    if key in db._trends:
        del db._trends[key]
        db._save()
        return f"Removed trend: {item_name}"
    
    return f"Trend '{item_name}' not found"


def get_trend_status() -> dict:
    """Get trend database status."""
    return _get_trend_db().get_status()


def get_trends_by_category(category: str) -> List[TrendEntry]:
    """Get trends by category."""
    db = _get_trend_db()
    return [t for t in db.get_all_trends() if t.category == category]


def list_all_trends() -> str:
    """List all trends."""
    db = _get_trend_db()
    trends = db.get_all_trends()
    
    if not trends:
        return "No trends tracked."
    
    # Group by category
    by_category: Dict[str, List[TrendEntry]] = {}
    for t in trends:
        if t.category not in by_category:
            by_category[t.category] = []
        by_category[t.category].append(t)
    
    result = "═══ TECHNOLOGY TRENDS ═══\n"
    for cat, items in sorted(by_category.items()):
        result += f"\n{cat.upper()}:\n"
        for t in items:
            status_icon = "✅" if t.status == "current" else "⚠️" if t.status == "outdated" else "❌"
            result += f"  {status_icon} {t.name} {t.version}\n"
    
    return result.strip()


# === DISPATCHER ===

def trend_adapter(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for trend adapter."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[TrendAdapter] {action}")
    
    try:
        if action == "check" or action == "scan":
            return check_trends()
        
        elif action == "add":
            name = params.get("name", "")
            category = params.get("category", "")
            version = params.get("version", "")
            notes = params.get("notes", "")
            
            if not name or not category or not version:
                return "Please specify name, category, and version"
            
            return add_trend(name, category, version, notes)
        
        elif action == "update":
            name = params.get("name", "")
            version = params.get("version", "")
            
            if not name:
                return "Please specify name"
            
            return update_knowledge(name, version)
        
        elif action == "outdated":
            name = params.get("name", "")
            if not name:
                return "Please specify name"
            return mark_outdated(name)
        
        elif action == "deprecated":
            name = params.get("name", "")
            if not name:
                return "Please specify name"
            return mark_deprecated(name)
        
        elif action == "remove":
            name = params.get("name", "")
            if not name:
                return "Please specify name"
            return remove_trend(name)
        
        elif action == "list":
            return list_all_trends()
        
        elif action == "category":
            category = params.get("category", "")
            if not category:
                return "Please specify category"
            
            trends = get_trends_by_category(category)
            if not trends:
                return f"No trends in category: {category}"
            
            return "\n".join([f"- {t.name} {t.version}" for t in trends])
        
        elif action == "status":
            status = get_trend_status()
            return f"Trends: {status['total_trends']} | Current: {status['current']} | Outdated: {status['outdated']} | Deprecated: {status['deprecated']}"
        
        else:
            return check_trends()
    
    except Exception as e:
        return f"TrendAdapter error: {e}"


if __name__ == "__main__":
    print("=== Trend Adapter Test ===")
    
    # Check trends
    print(check_trends())
    
    # List all
    print("\n" + list_all_trends())
    
    # Add test trend
    print("\n" + add_trend("GPT-5", "ai_models", "1.0", "Upcoming model"))
    
    print("\n✅ Trend Adapter ready")
