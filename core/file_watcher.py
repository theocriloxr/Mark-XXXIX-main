"""
File Watcher - Omniceptive File System (Real-Time Indexing)

JARVIS monitors the file system in real-time using watchdog.
Every file create, modify, or delete is silently indexed to SQLite.

This provides instant file lookup without disk scanning:
- "Where did I save that invoice?" → instant answer
- "Find the PDF I downloaded" → instant answer

Usage:
    from core.file_watcher import FileWatcher, start_file_watcher
    
    # Start the background watcher
    start_file_watcher()
    
    # Query the index
    result = query_index("invoice", recent=True)
"""

import hashlib
import logging
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "core" / "file_index.db"


class FileWatcher(threading.Thread):
    """
    Background daemon that watches the file system.
    Updates SQLite index on file events.
    """
    
    def __init__(self, watch_dirs: List[str] = None):
        """
        Initialize file watcher.
        
        Args:
            watch_dirs: Directories to watch (default: user home)
        """
        super().__init__(daemon=True)
        
        self.watch_dirs = watch_dirs or [
            str(BASE_DIR.parent / "Downloads"),
            str(BASE_DIR.parent / "Documents"),
            str(BASE_DIR.parent / "Desktop"),
        ]
        
        self.is_running = False
        self._observers = []
        self._db_lock = threading.Lock()
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database schema."""
        with self._db_lock:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            # Files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    modified REAL,
                    hash TEXT,
                    indexed_at REAL
                )
            """)
            
            # Events table for recent activity
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            
            # Index for fast lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON files(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext ON files(extension)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_modified ON files(modified)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"[FileWatcher] Database initialized: {DB_PATH}")
    
    def run(self):
        """Main watcher loop - runs in background."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            logger.error("watchdog not installed: pip install watchdog")
            return
        
        class WatcherHandler(FileSystemEventHandler):
            def __init__(self, watcher):
                self.watcher = watcher
            
            def on_any_event(self, event):
                if event.is_directory:
                    return
                
                event_type = event.event_type
                path = event.src_path
                
                # Ignore temp files
                if path.endswith(('.tmp', '.temp', '.cache')):
                    return
                
                if event_type in ('created', 'modified'):
                    self.watcher._index_file(path)
                elif event_type == 'deleted':
                    self.watcher._remove_file(path)
        
        self.is_running = True
        
        for watch_dir in self.watch_dirs:
            if not os.path.exists(watch_dir):
                continue
            
            observer = Observer()
            handler = WatcherHandler(self)
            observer.schedule(handler, watch_dir, recursive=True)
            observer.start()
            self._observers.append(observer)
            
            logger.info(f"[FileWatcher] Watching: {watch_dir}")
        
        # Keep thread alive
        while self.is_running:
            time.sleep(1)
    
    def stop(self):
        """Stop the file watcher."""
        self.is_running = False
        
        for observer in self._observers:
            observer.stop()
        
        self._observers.clear()
        logger.info("[FileWatcher] Stopped")
    
    def _get_file_hash(self, path: str) -> str:
        """Get quick file hash (first 64KB)."""
        try:
            with open(path, 'rb') as f:
                data = f.read(65536)
                return hashlib.md5(data).hexdigest()
        except:
            return ""
    
    def _index_file(self, path: str):
        """Index a file to the database."""
        try:
            if not os.path.exists(path):
                return
            
            stat = os.stat(path)
            
            # Skip large files (> 100MB)
            if stat.st_size > 100_000_000:
                return
            
            name = os.path.basename(path)
            ext = os.path.splitext(name)[1].lower()
            
            with self._db_lock:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                
                # Check if exists
                cursor.execute("SELECT id FROM files WHERE path = ?", (path,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update
                    cursor.execute("""
                        UPDATE files SET
                            name = ?, extension = ?, size = ?,
                            modified = ?, indexed_at = ?
                        WHERE path = ?
                    """, (name, ext, stat.st_size, stat.st_mtime, time.time(), path))
                else:
                    # Insert
                    cursor.execute("""
                        INSERT INTO files (path, name, extension, size, modified, indexed_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (path, name, ext, stat.st_size, stat.st_mtime, time.time()))
                
                # Log event
                cursor.execute("""
                    INSERT INTO events (event_type, path, timestamp)
                    VALUES (?, ?, ?)
                """, ("indexed", path, time.time()))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.debug(f"[FileWatcher] Index error: {e}")
    
    def _remove_file(self, path: str):
        """Remove a file from the index."""
        with self._db_lock:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM files WHERE path = ?", (path,))
            
            cursor.execute("""
                INSERT INTO events (event_type, path, timestamp)
                VALUES (?, ?, ?)
            """, ("deleted", path, time.time()))
            
            conn.commit()
            conn.close()


# === QUERY FUNCTIONS ===

def query_index(
    name: str = None,
    extension: str = None,
    recent: bool = False,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Query the file index.
    
    Args:
        name: Partial name to search
        extension: Extension (e.g., ".pdf")
        recent: Only show files from last hour
        limit: Max results
        
    Returns:
        List of file dicts
    """
    results = []
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        query = "SELECT path, name, extension, size, modified FROM files WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if extension:
            query += " AND extension = ?"
            params.append(extension.lower())
        
        if recent:
            one_hour_ago = time.time() - 3600
            query += " AND modified > ?"
            params.append(one_hour_ago)
        
        query += f" ORDER BY modified DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            results.append({
                "path": row[0],
                "name": row[1],
                "extension": row[2],
                "size": row[3],
                "modified": row[4]
            })
        
        conn.close()
        
    except Exception as e:
        logger.error(f"[FileWatcher] Query error: {e}")
    
    return results


def find_recent_files(limit: int = 10) -> List[Dict[str, Any]]:
    """Find recently modified files."""
    return query_index(recent=True, limit=limit)


def find_by_extension(ext: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Find files by extension."""
    return query_index(extension=ext, limit=limit)


def get_file_info(path: str) -> Optional[Dict[str, Any]]:
    """Get file info from index."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT path, name, extension, size, modified 
            FROM files WHERE path = ?
        """, (path,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "path": row[0],
                "name": row[1],
                "extension": row[2],
                "size": row[3],
                "modified": row[4]
            }
        
    except Exception as e:
        logger.error(f"[FileWatcher] Get info error: {e}")
    
    return None


def get_watcher_status() -> str:
    """Get file watcher status."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events WHERE timestamp > ?", 
                      (time.time() - 3600,))
        recent_events = cursor.fetchone()[0]
        
        conn.close()
        
        return f"File Index: {file_count} files | {recent_events} events in last hour"
        
    except:
        return "File Index: Not initialized"


# === GLOBAL WATCHER ===

_watcher: Optional[FileWatcher] = None


def get_file_watcher() -> FileWatcher:
    """Get global file watcher instance."""
    global _watcher
    if _watcher is None:
        _watcher = FileWatcher()
    return _watcher


def start_file_watcher() -> str:
    """Start the background file watcher."""
    watcher = get_file_watcher()
    
    if not watcher.is_running:
        watcher.start()
        return "File watcher started. JARVIS is now watching your files."
    
    return "File watcher already running."


def stop_file_watcher() -> str:
    """Stop the background file watcher."""
    global _watcher
    
    if _watcher:
        _watcher.stop()
        _watcher = None
    
    return "File watcher stopped."


if __name__ == "__main__":
    print("=== File Watcher Test ===")
    
    # Test query
    results = query_index(recent=True, limit=5)
    print(f"Recent files: {len(results)}")
    
    for f in results[:3]:
        print(f"  - {f['name']}")
    
    print("\n✅ File Watcher ready")
