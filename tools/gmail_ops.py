"""
Gmail Assistant Tools for Project Jarvis.
Provides Google OAuth2 authentication, unread email checking, search, thread summarization, drafting, and confirmation-gated sending.
"""

import os
import re
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

from tools.registry import tool

# Google API client imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

class GmailAuthManager:
    """Manages Google OAuth2 Desktop App credentials and service building."""
    
    def __init__(
        self,
        credentials_path: str = "data/credentials/credentials.json",
        token_path: str = "data/credentials/token.json"
    ):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self._service = None

    def get_service(self):
        """Get or build authenticated Gmail v1 service instance."""
        if self._service is not None:
            return self._service

        if not GOOGLE_LIBS_AVAILABLE:
            raise RuntimeError("Google API libraries are not installed. Run: pip install google-api-python-client google-auth-oauthlib")

        creds = None
        # Ensure credentials directory exists
        self.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Load cached token if available
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            except Exception as e:
                print(f"[GmailAuth] Warning: Failed to load existing token ({e}). Re-authenticating...")
                creds = None

        # 2. Refresh or trigger browser authentication if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed token
                    with open(self.token_path, "w", encoding="utf-8") as token_file:
                        token_file.write(creds.to_json())
                except Exception as e:
                    print(f"[GmailAuth] Refresh failed: {e}. Re-authenticating from credentials.json...")
                    creds = None

            if not creds:
                target_cred = self.credentials_path
                if not target_cred.exists():
                    # Check for client_secret_*.json in credentials dir
                    found = list(self.credentials_path.parent.glob("client_secret_*.json"))
                    if found:
                        target_cred = found[0]
                    else:
                        raise FileNotFoundError(
                            f"Gmail OAuth 'credentials.json' not found at: '{self.credentials_path}'. "
                            "Please download your OAuth client ID credentials from Google Cloud Console "
                            "and place it at data/credentials/credentials.json."
                        )
                
                flow = InstalledAppFlow.from_client_secrets_file(str(target_cred), SCOPES)
                print("[GmailAuth] 🌐 Opening browser for one-time Google Account login...")
                creds = flow.run_local_server(port=0)
                
                # Save the new token
                with open(self.token_path, "w", encoding="utf-8") as token_file:
                    token_file.write(creds.to_json())
                print("[GmailAuth] [OK] Google authentication successful and token saved.")

        self._service = build('gmail', 'v1', credentials=creds)
        return self._service


# Global Auth Manager instance
_auth_manager = GmailAuthManager()


def _clean_body_text(payload: Dict[str, Any]) -> str:
    """Extract and sanitize plain text from Gmail message payload."""
    body_text = ""
    
    def extract_parts(parts):
        nonlocal body_text
        for part in parts:
            mime_type = part.get("mimeType", "")
            data = part.get("body", {}).get("data", "")
            
            if data:
                try:
                    decoded = base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="ignore")
                    if mime_type == "text/plain":
                        body_text += decoded + "\n"
                    elif mime_type == "text/html" and not body_text:
                        soup = BeautifulSoup(decoded, "html.parser")
                        body_text += soup.get_text(separator=" ") + "\n"
                except Exception:
                    pass
            
            if "parts" in part:
                extract_parts(part["parts"])

    if "parts" in payload:
        extract_parts(payload["parts"])
    elif "body" in payload and payload["body"].get("data"):
        try:
            raw_data = payload["body"]["data"]
            decoded = base64.urlsafe_b64decode(raw_data.encode("ASCII")).decode("utf-8", errors="ignore")
            mime_type = payload.get("mimeType", "")
            if mime_type == "text/html":
                soup = BeautifulSoup(decoded, "html.parser")
                body_text = soup.get_text(separator=" ")
            else:
                body_text = decoded
        except Exception:
            body_text = ""

    # Sanitize, collapse repeated spaces, and truncate
    lines = []
    for line in body_text.splitlines():
        cleaned_line = re.sub(r'\s+', ' ', line).strip()
        if cleaned_line:
            lines.append(cleaned_line)
    
    cleaned = "\n".join(lines)
    return cleaned[:2500] if cleaned else "[No readable text content]"


import html

def _clean_str(text: str) -> str:
    """Unescape HTML entities and ensure safe string encoding for Windows console and LLM."""
    if not text:
        return ""
    try:
        unescaped = html.unescape(text)
        return unescaped.encode('ascii', errors='ignore').decode('ascii').strip()
    except Exception:
        return str(text).strip()

@tool(name="check_unread_emails", description="Check and list up to 15 latest unread emails in the user's Gmail inbox.")
def check_unread_emails(max_results: int = 15) -> list:
    """Fetch recent unread emails with sender, subject, date, and snippet."""
    try:
        service = _auth_manager.get_service()
        results = service.users().messages().list(
            userId='me',
            q='is:unread label:INBOX',
            maxResults=min(max_results, 25)
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            return [{"status": "No unread emails found in your inbox."}]

        unread_list = []
        for msg_summary in messages:
            msg_id = msg_summary['id']
            msg = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['From', 'Subject', 'Date']).execute()
            
            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
            unread_list.append({
                "id": msg_id,
                "from": _clean_str(headers.get('From', 'Unknown Sender')),
                "subject": _clean_str(headers.get('Subject', '(No Subject)')),
                "date": _clean_str(headers.get('Date', 'Unknown Date')),
                "snippet": _clean_str(msg.get('snippet', ''))
            })

        return unread_list
    except FileNotFoundError as e:
        return [{"error": str(e)}]
    except Exception as e:
        return [{"error": f"Failed to check unread emails: {str(e)}"}]


@tool(name="search_emails", description="Search Gmail inbox using standard keywords, senders, or query filters (e.g. query='from:github' or query='invoice').")
def search_emails(query: str, max_results: int = 15) -> list:
    """Search emails matching a query string."""
    try:
        service = _auth_manager.get_service()
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=min(max_results, 25)
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return [{"status": f"No emails found matching query: '{query}'"}]

        found = []
        for msg_summary in messages:
            msg_id = msg_summary['id']
            msg = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['From', 'Subject', 'Date']).execute()
            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
            found.append({
                "id": msg_id,
                "from": _clean_str(headers.get('From', 'Unknown Sender')),
                "subject": _clean_str(headers.get('Subject', '(No Subject)')),
                "date": _clean_str(headers.get('Date', 'Unknown Date')),
                "snippet": _clean_str(msg.get('snippet', ''))
            })

        return found
    except Exception as e:
        return [{"error": f"Email search failed: {str(e)}"}]



@tool(name="read_email_content", description="Read the full body text of a specific email by its ID.")
def read_email_content(email_id: str) -> dict:
    """Fetch and return full email content for summarization."""
    try:
        service = _auth_manager.get_service()
        msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()
        
        headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
        body = _clean_body_text(msg.get('payload', {}))
        
        return {
            "id": email_id,
            "from": headers.get('From', 'Unknown Sender'),
            "to": headers.get('To', ''),
            "subject": headers.get('Subject', '(No Subject)'),
            "date": headers.get('Date', ''),
            "body": body
        }
    except Exception as e:
        return {"error": f"Failed to read email '{email_id}': {str(e)}"}


@tool(name="draft_email", description="Create an email draft in Gmail without sending it immediately.")
def draft_email(to: str, subject: str, body: str) -> dict:
    """Create a draft message in user's Gmail."""
    try:
        service = _auth_manager.get_service()
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw_message}}
        ).execute()
        
        return {
            "status": "Draft created successfully in Gmail.",
            "draft_id": draft.get('id'),
            "to": to,
            "subject": subject
        }
    except Exception as e:
        return {"error": f"Failed to create draft: {str(e)}"}


@tool(name="send_email_confirmed", description="Send an email to a recipient after explicit user confirmation has been granted.")
def send_email_confirmed(to: str, subject: str, body: str) -> dict:
    """Send an email via Gmail API."""
    try:
        service = _auth_manager.get_service()
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent_msg = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return {
            "status": "Email sent successfully!",
            "message_id": sent_msg.get('id'),
            "to": to,
            "subject": subject
        }
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}
