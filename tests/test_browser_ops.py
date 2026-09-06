"""
Diagnostic test for Browser Operations & Multi-Browser Targeting (Brave, Chrome, Edge).
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from tools.browser_ops import _find_browser_exe, open_website, play_on_youtube
from core.router import BrainRouter

def main():
    print("=== [BROWSER OPS] Testing Gmail & Multi-Browser Targeting ===")
    
    # 1. Test Browser Executable Resolution
    print("\n1. Resolving Browser Executables on Windows:")
    for b in ["brave", "chrome", "edge", "firefox"]:
        exe = _find_browser_exe(b)
        print(f"  Browser '{b:8s}' -> Path: {exe}")

    # 2. Test BrainRouter Intent Dispatch
    print("\n2. Testing BrainRouter Intent Dispatch:")
    router = BrainRouter()
    
    test_queries = [
        "Jarvis, check my gmail on brave",
        "Jarvis, open gmail in brave",
        "Jarvis, check my mail",
        "Jarvis, open youtube on brave",
    ]
    for q in test_queries:
        print(f"\nUser: '{q}'")
        reply = router.chat(q)
        print(f"Jarvis: {reply}")

    print("\n[SUCCESS] Browser Ops Diagnostic Completed.")

if __name__ == "__main__":
    main()
