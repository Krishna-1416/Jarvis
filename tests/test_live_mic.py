"""
Interactive Live Microphone & STT Diagnostic Test.
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
from audio.stt import SpeechToText

def main():
    print("=== [LIVE MIC & STT TEST] ===")
    
    stt = SpeechToText(model_size="base.en", device="cpu", compute_type="int8", lazy_load=False)
    
    def on_started():
        print("\n[VAD] >>> SPEECH DETECTED! (User started speaking...)")
        
    def on_finished(audio_data):
        dur = len(audio_data) / 16000.0
        rms = float(np.sqrt(np.mean(audio_data ** 2)))
        print(f"\n[VAD] <<< SPEECH ENDED. Captured {dur:.2f}s audio (RMS: {rms:.4f}).")
        print("  -> Transcribing with faster-whisper...")
        text, latency = stt.transcribe(audio_data)
        print(f"  -> [TRANSCRIBED]: '{text}' (latency: {latency*1000:.1f}ms)\n")

    rec = AudioRecorder(
        sample_rate=16000,
        vad_threshold=0.30,  # Highly sensitive neural threshold
        silence_duration_ms=500,
        min_speech_duration_ms=250,
        on_speech_started=on_started,
        on_speech_finished=on_finished
    )
    
    print("\n[Recorder] Starting microphone stream. Speak into your microphone now...")
    rec.start()
    
    try:
        for i in range(8):
            time.sleep(1)
            # Print live stream health
            if not rec.is_user_speaking:
                print(f"  [Listening {i+1}/8s] Microphone active...", end="\r")
    except KeyboardInterrupt:
        pass
    finally:
        rec.stop()
        print("\n[SUCCESS] Live Mic Test Finished.")

if __name__ == "__main__":
    main()
