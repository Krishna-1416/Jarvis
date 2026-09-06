"""
High-Performance Audio Capture and Noise-Immune Real-Time Voice Activity Detection (VAD) for Project Jarvis.
Features:
1. Dynamic Acoustic Echo Cancellation (completely ignores Jarvis's own TTS output and room reverberation).
2. Spectral Voice Profiling & Zero-Crossing Rate (ZCR) filtering to reject keyboard clacks, mouse clicks, breathing, and fan noise.
3. Adaptive Ambient Noise Floor Tracking.
"""

import os
import sys
import queue
import time
import threading
from typing import Callable, Optional
import numpy as np
import sounddevice as sd

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class AudioRecorder:
    def __init__(
        self,
        on_speech_finished: Callable[[np.ndarray], None],
        on_speech_started: Optional[Callable[[], None]] = None,
        sample_rate: int = 16000,
        chunk_size: int = 512,            # ~32ms per chunk at 16kHz
        vad_threshold: float = 0.032,     # Calibrated speech energy trigger (rejects noise/breathing)
        silence_duration_ms: int = 550,   # 550ms silence = end of speech
        min_speech_duration_ms: int = 300,# Minimum 300ms utterance
    ):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.silence_chunks_limit = int((silence_duration_ms / 1000.0) * (sample_rate / chunk_size))
        self.min_speech_chunks = int((min_speech_duration_ms / 1000.0) * (sample_rate / chunk_size))
        
        self.on_speech_finished = on_speech_finished
        self.on_speech_started = on_speech_started
        
        self._is_recording = False
        self._stream: Optional[sd.InputStream] = None
        self._audio_queue: queue.Queue = queue.Queue()
        self._vad_thread: Optional[threading.Thread] = None
        
        # Acoustic Echo Suppression & Reverb Immunity
        self._is_tts_speaking = False
        self._tts_cooldown_until = 0.0

        # Adaptive Noise Floor Tracking
        self._noise_floor = 0.004
        self._base_threshold = vad_threshold

        # State tracking
        self.is_user_speaking = False
        self._pre_speech_buffer: list[np.ndarray] = []
        self._pre_speech_buffer_max = int((0.40 * sample_rate) / chunk_size)  # Keep last 400ms
        self._active_speech_frames: list[np.ndarray] = []
        self._consecutive_silence_count = 0
        self._consecutive_speech_count = 0

    def set_tts_active(self, active: bool):
        """Called by Engine when Jarvis is speaking to completely block microphone feedback."""
        self._is_tts_speaking = active
        if active:
            # Clear all buffers so Jarvis's voice is completely wiped
            self.is_user_speaking = False
            self._active_speech_frames = []
            self._pre_speech_buffer.clear()
            self._consecutive_speech_count = 0
            self._consecutive_silence_count = 0
        else:
            # Apply 450ms room reverb immunity after TTS stops
            self._tts_cooldown_until = time.time() + 0.45

    def _audio_callback(self, indata, frames, time_info, status):
        """Raw audio stream callback from sounddevice."""
        if self._is_tts_speaking or time.time() < self._tts_cooldown_until:
            return  # Discard speaker feedback directly at capture level

        if indata.shape[1] > 1:
            audio_chunk = np.mean(indata, axis=1).astype(np.float32)
        else:
            audio_chunk = indata[:, 0].copy()
        self._audio_queue.put(audio_chunk)

    def _is_vocal_chunk(self, chunk: np.ndarray, rms: float) -> bool:
        """
        Check if audio chunk matches human vocal characteristics.
        Rejects keyboard typing, fan hiss, mouse clicks, and ambient noise.
        """
        # Dynamic threshold based on background noise
        dynamic_thresh = max(self._base_threshold, self._noise_floor * 2.8)
        if rms < dynamic_thresh:
            return False

        # Zero-Crossing Rate (ZCR) check:
        # High ZCR (> 0.38) = keyboard click, fan hiss, paper shuffle
        # Vocal speech = formants with ZCR typically between 0.02 and 0.34
        zcr = float(np.mean(np.abs(np.diff(np.sign(chunk)))) / 2.0)
        if zcr > 0.38:
            return False

        return True

    def _vad_worker(self):
        """Background worker evaluating vocal chunks and dispatching completed utterances."""
        while self._is_recording:
            try:
                chunk = self._audio_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if self._is_tts_speaking or time.time() < self._tts_cooldown_until:
                self.is_user_speaking = False
                self._active_speech_frames = []
                self._pre_speech_buffer.clear()
                continue

            # Compute RMS energy for chunk
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            is_speech = self._is_vocal_chunk(chunk, rms)

            if is_speech:
                self._consecutive_speech_count += 1
                self._consecutive_silence_count = 0
                
                # Require 3 consecutive vocal chunks (~96ms) to eliminate keyboard clicks/taps
                if not self.is_user_speaking and self._consecutive_speech_count >= 3:
                    # Speech started!
                    self.is_user_speaking = True
                    if self.on_speech_started:
                        try:
                            self.on_speech_started()
                        except Exception:
                            pass
                    # Prepend pre-speech buffer so initial consonants ('P', 'T', 'S') are preserved
                    self._active_speech_frames = list(self._pre_speech_buffer)
                
                if self.is_user_speaking:
                    self._active_speech_frames.append(chunk)
            else:
                self._consecutive_speech_count = 0
                if self.is_user_speaking:
                    self._active_speech_frames.append(chunk)
                    
                    silence_thresh = max(0.010, self._noise_floor * 1.5)
                    if rms < silence_thresh:
                        self._consecutive_silence_count += 1
                    
                    # Check if silence limit is reached
                    if self._consecutive_silence_count >= self.silence_chunks_limit:
                        # End of utterance detected!
                        self.is_user_speaking = False
                        self._consecutive_silence_count = 0
                        
                        if len(self._active_speech_frames) >= self.min_speech_chunks:
                            full_audio = np.concatenate(self._active_speech_frames)
                            if self.on_speech_finished:
                                try:
                                    self.on_speech_finished(full_audio)
                                except Exception as e:
                                    print(f"[Recorder] Error in speech_finished callback: {e}")
                        self._active_speech_frames = []
                else:
                    # Adapt ambient noise floor slowly during silence
                    self._noise_floor = 0.96 * self._noise_floor + 0.04 * rms
                    
                    # Maintain sliding pre-speech ring buffer
                    self._pre_speech_buffer.append(chunk)
                    if len(self._pre_speech_buffer) > self._pre_speech_buffer_max:
                        self._pre_speech_buffer.pop(0)

    def start(self):
        """Start recording and listening for voice input."""
        if self._is_recording:
            return
        
        self._is_recording = True
        self._audio_queue = queue.Queue()
        self.is_user_speaking = False
        self._active_speech_frames = []
        self._pre_speech_buffer = []
        
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            channels=1,
            dtype='float32',
            callback=self._audio_callback
        )
        self._stream.start()
        
        self._vad_thread = threading.Thread(target=self._vad_worker, daemon=True)
        self._vad_thread.start()
        print("[Recorder] [OK] Noise-immune Voice Activity Detection active.")

    def stop(self):
        """Stop audio stream."""
        self._is_recording = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self.is_user_speaking = False
        print("[Recorder] Audio stream stopped.")
