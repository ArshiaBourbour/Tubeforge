from __future__ import annotations

import shutil
from pathlib import Path


def human_size(num_bytes: float | None) -> str:
    """Format a byte count as a human-readable string, e.g. 12.4 MB."""
    if num_bytes is None:
        return "Unknown"
    num_bytes = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def human_duration(seconds: float | None) -> str:
    """Format seconds as H:MM:SS or M:SS."""
    if seconds is None:
        return "Unknown"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def ffmpeg_available() -> bool:
    """True if ffmpeg is discoverable on PATH."""
    return shutil.which("ffmpeg") is not None


def node_available() -> bool:
    """True if a Node.js runtime is discoverable on PATH (needed by yt-dlp
    to solve YouTube's playback signature/n-challenge on some videos)."""
    return shutil.which("node") is not None


def ensure_dir(path: str | Path) -> Path:
    p = Path(path).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def free_space_bytes(path: str | Path) -> int:
    """Return free disk space (bytes) for the volume containing `path`."""
    p = Path(path).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(p)
    return usage.free


def has_enough_space(path: str | Path, required_bytes: int | None, margin: float = 1.05) -> bool:
    """Check free space against an estimated requirement with a safety margin."""
    if not required_bytes:
        return True
    return free_space_bytes(path) >= required_bytes * margin
