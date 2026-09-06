"""
End-to-End Live Voice & STT Interactive Diagnostic.
Records from microphone, detects speech via Silero VAD, transcribes with faster-whisper,
and confirms via SAPI5 speech output.
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
from audio.tts import TextToSpeech
from audio.sound_effects import sfx

def main():
    print("=================================================================")
    print("   🎙️ JARVIS LIVE SPEECH-TO-TEXT (STT) DIAGNOSTIC TEST")
    print("=================================================================")
    print("[Init] Loading faster-whisper on CPU (int8)...")
    stt = SpeechToText(model_size="base.en", device="cpu", compute_type="int8", lazy_load=False)
    tts = TextToSpeech(rate=195)
    
    def on_started():
        print("\n  [VAD] 🗣️ Speech detected! Listening...")
        sfx.play_wake()

    def on_finished(audio_data: np.ndarray):
        duration = len(audio_data) / 16000.0
        print(f"  [VAD] 🛑 Utterance captured ({duration:.2f}s). Transcribing...")
        text, latency = stt.transcribe(audio_data)
        print(f"\n  🎯 [TRANSCRIBED TEXT]: \"{text}\" (Latency: {latency*1000:.1f}ms)")
        if text.strip():
            sfx.play_success()
            tts.speak_sync(f"I heard you say: {text}")
        else:
            print("  ⚠️ [WARN] Transcription was empty. Try speaking closer to the microphone.")

    recorder = AudioRecorder(
        sample_rate=16000,
        vad_threshold=0.28,
        silence_duration_ms=500,
        on_speech_started=on_started,
        on_speech_finished=on_finished
    )

    print("\n[Status] 🚀 Microphone stream is LIVE for 15 seconds.")
    print("👉 Please speak any sentence now (e.g. 'Hello Jarvis, how is the weather today?')...\n")
    recorder.start()
    
    try:
        for i in range(15, 0, -1):
            print(f"  Listening... ({i:2d}s remaining)", end="\r")
            time.sleep(1.0)
    finally:
        recorder.stop()
        
    print("\n\n[SUCCESS] Live Voice & STT Test Completed.")

if __name__ == "__main__":
    main()
