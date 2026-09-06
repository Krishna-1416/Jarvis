"""
Core Orchestration Engine for Project Jarvis.
Asynchronously coordinates audio input, LLM reasoning (BrainRouter), memory recall,
tool execution, acoustic echo cancellation gating, and smart voice output.
"""

import time
import threading
from typing import Optional, Callable
import numpy as np

from core.config import config
from core.router import BrainRouter
from core.context_manager import ContextManager
from memory.memory_manager import memory_manager
from audio.sound_effects import sfx
from audio.recorder import AudioRecorder
from audio.stt import SpeechToText
from audio.tts import TextToSpeech

class JarvisEngine:
    def __init__(
        self,
        on_status_change: Optional[Callable[[str], None]] = None,
        on_transcript: Optional[Callable[[str, str], None]] = None,
    ):
        self.on_status_change = on_status_change  # "Idle", "Listening", "Thinking", "Speaking"
        self.on_transcript = on_transcript        # (speaker: "user" | "jarvis", text: str)
        
        self.status = "Initializing"
        self._set_status("Initializing")

        # Initialize Long-Term Memory
        print("[Engine] Initializing Persistent Memory...")
        self.memory = memory_manager

        # Initialize Intelligence Brain & Context
        print("[Engine] Initializing Hybrid Brain Router...")
        self.context_manager = ContextManager(max_turns=config.settings.get("memory", {}).get("max_context_turns", 6))
        self.router = BrainRouter(context_manager=self.context_manager)

        # Initialize audio subsystems
        print("[Engine] Initializing Audio Subsystem...")
        self.sfx = sfx
        self.stt = SpeechToText(
            model_size=config.stt_model_size,
            device=config.stt_device
        )
        self.tts = TextToSpeech(
            rate=config.settings.get("voice", {}).get("tts", {}).get("rate", 195),
            volume=config.settings.get("voice", {}).get("tts", {}).get("volume", 1.0)
        )
        self.recorder = AudioRecorder(
            sample_rate=16000,
            vad_threshold=config.vad_threshold,
            silence_duration_ms=config.silence_duration_ms,
            on_speech_started=self._handle_speech_started,
            on_speech_finished=self._handle_speech_finished
        )

        # Initialize Background Email Daemon
        from core.email_daemon import EmailDaemon
        email_settings = config.settings.get("email", {})
        self.email_daemon = EmailDaemon(
            polling_interval_minutes=email_settings.get("polling_interval_minutes", 10),
            on_new_emails=self._handle_new_emails,
            enabled=email_settings.get("enabled", True)
        )
        
        self._is_running = False
        self._lock = threading.Lock()
        self._last_tts_end_time = 0.0
        self._last_interaction_time = 0.0
        self._set_status("Idle")
        print("[Engine] [OK] Jarvis Engine Fully Online with Episodic Memory & Gmail Monitor.")

    def _set_status(self, new_status: str):
        self.status = new_status
        if self.on_status_change:
            try:
                self.on_status_change(new_status)
            except Exception:
                pass

    def _emit_transcript(self, speaker: str, text: str):
        if self.on_transcript:
            try:
                self.on_transcript(speaker, text)
            except Exception:
                pass

    def _handle_speech_started(self):
        """Called when user starts speaking. Handles instant barge-in interruption."""
        if self.tts.is_speaking:
            print("[Engine] ⚡ User interrupted Jarvis. Halting TTS output...")
            self.tts.stop()
        
        self._set_status("Listening")

    def _handle_speech_finished(self, audio_data: np.ndarray):
        """Called when user stops speaking (silence detected by VAD)."""
        # Acoustic Echo Protection: Ignore audio captured within 350ms of Jarvis finishing TTS
        if time.time() - self._last_tts_end_time < 0.35:
            self._set_status("Idle")
            return

        duration = len(audio_data) / 16000.0
        if duration < 0.3:  # Ignore micro-clicks/pops under 300ms
            self._set_status("Idle")
            return

        print(f"[Engine] Processing voice input ({duration:.2f}s)...")
        self._set_status("Thinking")

        # 1. Transcribe with Whisper STT (int8 CPU)
        transcribed_text, latency = self.stt.transcribe(audio_data)
        
        if not transcribed_text.strip():
            # Hallucination or silence was rejected
            self._set_status("Idle")
            return

        # 2. TV & Background Conversation Filter
        clean_lower = transcribed_text.lower().strip()
        wake_words = ("jarvis", "hey jarvis", "hello jarvis", "hi jarvis", "service", "travis", "harvis")
        has_wake_word = any(w in clean_lower for w in wake_words)
        is_in_active_session = (time.time() - self._last_interaction_time) < 12.0

        if not has_wake_word and not is_in_active_session:
            print(f"[Engine] 🔇 Ignored background conversation / TV: '{transcribed_text}'")
            self._set_status("Idle")
            return

        self._last_interaction_time = time.time()
        print(f"[Engine] 📝 Transcribed: '{transcribed_text}' (took {latency*1000:.1f}ms)")
        self.sfx.play_processing()
        self._emit_transcript("user", transcribed_text)

        # 3. Process query through Hybrid Brain & Tools
        self.process_query(transcribed_text)

    def process_query(self, user_text: str):
        """Process a text command (from voice transcription or HUD text input)."""
        threading.Thread(target=self._process_query_worker, args=(user_text,), daemon=True).start()

    def _process_query_worker(self, user_text: str):
        with self._lock:
            self._set_status("Thinking")
            
            # 1. Log user turn to SQLite
            self.memory.db.log_conversation(speaker="user", text=user_text)

            # 2. Retrieve relevant long-term memory context
            memory_facts = self.memory.get_prompt_context(user_text)

            # 3. Send to Hybrid Brain Router (Ollama + Tools)
            reply = self.router.chat(user_text, extra_memory_facts=memory_facts)

            # 4. Log assistant turn to SQLite
            self.memory.db.log_conversation(speaker="jarvis", text=reply)

            # 5. Output response
            self._emit_transcript("jarvis", reply)
            self._set_status("Speaking")
            self.recorder.set_tts_active(True)
            try:
                self.tts.speak_sync(reply)
            finally:
                self.recorder.set_tts_active(False)
            self._last_tts_end_time = time.time()
            self._set_status("Idle")

    def _handle_new_emails(self, new_emails: list):
        """Called when new emails arrive from the background daemon."""
        count = len(new_emails)
        if count == 1:
            sender = new_emails[0].get('from', 'Someone').split('<')[0].strip()
            subject = new_emails[0].get('subject', 'No subject')
            alert_msg = f"📬 New email from {sender}: {subject}"
        else:
            alert_msg = f"📬 You have {count} new unread emails."

        self._emit_transcript("jarvis", alert_msg)
        self.sfx.play_wake()

    def start(self):
        """Start listening loop and background daemons."""
        self._is_running = True
        self.sfx.play_wake()
        self.recorder.start()
        self.email_daemon.start()

        # Optional Startup Email Briefing
        email_settings = config.settings.get("email", {})
        if email_settings.get("startup_briefing", True):
            threading.Thread(target=self._run_startup_briefing, daemon=True).start()

        print("[Engine] 🚀 Jarvis listening loop active. Press Ctrl+C in terminal to exit.")

    def _run_startup_briefing(self):
        time.sleep(2.0)
        briefing = self.email_daemon.get_startup_briefing()
        if briefing:
            full_msg = f"Sir, as a quick update: {briefing}"
            self._emit_transcript("jarvis", full_msg)
            self.tts.speak_async(full_msg)

    def stop(self):
        """Stop listening loop and cleanup."""
        self._is_running = False
        self.recorder.stop()
        self.email_daemon.stop()
        self.tts.stop()
        print("[Engine] Jarvis stopped.")

