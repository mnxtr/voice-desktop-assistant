import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".desktop_llm_assistant"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "wake_word": "hey assistant",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "mistral",
    "vosk_model_path": str(CONFIG_DIR / "vosk-model"),
    "voice_rate": 175,
    "voice_volume": 1.0,
    "dwell_time": 1.5,
    "gaze_enabled": False,
    "gaze_smoothing": 5,
    "gaze_cursor_visible": True,
    "grid_rows": 3,
    "grid_cols": 3,
    "overlay_opacity": 0.85,
    "overlay_position": "top-right",
    "sample_rate": 16000,
    "audio_block_size": 8000,
    "failsafe_enabled": True,
    "mouse_move_speed": 0.3,
}


class Config:
    def __init__(self):
        self._data = dict(DEFAULTS)
        self._ensure_config_dir()
        self._load()

    def _ensure_config_dir(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    stored = json.load(f)
                self._data.update(stored)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def __getattr__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Config has no attribute '{name}'")


config = Config()
