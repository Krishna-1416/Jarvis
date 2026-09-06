"""
Configuration Loader for Project Jarvis.
Loads and validates settings.yaml and tools_config.yaml.
"""

from pathlib import Path
from typing import Any, Dict
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"

class Config:
    def __init__(self):
        self.settings_file = CONFIG_DIR / "settings.yaml"
        self.tools_file = CONFIG_DIR / "tools_config.yaml"
        
        self.settings: Dict[str, Any] = self._load_yaml(self.settings_file)
        self.tools_config: Dict[str, Any] = self._load_yaml(self.tools_file)

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[Config] Error reading {path.name}: {e}")
            return {}

    @property
    def assistant_name(self) -> str:
        return self.settings.get("assistant", {}).get("name", "Jarvis")

    @property
    def summon_hotkey(self) -> str:
        return self.settings.get("assistant", {}).get("summon_hotkey", "<ctrl>+<shift>+j")

    @property
    def push_to_talk_hotkey(self) -> str:
        return self.settings.get("assistant", {}).get("push_to_talk_hotkey", "<ctrl>+space")

    @property
    def local_model(self) -> str:
        return self.settings.get("llm", {}).get("local_model", "qwen2.5:1.5b")

    @property
    def ollama_url(self) -> str:
        return self.settings.get("llm", {}).get("ollama_base_url", "http://localhost:11434")

    @property
    def stt_model_size(self) -> str:
        return self.settings.get("voice", {}).get("stt", {}).get("model_size", "base.en")

    @property
    def stt_device(self) -> str:
        return self.settings.get("voice", {}).get("stt", {}).get("device", "cuda")

    @property
    def tts_voice(self) -> str:
        return self.settings.get("voice", {}).get("tts", {}).get("voice_name", "bm_george")

    @property
    def tts_speed(self) -> float:
        return float(self.settings.get("voice", {}).get("tts", {}).get("speed", 1.05))

    @property
    def vad_threshold(self) -> float:
        return float(self.settings.get("voice", {}).get("vad", {}).get("threshold", 0.5))

    @property
    def silence_duration_ms(self) -> int:
        return int(self.settings.get("voice", {}).get("vad", {}).get("silence_duration_ms", 600))

# Global config instance
config = Config()
