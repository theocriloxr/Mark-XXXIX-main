"""
Vision Tools for JARVIS - Screen Capture with Grid Overlay & Desktop Control

This module provides:
- InspectScreenTool: Captures screen and overlays a numbered coordinate grid
  for pixel-perfect spatial coordination with vision models
- DesktopClickTool: Moves mouse and clicks at specific X,Y coordinates

Usage:
    from actions.vision_tools import InspectScreenTool, DesktopClickTool
    
    # For screen inspection
    inspect_tool = InspectScreenTool()
    result = inspect_tool.forward()
    
    # For clicking
    click_tool = DesktopClickTool()
    result = click_tool.forward(x=500, y=300)
"""

import io
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

# Screen capture and image processing
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    _PYAUTOGUI = True
except ImportError:
    _PYAUTOGUI = False

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL = True
except ImportError:
    _PIL = False

# Try mss for faster screen capture
try:
    import mss
    import mss.tools
    _MSS = True
except ImportError:
    _MSS = False

# smolagents Tool base class
try:
    from smolagents import Tool
    _SMOLAGENTS = True
except ImportError:
    _SMOLAGENTS = False
    # Fallback to basic Tool if smolagents not available
    class Tool:
        name: str = ""
        description: str = ""
        inputs: dict = {}
        output_type: str = "string"
        
        def forward(self, **kwargs):
            raise NotImplementedError


def _get_base_dir() -> Path:
    """Get the base directory of the application."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()

# Screenshot paths
SCREENSHOT_PATH = BASE_DIR / "current_screen.png"
GRID_SCREENSHOT_PATH = BASE_DIR / "current_screen_grid.png"


def _get_screen_size() -> tuple[int, int]:
    """Get screen dimensions."""
    if _PYAUTOGUI:
        return pyautogui.size()
    elif _MSS:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            return monitor["width"], monitor["height"]
    return 1920, 1080  # Default fallback


def _capture_screen_pil() -> Image.Image:
    """Capture screen using PIL/pyautogui."""
    if _PYAUTOGUI:
        screenshot = pyautogui.screenshot()
        return screenshot
    raise RuntimeError("No screen capture method available. Install pyautogui or mss.")


def _capture_screen_mss() -> bytes:
    """Capture screen using mss and return PNG bytes."""
    if not _MSS:
        raise RuntimeError("mss not installed. Run: pip install mss")
    
    with mss.mss() as sct:
        monitors = sct.monitors
        target = monitors[1] if len(monitors) > 1 else monitors[0]
        shot = sct.grab(target)
        png_bytes = mss.tools.to_png(shot.rgb, shot.size)
    return png_bytes


def _draw_grid_overlay(image: Image.Image, grid_size: int = 10) -> Image.Image:
    """
    Draw a numbered coordinate grid over the image.
    
    Args:
        image: PIL Image to overlay grid on
        grid_size: Number of grid cells (default 10x10)
    
    Returns:
        PIL Image with grid overlay
    """
    if not _PIL:
        return image
    
    # Create a copy to draw on
    grid_img = image.copy()
    draw = ImageDraw.Draw(grid_img)
    width, height = grid_img.size
    
    # Calculate cell sizes
    cell_width = width // grid_size
    cell_height = height // grid_size
    
    # Try to use a default font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except (OSError, IOError):
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
    
    # Draw vertical lines and X coordinates
    for i in range(grid_size + 1):
        x = i * cell_width
        # Draw line
        draw.line([(x, 0), (x, height)], fill="red", width=2)
        # Draw X coordinate label (skip every other for cleaner look)
        if i < grid_size and font:
            draw.text((x + 5, 5), f"X:{x}", fill="red", font=font)
    
    # Draw horizontal lines and Y coordinates
    for i in range(grid_size + 1):
        y = i * cell_height
        # Draw line
        draw.line([(0, y), (width, y)], fill="red", width=2)
        # Draw Y coordinate label
        if i < grid_size and font:
            draw.text((5, y + 5), f"Y:{y}", fill="red", font=font)
    
    # Add grid size info in corner
    info_text = f"Grid: {grid_size}x{grid_size} | Size: {width}x{height}"
    if font:
        draw.rectangle([(5, height - 30), (250, height - 5)], fill="black", outline="red")
        draw.text((10, height - 25), info_text, fill="white", font=font)
    
    return grid_img


if _SMOLAGENTS:
    class InspectScreenTool(Tool):
        """
        Takes a screenshot of the user's current desktop screen, draws a 
        numbered coordinate grid over it, and saves it so the agent can 
        see what is currently open.
        
        This tool captures:
        1. Standard screenshot saved to 'current_screen.png'
        2. Grid-overlayed version saved to 'current_screen_grid.png'
        
        The grid overlay helps vision models identify exact coordinates for
        clicking/interacting with UI elements.
        """
        name = "inspect_screen"
        description = (
            "Takes a screenshot of the user's current desktop screen, draws a "
            "numbered coordinate grid over it, and saves it so the agent can see what "
            "is currently open. Returns paths to the saved images and screen dimensions."
        )
        inputs = {}
        output_type = "string"

        def forward(self) -> str:
            """
            Capture screen and create grid overlay.
            
            Returns:
                str: Status message with saved file paths and dimensions
            """
            if not _PYAUTOGUI and not _MSS:
                return "Error: No screen capture library available. Install pyautogui or mss."
            
            try:
                width, height = _get_screen_size()
                
                # Method 1: Use PIL/pyautogui (more flexible)
                if _PYAUTOGUI:
                    # Capture standard screenshot
                    screenshot = _capture_screen_pil()
                    screenshot.save(str(SCREENSHOT_PATH))
                    
                    # Create grid overlay version
                    grid_img = _draw_grid_overlay(screenshot)
                    grid_img.save(str(GRID_SCREENSHOT_PATH))
                    
                    return (
                        f"Screenshot successfully captured. "
                        f"Standard image saved to '{SCREENSHOT_PATH}'. "
                        f"Grid system image saved to '{GRID_SCREENSHOT_PATH}'. "
                        f"Width: {width}, Height: {height}."
                    )
                
                # Method 2: Use mss (faster)
                elif _MSS:
                    png_bytes = _capture_screen_mss()
                    
                    # Save standard
                    with open(SCREENSHOT_PATH, "wb") as f:
                        f.write(png_bytes)
                    
                    # Create grid version
                    if _PIL:
                        from PIL import Image
                        img = Image.open(io.BytesIO(png_bytes))
                        grid_img = _draw_grid_overlay(img)
                        grid_img.save(str(GRID_SCREENSHOT_PATH))
                    
                    return (
                        f"Screenshot successfully captured. "
                        f"Standard image saved to '{SCREENSHOT_PATH}'. "
                        f"Grid system image saved to '{GRID_SCREENSHOT_PATH}'. "
                        f"Width: {width}, Height: {height}."
                    )
                    
            except Exception as e:
                return f"Error capturing screen: {str(e)}"

        def __repr__(self):
            return f"<InspectScreenTool: {self.name}>"


    class DesktopClickTool(Tool):
        """
        Clicks on a specific X, Y coordinate on the user's screen.
        
        This tool is used after InspectScreenTool identifies a target coordinate.
        It's typically called with the coordinates returned by a vision model
        after analyzing the grid-overlayed screenshot.
        """
        name = "desktop_click"
        description = (
            "Clicks on a specific X, Y coordinate on the user's screen. "
            "Use this after inspect_screen identifies the target element location. "
            "The coordinates should be exact pixel values from the grid system."
        )
        inputs = {
            "x": {"type": "integer", "description": "The target X coordinate pixel."},
            "y": {"type": "integer", "description": "The target Y coordinate pixel."}
        }
        output_type = "string"

        def forward(self, x: int, y: int) -> str:
            """
            Move mouse to coordinates and click.
            
            Args:
                x: X coordinate in pixels
                y: Y coordinate in pixels
            
            Returns:
                str: Status message with clicked coordinates
            """
            if not _PYAUTOGUI:
                return "Error: pyautogui not installed. Run: pip install pyautogui"
            
            try:
                # Get screen size for bounds checking
                screen_width, screen_height = _get_screen_size()
                
                # Clamp to screen bounds
                x = max(0, min(x, screen_width - 1))
                y = max(0, min(y, screen_height - 1))
                
                # Move safely and click
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                
                return f"Successfully moved mouse and clicked at coordinate ({x}, {y})."
                
            except Exception as e:
                return f"Error clicking at ({x}, {y}): {str(e)}"

        def __repr__(self):
            return f"<DesktopClickTool: {self.name}>"

else:
    # Fallback classes if smolagents not available
    class InspectScreenTool:
        """Fallback InspectScreenTool without smolagents."""
        name = "inspect_screen"
        
        def forward(self) -> str:
            if not _PYAUTOGUI and not _MSS:
                return "Error: No screen capture library available."
            
            try:
                width, height = _get_screen_size()
                
                if _PYAUTOGUI:
                    screenshot = _capture_screen_pil()
                    screenshot.save(str(SCREENSHOT_PATH))
                    grid_img = _draw_grid_overlay(screenshot)
                    grid_img.save(str(GRID_SCREENSHOT_PATH))
                
                return (
                    f"Screenshot captured. "
                    f"Standard: '{SCREENSHOT_PATH}'. "
                    f"Grid: '{GRID_SCREENSHOT_PATH}'. "
                    f"Size: {width}x{height}."
                )
            except Exception as e:
                return f"Error: {str(e)}"


    class DesktopClickTool:
        """Fallback DesktopClickTool without smolagents."""
        name = "desktop_click"
        
        def forward(self, x: int, y: int) -> str:
            if not _PYAUTOGUI:
                return "Error: pyautogui not installed."
            
            try:
                screen_width, screen_height = _get_screen_size()
                x = max(0, min(x, screen_width - 1))
                y = max(0, min(y, screen_height - 1))
                
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                
                return f"Clicked at ({x}, {y})."
            except Exception as e:
                return f"Error: {str(e)}"


# Convenience functions for direct usage
def inspect_screen() -> str:
    """Convenience function to inspect screen."""
    tool = InspectScreenTool()
    return tool.forward()


def desktop_click(x: int, y: int) -> str:
    """Convenience function to click at coordinates."""
    tool = DesktopClickTool()
    return tool.forward(x=x, y=y)


# Test when run directly
if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS Vision Tools Test")
    print("=" * 60)
    
    # Test InspectScreenTool
    print("\n[1] Testing InspectScreenTool...")
    try:
        inspect = InspectScreenTool()
        result = inspect.forward()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test DesktopClickTool
    print("\n[2] Testing DesktopClickTool...")
    try:
        click_tool = DesktopClickTool()
        # Test with center of screen
        w, h = _get_screen_size()
        result = click_tool.forward(x=w//2, y=h//2)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✓ Vision tools test complete")
