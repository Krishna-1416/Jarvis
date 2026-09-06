"""
Background Email Monitoring Daemon for Project Jarvis.
Periodically checks for new unread Gmail messages, emits notification signals to HUD & Audio,
and provides email digest briefings on startup.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from tools.gmail_ops import _auth_manager, check_unread_emails

class EmailDaemon:
    def __init__(
        self,
        polling_interval_minutes: int = 10,
        on_new_emails: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
        enabled: bool = True
    ):
        self.polling_interval_sec = max(60, polling_interval_minutes * 60)
        self.on_new_emails = on_new_emails
        self.enabled = enabled
        
        self._seen_message_ids = set()
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._first_run = True

    def start(self):
        """Start the background email monitoring daemon thread."""
        if not self.enabled:
            print("[EmailDaemon] Gmail monitoring is disabled in settings.")
            return

        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._run_loop, name="JarvisEmailDaemon", daemon=True)
        self._thread.start()
        print(f"[EmailDaemon] [OK] Background Gmail monitor active (polling every {self.polling_interval_sec // 60} min).")

    def stop(self):
        """Stop daemon thread."""
        self._is_running = False

    def _run_loop(self):
        # Initial check after 10s delay to allow engine and HUD to finish boot
        time.sleep(10)
        
        while self._is_running:
            try:
                self.check_now()
            except Exception as e:
                # Log without crashing daemon
                print(f"[EmailDaemon] Poll cycle exception: {e}")
                
            # Sleep in small increments for responsive shutdown
            for _ in range(int(self.polling_interval_sec)):
                if not self._is_running:
                    break
                time.sleep(1)

    def check_now(self) -> List[Dict[str, Any]]:
        """Perform an immediate check for unread messages."""
        # Only poll if credentials exist
        if not _auth_manager.credentials_path.exists() and not _auth_manager.token_path.exists():
            return []

        try:
            results = check_unread_emails(max_results=15)
            if not results or isinstance(results, list) and "error" in results[0]:
                return []
            if isinstance(results, list) and "status" in results[0]:
                # No unread emails
                return []

            new_emails = []
            for item in results:
                msg_id = item.get("id")
                if msg_id and msg_id not in self._seen_message_ids:
                    self._seen_message_ids.add(msg_id)
                    if not self._first_run:
                        new_emails.append(item)
                    else:
                        # On first boot, populate seen cache without flooding toasts
                        self._seen_message_ids.add(msg_id)

            if self._first_run:
                self._first_run = False

            if new_emails and self.on_new_emails:
                print(f"[EmailDaemon] 📬 Received {len(new_emails)} new email(s).")
                self.on_new_emails(new_emails)

            return results
        except Exception as e:
            return []

    def get_startup_briefing(self) -> Optional[str]:
        """Generate a concise text summary of unread emails for Jarvis's startup greeting."""
        if not _auth_manager.credentials_path.exists() and not _auth_manager.token_path.exists():
            return None

        try:
            results = check_unread_emails(max_results=15)
            if not results or "error" in results[0] or "status" in results[0]:
                return None

            count = len(results)
            senders = list(dict.fromkeys([item.get('from', '').split('<')[0].strip() for item in results[:4]]))
            senders_str = ", ".join(senders[:-1]) + f", and {senders[-1]}" if len(senders) > 1 else senders[0]
            
            if count == 1:
                return f"You have 1 unread email from {senders[0]}."
            else:
                return f"You have {count} unread emails in your inbox, including messages from {senders_str}."
        except Exception:
            return None
