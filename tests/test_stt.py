"""
Diagnostic test for faster-whisper Speech-to-Text transcription.
Can be executed directly: python tests/test_stt.py
"""
import sys
import time
from pathlib import Path
import numpy as np

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from audio.stt import SpeechToText

def main():
    print("=== [STT] Testing Jarvis faster-whisper STT ===")
    
    stt = SpeechToText(model_size="base.en", device="cpu", compute_type="int8", lazy_load=False)
    
    # Generate 1.0 second test audio
    test_audio = np.zeros(int(1.0 * 16000), dtype=np.float32)
    print("  -> Running benchmark on test audio tensor...")
    text, latency = stt.transcribe(test_audio)
    print(f"  -> Benchmark transcription completed in {latency*1000:.1f}ms (Result: '{text}')")
    
    print("[SUCCESS] STT Diagnostic Finished.")

if __name__ == "__main__":
    main()
