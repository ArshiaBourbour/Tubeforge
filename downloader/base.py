"""
Shared yt-dlp plumbing used by every downloader module (video/audio/playlist/
subtitles/thumbnail). Centralizes:

- metadata extraction (`fetch_info`)
- a progress-hook protocol that the CLI's Rich progress bars subscribe to
- common yt-dlp option scaffolding (output template, proxy, concurrency)
- a uniform exception type so the CLI can render clean error messages
  instead of raw tracebacks (see cli/ui.py -> show_error)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import yt_dlp

from config import Config
from utils.logger import get_logger

log = get_logger("downloader.base")

ProgressCallback = Callable[[dict], None]


class DownloadError(Exception):
    """Raised for any failure we want the UI to show as a friendly message."""

    def __init__(self, message: str, cause: Exception | None = None, detail: str | None = None):
        super().__init__(message)
        self.cause = cause
        self.detail = detail or (str(cause).splitlines()[-1] if cause else None)


@dataclass
class VideoInfo:
    title: str
    uploader: str
    duration: Optional[float]
    upload_date: Optional[str]
    thumbnail_url: Optional[str]
    view_count: Optional[int]
    like_count: Optional[int]
    webpage_url: str
    formats: list[dict] = field(default_factory=list)
    is_playlist: bool = False
    playlist_count: Optional[int] = None
    entries: list[dict] = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    def available_resolutions(self) -> list[str]:
        heights = sorted(
            {f.get("height") for f in self.formats if f.get("height") and f.get("vcodec") != "none"},
            reverse=True,
        )
        return [f"{h}p" for h in heights]

    def estimated_size(self, height: Optional[int] = None) -> Optional[int]:
        """Best-effort estimated file size for a given target height (or overall best)."""
        candidates = [
            f for f in self.formats
            if f.get("vcodec") != "none" and (height is None or f.get("height") == height)
        ]
        sizes = [f.get("filesize") or f.get("filesize_approx") for f in candidates]
        sizes = [s for s in sizes if s]
        return max(sizes) if sizes else None


class _SilentLogger:
    """Swallows yt-dlp's own stdout/stderr messages; we render all
    success/error/warning states ourselves via Rich panels instead."""

    def debug(self, msg: str) -> None:
        log.debug(msg)

    def warning(self, msg: str) -> None:
        log.warning(msg)

    def error(self, msg: str) -> None:
        log.error(msg)


def base_opts(cfg: Config, progress_hook: Optional[ProgressCallback] = None) -> dict[str, Any]:
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "ignoreerrors": False,
        "logger": _SilentLogger(),
        "outtmpl": str(Path(cfg.download_folder).expanduser() / cfg.filename_template),
        "restrictfilenames": False,
        "concurrent_fragment_downloads": max(1, cfg.concurrent_downloads),
        "retries": 5,
        "fragment_retries": 5,
        # The web client is the one most often hit by YouTube's bot/sign-in
        # check. Trying android/tv first sometimes avoids it, but as of 2026
        # this is not reliable on its own — cookies (cfg.cookie_source) are
        # the actual fix when this still fails. Keep this as a cheap first
        # attempt, not a substitute for authentication.
        "extractor_args": {"youtube": {"player_client": ["android", "tv", "web"]}},
    }
    if cfg.proxy:
        opts["proxy"] = cfg.proxy
    if progress_hook is not None:
        opts["progress_hooks"] = [progress_hook]

    # Cookie source: lets yt-dlp present an authenticated session, which
    # resolves most "Sign in to confirm..." / bot-check walls that YouTube
    # now shows even for ordinary public videos.
    source = getattr(cfg, "cookie_source", "none")
    if source and source not in ("none", "file"):
        opts["cookiesfrombrowser"] = (source,)
    elif source == "file" and getattr(cfg, "cookie_file_path", ""):
        opts["cookiefile"] = str(Path(cfg.cookie_file_path).expanduser())

    return opts


def fetch_info(url: str, cfg: Config, flat_playlist: bool = False) -> VideoInfo:
    """
    Extract metadata for a single video, shorts URL, or playlist without
    downloading anything. Raises DownloadError on any failure (age-gate,
    removed video, network issue, private video, etc.).
    """
    opts = base_opts(cfg)
    opts["extract_flat"] = "in_playlist" if flat_playlist else False
    opts["skip_download"] = True

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as exc:
        raise DownloadError(friendly_message(str(exc)), cause=exc) from exc
    except Exception as exc:  # pragma: no cover - defensive catch-all
        raise DownloadError(f"Unexpected error while fetching info: {exc}", cause=exc) from exc

    if data is None:
        raise DownloadError("No data returned for this URL.")

    is_playlist = data.get("_type") == "playlist" or "entries" in data
    entries = list(data.get("entries") or []) if is_playlist else []

    return VideoInfo(
        title=data.get("title", "Unknown title"),
        uploader=data.get("uploader") or data.get("channel") or "Unknown uploader",
        duration=data.get("duration"),
        upload_date=data.get("upload_date"),
        thumbnail_url=data.get("thumbnail"),
        view_count=data.get("view_count"),
        like_count=data.get("like_count"),
        webpage_url=data.get("webpage_url", url),
        formats=data.get("formats") or [],
        is_playlist=is_playlist,
        playlist_count=data.get("playlist_count") or (len(entries) if entries else None),
        entries=entries,
        raw=data,
    )


def friendly_message(raw_error: str) -> str:
    """Translate common yt-dlp error substrings into user-friendly text.

    Matches are ordered most-specific-first and use whole-phrase needles
    (never a bare word like "age", which would falsely match inside
    unrelated words such as "page" or "storage").
    """
    lowered = raw_error.lower()
    mapping = [
        ("age-restricted", "This video is age-restricted and cannot be accessed without authentication."),
        ("confirm your age", "This video is age-restricted and cannot be accessed without authentication."),
        ("private video", "This video is private and cannot be downloaded."),
        ("video unavailable", "This video is unavailable (it may have been removed or region-blocked)."),
        ("could not find", "TubeForge couldn't read cookies from the selected browser (it may not be installed, or its cookie database is locked/encrypted on this OS). Try a different browser in Settings → Cookie Source, or use the 'file' option with an exported cookies.txt instead."),
        ("could not copy", "TubeForge couldn't read cookies from the selected browser — make sure the browser is completely closed (not just minimized) and try again."),
        ("decrypt", "TubeForge couldn't decrypt the selected browser's cookies on this system. Use the 'file' option in Settings → Cookie Source with an exported cookies.txt instead."),
        ("sign in to confirm", "YouTube's bot-check is blocking this download. Fix, in order: (1) update yt-dlp — 'pip install -U yt-dlp', (2) in Settings → Cookie Source, pick your browser and make sure it's fully closed and logged into YouTube (try Firefox if Chrome fails), (3) if still blocked, export a cookies.txt file and select it under Cookie Source → file, (4) turn off any VPN/proxy."),
        ("copyright", "This video was taken down due to a copyright claim."),
        ("certificate verify failed", "A secure connection could not be established (SSL certificate error). Check your network/proxy settings."),
        ("name or service not known", "Could not resolve the network address. Check your internet connection."),
        ("network is unreachable", "A network error occurred. Check your internet connection and try again."),
        ("connection refused", "The connection was refused. Check your internet connection or proxy settings."),
        ("timed out", "The connection timed out. Check your internet connection and try again."),
        ("unsupported url", "This URL is not a valid or supported YouTube link."),
    ]
    for needle, friendly in mapping:
        if needle in lowered:
            return friendly
    return f"Download failed: {raw_error.splitlines()[-1] if raw_error else 'Unknown error'}"


def build_progress_hook(callback: ProgressCallback) -> ProgressCallback:
    """Wrap a UI callback so hook exceptions never crash yt-dlp's download thread."""

    def _hook(d: dict) -> None:
        try:
            callback(d)
        except Exception:  # pragma: no cover - UI callbacks must never break downloads
            log.exception("Progress callback raised an exception")

    return _hook
