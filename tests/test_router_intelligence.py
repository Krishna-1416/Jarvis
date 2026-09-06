import json
import unittest
from unittest.mock import patch
from core.router import BrainRouter

class TestBrainRouterIntelligence(unittest.TestCase):
    def setUp(self):
        self.router = BrainRouter()

    @patch('tools.registry.ToolRegistry.execute_tool_call')
    def test_mail_fast_paths(self, mock_tool):
        mock_tool.return_value = json.dumps([
            {"from": "Test Sender", "subject": "Quarterly Report", "date": "Today", "snippet": "..."}
        ])
        phrases = [
            "check for the more unread mails",
            "check my unread emails",
            "what about my mail",
            "check inbox"
        ]
        for p in phrases:
            reply = self.router._try_deterministic_intent(p)
            self.assertIsNotNone(reply, f"Failed on phrase: '{p}'")
            self.assertTrue("unread email" in reply.lower() or "inbox" in reply.lower() or "notice" in reply.lower())

if __name__ == "__main__":
    unittest.main()

