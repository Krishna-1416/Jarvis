"""
Live Hot-Reloader Daemon for Project Jarvis.
Monitors source code files and instantly restarts Jarvis on any change.
Usage: python dev.py [--cli]
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent

IGNORE_DIRS = {
    "venv", ".git", "data", "models", "__pycache__", 
    ".system_generated", "scratch", ".gemini", "logs", ".pytest_cache"
}

WATCH_EXTENSIONS = {".py", ".yaml", ".yml"}

class JarvisReloadHandler(FileSystemEventHandler):
    def __init__(self, reload_callback):
        self.reload_callback = reload_callback
        self.last_reload_time = 0.0
        self.debounce_sec = 0.5

    def on_any_event(self, event):
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        # Check if any parent dir is in ignore list
        if any(part in IGNORE_DIRS for part in path.parts):
            return

        # Check extension
        if path.suffix not in WATCH_EXTENSIONS:
            return

        now = time.time()
        if now - self.last_reload_time > self.debounce_sec:
            self.last_reload_time = now
            rel_path = path.relative_to(BASE_DIR) if path.is_relative_to(BASE_DIR) else path.name
            print(f"\n[HotReload] 🔄 Detected change in '{rel_path}'. Restarting Jarvis...")
            self.reload_callback()

class HotReloadManager:
    def __init__(self, cli_args: list[str]):
        self.cli_args = cli_args
        self.process = None
        self.python_exe = sys.executable

    def start_jarvis(self):
        """Start Jarvis subprocess."""
        cmd = [self.python_exe, str(BASE_DIR / "main.py")] + self.cli_args
        self.process = subprocess.Popen(cmd)

    def stop_jarvis(self):
        """Force terminate running Jarvis process tree."""
        if self.process and self.process.poll() is None:
            try:
                # Force kill process and all children on Windows
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self.process.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=1.0)
                except Exception:
                    pass
            self.process = None

    def restart(self):
        """Kill and restart process."""
        self.stop_jarvis()
        time.sleep(0.3)
        self.start_jarvis()

    def run(self):
        """Start watcher and supervisor loop."""
        print("=================================================================")
        print("   🔥 PROJECT JARVIS - LIVE HOT RELOAD SERVER ACTIVE")
        print(f"   Watching: {BASE_DIR}")
        print("   Auto-reloads on edits in: core/, tools/, ui/, audio/, memory/, config/")
        print("=================================================================\n")

        self.start_jarvis()

        event_handler = JarvisReloadHandler(self.restart)
        observer = Observer()
        observer.schedule(event_handler, str(BASE_DIR), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1.0)
                # If child process exited unexpectedly and wasn't killed by reload
                if self.process and self.process.poll() is not None:
                    pass
        except KeyboardInterrupt:
            print("\n[HotReload] 🛑 Stopping Hot Reload Server...")
            observer.stop()
            self.stop_jarvis()
        observer.join()

def main():
    forward_args = [a for a in sys.argv[1:] if a not in ("--reload", "-r")]
    manager = HotReloadManager(forward_args)
    manager.run()

if __name__ == "__main__":
    main()
