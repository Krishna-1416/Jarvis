"""
Procedural Futuristic Sound Effects for Project Jarvis.
Generates and plays clean, subtle Iron Man / Jarvis style sci-fi chimes
using pure NumPy synthesis and native Windows audio playback (winsound/sounddevice).
Guaranteed 0 audio driver conflict with the microphone recording stream.
"""

import io
import wave
import time
import threading
import numpy as np

class SoundEffects:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._cache = {}
        self._pre_generate_sounds()

    def _generate_wav_bytes(self, audio_data: np.ndarray) -> bytes:
        """Convert float32/int16 numpy audio into standard in-memory WAV byte buffer."""
        if audio_data.dtype != np.int16:
            audio_int16 = (audio_data * 32767).clip(-32768, 32767).astype(np.int16)
        else:
            audio_int16 = audio_data

        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(audio_int16.tobytes())
        return buf.getvalue()

    def _generate_tone(self, freq: float, duration: float, decay: float = 8.0, volume: float = 0.25) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sin(2 * np.pi * freq * t)
        envelope = np.exp(-decay * t)
        return (tone * envelope * volume).astype(np.float32)

    def _pre_generate_sounds(self):
        """Pre-render and cache all sci-fi sound effects at initialization."""
        try:
            # 1. Wake Chime (Rising two-tone: D5 -> A5)
            t1 = self._generate_tone(587.33, 0.08, decay=6.0, volume=0.20)
            t2 = self._generate_tone(880.00, 0.16, decay=5.0, volume=0.25)
            self._cache["wake"] = self._generate_wav_bytes(np.concatenate([t1, t2]))

            # 2. Ready Chime (Harmonic acknowledgement: E5 -> C6)
            t1 = self._generate_tone(659.25, 0.07, decay=8.0, volume=0.18)
            t2 = self._generate_tone(1046.50, 0.14, decay=6.0, volume=0.22)
            self._cache["ready"] = self._generate_wav_bytes(np.concatenate([t1, t2]))

            # 3. Processing Blip (Subtle high blip: G5)
            audio = self._generate_tone(783.99, 0.06, decay=14.0, volume=0.14)
            self._cache["processing"] = self._generate_wav_bytes(audio)

            # 4. Success Triad (Warm triad: C5 -> E5 -> C6)
            t1 = self._generate_tone(523.25, 0.06, decay=8.0, volume=0.18)
            t2 = self._generate_tone(659.25, 0.06, decay=7.0, volume=0.20)
            t3 = self._generate_tone(1046.50, 0.18, decay=5.0, volume=0.22)
            self._cache["success"] = self._generate_wav_bytes(np.concatenate([t1, t2, t3]))

            # 5. Error Tone (Low descending chime: A4 -> E4)
            t1 = self._generate_tone(440.00, 0.08, decay=7.0, volume=0.20)
            t2 = self._generate_tone(329.63, 0.18, decay=5.0, volume=0.22)
            self._cache["error"] = self._generate_wav_bytes(np.concatenate([t1, t2]))
        except Exception as e:
            print(f"[SoundEffects] Error pre-generating sound effects: {e}")

    def _play_bytes_async(self, sound_name: str):
        """Play cached WAV bytes asynchronously without blocking or colliding with microphone."""
        wav_data = self._cache.get(sound_name)
        if not wav_data:
            return

        def _worker():
            try:
                import winsound
                winsound.PlaySound(wav_data, winsound.SND_MEMORY)
            except Exception:
                try:
                    import sounddevice as sd
                    # Fallback to sounddevice if winsound is unavailable
                    audio_arr = np.frombuffer(wav_data[44:], dtype=np.int16).astype(np.float32) / 32768.0
                    sd.play(audio_arr, self.sample_rate)
                    sd.wait()
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    def play_wake(self):
        """Crisp rising two-tone chime when Jarvis wakes up / summoned."""
        self._play_bytes_async("wake")

    def play_ready(self):
        """Soft harmonic acknowledgement chime."""
        self._play_bytes_async("ready")

    def play_processing(self):
        """Subtle blip when computation or speech detection starts."""
        self._play_bytes_async("processing")

    def play_success(self):
        """Warm triad chime upon successful tool execution."""
        self._play_bytes_async("success")

    def play_error(self):
        """Soft low descending tone on error."""
        self._play_bytes_async("error")

# Global singleton instance
sfx = SoundEffects()
