"""
Project Jarvis - Personal AI Desktop Assistant for Windows.
Main Entry Point supporting GUI mode (Floating HUD + System Tray) and Headless CLI mode.
"""

import sys
import time
import signal
import argparse

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure UTF-8 for Windows PowerShell output
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Project Jarvis - Windows AI Assistant")
    parser.add_argument("--cli", action="store_true", help="Run in headless terminal/CLI mode without PyQt6 GUI")
    parser.add_argument("--reload", "-r", action="store_true", help="Run with automatic live hot-reloading on file edits")
    args, unknown = parser.parse_known_args()

    if args.reload:
        from dev import HotReloadManager
        forward_args = [a for a in sys.argv[1:] if a not in ("--reload", "-r")]
        manager = HotReloadManager(forward_args)
        manager.run()
        return

    if not args.cli:
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.4)
            sock.connect(('127.0.0.1', 54123))
            sock.sendall(b"SUMMON\n")
            sock.close()
            print("[Jarvis] ℹ️ Jarvis is already running in the background. Brought window to front.")
            return
        except Exception:
            pass

    print("=" * 65)
    print("   [JARVIS] PROJECT JARVIS - PERSONAL AI DESKTOP ASSISTANT")
    print("   Hardware Target: NVIDIA RTX 3050A (4GB VRAM)")
    print("=" * 65)

    if args.cli:
        print("[Mode] Starting in Headless CLI Mode...")
        from core.engine import JarvisEngine
        
        engine = JarvisEngine(
            on_status_change=lambda s: print(f"[STATUS] >>> {s}"),
            on_transcript=lambda spk, txt: print(f"[{spk.upper()}]: {txt}")
        )

        def sigint_handler(sig, frame):
            print("\n[Jarvis] Shutting down...")
            engine.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, sigint_handler)
        engine.start()

        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            sigint_handler(None, None)
    else:
        print("[Mode] Starting in Desktop GUI Mode (Floating HUD + System Tray)...")
        from ui.app import run_app
        run_app()

if __name__ == "__main__":
    main()
