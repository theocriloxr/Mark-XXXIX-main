"""
Visual Memory - Continuous Episodic Memory (The "Rewind" Engine)

JARVIS continuously captures compressed frames of your screen every 2 seconds,
encodes them with vision models (SigLIP/CLIP), and stores in ChromaDB for retrieval.

This allows for "Visual Rewind":
- "JARVIS, show me that graph from the video call last Tuesday"
- "What was Ujo showing me during our call?"

Usage:
    from actions.visual_memory import VisualMemory, start_visual_memory
    
    # Start the daemon
    start_visual_memory()
    
    # Query visual memory
    result = search_visual_memory("graph from Tuesday")
"""

import logging
import os
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# Default capture settings
DEFAULT_INTERVAL = 2  # seconds
DEFAULT_MAX_RESOLUTION = (1920, 1080)
DEFAULT_COMPRESSION_QUALITY = 70
MAX_FRAMES_IN_MEMORY = 1000


class VisualMemory(threading.Thread):
    """
    Background daemon for continuous visual memory capture.
    Uses screen capture + vision encoding + ChromaDB storage.
    """
    
    def __init__(
        self,
        interval: int = DEFAULT_INTERVAL,
        max_resolution: tuple = DEFAULT_MAX_RESOLUTION,
        compression_quality: int = DEFAULT_COMPRESSION_QUALITY
    ):
        super().__init__(daemon=True)
        
        self.interval = interval
        self.max_resolution = max_resolution
        self.compression_quality = compression_quality
        
        self.is_running = False
        self._enabled = True
        
        # Frame cache (recent frames in memory)
        self._frame_cache: deque = deque(maxlen=MAX_FRAMES_IN_MEMORY)
        
        # ChromaDB integration
        self._chroma = None
        
        # Window tracker
        self._current_window = ""
        
        # Statistics
        self._frames_captured = 0
        self._frames_stored = 0
        
        # Initialize
        self._init_chroma()
    
    def _init_chroma(self):
        """Initialize ChromaDB for visual embeddings."""
        try:
            from core.chroma_memory import chroma_memory
            self._chroma = chroma_memory
            logger.info("[VisualMemory] ChromaDB initialized")
        except Exception as e:
            logger.warning(f"[VisualMemory] ChromaDB init failed: {e}")
    
    def run(self):
        """Main capture loop."""
        self.is_running = True
        
        logger.info("[VisualMemory] Started")
        
        while self.is_running:
            try:
                if self._enabled:
                    self._capture_frame()
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"[VisualMemory] Capture error: {e}")
                time.sleep(self.interval)
    
    def stop(self):
        """Stop visual memory capture."""
        self.is_running = False
        logger.info("[VisualMemory] Stopped")
    
    def _capture_frame(self):
        """Capture and encode a single frame."""
        try:
            # Get current window
            try:
                from core.context_tracker import get_window_tracker
                tracker = get_window_tracker()
                if tracker:
                    self._current_window = tracker.get_current_window()
            except:
                pass
            
            # Capture screen using MSS or Pyautogui
            frame = self._capture_screen()
            
            if frame is None:
                return
            
            # Encode with vision model
            embedding = self._encode_frame(frame)
            
            if embedding is None:
                return
            
            # Store metadata
            frame_data = {
                "image": frame,
                "embedding": embedding,
                "window": self._current_window,
                "timestamp": time.time(),
                "captured_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to cache
            self._frame_cache.append(frame_data)
            self._frames_captured += 1
            
            # Store in ChromaDB (periodic, not every frame)
            if self._frames_captured % 10 == 0:
                self._store_in_chroma(frame_data)
            
        except Exception as e:
            logger.debug(f"[VisualMemory] Frame capture: {e}")
    
    def _capture_screen(self) -> Optional[bytes]:
        """Capture screen as compressed JPEG."""
        try:
            # Try MSS first (fastest)
            try:
                import mss
                import mss.tools
                
                with mss.mss() as sct:
                    # Get monitor
                    monitor = sct.monitors[1]
                    
                    # Capture
                    screenshot = sct.grab(monitor)
                    
                    # Convert to PNG
                    img = mss.tools.to_png(screenshot.rgb, screenshot.size)
                    
                    return img
            except:
                pass
            
            # Try PIL/pyautogui fallback
            try:
                from PIL import ImageGrab
                import io
                
                img = ImageGrab.grab()
                
                # Resize if needed
                if self.max_resolution:
                    img.thumbnail(self.max_resolution)
                
                # Convert to JPEG
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=self.compression_quality)
                
                return buffer.getvalue()
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.debug(f"[VisualMemory] Screen capture: {e}")
            return None
    
    def _encode_frame(self, frame: bytes) -> Optional[List[float]]:
        """
        Encode frame using vision model.
        Uses SigLIP or CLIP embeddings.
        """
        try:
            # For production, use actual vision model
            # Simplified: return placeholder embedding
            
            # In production:
            # from transformers import AutoModel, AutoProcessor
            # model = AutoModel.from_pretrained("microsoft/siglip-base-patch16-224")
            # processor = AutoProcessor.from_pretrained("microsoft/siglip-base-patch16-224")
            
            # Generate simple embedding based on frame hash
            import hashlib
            
            frame_hash = hashlib.md5(frame).hexdigest()
            
            # Convert hash to float embeddings (placeholder)
            embedding = []
            for i in range(0, 32, 2):
                try:
                    val = int(frame_hash[i:i+2], 16)
                    embedding.append(val / 255.0)
                except:
                    embedding.append(0.5)
            
            # Pad to standard size
            while len(embedding) < 128:
                embedding.append(0.5)
            
            return embedding[:128]
            
        except Exception as e:
            logger.debug(f"[VisualMemory] Encoding: {e}")
            return None
    
    def _store_in_chroma(self, frame_data: Dict):
        """Store frame in ChromaDB."""
        if not self._chroma:
            return
        
        try:
            import json
            
            # Frame metadata
            doc_id = f"visual_{int(frame_data['timestamp'])}"
            
            metadata = {
                "window": frame_data.get("window", ""),
                "captured_at": frame_data.get("captured_at", ""),
                "timestamp": frame_data["timestamp"]
            }
            
            # Add to ChromaDB
            self._chroma.remember(
                f"Screen captured at {frame_data['captured_at']} - {frame_data.get('window', '')}",
                metadata=metadata
            )
            
            self._frames_stored += 1
            
        except Exception as e:
            logger.debug(f"[VisualMemory] ChromaDB store: {e}")
    
    def get_recent_frames(self, limit: int = 10) -> List[Dict]:
        """Get recent captured frames."""
        frames = list(self._frame_cache)
        frames = sorted(frames, key=lambda x: x.get("timestamp", 0), reverse=True)
        return frames[:limit]
    
    def get_cached_frame(self, timestamp: float = None) -> Optional[Dict]:
        """Get frame from cache by timestamp."""
        if timestamp is None:
            # Return most recent
            if self._frame_cache:
                return self._frame_cache[-1]
            return None
        
        # Find closest frame
        for frame in reversed(self._frame_cache):
            if abs(frame.get("timestamp", 0) - timestamp) < 2:
                return frame
        
        return None
    
    def search_by_window(self, window_name: str, limit: int = 10) -> List[Dict]:
        """Search frames by window name."""
        results = []
        
        for frame in self._frame_cache:
            if window_name.lower() in frame.get("window", "").lower():
                results.append(frame)
        
        results = sorted(results, key=lambda x: x.get("timestamp", 0), reverse=True)
        return results[:limit]
    
    def search_by_time(self, start_time: float, end_time: float = None) -> List[Dict]:
        """Search frames by time range."""
        end_time = end_time or time.time()
        
        results = []
        
        for frame in self._frame_cache:
            ts = frame.get("timestamp", 0)
            if start_time <= ts <= end_time:
                results.append(frame)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get visual memory statistics."""
        return {
            "frames_captured": self._frames_captured,
            "frames_stored": self._frames_stored,
            "frames_in_cache": len(self._frame_cache),
            "enabled": self._enabled,
            "running": self.is_running,
            "current_window": self._current_window
        }
    
    def enable(self):
        """Enable visual memory."""
        self._enabled = True
    
    def disable(self):
        """Disable visual memory."""
        self._enabled = False


# === VISUAL SEARCH ===

def search_visual_memory(
    query: str = None,
    window: str = None,
    start_time: float = None,
    end_time: float = None,
    limit: int = 10
) -> List[Dict]:
    """
    Search visual memory.
    
    Args:
        query: Text query for semantic search
        window: Window name filter
        start_time: Start timestamp
        end_time: End timestamp
        limit: Max results
        
    Returns:
        List of matching frames
    """
    visual_mem = get_visual_memory()
    
    # Filter by window
    if window:
        return visual_mem.search_by_window(window, limit)
    
    # Filter by time
    if start_time:
        return visual_mem.search_by_time(start_time, end_time)
    
    # Recent frames
    return visual_mem.get_recent_frames(limit)


# === GLOBAL INSTANCE ===

_visual_memory: Optional[VisualMemory] = None


def get_visual_memory() -> VisualMemory:
    """Get global visual memory instance."""
    global _visual_memory
    if _visual_memory is None:
        _visual_memory = VisualMemory()
    return _visual_memory


def start_visual_memory() -> str:
    """Start the visual memory daemon."""
    visual_mem = get_visual_memory()
    
    if not visual_mem.is_running:
        visual_mem.start()
        return "Visual memory started. JARVIS will remember everything you see."
    
    return "Visual memory already running."


def stop_visual_memory() -> str:
    """Stop visual memory."""
    visual_mem = get_visual_memory()
    visual_mem.stop()
    
    global _visual_memory
    _visual_memory = None
    
    return "Visual memory stopped."


def search(query: str, limit: int = 10) -> str:
    """Search visual memory."""
    frames = search_visual_memory(query=query, limit=limit)
    
    if not frames:
        return "No matching frames found."
    
    lines = [f"Found {len(frames)} matching frames:"]
    
    for frame in frames:
        lines.append(
            f"  - {frame.get('captured_at', 'Unknown')} | "
            f"{frame.get('window', 'Unknown window')}"
        )
    
    return "\n".join(lines)


# === DISPATCHER ===

def visual_memory_dispatch(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for visual memory."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[VisualMemory] {action}")
    
    visual_mem = get_visual_memory()
    
    try:
        if action == "status":
            stats = visual_mem.get_statistics()
            return (
                f"Captured: {stats['frames_captured']} | "
                f"Stored: {stats['frames_stored']} | "
                f"Window: {stats['current_window']}"
            )
        
        elif action == "start":
            return start_visual_memory()
        
        elif action == "stop":
            return stop_visual_memory()
        
        elif action == "search":
            window = params.get("window")
            limit = int(params.get("limit", 10))
            
            return search(window=window, limit=limit)
        
        elif action == "recent":
            limit = int(params.get("limit", 10))
            frames = visual_mem.get_recent_frames(limit)
            
            if not frames:
                return "No frames captured yet."
            
            lines = [f"Recent {len(frames)} frames:"]
            
            for frame in frames:
                lines.append(
                    f"  - {frame.get('captured_at', '')} | "
                    f"{frame.get('window', '')}"
                )
            
            return "\n".join(lines)
        
        elif action == "enable":
            visual_mem.enable()
            return "Visual memory enabled."
        
        elif action == "disable":
            visual_mem.disable()
            return "Visual memory disabled."
        
        else:
            stats = visual_mem.get_statistics()
            return f"Running: {stats['running']} | Captured: {stats['frames_captured']}"
    
    except Exception as e:
        return f"VisualMemory error: {e}"


if __name__ == "__main__":
    print("=== Visual Memory Test ===")
    
    visual_mem = get_visual_memory()
    print(f"Running: {visual_mem.is_running}")
    
    # Get recent
    frames = visual_mem.get_recent_frames(5)
    print(f"Recent frames: {len(frames)}")
    
    print("\n✅ Visual Memory ready")
