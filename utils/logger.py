"""
Centralized logging configuration for TubeForge.

Provides a single `get_logger` factory that all modules use, ensuring
consistent formatting and a persistent rotating log file under
`~/.tubeforge/logs/tubeforge.log`. The console handler is intentionally
quiet (WARNING+) because the Rich-powered TUI owns the screen; the file
handler captures everything (DEBUG+) for troubleshooting and the
in-app Log Viewer (see cli/ui.py -> show_log_viewer).
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

APP_DIR = Path.home() / ".tubeforge"
LOG_DIR = APP_DIR / "logs"
LOG_FILE = LOG_DIR / "tubeforge.log"

_CONFIGURED = False


def _ensure_dirs() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging(level: int = logging.DEBUG) -> None:
    """Configure the root 'tubeforge' logger exactly once per process."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    _ensure_dirs()

    root = logging.getLogger("tubeforge")
    root.setLevel(level)
    root.propagate = False

    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_fmt)
    root.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced child logger, e.g. get_logger('downloader.video')."""
    configure_logging()
    return logging.getLogger(f"tubeforge.{name}")


def tail_log(n: int = 200) -> list[str]:
    """Return the last `n` lines of the log file (used by the Log Viewer)."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    return lines[-n:]
