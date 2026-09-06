"""
Diagnostic test for Sound Effects & Audio Subsystem.
"""
import sys
import time
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from audio.sound_effects import sfx
from audio.recorder import AudioRecorder

def main():
    print("=== [SOUND EFFECTS] Testing Sci-Fi Chimes & Audio Subsystem ===")
    
    # Start audio recorder to test concurrent playback without stream collision
    print("\n1. Initializing AudioRecorder stream...")
    rec = AudioRecorder(on_speech_finished=lambda a: None, on_speech_started=lambda: None)
    rec.start()
    time.sleep(0.5)

    print("\n2. Playing Sound Effects in sequence:")
    
    print("  [SFX] Playing Wake Chime (Rising D5 -> A5)...")
    sfx.play_wake()
    time.sleep(0.6)

    print("  [SFX] Playing Ready Chime (E5 -> C6)...")
    sfx.play_ready()
    time.sleep(0.6)

    print("  [SFX] Playing Processing Blip (G5)...")
    sfx.play_processing()
    time.sleep(0.6)

    print("  [SFX] Playing Success Triad (C5 -> E5 -> C6)...")
    sfx.play_success()
    time.sleep(0.8)

    print("  [SFX] Playing Error Tone (A4 -> E4)...")
    sfx.play_error()
    time.sleep(0.8)

    print("\n3. Stopping AudioRecorder stream...")
    rec.stop()

    print("\n[SUCCESS] Sound Effects Test Completed.")

if __name__ == "__main__":
    main()
