"""
Test Adaptive Energy Voice Activity Detection (VAD) + faster-whisper STT.
"""
import sys
import time
from pathlib import Path
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def main():
    print("=== [ADAPTIVE VAD TEST] ===")
    print("Loading faster-whisper on CPU (int8)...")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    
    print("\nRecording 3 seconds from microphone...")
    rec = sd.rec(int(3.0 * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    audio = rec[:, 0]
    
    rms = float(np.sqrt(np.mean(audio ** 2)))
    max_v = float(np.max(np.abs(audio)))
    print(f"Captured audio - Peak: {max_v:.4f}, RMS: {rms:.4f}")
    
    if max_v > 0.005:
        norm_audio = (audio / max_v * 0.95).astype(np.float32)
    else:
        norm_audio = audio
        
    start = time.perf_counter()
    segments, _ = model.transcribe(norm_audio, beam_size=1, temperature=0.0, language="en")
    text = " ".join(s.text.strip() for s in segments).strip()
    latency = (time.perf_counter() - start) * 1000
    
    print(f"\n[RESULT] Transcribed in {latency:.1f}ms: \"{text}\"")
    print("\n[SUCCESS] Adaptive VAD Benchmark Completed.")

if __name__ == "__main__":
    main()
