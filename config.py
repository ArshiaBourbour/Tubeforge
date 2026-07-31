"""
Application-wide configuration.

Settings are persisted as JSON at ~/.tubeforge/config.json (falls back to
settings/config.json defaults shipped with the repo on first run). The
`Config` class is a thin, validated wrapper so the rest of the app never
touches raw dict keys directly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from utils.logger import get_logger

log = get_logger("config")

APP_DIR = Path.home() / ".tubeforge"
USER_CONFIG_PATH = APP_DIR / "config.json"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "settings" / "config.json"

VIDEO_QUALITIES = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "Best", "Worst"]
AUDIO_QUALITIES = ["320kbps", "256kbps", "192kbps", "128kbps", "Best"]
AUDIO_FORMATS = ["mp3", "wav", "aac", "flac", "m4a", "opus"]
THEMES = ["midnight", "dracula", "solarized", "nord", "mono"]
LANGUAGES = ["en", "fa"]
COOKIE_BROWSERS = ["none", "chrome", "firefox", "edge", "brave", "opera", "vivaldi", "safari", "file"]


@dataclass
class Config:
    download_folder: str = str(Path.home() / "Downloads" / "TubeForge")
    video_quality: str = "1080p"
    audio_quality: str = "192kbps"
    audio_format: str = "mp3"
    theme: str = "midnight"
    concurrent_downloads: int = 3
    filename_template: str = "%(title)s.%(ext)s"
    proxy: str = ""
    language: str = "en"
    check_for_updates: bool = True
    embed_thumbnail: bool = True
    embed_subtitles: bool = False
    write_metadata: bool = True
    cookie_source: str = "none"       # "none" | a browser name from COOKIE_BROWSERS | "file"
    cookie_file_path: str = ""        # used when cookie_source == "file"

    # ---- persistence -----------------------------------------------------

    @classmethod
    def load(cls) -> "Config":
        source = USER_CONFIG_PATH if USER_CONFIG_PATH.exists() else DEFAULT_CONFIG_PATH
        try:
            with open(source, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            log.debug("Loaded config from %s", source)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            log.warning("Could not load config (%s); using defaults", exc)
            cfg = cls()
        cfg.save()  # normalize / create user config on first run
        return cfg

    def save(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with open(USER_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        log.debug("Saved config to %s", USER_CONFIG_PATH)

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in self.__dataclass_fields__:
                setattr(self, key, value)
        self.save()

    def as_dict(self) -> dict:
        return asdict(self)
