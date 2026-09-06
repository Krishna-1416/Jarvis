"""
Quick Gmail Setup and Authorization Helper for Project Jarvis.
Run this script to verify credentials.json and generate token.json with 1-click browser login.
"""

import sys
import os
from pathlib import Path

# Add project root directory to sys.path so 'tools', 'core', etc. can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(str(PROJECT_ROOT))

from tools.gmail_ops import _auth_manager

def main():
    print("=================================================================")
    print("      📧 PROJECT JARVIS - GMAIL INTEGRATION SETUP")
    print("=================================================================")
    print()
    
    cred_path = Path("data/credentials/credentials.json")
    token_path = Path("data/credentials/token.json")
    
    if not cred_path.exists():
        found = list(Path("data/credentials").glob("client_secret_*.json"))
        if not found:
            print("[!] Missing 'credentials.json' file in data/credentials/.")
            print("Please place your downloaded OAuth JSON into data/credentials/credentials.json")
            return 1

    print("[*] Found credentials. Initializing Google OAuth2 browser login...")
    print("[*] A browser window will open shortly. Please sign in and approve permissions.")
    print()
    try:
        service = _auth_manager.get_service()
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress', 'Unknown')
        print("-----------------------------------------------------------------")
        print(f"[✅] SUCCESS! Authenticated with Gmail: {email_address}")
        print(f"[✅] Token saved to: {token_path.resolve()}")
        print("-----------------------------------------------------------------")
        print()
        print("Jarvis is now ready! You can ask Jarvis:")
        print('  - "Jarvis, check my unread emails"')
        print('  - "Do I have any new messages?"')
        print('  - "Search emails from GitHub"')
        return 0
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
