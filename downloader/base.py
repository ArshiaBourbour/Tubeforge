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
    success/error/warning states ourselves via Rich panels instead.

    Also accumulates warning/debug lines into `captured` so callers can
    inspect them after a failure — this matters because yt-dlp reports
    important context (e.g. "YouTube is forcing SABR streaming for this
    client") as a *warning*, separate from the final raised exception's
    message, and we need that text to diagnose the real cause.
    """

    def __init__(self):
        self.captured: list[str] = []

    def debug(self, msg: str) -> None:
        self.captured.append(msg)
        log.debug(msg)

    def warning(self, msg: str) -> None:
        self.captured.append(msg)
        log.warning(msg)

    def error(self, msg: str) -> None:
        self.captured.append(msg)
        log.error(msg)

    def text(self) -> str:
        return "\n".join(self.captured)


def base_opts(cfg: Config, progress_hook: Optional[ProgressCallback] = None) -> dict[str, Any]:
    source = getattr(cfg, "cookie_source", "none")

    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "ignoreerrors": False,
        "verbose": True,
        "logger": _SilentLogger(),
        "outtmpl": str(Path(cfg.download_folder).expanduser() / cfg.filename_template),
        "restrictfilenames": False,
        "concurrent_fragment_downloads": max(1, cfg.concurrent_downloads),
        "retries": 5,
        "fragment_retries": 5,
        # YouTube is currently (2026) rolling out "SABR" streaming, which
        # strips download URLs from the *web* client's formats entirely —
        # this happens independent of sign-in/cookies and shows up as
        # "Requested format is not available" even for ordinary public
        # videos. The android client is generally not subject to this, so
        # we always try it first; web/tv are kept as fallbacks in case a
        # given video's formats are only exposed there.
        "extractor_args": {"youtube": {"player_client": ["android", "web", "tv"]}},
        # yt-dlp requires explicit opt-in to download the actual JS
        # challenge-solver script bundle on first use (even with the
        # yt-dlp-ejs package installed, this is off by default). Without
        # this, playback signature solving silently fails and only
        # storyboard/thumbnail "formats" are returned.
        "remote_components": ["ejs:github", "ejs:npm"],
        # yt-dlp only enables the "deno" JS runtime by default for solving
        # YouTube's playback signature challenge — it will NOT use Node.js
        # even if it's installed on PATH unless explicitly told to. Enable
        # every commonly-available runtime here; yt-dlp picks whichever is
        # actually present, in priority order (deno > node > quickjs > bun).
        "js_runtimes": {"deno": {}, "node": {}, "quickjs": {}, "bun": {}},
    }

    if cfg.proxy:
        opts["proxy"] = cfg.proxy
    if progress_hook is not None:
        opts["progress_hooks"] = [progress_hook]

    # Cookie source: lets yt-dlp present an authenticated session, which
    # resolves most "Sign in to confirm..." / bot-check walls that YouTube
    # now shows even for ordinary public videos. This is a *separate*
    # concern from the SABR/format issue above — both can be needed.
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
        if "requested format is not available" in str(exc).lower():
            log.warning("Default format unavailable while fetching info for %s, retrying with 'format=best'", url)
            captured_1 = opts["logger"].text()
            opts["format"] = "best"
            opts["logger"] = _SilentLogger()
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError as exc2:
                combined_log = captured_1 + "\n" + opts["logger"].text()
                raise DownloadError(_no_formats_message(str(exc2), combined_log), cause=exc2, detail=_tail(combined_log)) from exc2
        else:
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


def _tail(text: str, max_lines: int = 14) -> str:
    """Return the last several non-empty lines of a captured log, for display."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines[-max_lines:])


def _no_formats_message(raw_error: str, captured_log: str = "") -> str:
    """
    Used when even the most permissive format selector fails after trying
    android/web/tv clients. As of 2026, this is most often caused by
    YouTube's "SABR" streaming rollout stripping download URLs from the
    web client's formats — a widespread, currently ongoing yt-dlp/YouTube
    issue, not something specific to this app or this video. Give an
    accurate explanation rather than guessing DRM/livestream.

    `captured_log` should include any warning/debug lines yt-dlp emitted
    during the attempt (see _SilentLogger) — the SABR signature usually
    only appears there, not in the final raised exception's own text.
    """
    lowered = (raw_error + "\n" + captured_log).lower()
    if "n challenge solving failed" in lowered or "javascript runtime" in lowered or "signature solving failed" in lowered:
        from utils.filesystem import node_available

        node_status = (
            "Node.js is installed and was detected on this system, so that part is fine."
            if node_available()
            else "No JavaScript runtime (e.g. Node.js) was detected on this system — install it from https://nodejs.org."
        )
        return (
            "yt-dlp couldn't solve YouTube's playback signature challenge. As of 2026 this needs "
            "two things: (1) a JavaScript runtime — " + node_status + " (2) the 'yt-dlp-ejs' "
            "package: run 'pip install -U yt-dlp-ejs' in the same environment/venv as yt-dlp. "
            "On first use, yt-dlp also needs network access to download the actual solver "
            "script — if you're behind a firewall/proxy, that download may be getting blocked. "
            "See https://github.com/yt-dlp/yt-dlp/wiki/EJS for details."
        )
    if "sabr" in lowered or "only images are available" in lowered or "missing a url" in lowered:
        return (
            "YouTube is currently forcing a newer streaming method (SABR) that yt-dlp's "
            "extractors haven't fully caught up with yet for this video — this is a known, "
            "ongoing issue affecting yt-dlp broadly right now, not specific to this video or "
            "this app. Try: (1) update yt-dlp to the latest version — 'pip install -U yt-dlp' "
            "(the project patches around this frequently), (2) install Node.js so yt-dlp can "
            "run its JS challenge solver, (3) if it still fails, this specific video may need "
            "to wait for yt-dlp's next fix — check https://github.com/yt-dlp/yt-dlp/issues for "
            "the current status."
        )
    return (
        "This video has no downloadable formats available (it may be a live stream still in "
        "progress, a members-only/DRM-protected upload, or otherwise restricted)."
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
