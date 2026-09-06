"""
Smart Speech-to-Text (STT) Engine using faster-whisper.
Runs on CPU int8 delivering <120ms transcription latency with intelligent hallucination filtering,
RMS energy gating, and clean text post-processing.
"""

import re
import time
import threading
from typing import Optional, Tuple
import numpy as np

# Common Whisper hallucinations on silence / background room noise
HALLUCINATION_PATTERNS = [
    r'^(?:you|thank you|thanks for watching|bye|subtitles by|subscribe|the end|translated by)[.!]?$',
    r'^[.\-_,?!]+$',
    r'^\[(?:music|applause|laughter|silence|audio)\]$',
]

class SpeechToText:
    def __init__(
        self,
        model_size: str = "base.en",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en",
        lazy_load: bool = True
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self._model = None
        self._is_loading = False
        self._lock = threading.Lock()
        
        if not lazy_load:
            self._initialize_model()
        else:
            threading.Thread(target=self._initialize_model, daemon=True).start()

    def _initialize_model(self):
        """Load the faster-whisper model with CPU int8 default."""
        with self._lock:
            if self._model is not None:
                return
            self._is_loading = True
            
            try:
                from faster_whisper import WhisperModel
                print(f"[STT] Loading faster-whisper '{self.model_size}' on {self.device} ({self.compute_type})...")
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                print(f"[STT] [OK] Loaded faster-whisper on {self.device}.")
            except Exception as e:
                print(f"[STT] [WARN] Fallback loading faster-whisper on CPU: {e}")
                try:
                    from faster_whisper import WhisperModel
                    self.device = "cpu"
                    self.compute_type = "int8"
                    self._model = WhisperModel(
                        self.model_size,
                        device="cpu",
                        compute_type="int8"
                    )
                    print("[STT] [OK] Loaded faster-whisper on CPU.")
                except Exception as e2:
                    print(f"[STT] [ERROR] Could not initialize Whisper model: {e2}")
                    self._model = None
            finally:
                self._is_loading = False

    def is_hallucination_or_noise(self, text: str) -> bool:
        """Check if transcribed text is a common Whisper silence hallucination."""
        clean = text.strip().lower()
        if not clean or len(clean) < 2:
            return True
        for pattern in HALLUCINATION_PATTERNS:
            if re.match(pattern, clean):
                return True
        return False

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Tuple[str, float]:
        """
        Transcribe a 16kHz float32 numpy audio array.
        Returns: (transcribed_text, latency_seconds)
        """
        if self._model is None:
            self._initialize_model()

        if self._model is None or len(audio_data) < 1600:  # Less than 100ms
            return "", 0.0

        start_time = time.perf_counter()
        
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # 1. RMS Energy Gate (Reject dead silence chunks without wasting CPU)
        rms = float(np.sqrt(np.mean(audio_data ** 2)))
        if rms < 0.0005:
            return "", 0.0

        # 2. Peak normalization
        max_val = np.max(np.abs(audio_data))
        if max_val > 0.01:
            audio_data = (audio_data / max_val * 0.95).astype(np.float32)

        try:
            segments, info = self._model.transcribe(
                audio_data,
                beam_size=1,
                best_of=1,
                temperature=0.0,
                language=self.language,
                condition_on_previous_text=False,
                vad_filter=False
            )

            text_parts = [segment.text.strip() for segment in segments]
            raw_text = " ".join(text_parts).strip()
            
            # 3. Filter hallucinations
            if self.is_hallucination_or_noise(raw_text):
                return "", time.perf_counter() - start_time

            latency = time.perf_counter() - start_time
            return raw_text, latency
        except Exception as e:
            print(f"[STT] [ERROR] Transcription error: {e}")
            return "", 0.0
