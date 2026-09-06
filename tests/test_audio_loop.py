"""
End-to-End Audio Loopback Diagnostic:
Microphone -> Silero VAD -> faster-whisper STT -> Kokoro TTS -> Speaker
"""
import time
import numpy as np
from audio.recorder import AudioRecorder
from audio.stt import SpeechToText
from audio.tts import TextToSpeech
from audio.sound_effects import sfx

def main():
    print("=== 🔄 Testing Jarvis End-to-End Audio Loop ===")
    
    print("\nInitializing STT and TTS engines...")
    stt = SpeechToText(model_size="base.en", device="cuda", compute_type="int8")
    tts = TextToSpeech(voice_name="bm_george")
    
    def on_speech_started():
        print("\n[EVENT] 🎙️ Speech detected! Listening...")
        sfx.play_processing()

    def on_speech_finished(audio_data: np.ndarray):
        duration = len(audio_data) / 16000.0
        print(f"[EVENT] 🛑 Processing utterance ({duration:.2f}s)...")
        
        text, latency = stt.transcribe(audio_data)
        print(f"  📝 Transcribed: '{text}' (in {latency*1000:.1f}ms)")
        
        if text.strip():
            reply = f"You said: {text}"
            print(f"  🔊 Jarvis replying: '{reply}'")
            tts.speak_sync(reply)
        else:
            print("  (Empty transcription)")

    recorder = AudioRecorder(
        sample_rate=16000,
        vad_threshold=0.5,
        silence_duration_ms=600,
        on_speech_started=on_speech_started,
        on_speech_finished=on_speech_finished
    )

    sfx.play_wake()
    print("\nJarvis is now listening! Speak into your microphone (e.g. 'Hello Jarvis').")
    print("Will run for 15 seconds. Press Ctrl+C to stop early.\n")
    
    recorder.start()
    try:
        time.sleep(15.0)
    except KeyboardInterrupt:
        pass
    finally:
        recorder.stop()

    print("\n✅ End-to-End Audio Loop Test Complete.")

if __name__ == "__main__":
    main()
