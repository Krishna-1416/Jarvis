"""
Diagnostic test for Jarvis Microphone input and VAD detection.
Can be executed directly: python tests/test_audio_input.py
"""
import sys
import time
from pathlib import Path
import numpy as np

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from audio.recorder import AudioRecorder

def on_started():
    print("\n  [VAD EVENT] Speech start detected!")

def on_finished(audio_data: np.ndarray):
    duration = len(audio_data) / 16000.0
    print(f"\n  [VAD EVENT] Speech finished! Captured {duration:.2f}s ({len(audio_data)} samples)")

def main():
    print("=== [AUDIO INPUT] Testing Jarvis Microphone & Neural Silero VAD ===")
    
    recorder = AudioRecorder(
        sample_rate=16000,
        vad_threshold=0.45,
        silence_duration_ms=700,
        on_speech_started=on_started,
        on_speech_finished=on_finished
    )
    
    print("\nStarting listener stream for 8 seconds. Please speak a sentence into your microphone...")
    recorder.start()
    
    try:
        for i in range(8, 0, -1):
            print(f"  Listening... ({i}s remaining) ", end="\r")
            time.sleep(1.0)
    finally:
        recorder.stop()
    
    print("\n[SUCCESS] Microphone & VAD Diagnostic Finished.")

if __name__ == "__main__":
    main()
