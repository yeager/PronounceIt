"""Application configuration management."""

import json
import os


DEFAULT_CONFIG = {
    "language": "sv",
    "sample_rate": 44100,
    "chunk_size": 1024,
    "theme": "dark",
}


class AppConfig:
    """Läser och skriver konfiguration till JSON-fil."""

    def __init__(self):
        config_dir = os.path.join(
            os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
            "pronounceit",
        )
        os.makedirs(config_dir, exist_ok=True)
        self._path = os.path.join(config_dir, "config.json")
        self._data = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        if os.path.isfile(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()
