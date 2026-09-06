"""
Unit & Mock Verification Tests for Gmail Assistant Tools.
Verifies payload decoding, tool schemas, error handling, and mock API execution.
"""

import unittest
from unittest.mock import MagicMock, patch
import base64

from tools.gmail_ops import _clean_body_text, check_unread_emails, search_emails, read_email_content, draft_email, send_email_confirmed, _auth_manager
from tools.registry import registry

class TestGmailOps(unittest.TestCase):

    def test_clean_body_text_plain(self):
        sample_text = "Hello Krishna, here is your project update."
        encoded = base64.urlsafe_b64encode(sample_text.encode("utf-8")).decode("utf-8")
        payload = {
            "mimeType": "text/plain",
            "body": {"data": encoded}
        }
        result = _clean_body_text(payload)
        self.assertEqual(result, sample_text)

    def test_clean_body_text_html(self):
        sample_html = "<html><body><h1>Update</h1><p>Your server is <b>ready</b>.</p></body></html>"
        encoded = base64.urlsafe_b64encode(sample_html.encode("utf-8")).decode("utf-8")
        payload = {
            "mimeType": "text/html",
            "body": {"data": encoded}
        }
        result = _clean_body_text(payload)
        self.assertIn("Update", result)
        self.assertIn("Your server is ready", result)

    def test_tools_registered(self):
        schemas = registry.get_all_schemas()
        tool_names = [t["function"]["name"] for t in schemas]
        self.assertIn("check_unread_emails", tool_names)
        self.assertIn("search_emails", tool_names)
        self.assertIn("read_email_content", tool_names)
        self.assertIn("draft_email", tool_names)
        self.assertIn("send_email_confirmed", tool_names)

    @patch.object(_auth_manager, 'get_service')
    def test_check_unread_emails_mock(self, mock_get_service):
        # Mock service
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg_001"}, {"id": "msg_002"}]
        }
        mock_service.users().messages().get().execute.side_effect = [
            {
                "id": "msg_001",
                "snippet": "Meeting tomorrow at 10 AM",
                "payload": {"headers": [{"name": "From", "value": "Alice <alice@test.com>"}, {"name": "Subject", "value": "Team Sync"}, {"name": "Date", "value": "Today"}]}
            },
            {
                "id": "msg_002",
                "snippet": "Your AWS Invoice is ready",
                "payload": {"headers": [{"name": "From", "value": "AWS <no-reply@aws.com>"}, {"name": "Subject", "value": "Invoice #123"}, {"name": "Date", "value": "Yesterday"}]}
            }
        ]

        results = check_unread_emails(max_results=5)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "msg_001")
        self.assertEqual(results[0]["from"], "Alice <alice@test.com>")
        self.assertEqual(results[0]["subject"], "Team Sync")

    @patch.object(_auth_manager, 'get_service')
    def test_draft_email_mock(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_service.users().drafts().create().execute.return_value = {"id": "draft_999"}

        res = draft_email(to="test@example.com", subject="Test Draft", body="Hello World")
        self.assertIn("status", res)
        self.assertEqual(res["draft_id"], "draft_999")

if __name__ == "__main__":
    unittest.main()
