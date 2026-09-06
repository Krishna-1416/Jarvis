"""
Diagnostic test for Windows Window, Tab, and Settings Automation.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from core.router import BrainRouter

def main():
    print("=== [USER COMMANDS TEST] Testing Tab, Settings & Explorer Intents ===")
    
    router = BrainRouter()
    
    test_queries = [
        "Jarvis, close the whatsapp tab from the brave",
        "Jarvis, close the tab in brave",
        "Jarvis, open mouse settings",
        "Jarvis, open sound settings",
        "Jarvis, close file explorer",
    ]
    for q in test_queries:
        print(f"\nUser: '{q}'")
        reply = router.chat(q)
        print(f"Jarvis: {reply}")

    print("\n[SUCCESS] User Commands Diagnostic Completed.")

if __name__ == "__main__":
    main()
