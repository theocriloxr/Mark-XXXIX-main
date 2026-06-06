"""
Episodic Memory - Continuous Visual Rewind Engine

JARVIS remembers everything you've ever seen on your screen.
Captures compressed frames every 2 seconds, embeds with vision encoder,
and stores in ChromaDB for instant visual recall.

This enables:
- "JARVIS, what was that graph Ujo showed me last Tuesday?"
- "Find the screenshot from my call with Bob"
- Visual semantic search of your entire screen history

Usage:
    from core.episodic_memory import EpisodicMemory, start_episodic_memory
    
    start_episodic_memory()
    
    # Query visual memory
    result = query_episodic("Ujo graph")
"""

import base64
import hashlib
import logging
import threading
import time
import zlib
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# Configuration
CAPTURE_INTERVAL = 2  # seconds between captures
MAX_FRAMES_IN_MEMORY = 1000  # frames to keep in quick access
IMAGE_QUALITY = 30  # JPEG quality for compression
RESIZE_WIDTH = 320  # Resize width for embedding
RESIZE_HEIGHT = 180  # Resize height (16:9 aspect)


class EpisodicMemory:
    """
    Continuous episodic memory daemon.
    Captures screen, embeds, and indexes to ChromaDB.
    """
    
    def __init__(self):
        super().__init__(daemon=True)
        
        self.is_running = False
        self._enabled = True
        
        # Quick access buffer (not in ChromaDB)
        self._frame_buffer: deque = deque(maxlen=MAX_FRAMES_IN_MEMORY)
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Vision model for embeddings
        self._vision_model = None
        self._model_loaded = False
        
        # Statistics
        self._capture_count = 0
        self._last_capture_time = 0
        
        # Initialize embedding model
        self._init_model()
    
    def _init_model(self):
        """Initialize vision embedding model."""
        try:
            # Try loading sentence-transformers with CLIP
            from sentence_transformers import SentenceTransformer
            
            # Use a lightweight CLIP model
            self._vision_model = SentenceTransformer('clip-ViT-B-32')
            self._model_loaded = True
            
            logger.info("[EpisodicMemory] CLIP model loaded")
        except Exception as e:
            logger.warning(f"[EpisodicMemory] CLIP model not available: {e}")
            logger.info("[EpisodicMemory] Using fallback hashing for embeddings")
            self._model_loaded = False
    
    def run(self):
        """Main capture loop."""
        self.is_running = True
        
        logger.info("[EpisodicMemory] Starting episodic capture")
        
        while self.is_running:
            try:
                # Capture screen
                frame = self._capture_screen()
                
                if frame:
                    # Process and store
                    self._process_frame(frame)
                    self._capture_count += 1
                    self._last_capture_time = time.time()
                
            except Exception as e:
                logger.error(f"[EpisodicMemory] Capture error: {e}")
            
            time.sleep(CAPTURE_INTERVAL)
    
    def stop(self):
        """Stop the episodic memory daemon."""
        self.is_running = False
        logger.info("[EpisodicMemory] Stopped")
    
    def _capture_screen(self) -> Optional[bytes]:
        """Capture the current screen as compressed JPEG."""
        try:
            # Use PIL for screenshot
            from PIL import Image
            import io
            
            # Get screen dimensions
            import mss
            with mss.mss() as sct:
                # Capture primary monitor
                img = sct.grab(sct.monitors[1])
            
            # Convert to PIL Image
            image = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
            
            # Resize for efficiency
            image = image.resize((RESIZE_WIDTH, RESIZE_HEIGHT), Image.LANCZOS)
            
            # Compress as JPEG
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=IMAGE_QUALITY)
            jpeg_data = buffer.getvalue()
            
            return jpeg_data
            
        except Exception as e:
            logger.debug(f"[EpisodicMemory] Screen capture: {e}")
            return None
    
    def _process_frame(self, frame_data: bytes):
        """Process and index a captured frame."""
        timestamp = time.time()
        
        # Create embedding
        embedding = self._create_embedding(frame_data)
        
        # Create frame record
        frame_record = {
            "timestamp": timestamp,
            "frame": frame_data,
            "embedding": embedding,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "capture_index": self._capture_count
        }
        
        # Store in buffer
        with self._lock:
            self._frame_buffer.append(frame_record)
        
        # Also store to ChromaDB for persistent search
        self._store_to_chroma(frame_record)
    
    def _create_embedding(self, frame_data: bytes) -> np.ndarray:
        """Create embedding from frame data."""
        if self._model_loaded and self._vision_model:
            try:
                # Decode image for model
                from PIL import Image
                import io
                
                image = Image.open(io.BytesIO(frame_data))
                
                # Get embedding
                embedding = self._vision_model.encode(image)
                
                return embedding
            except Exception as e:
                logger.debug(f"[EpisodicMemory] Embedding: {e}")
        
        # Fallback: Create hash-based embedding
        # This won't be semantically searchable but provides uniqueness
        return self._hash_embedding(frame_data)
    
    def _hash_embedding(self, frame_data: bytes) -> np.ndarray:
        """Create hash-based representation (fallback)."""
        # Compress and hash the frame
        compressed = zlib.compress(frame_data)
        hash_val = hashlib.sha256(compressed).digest()
        
        # Convert to numpy array and normalize
        embedding = np.frombuffer(hash_val[:32], dtype=np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def _store_to_chroma(self, frame_record: dict):
        """Store frame to ChromaDB for semantic search."""
        try:
            from core.chroma_memory import chroma_memory
            
            # Create metadata
            metadata = {
                "timestamp": frame_record["timestamp"],
                "date": frame_record["date"],
                "time": frame_record["time"],
                "capture_index": frame_record["capture_index"]
            }
            
            # Store embedding
            embedding = frame_record["embedding"].tolist() if hasattr(frame_record["embedding"], 'tolist') else frame_record["embedding"]
            
            # Add to ChromaDB
            chroma_memory.embeddings.add(
                ids=[f"frame_{frame_record['capture_index']}"],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[f"Screen capture at {frame_record['time']}"]
            )
            
        except Exception as e:
            logger.debug(f"[EpisodicMemory] ChromaDB store: {e}")
    
    def get_recent_frames(self, count: int = 10) -> List[Dict]:
        """Get recent frames from buffer."""
        with self._lock:
            frames = list(self._frame_buffer)[-count:]
            return [
                {
                    "timestamp": f["timestamp"],
                    "date": f["date"],
                    "time": f["time"]
                }
                for f in frames
            ]
    
    def get_frame(self, capture_index: int = None) -> Optional[bytes]:
        """Get a specific frame by index."""
        with self._lock:
            if capture_index is None:
                # Return latest
                if self._frame_buffer:
                    return self._frame_buffer[-1]["frame"]
            else:
                # Find by index
                for frame in reversed(self._frame_buffer):
                    if frame["capture_index"] == capture_index:
                        return frame["frame"]
        
        return None
    
    def search_frames(self, query: str, limit: int = 5) -> List[Dict]:
        """Search frames by semantic query."""
        results = []
        
        try:
            from core.chroma_memory import chroma_memory
            
            # Query ChromaDB
            query_embedding = None
            
            # Try to create embedding for query
            if self._model_loaded and self._vision_model:
                try:
                    query_embedding = self._vision_model.encode(query).tolist()
                except:
                    pass
            
            if query_embedding:
                # Search semantic
                results = chroma_memory.recall(query, n_results=limit)
                
                return [
                    {
                        "text": r,
                        "type": "semantic"
                    }
                    for r in results
                ]
            
        except Exception as e:
            logger.error(f"[EpisodicMemory] Search error: {e}")
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get episodic memory statistics."""
        with self._lock:
            return {
                "total_captures": self._capture_count,
                "buffer_size": len(self._frame_buffer),
                "last_capture": self._last_capture_time,
                "model_loaded": self._model_loaded,
                "status": "running" if self.is_running else "stopped"
            }
    
    def enable(self):
        """Enable episodic capture."""
        self._enabled = True
    
    def disable(self):
        """Disable episodic capture."""
        self._enabled = False


# === GLOBAL INSTANCE ===

_episodic_memory: Optional[EpisodicMemory] = None


def get_episodic_memory() -> EpisodicMemory:
    """Get global episodic memory instance."""
    global _episodic_memory
    if _episodic_memory is None:
        _episodic_memory = EpisodicMemory()
    return _episodic_memory


def start_episodic_memory() -> str:
    """Start the episodic memory daemon."""
    memory = get_episodic_memory()
    
    if not memory.is_running:
        memory.start()
        return "Episodic memory started. JARVIS will remember everything you see."
    
    return "Episodic memory already running."


def stop_episodic_memory() -> str:
    """Stop the episodic memory daemon."""
    memory = get_episodic_memory()
    memory.stop()
    
    return "Episodic memory stopped."


def query_episodic(query: str, limit: int = 5) -> List[Dict]:
    """Query episodic memory."""
    return get_episodic_memory().search_frames(query, limit)


def get_recent_visual_history(count: int = 10) -> List[Dict]:
    """Get recent visual history."""
    return get_episodic_memory().get_recent_frames(count)


def get_frame_at_index(index: int) -> Optional[bytes]:
    """Get frame at specific index."""
    return get_episodic_memory().get_frame(index)


# === DISPATCHER ===

def episodic_memory(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for episodic memory."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[EpisodicMemory] {action}")
    
    memory = get_episodic_memory()
    
    try:
        if action == "status":
            stats = memory.get_statistics()
            return f"Captures: {stats['total_captures']} | Buffer: {stats['buffer_size']} | Model: {'Loaded' if stats['model_loaded'] else 'Fallback'}"
        
        elif action == "search":
            query = params.get("query", "")
            if not query:
                return "Please provide a query."
            
            results = memory.search_frames(query, limit=params.get("limit", 5))
            if results:
                lines = ["Visual search results:"]
                for r in results:
                    lines.append(f"- {r.get('date')} {r.get('time')}: {r.get('text', 'Match')}")
                return "\n".join(lines)
            return "No matching frames found."
        
        elif action == "recent":
            count = params.get("count", 10)
            frames = memory.get_recent_frames(count)
            if frames:
                lines = ["Recent frames:"]
                for f in frames[:5]:
                    lines.append(f"- {f['date']} {f['time']}")
                return "\n".join(lines)
            return "No recent frames."
        
        elif action == "get":
            index = params.get("index")
            frame = memory.get_frame(int(index) if index else None)
            if frame:
                return f"Frame retrieved (size: {len(frame)} bytes)"
            return "Frame not found."
        
        elif action == "enable":
            memory.enable()
            return "Episodic memory enabled."
        
        elif action == "disable":
            memory.disable()
            return "Episodic memory disabled."
        
        else:
            stats = memory.get_statistics()
            return f"EpisodicMemory: {stats['total_captures']} captures | Running: {stats['status']}"
    
    except Exception as e:
        return f"EpisodicMemory error: {e}"


if __name__ == "__main__":
    print("=== Episodic Memory Test ===")
    
    # Test capture
    memory = get_episodic_memory()
    print(f"Model loaded: {memory._model_loaded}")
    print(f"Status: {memory.get_statistics()}")
    
    print("\n✅ Episodic Memory ready")
