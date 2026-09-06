"""
Conversation Context & Sliding History Manager for Project Jarvis.
Maintains short-term chat turns, formats the Jarvis system persona, and prevents context bloat.
"""

import time
from typing import List, Dict, Any, Optional
from core.config import config

SYSTEM_PROMPT_TEMPLATE = """You are Jarvis, a sophisticated, highly intelligent, and loyal personal AI desktop companion for Windows.
You speak in a polite, concise, slightly British demeanor (like Iron Man's JARVIS). Address the user as 'sir' when appropriate.

CURRENT SYSTEM CONTEXT:
- Local Time: {current_time}
- Date: {current_date}
- Platform: Windows (x64)

GUIDELINES:
1. Always be direct, sharp, proactive, and concise. Address the user as 'sir' when appropriate.
2. You have access to powerful local and online tools:
   - Gmail & Inbox: 'check_unread_emails' (check unread messages, fetch up to 25 emails), 'search_emails' (search inbox by sender/subject/query), 'read_email_content' (read full email body), 'draft_email', 'send_email_confirmed'.
     * CRITICAL GMAIL RULE: Your Google OAuth is ALREADY authenticated. NEVER ask the user for their email address or password. When the user asks to check emails, read unread mail, search messages, or check more emails, IMMEDIATELY call 'check_unread_emails' or 'search_emails'. When the user asks to read a specific email or get details on a message, call 'read_email_content' or 'search_emails'.
   - Media & YouTube: 'play_on_youtube' (search/play any song or video on YouTube), 'play_on_spotify' (search/play music on Spotify).
   - Websites & Browser: 'open_website' (e.g. YouTube, WhatsApp Web, ChatGPT, GitHub, Netflix, Reddit, Amazon) and 'search_and_open_in_browser' (search Google in browser).
   - Applications: 'launch_application' (e.g. Spotify, VS Code, Notepad, Calculator, Terminal, Settings).
   - System & Windows Control: 'set_system_volume', 'get_system_volume', 'toggle_audio_mute', 'set_system_brightness', 'lock_workstation', 'get_system_stats', 'close_active_window', 'minimize_active_window'.
   - Research & Web Scraping: 'deep_web_research', 'scrape_and_analyze_url', 'web_search'.
   - File & Terminal: 'list_directory_contents', 'read_text_file', 'write_text_file', 'search_files', 'run_powershell_command'.
   - Memory: 'remember_user_fact', 'recall_user_facts'.
3. CRITICAL ACTION RULES:
   - When asked to perform an action (check email, play music, open app, adjust settings, research a topic), DO NOT talk about doing it — IMMEDIATELY call the appropriate tool.
   - When tool results are returned, synthesize them into a crisp, clean summary with bullet points.
   - If the user asks a follow-up about a previous result (e.g. "tell me more about the Oxford email" or "read that message"), proactively search or read the content using your tools.
4. If the user is just chatting or asking a general knowledge question, answer directly with wit and precision without tool calls.
"""

class ContextManager:
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.history: List[Dict[str, Any]] = []

    def get_system_prompt(self, extra_memory_context: Optional[str] = None) -> str:
        """Assemble dynamic system prompt with real-time timestamp and optional memory facts."""
        now = time.localtime()
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            current_time=time.strftime("%I:%M %p", now),
            current_date=time.strftime("%A, %B %d, %Y", now)
        )
        if extra_memory_context:
            prompt += f"\nRELEVANT USER FACTS & LONG-TERM MEMORY:\n{extra_memory_context}\n"
        return prompt

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})
        self._trim_history()

    def add_assistant_message(self, content: Optional[str] = None, tool_calls: Optional[List[Any]] = None):
        msg: Dict[str, Any] = {"role": "assistant"}
        if content is not None:
            msg["content"] = content
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.history.append(msg)
        self._trim_history()

    def add_tool_message(self, tool_call_id: str, tool_name: str, content: str):
        self.history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": content
        })

    def get_compiled_messages(self, extra_memory_context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return full messages list starting with system prompt."""
        system_msg = {"role": "system", "content": self.get_system_prompt(extra_memory_context)}
        return [system_msg] + self.history

    def _trim_history(self):
        """Keep history within configured max turns to maintain sub-second latency."""
        # Count user turns
        user_turn_indices = [i for i, m in enumerate(self.history) if m.get("role") == "user"]
        if len(user_turn_indices) > self.max_turns:
            cutoff = user_turn_indices[-self.max_turns]
            self.history = self.history[cutoff:]

    def clear(self):
        self.history = []
