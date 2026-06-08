"""
Data Siphon - Background Data Pipeline
===================================

Continuously monitors external data sources and feeds information to JARVIS:
- GitHub trending repositories
- Cryptocurrency market data (NGN/USDT)
- AI research papers (ArXiv)
- News feeds

This data is synthesized into a "Morning Briefing" for the user.

Usage:
    from core.data_siphon import DataSiphon, get_data_siphon
    
    siphon = get_data_siphon()
    briefing = siphon.get_morning_briefing()
"""

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def get_base_dir() -> Path:
    """Get base directory."""
    import sys
    from pathlib import Path
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


@dataclass
class DataItem:
    """Single data item from a source."""
    source: str
    title: str
    data: Any
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)


class DataSiphon:
    """
    Background data pipeline for JARVIS.
    Monitors multiple data sources and provides synthesized briefings.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._lock = threading.Lock()
        
        # Data buffers
        self._github_trending: List[Dict] = []
        self._crypto_data: Dict = {}
        self._arxiv_papers: List[Dict] = []
        self._news_items: List[Dict] = []
        
        # Configuration
        self._config = self._load_config()
        
        # Last fetch times
        self._last_github = 0
        self._last_crypto = 0
        self._last_arxiv = 0
        self._last_news = 0
        
        # Fetch intervals (seconds)
        self._interval_github = 3600  # 1 hour
        self._interval_crypto = 60    # 1 minute
        self._interval_arxiv = 3600  # 1 hour
        self._interval_news = 300     # 5 minutes
        
        self._initialized = True
        logger.info("[DataSiphon] Initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration."""
        config_file = BASE_DIR / "config" / "data_siphon.json"
        
        if not config_file.exists():
            return {
                "enabled": True,
                "github_enabled": True,
                "crypto_enabled": False,  # Requires API
                "arxiv_enabled": True,
                "news_enabled": True,
                " briefing_time": "08:00"
            }
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"enabled": True}
    
    def enable(self):
        """Enable data siphon."""
        self._config["enabled"] = True
    
    def disable(self):
        """Disable data siphon."""
        self._config["enabled"] = False
    
    def is_enabled(self) -> bool:
        """Check if enabled."""
        return self._config.get("enabled", True)
    
    def ingest_world_data(self) -> Optional[Dict]:
        """
        Main ingestion method - called by Omni Engine.
        Checks all sources and returns new data if available.
        """
        if not self.is_enabled():
            return None
        
        new_data = {}
        
        # GitHub trending
        if self._config.get("github_enabled", True):
            if time.time() - self._last_github > self._interval_github:
                github_data = self._fetch_github_trending()
                if github_data:
                    self._github_trending = github_data
                    self._last_github = time.time()
                    new_data["github"] = github_data
        
        # Crypto (mock for now)
        if self._config.get("crypto_enabled", False):
            if time.time() - self._last_crypto > self._interval_crypto:
                # Would fetch real crypto data
                self._last_crypto = time.time()
        
        # ArXiv papers
        if self._config.get("arxiv_enabled", True):
            if time.time() - self._last_arxiv > self._interval_arxiv:
                arxiv_data = self._fetch_arxiv_papers()
                if arxiv_data:
                    self._arxiv_papers = arxiv_data
                    self._last_arxiv = time.time()
                    new_data["arxiv"] = arxiv_data
        
        return new_data if new_data else None
    
    def _fetch_github_trending(self) -> List[Dict]:
        """Fetch GitHub trending repositories."""
        # Note: Requires network access
        # This is a mock implementation
        try:
            # Try to fetch from GitHub API (no auth needed for trending)
            import requests
            
            url = "https://api.github.com/search/repositories"
            params = {
                "q": "created:>2024-01-01",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for item in data.get("items", [])[:10]:
                    repos.append({
                        "name": item.get("full_name", ""),
                        "description": item.get("description", "")[:100],
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", ""),
                        "url": item.get("html_url", "")
                    })
                
                return repos
        except Exception as e:
            logger.debug(f"[DataSiphon] GitHub fetch error: {e}")
        
        return []
    
    def _fetch_arxiv_papers(self) -> List[Dict]:
        """Fetch latest AI papers from ArXiv."""
        try:
            import requests
            
            # ArXiv API for AI papers
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Parse XML response (simplified)
                papers = []
                content = response.text
                
                # Simple extraction (in production, use xml.etree)
                if "<entry>" in content:
                    entries = content.split("<entry>")
                    for entry in entries[1:6]:  # First 5 papers
                        title_start = entry.find("<title>")
                        title_end = entry.find("</title>")
                        if title_start > 0 and title_end > title_start:
                            title = entry[title_start+7:title_end].strip()
                            papers.append({
                                "title": title,
                                "source": "arXiv"
                            })
                
                return papers
        except Exception as e:
            logger.debug(f"[DataSiphon] ArXiv fetch error: {e}")
        
        return []
    
    def get_morning_briefing(self) -> str:
        """
        Generate morning briefing from collected data.
        """
        lines = ["☀ MORNING BRIEFING"]
        lines.append("")
        
        # GitHub trending
        if self._github_trending:
            lines.append("📊 TOP GITHUB REPOS:")
            for repo in self._github_trending[:5]:
                lines.append(f"  ★ {repo.get('stars', 0)} - {repo.get('name', '')}")
                lines.append(f"     {repo.get('description', '')[:60]}")
            lines.append("")
        
        # Crypto (mock)
        if self._crypto_data:
            lines.append("💹 MARKET DATA:")
            for symbol, data in self._crypto_data.items():
                price = data.get("price", "N/A")
                change = data.get("change", 0)
                sign = "+" if change > 0 else ""
                lines.append(f"  {symbol}: ${price} ({sign}{change}%)")
            lines.append("")
        
        # ArXiv papers
        if self._arxiv_papers:
            lines.append("📄 LATEST AI PAPERS:")
            for paper in self._arxiv_papers[:3]:
                title = paper.get("title", "")[:60]
                lines.append(f"  - {title}")
            lines.append("")
        
        # News
        if self._news_items:
            lines.append("📰 TOP NEWS:")
            for item in self._news_items[:3]:
                lines.append(f"  - {item.get('title', '')[:60]}")
            lines.append("")
        
        if len(lines) <= 2:
            return "No briefing data available yet. Run with network access."
        
        return "\n".join(lines)
    
    def get_github_trending(self) -> List[Dict]:
        """Get GitHub trending data."""
        return self._github_trending
    
    def get_crypto_data(self) -> Dict:
        """Get crypto market data."""
        return self._crypto_data
    
    def get_arxiv_papers(self) -> List[Dict]:
        """Get ArXiv papers."""
        return self._arxiv_papers
    
    def get_status(self) -> Dict:
        """Get siphon status."""
        return {
            "enabled": self.is_enabled(),
            "github_count": len(self._github_trending),
            "arxiv_count": len(self._arxiv_papers),
            "crypto_keys": list(self._crypto_data.keys()),
            "last_github": self._last_github,
            "last_arxiv": self._last_arxiv
        }


# === GLOBAL INSTANCE ===

_data_siphon: Optional[DataSiphon] = None


def get_data_siphon() -> DataSiphon:
    """Get global DataSiphon instance."""
    global _data_siphon
    if _data_siphon is None:
        _data_siphon = DataSiphon()
    return _data_siphon


# === DISPATCHER ===

def data_siphon_dispatch(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for DataSiphon."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[DataSiphon] {action}")
    
    try:
        siphon = get_data_siphon()
        
        if action == "status":
            status = siphon.get_status()
            return (
                f"Enabled: {status['enabled']} | "
                f"GitHub: {status['github_count']} | "
                f"ArXiv: {status['arxiv_count']}"
            )
        
        elif action == "enable":
            siphon.enable()
            return "Data Siphon enabled"
        
        elif action == "disable":
            siphon.disable()
            return "Data Siphon disabled"
        
        elif action == "ingest":
            data = siphon.ingest_world_data()
            if data:
                return f"Ingested: {list(data.keys())}"
            return "No new data"
        
        elif action == "briefing":
            return siphon.get_morning_briefing()
        
        elif action == "github":
            repos = siphon.get_github_trending()
            if repos:
                lines = ["GitHub Trending:"]
                for repo in repos[:5]:
                    lines.append(f"  {repo.get('name')}: {repo.get('stars')} stars")
                return "\n".join(lines)
            return "No GitHub data"
        
        elif action == "arxiv":
            papers = siphon.get_arxiv_papers()
            if papers:
                lines = ["ArXiv Papers:"]
                for paper in papers[:5]:
                    lines.append(f"  - {paper.get('title')[:50]}")
                return "\n".join(lines)
            return "No ArXiv data"
        
        else:
            status = siphon.get_status()
            return f"DataSiphon: {status['enabled']}"
    
    except Exception as e:
        return f"DataSiphon error: {e}"


if __name__ == "__main__":
    print("=== Data Siphon Test ===")
    
    siphon = get_data_siphon()
    print(siphon.get_status())
    
    # Try to ingest
    print("\nIngesting data...")
    data = siphon.ingest_world_data()
    print(f"Data: {data}")
    
    # Get briefing
    print("\n" + siphon.get_morning_briefing())
    
    print("\n✅ Data Siphon ready")
