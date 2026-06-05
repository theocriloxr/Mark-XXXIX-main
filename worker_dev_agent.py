#!/usr/bin/env python3
"""
Worker script for DevAgent operations.
Runs in a separate process to prevent blocking the main WebSocket event loop.

Usage:
    python worker_dev_agent.py --task "<project description>" --language python --timeout 30

Communication:
    - Reads task from JSON file: worker_task.json
    - Writes result to JSON file: worker_result.json
    
Or via command line arguments for simple tasks.
"""

import argparse
import json
import sys
import threading
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()


def run_dev_agent(description: str, language: str = "python", project_name: str = "", timeout: int = 30) -> dict:
    """
    Run the development agent in a separate process.
    Returns a dict with status and result.
    """
    # Import here to avoid circular imports
    from actions.dev_agent import dev_agent
    
    result = {
        "status": "running",
        "result": "",
        "error": ""
    }
    
    try:
        # Create a mock player object for logging
        class MockPlayer:
            def __init__(self):
                self.logs = []
            
            def write_log(self, msg):
                self.logs.append(msg)
                print(f"[DevAgent] {msg}")
        
        class MockSpeak:
            def __init__(self):
                self.messages = []
            
            def __call__(self, msg):
                self.messages.append(msg)
                print(f"[Jarvis] {msg}")
        
        player = MockPlayer()
        speak = MockSpeak()
        
        parameters = {
            "description": description,
            "language": language,
            "project_name": project_name,
            "timeout": str(timeout)
        }
        
        # Run in thread to allow for interruption
        output = {"result": None, "error": None}
        
        def run_in_thread():
            try:
                output["result"] = dev_agent(
                    parameters=parameters,
                    player=player,
                    speak=speak
                )
            except Exception as e:
                output["error"] = str(e)
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        thread.join(timeout=timeout * 2)  # Allow extra time
        
        if thread.is_alive():
            result["status"] = "timeout"
            result["error"] = f"Task timed out after {timeout * 2}s"
        elif output.get("error"):
            result["status"] = "error"
            result["error"] = output["error"]
        else:
            result["status"] = "success"
            result["result"] = output.get("result", "Done")
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Worker for DevAgent operations")
    parser.add_argument("--task", type=str, required=True, help="Project description")
    parser.add_argument("--language", type=str, default="python", help="Programming language")
    parser.add_argument("--project_name", type=str, default="", help="Project name")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--task_file", type=str, help="JSON file to read task from")
    parser.add_argument("--result_file", type=str, help="JSON file to write result to")
    
    args = parser.parse_args()
    
    # If task_file is provided, read from it
    if args.task_file:
        try:
            with open(args.task_file, "r") as f:
                task_data = json.load(f)
            args.task = task_data.get("description", args.task)
            args.language = task_data.get("language", args.language)
            args.project_name = task_data.get("project_name", args.project_name)
            args.timeout = task_data.get("timeout", args.timeout)
        except Exception as e:
            print(f"Error reading task file: {e}")
            sys.exit(1)
    
    # Run the dev agent
    result = run_dev_agent(
        description=args.task,
        language=args.language,
        project_name=args.project_name,
        timeout=args.timeout
    )
    
    # If result_file is provided, write to it
    if args.result_file:
        try:
            with open(args.result_file, "w") as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            print(f"Error writing result file: {e}")
            sys.exit(1)
    
    # Print result to stdout for subprocess communication
    print(json.dumps(result, indent=2))
    
    if result["status"] == "error":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
