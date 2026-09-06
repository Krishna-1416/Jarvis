"""
Hybrid Brain Router for Project Jarvis.
Orchestrates reasoning via local Ollama (qwen2.5:1.5b), deterministic high-speed intent routing,
and dynamic tool execution loops with automatic Cloud API fallback support.
"""

import os
import re
import json
import time
from typing import Optional, List, Dict, Any, Tuple
import ollama
from openai import OpenAI

from core.config import config
from core.context_manager import ContextManager
from tools.registry import registry
from tools import *  # Ensure all tools are registered
from tools.browser_ops import play_on_youtube, play_on_spotify, open_website, search_and_open_in_browser

class BrainRouter:
    def __init__(self, context_manager: Optional[ContextManager] = None):
        self.context_manager = context_manager or ContextManager()
        self.local_model = config.settings.get("llm", {}).get("local_model", "qwen3.5:4b")
        self.fallback_model = config.settings.get("llm", {}).get("fallback_model", "qwen2.5:1.5b")
        self.ollama_url = config.ollama_url
        self.ollama_client = ollama.Client(host=self.ollama_url)
        
        # --- Cloud API Configuration (Discarded in favor of 100% Local Offline Operation) ---
        # self.cloud_enabled = config.settings.get("llm", {}).get("cloud_fallback", {}).get("enabled", False)
        # self.cloud_provider = config.settings.get("llm", {}).get("cloud_fallback", {}).get("provider", "openai")
        # self.cloud_model = config.settings.get("llm", {}).get("cloud_fallback", {}).get("model", "gpt-4o-mini")
        # self.cloud_api_key = os.getenv("OPENAI_API_KEY", "")

    # def _should_escalate_to_cloud(self, user_text: str) -> bool:
    #     """[COMMENTED OUT] Cloud escalation disabled - Jarvis runs 100% locally."""
    #     if not getattr(self, "cloud_enabled", False) or not getattr(self, "cloud_api_key", ""):
    #         return False
    #     lower = user_text.lower()
    #     if "use cloud" in lower or "deep reasoning" in lower or "complex analysis" in lower:
    #         return True
    #     return False


    def _try_deterministic_intent(self, user_query: str) -> Optional[str]:
        """
        Fast-path deterministic intent matcher for media, websites, volume, and email commands.
        Delivers 0ms reasoning latency and 100% accuracy for clear voice commands.
        """
        q_clean = user_query.strip().lower()
        # Strip greeting prefixes
        q_clean = re.sub(r'^(jarvis|hey jarvis|hello jarvis|please|could you|can you)\s*[,:]?\s*', '', q_clean).strip()

        # 1. YouTube playback: "play loser on youtube", "open loser on youtube", "watch interstellar trailer on youtube"
        yt_match = re.search(r'^(?:open|play|watch|search)\s+(.+?)\s+(?:on|in)\s+youtube\b', q_clean)
        if yt_match:
            song = yt_match.group(1).strip()
            res = play_on_youtube(song)
            return f"Opening '{song}' on YouTube for you, sir."

        if q_clean.endswith(" on youtube") or q_clean.endswith(" in youtube"):
            song = re.sub(r'\s+(?:on|in)\s+youtube$', '', q_clean)
            song = re.sub(r'^(open|play|watch|search)\s+', '', song).strip()
            res = play_on_youtube(song)
            return f"Playing '{song}' on YouTube right away, sir."

        # 2. Spotify playback: "play starboy on spotify", "open bohemian rhapsody on spotify"
        sp_match = re.search(r'^(?:open|play|search)\s+(.+?)\s+(?:on|in)\s+spotify\b', q_clean)
        if sp_match:
            song = sp_match.group(1).strip()
            res = play_on_spotify(song)
            return f"Searching and playing '{song}' on Spotify, sir."

        # Specific browser targeting: "open gmail in browser", "open youtube on brave", "open github on chrome"
        browser_match = re.search(r'^(?:open|launch|view|show)\s+(.+?)\s+(?:on|in)\s+(brave|chrome|edge|firefox|browser)\b', q_clean)
        if browser_match:
            site = browser_match.group(1).strip()
            browser_name = browser_match.group(2).strip()
            site = re.sub(r'\b(my|the)\b', '', site).strip()
            res = open_website(site, browser=browser_name)
            return f"Opening {site.title()} in {browser_name.title()} for you, sir."

        # Browser opening for Gmail only when explicit "open gmail in browser" or "open mail website"
        if re.search(r'^(?:open|launch)\s*(?:my|the)?\s*(?:gmail|email|mail)\s*(?:website|in\s*browser|in\s*brave|tab)\b', q_clean):
            res = open_website("gmail", browser="brave")
            return "Opening your Gmail in Brave right away, sir."

        # 2.5 Media Playback Toggle & Resume (Play / Pause / Resume / Unpause)
        if re.search(r'^(pause|resume|unpause|continue|play)\s*(?:the|my)?\s*(?:video|song|music|playback|track|playing|media)?$', q_clean):
            res = registry.execute_tool_call("media_play_pause", {})
            action = "Resumed" if any(w in q_clean for w in ("resume", "unpause", "continue", "play")) else "Paused"
            return f"{action} media playback, sir."

        if re.search(r'\b(pause\s+(?:the\s+)?(?:video|song|music|youtube|spotify|playback)|resume\s+(?:the\s+)?(?:video|song|music|playback)|unpause|continue\s+playback)\b', q_clean):
            res = registry.execute_tool_call("media_play_pause", {})
            action = "Resumed" if any(w in q_clean for w in ("resume", "unpause", "continue")) else "Paused"
            return f"{action} media playback, sir."

        if re.search(r'\b(next\s+(?:video|track|song|music)|skip\s+(?:the\s+)?(?:video|track|song|music)|forward\s+(?:the\s+)?video|skip\s+track|next\s+one)\b', q_clean):
            res = registry.execute_tool_call("media_next_track", {})
            return "Skipped to the next video/track, sir."

        if re.search(r'\b(previous\s+(?:video|track|song|music)|prev\s+(?:video|track|song)|last\s+(?:video|song)|go\s+back|replay\s+(?:video|song))\b', q_clean):
            res = registry.execute_tool_call("media_previous_track", {})
            return "Returned to the previous video/track, sir."

        if re.search(r'\b(fast\s*forward|forward\s+\d+\s+seconds?|skip\s+ahead)\b', q_clean):
            res = registry.execute_tool_call("media_fast_forward", {"seconds": 5})
            return "Fast-forwarded video, sir."

        if re.search(r'\b(rewind|go\s+back\s+\d+\s+seconds?|step\s+back)\b', q_clean):
            res = registry.execute_tool_call("media_rewind", {"seconds": 5})
            return "Rewound video, sir."

        if re.search(r'\b(stop\s+music|stop\s+playback|stop\s+media|stop\s+playing)\b', q_clean):
            res = registry.execute_tool_call("media_stop", {})
            return "Stopped playback, sir."

        # 3. Volume Commands (Natural Phrasing)
        vol_set = re.search(r'\b(?:set|change|adjust|put|make|turn)?\s*(?:the|my)?\s*(?:audio|sound|master)?\s*volume\s*(?:to|at|is)?\s*(\d{1,3})\s*%?\b', q_clean)
        if vol_set:
            lvl = int(vol_set.group(1))
            res = registry.execute_tool_call("set_system_volume", {"level": lvl})
            return f"Master volume set to {lvl}%, sir."

        if re.search(r'\b(increase|raise|boost|turn up|crank up|up|higher|louder)\s*(?:the|my)?\s*(?:audio|sound|master)?\s*volume\b|\b(volume\s+up|louder)\b', q_clean):
            res = registry.execute_tool_call("increase_system_volume", {"delta": 10})
            return f"{res} sir."

        if re.search(r'\b(decrease|lower|reduce|turn down|down|quieter|softer)\s*(?:the|my)?\s*(?:audio|sound|master)?\s*volume\b|\b(volume\s+down|quieter|softer)\b', q_clean):
            res = registry.execute_tool_call("decrease_system_volume", {"delta": 10})
            return f"{res} sir."

        if "unmute" in q_clean:
            res = registry.execute_tool_call("toggle_audio_mute", {"mute": False})
            return "Audio unmuted, sir."

        if re.search(r'\b(mute|silence)\s*(?:the)?\s*(?:audio|sound|speakers|pc)?\b', q_clean):
            res = registry.execute_tool_call("toggle_audio_mute", {"mute": True})
            return "Audio muted, sir."

        # 4. Brightness Commands (Natural Phrasing)
        bri_set = re.search(r'\b(?:set|change|adjust|put|make|turn)?\s*(?:the|my)?\s*(?:screen|display)?\s*brightness\s*(?:to|at|is)?\s*(\d{1,3})\s*%?\b', q_clean)
        if bri_set:
            lvl = int(bri_set.group(1))
            res = registry.execute_tool_call("set_system_brightness", {"level": lvl})
            return f"Screen brightness set to {lvl}%, sir."

        if re.search(r'\b(increase|raise|boost|turn up|up|higher|brighter)\s*(?:the|my)?\s*(?:screen|display)?\s*brightness\b|\b(brightness\s+up|brighter)\b', q_clean):
            res = registry.execute_tool_call("increase_system_brightness", {"delta": 10})
            return f"{res} sir."

        if re.search(r'\b(decrease|lower|reduce|turn down|down)\s*(?:the|my)?\s*(?:screen|display)?\s*brightness\b|\b(brightness\s+down|dim\s*(?:the|my)?\s*(?:screen|display)|dimmer)\b', q_clean):
            res = registry.execute_tool_call("decrease_system_brightness", {"delta": 10})
            return f"{res} sir."

        # 5. System Stats & Diagnostics
        if any(phrase in q_clean for phrase in ("system stats", "cpu usage", "battery status", "system status", "ram usage", "how is my system", "how is the system")):
            res = registry.execute_tool_call("get_system_stats", {})
            return f"Here are your system parameters, sir:\n{res}"

        # 6. Lock Workstation
        if re.search(r'\block\s*(?:the)?\s*(?:workstation|screen|computer|pc|desktop)\b', q_clean):
            res = registry.execute_tool_call("lock_workstation", {})
            return "Workstation locked for your security, sir."

        # 7. Browser Tab Controls
        if re.search(r'\b(close|exit|kill|shut)\b.*\btabs?\b', q_clean) or "tab from" in q_clean or "tab in" in q_clean:
            res = registry.execute_tool_call("close_active_tab", {})
            return "Closed the active browser tab, sir."

        if re.search(r'\b(reopen|restore|undo\s+close)\s*(?:the\s+)?(?:browser\s+)?tabs?\b', q_clean):
            res = registry.execute_tool_call("reopen_closed_tab", {})
            return "Reopened the previous browser tab, sir."

        if re.search(r'\bnext\s+tab\b', q_clean):
            res = registry.execute_tool_call("next_browser_tab", {})
            return "Switched to next tab, sir."

        if re.search(r'\bprevious\s+tab\b', q_clean):
            res = registry.execute_tool_call("previous_browser_tab", {})
            return "Switched to previous tab, sir."

        # 8. Close / Exit Application or Window
        if re.search(r'\b(close|exit|quit|kill)\s+(?:this|the|current)\s+(?:app|application|window|program)\b', q_clean) or q_clean in ("close window", "exit window", "close app", "exit app"):
            res = registry.execute_tool_call("close_active_window", {})
            return "Closed the active window, sir."

        close_app_match = re.match(r'^(?:close|exit|quit|kill|terminate)\s+(.+?)(?:\s+for\s+me)?$', q_clean)
        if close_app_match:
            target = close_app_match.group(1).strip()
            if target not in ("this", "the window", "tab", "the tab", "audio", "music", "video", "media"):
                res = registry.execute_tool_call("close_application_by_name", {"app_name": target})
                return f"{res} sir."

        if re.search(r'\b(minimize|hide)\s*(?:the)?\s*(?:window|screen|app)?\b', q_clean):
            res = registry.execute_tool_call("minimize_active_window", {})
            return "Minimized window, sir."

        # 9. Direct Website / App Launch: "open youtube", "open github", "open whatsapp", "open spotify", "open chatgpt"
        open_match = re.match(r'^(?:open|launch|start)\s+(.+?)(?:\s+for\s+me)?$', q_clean)
        if open_match:
            target = open_match.group(1).strip()
            target = re.sub(r'\s+for\s+me$', '', target).strip()
            res = registry.execute_tool_call("launch_application", {"app_name": target})
            return f"Opening {target.title()} right now, sir."

        # 10. RAG Deep Research & Scraping: "research <topic>", "scrape and summarize <url>", "scrape <url>"
        scrape_url_match = re.search(r'^(?:scrape|analyze|summarize)\s+(?:the\s+)?(?:page|website|url|article)?\s*(https?://\S+)', q_clean)
        if scrape_url_match:
            target_url = scrape_url_match.group(1).strip()
            res = registry.execute_tool_call("scrape_and_analyze_url", {"url": target_url})
            return res

        # 11. Gmail Intent Fast-Paths
        if re.search(r'\b(?:check|read|get|fetch|show|list|any|what about)\s*(?:for\s+)?(?:the\s+)?(?:more\s+)?(?:my\s+)?(?:new\s+|latest\s+|recent\s+)?(?:unread\s+)?(?:emails?|mails?|inbox)\b|\b(?:unread|more)\s+(?:emails?|mails?)\b', q_clean):
            # Check if user specified a count
            count_match = re.search(r'\b(?:last|latest|top|first|more|show)?\s*(\d{1,2})\b', q_clean)
            limit = int(count_match.group(1)) if count_match else 15
            limit = max(1, min(limit, 25))
            
            unread_data = registry.execute_tool_call("check_unread_emails", {"max_results": limit})
            if isinstance(unread_data, str):
                try:
                    unread_data = json.loads(unread_data)
                except Exception:
                    pass

            if isinstance(unread_data, list) and unread_data:
                if "status" in unread_data[0]:
                    return f"{unread_data[0]['status']}, sir."
                if "error" in unread_data[0]:
                    return f"Email check notice: {unread_data[0]['error']}"
                
                count = len(unread_data)
                summary_lines = [f"Sir, here are your latest {count} unread email{'s' if count != 1 else ''}:"]
                for idx, item in enumerate(unread_data, 1):
                    sender = item.get('from', 'Unknown').split('<')[0].strip()
                    subject = item.get('subject', '(No Subject)')
                    summary_lines.append(f"• From {sender}: \"{subject}\"")
                summary_lines.append("\nWould you like me to read the full body of any specific email, sir?")
                return "\n".join(summary_lines)

        # 12. Search Emails Fast-Path: "search emails from github", "search emails about invoice"
        email_search_match = re.search(r'^(?:search|find)\s+(?:my\s+)?emails?\s+(?:from|about|with|for)\s+(.+?)$', q_clean)
        if email_search_match:
            search_term = email_search_match.group(1).strip()
            found = registry.execute_tool_call("search_emails", {"query": search_term, "max_results": 10})
            if isinstance(found, str):
                try:
                    found = json.loads(found)
                except Exception:
                    pass

            if isinstance(found, list) and found:
                if "status" in found[0]:
                    return f"{found[0]['status']}, sir."
                if "error" in found[0]:
                    return f"Email search notice: {found[0]['error']}"
                count = len(found)
                lines = [f"Found {count} email{'s' if count != 1 else ''} matching '{search_term}':"]
                for item in found:
                    sender = item.get('from', 'Unknown').split('<')[0].strip()
                    subject = item.get('subject', '(No Subject)')
                    lines.append(f"• From {sender}: \"{subject}\"")
                return "\n".join(lines)

        research_match = re.search(r'^(?:research|deep\s+research|scrape\s+and\s+explain|find\s+info\s+on|gather\s+intel\s+on)\s+(.+?)(?:\s+for\s+me)?$', q_clean)
        if research_match:
            topic = research_match.group(1).strip()
            res = registry.execute_tool_call("deep_web_research", {"topic": topic, "max_sources": 10})
            return res

        return None

    def chat(self, user_query: str, extra_memory_facts: Optional[str] = None) -> str:
        """
        Process a user query, handle any tool execution turns, and return final synthesized response.
        """
        # Append user message to context manager
        self.context_manager.add_user_message(user_query)

        # 1. Check deterministic fast-path
        fast_reply = self._try_deterministic_intent(user_query)
        if fast_reply:
            self.context_manager.add_assistant_message(content=fast_reply)
            return fast_reply

        # 2. [COMMENTED OUT] Cloud escalation disabled for pure local operation
        # if self._should_escalate_to_cloud(user_query):
        #     print("[Brain] 🌐 Escalating query to Cloud Model...")
        #     return self._chat_cloud()

        # 3. Run Local Ollama reasoning loop
        try:
            return self._chat_local(extra_memory_facts)
        except Exception as e:
            print(f"[Brain] ⚠️ Local Ollama inference error: {e}")
            # --- Cloud Fallback (Commented Out for Pure Local Mode) ---
            # if getattr(self, "cloud_enabled", False) and getattr(self, "cloud_api_key", ""):
            #     print("[Brain] 🌐 Falling back to Cloud API...")
            #     return self._chat_cloud()
            return f"I encountered an issue contacting my local brain at {self.ollama_url}. Please ensure Ollama is running, sir."

    def _chat_local(self, extra_memory_facts: Optional[str] = None) -> str:
        """Execute local Ollama chat with tool calling support and model fallback cascade."""
        tools_schemas = registry.get_all_schemas()
        models_to_try = [self.local_model]
        if self.fallback_model and self.fallback_model != self.local_model:
            models_to_try.append(self.fallback_model)
        
        last_error = None
        for current_model in models_to_try:
            try:
                # Maximum 4 tool call rounds per turn to prevent infinite loops
                for round_idx in range(4):
                    messages = self.context_manager.get_compiled_messages(extra_memory_facts)
                    
                    response = self.ollama_client.chat(
                        model=current_model,
                        messages=messages,
                        tools=tools_schemas,
                        options={"temperature": 0.2}
                    )
                    
                    msg = response.get("message", {})
                    content = msg.get("content", "")
                    tool_calls = msg.get("tool_calls", [])

                    if not tool_calls:
                        # No more tools called; we have the final verbal response!
                        self.context_manager.add_assistant_message(content=content)
                        return content or "Task complete, sir."

                    # Save assistant message with tool call requests
                    self.context_manager.add_assistant_message(content=content, tool_calls=tool_calls)

                    # Execute all requested tool calls
                    for t_call in tool_calls:
                        fn = t_call.get("function", {})
                        fn_name = fn.get("name", "")
                        fn_args = fn.get("arguments", {})
                        
                        # Execute tool
                        tool_output = registry.execute_tool_call(fn_name, fn_args)
                        
                        # Append tool output to context
                        self.context_manager.add_tool_message(
                            tool_call_id=t_call.get("id", f"call_{round_idx}"),
                            tool_name=fn_name,
                            content=tool_output
                        )

                return "I completed the requested actions, sir."
            except Exception as err:
                last_error = err
                print(f"[Brain] Model '{current_model}' inference notice: {err}. Attempting fallback...")
                continue
                
        if last_error:
            raise last_error
        return "I was unable to process the query, sir."

    # def _chat_cloud(self) -> str:
    #     """[COMMENTED OUT] Cloud API chat fallback via OpenAI SDK."""
    #     try:
    #         client = OpenAI(api_key=getattr(self, "cloud_api_key", ""))
    #         messages = self.context_manager.get_compiled_messages()
    #         tools_schemas = registry.get_all_schemas()
    #         
    #         response = client.chat.completions.create(
    #             model=getattr(self, "cloud_model", "gpt-4o-mini"),
    #             messages=messages,
    #             tools=tools_schemas,
    #             temperature=0.3
    #         )
    #         
    #         choice = response.choices[0].message
    #         content = choice.content or ""
    #         
    #         if choice.tool_calls:
    #             for t in choice.tool_calls:
    #                 fn_name = t.function.name
    #                 args = json.loads(t.function.arguments) if t.function.arguments else {}
    #                 registry.execute_tool_call(fn_name, args)
    #             return content or "I executed the requested action via Cloud Reasoning, sir."
    #             
    #         self.context_manager.add_assistant_message(content=content)
    #         return content
    #     except Exception as e:
    #         return f"Cloud API error: {e}"

