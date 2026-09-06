"""
Diagnostic test for Jarvis Sound Effects and TTS engine.
Can be executed directly: python tests/test_tts.py
"""
import sys
import time
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from audio.sound_effects import sfx
from audio.tts import TextToSpeech

def main():
    print("=== [AUDIO] Testing Jarvis Audio & Speech Output ===")
    
    print("\n1. Testing Procedural Sound Effects...")
    print("  -> Playing wake chime...")
    sfx.play_wake()
    time.sleep(1.0)
    
    print("  -> Playing success chime...")
    sfx.play_success()
    time.sleep(1.0)
    
    print("  -> Playing processing ping...")
    sfx.play_processing()
    time.sleep(0.8)
    
    print("\n2. Testing Text-to-Speech Engine...")
    tts = TextToSpeech()
    test_phrase = "Good afternoon, sir. Systems are online and all parameters are nominal."
    print(f"  -> Speaking: '{test_phrase}'")
    tts.speak_sync(test_phrase)
    
    print("\n[SUCCESS] Audio & TTS Diagnostic Finished.")

if __name__ == "__main__":
    main()
