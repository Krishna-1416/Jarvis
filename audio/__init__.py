"""
Jarvis Audio Subsystem
Contains VAD, Speech-to-Text (STT), Text-to-Speech (TTS), and Sound Effects.
"""

from .sound_effects import SoundEffects
from .recorder import AudioRecorder
from .stt import SpeechToText
from .tts import TextToSpeech

__all__ = ["SoundEffects", "AudioRecorder", "SpeechToText", "TextToSpeech"]
