"""
Validation helpers: YouTube URL detection/classification and misc input checks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


class URLType(Enum):
    VIDEO = auto()
    PLAYLIST = auto()
    CHANNEL = auto()
    SHORTS = auto()
    INVALID = auto()


@dataclass(frozen=True)
class URLInfo:
    url: str
    kind: URLType
    video_id: str | None = None
    playlist_id: str | None = None


_YOUTUBE_HOST_RE = re.compile(
    r"^(https?://)?(www\.|m\.|music\.)?(youtube\.com|youtu\.be)", re.IGNORECASE
)
_VIDEO_ID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})")
_PLAYLIST_ID_RE = re.compile(r"[?&]list=([A-Za-z0-9_-]+)")
_CHANNEL_RE = re.compile(r"youtube\.com/(?:channel/|c/|@)([A-Za-z0-9_.-]+)", re.IGNORECASE)


def is_youtube_url(url: str) -> bool:
    return bool(_YOUTUBE_HOST_RE.match(url.strip()))


def classify_url(url: str) -> URLInfo:
    """Classify a pasted URL into video / playlist / channel / shorts / invalid."""
    url = url.strip()
    if not url or not is_youtube_url(url):
        return URLInfo(url=url, kind=URLType.INVALID)

    playlist_match = _PLAYLIST_ID_RE.search(url)
    video_match = _VIDEO_ID_RE.search(url)
    channel_match = _CHANNEL_RE.search(url)

    if "/shorts/" in url and video_match:
        return URLInfo(url=url, kind=URLType.SHORTS, video_id=video_match.group(1))

    # A bare playlist link (no v=) is a full playlist request.
    if playlist_match and not video_match:
        return URLInfo(url=url, kind=URLType.PLAYLIST, playlist_id=playlist_match.group(1))

    if video_match:
        return URLInfo(
            url=url,
            kind=URLType.VIDEO,
            video_id=video_match.group(1),
            playlist_id=playlist_match.group(1) if playlist_match else None,
        )

    if channel_match and "/videos" in url or (channel_match and not video_match and not playlist_match):
        return URLInfo(url=url, kind=URLType.CHANNEL)

    return URLInfo(url=url, kind=URLType.INVALID)


def sanitize_filename(name: str, max_length: int = 150) -> str:
    """Strip characters that are illegal/problematic across Windows/macOS/Linux filesystems."""
    name = re.sub(r'[\\/:*?"<>|]', "_", name).strip()
    name = re.sub(r"\s+", " ", name)
    if len(name) > max_length:
        name = name[:max_length].rstrip()
    return name or "untitled"


def parse_index_range(spec: str, count: int) -> list[int]:
    """
    Parse a user-provided range spec like '1,3,5-8' into a sorted list of
    0-based indices, clamped to [0, count).
    """
    indices: set[int] = set()
    spec = spec.strip()
    if not spec:
        return list(range(count))

    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, _, end_s = part.partition("-")
            try:
                start, end = int(start_s), int(end_s)
            except ValueError:
                continue
            for i in range(start, end + 1):
                if 1 <= i <= count:
                    indices.add(i - 1)
        else:
            try:
                i = int(part)
            except ValueError:
                continue
            if 1 <= i <= count:
                indices.add(i - 1)

    return sorted(indices)
