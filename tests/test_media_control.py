"""
Diagnostic test for Media Controls and Video/Song Navigation.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from core.router import BrainRouter

def main():
    print("=== [MEDIA] Testing Play / Pause / Resume / Next / Prev Controls ===")
    
    router = BrainRouter()
    
    test_queries = [
        "Jarvis, pause the video",
        "Jarvis, resume the video",
        "Jarvis, play the song",
        "Jarvis, unpause",
        "Jarvis, next video",
        "Jarvis, forward the video",
        "Jarvis, previous video",
        "Jarvis, fast forward",
        "Jarvis, rewind",
    ]
    
    for q in test_queries:
        print(f"\nUser: '{q}'")
        reply = router.chat(q)
        print(f"Jarvis: {reply}")

    print("\n[SUCCESS] Media Navigation Diagnostic Completed.")

if __name__ == "__main__":
    main()
