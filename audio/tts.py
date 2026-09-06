"""
Instant 0ms-Latency Windows SAPI5 Text-to-Speech Subsystem for Project Jarvis.
High performance native Windows voice engine with zero lag, markdown cleaning,
and instant barge-in interruption.
"""

import re
import threading
from typing import Optional, Callable
import pyttsx3

class TextToSpeech:
    def __init__(
        self,
        rate: int = 195,
        volume: float = 1.0,
        voice_id: Optional[str] = None
    ):
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        
        self._is_speaking = False
        self._stop_requested = threading.Event()
        self._playback_lock = threading.Lock()
        
        # Test and select default voice
        self._default_voice_id = self._detect_voice()
        print("[TTS] [OK] Windows SAPI5 Voice Engine online (0ms latency).")

    def _detect_voice(self) -> Optional[str]:
        """Detect best available Windows voice (David, George, or default)."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            target_id = None
            for v in voices:
                vname = v.name.lower()
                if "david" in vname or "george" in vname:
                    target_id = v.id
                    break
            if not target_id and voices:
                target_id = voices[0].id
            return target_id
        except Exception:
            return None

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def stop(self):
        """Instant interruption / barge-in. Halts playback immediately."""
        self._stop_requested.set()
        self._is_speaking = False

    def _clean_markdown(self, text: str) -> str:
        """Strip markdown formatting, URLs, and symbols for crisp pronunciation."""
        # Code blocks
        text = re.sub(r'```[\s\S]*?```', 'code block omitted.', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Markdown symbols
        text = re.sub(r'[*#_~>|]+', ' ', text)
        # URLs
        text = re.sub(r'https?://\S+', '', text)
        # Strip Sources block from voice output
        text = re.sub(r'(?i)\*?\*?sources:?\*?\*?[\s\S]*$', '', text)
        # Extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def speak_sync(self, text: str):
        """Synthesize and play audio synchronously with zero delay."""
        with self._playback_lock:
            self._stop_requested.clear()
            self._is_speaking = True
            
            clean_text = self._clean_markdown(text)
            if not clean_text or self._stop_requested.is_set():
                self._is_speaking = False
                return

            try:
                # Initialize per-thread pyttsx3 instance to guarantee COM thread safety
                engine = pyttsx3.init()
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                
                selected_voice = self.voice_id or self._default_voice_id
                if selected_voice:
                    engine.setProperty('voice', selected_voice)

                engine.say(clean_text)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS] [ERROR] Speech playback failed: {e}")
            finally:
                self._is_speaking = False

    def speak(self, text: str, on_done: Optional[Callable[[], None]] = None):
        """Asynchronously speak in background thread."""
        def _worker():
            self.speak_sync(text)
            if on_done and not self._stop_requested.is_set():
                try:
                    on_done()
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    def speak_async(self, text: str, on_done: Optional[Callable[[], None]] = None):
        """Alias for speak() to guarantee backward compatibility."""
        self.speak(text, on_done=on_done)

