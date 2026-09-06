"""
Diagnostic test for Windows System Ops (Volume, Brightness, Power, Battery).
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from core.router import BrainRouter

def main():
    print("=== [SYSTEM OPS] Testing Natural Phrasing for Volume & Brightness ===")
    
    router = BrainRouter()
    
    test_queries = [
        "Jarvis, set the volume to 45%",
        "Jarvis, increase the volume",
        "Jarvis, mute the audio",
        "Jarvis, unmute",
        "Jarvis, set the brightness to 65%",
        "Jarvis, increase the brightness",
        "Jarvis, dim the screen",
        "Jarvis, what is my cpu usage?",
    ]
    
    for q in test_queries:
        print(f"\nUser: '{q}'")
        reply = router.chat(q)
        print(f"Jarvis: {reply}")

    print("\n[SUCCESS] Natural Phrasing System Ops Test Completed.")

if __name__ == "__main__":
    main()
