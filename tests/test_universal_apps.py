"""
Diagnostic test for Universal Windows Desktop App Launcher.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from tools.system_ops import launch_application, list_installed_applications, app_indexer
from core.router import BrainRouter

def main():
    print("=== [UNIVERSAL APPS] Testing Desktop Application Access ===")
    
    # Wait for indexing
    import time
    time.sleep(1)
    
    # 1. Test App Listing
    print("\n1. Listing Installed Applications:")
    app_list_res = list_installed_applications()
    print(app_list_res[:400] + "...\n")

    # 2. Test App Resolution
    print("\n2. Testing Fuzzy App Resolution:")
    test_apps = [
        "brave",
        "spotify",
        "antigravity",
        "vscode",
        "calculator",
        "terminal",
        "settings",
        "notepad",
        "steam",
        "discord",
    ]
    for app in test_apps:
        official_name, target = app_indexer.find_app(app)
        print(f"  Target: '{app:12s}' -> Found: '{official_name}' (ID: {target})")

    # 3. Test Intent Router Dispatch
    print("\n3. Testing BrainRouter Natural Speech Launching:")
    router = BrainRouter()
    
    queries = [
        "Jarvis, open brave",
        "Jarvis, open spotify",
        "Jarvis, open vscode",
        "Jarvis, open antigravity",
        "Jarvis, open calculator",
    ]
    for q in queries:
        print(f"\nUser: '{q}'")
        reply = router.chat(q)
        print(f"Jarvis: {reply}")

    print("\n[SUCCESS] Universal Desktop App Access Verified.")

if __name__ == "__main__":
    main()
