"""
Test App Discovery & Fuzzy Matching against all installed Windows applications.
"""
import sys
import json
import difflib
import subprocess
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def main():
    print("=== [APPS] Discovering all installed Windows Applications ===")
    p = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', 'Get-StartApps | ConvertTo-Json'], capture_output=True, text=True)
    apps = json.loads(p.stdout)
    print(f"Total Apps Discovered: {len(apps)}")
    
    app_map = {x['Name']: x['AppID'] for x in apps}
    
    def find_app(query: str):
        q = query.lower().strip()
        # Exact match
        for name, aid in app_map.items():
            if q == name.lower():
                return name, aid
        # Substring match
        for name, aid in app_map.items():
            if q in name.lower() or name.lower() in q:
                return name, aid
        # Fuzzy match
        names_lower = {k.lower(): k for k in app_map.keys()}
        matches = difflib.get_close_matches(q, list(names_lower.keys()), n=1, cutoff=0.5)
        if matches:
            orig_name = names_lower[matches[0]]
            return orig_name, app_map[orig_name]
        return None, None

    test_queries = ['brave', 'spotify', 'antigravity', 'vscode', 'code', 'whatsapp', 'calculator', 'terminal', 'settings', 'notepad', 'steam', 'discord']
    for q in test_queries:
        matched_name, aid = find_app(q)
        print(f"  Query: '{q:12s}' -> Matched: '{matched_name}' (AppID: {aid})")

    print("\n[SUCCESS] App Discovery Test Finished.")

if __name__ == "__main__":
    main()
