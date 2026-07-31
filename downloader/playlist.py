"""
Playlist download logic. Supports downloading an entire playlist, a
user-selected subset of indices, or a contiguous range, reusing the
video/audio downloader functions per-entry so behavior stays consistent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from config import Config
from downloader.audio import download_audio
from downloader.base import DownloadError, VideoInfo, fetch_info
from downloader.video import download_video
from utils.logger import get_logger

log = get_logger("downloader.playlist")

PlaylistItemCallback = Callable[[int, int, str, str], None]  # (index, total, title, status)


def get_playlist_info(url: str, cfg: Config) -> VideoInfo:
    """Fetch flat playlist metadata (fast — doesn't resolve each video's formats)."""
    info = fetch_info(url, cfg, flat_playlist=True)
    if not info.is_playlist:
        raise DownloadError("The provided URL does not point to a playlist.")
    return info


def estimate_playlist_size(info: VideoInfo) -> Optional[int]:
    """Rough total size estimate: entries rarely carry filesize in flat mode,
    so this returns None when unavailable rather than guessing."""
    sizes = [e.get("filesize") or e.get("filesize_approx") for e in info.entries]
    sizes = [s for s in sizes if s]
    if not sizes or len(sizes) < len(info.entries):
        return None
    return sum(sizes)


def download_playlist(
    info: VideoInfo,
    cfg: Config,
    indices: list[int],
    mode: str = "video",
    quality: str = "1080p",
    audio_format: str = "mp3",
    output_dir: Optional[str] = None,
    on_item: Optional[PlaylistItemCallback] = None,
    on_progress=None,
) -> tuple[list[Path], list[tuple[str, str]]]:
    """
    Download selected entries (by 0-based index into info.entries).

    Returns (successful_paths, failures) where failures is a list of
    (title, error_message) tuples so the UI can report partial-success
    clearly instead of aborting the whole batch on one bad video.
    """
    successes: list[Path] = []
    failures: list[tuple[str, str]] = []
    total = len(indices)

    playlist_dir = Path(output_dir).expanduser() if output_dir else Path(cfg.download_folder).expanduser()
    playlist_subdir = playlist_dir / _safe_playlist_name(info.title)
    playlist_subdir.mkdir(parents=True, exist_ok=True)

    for pos, idx in enumerate(indices, start=1):
        if idx >= len(info.entries):
            continue
        entry = info.entries[idx]
        title = entry.get("title", f"Video {idx + 1}")
        video_url = entry.get("url") or entry.get("webpage_url") or entry.get("id")
        if video_url and not str(video_url).startswith("http"):
            video_url = f"https://www.youtube.com/watch?v={video_url}"

        if on_item:
            on_item(pos, total, title, "starting")

        try:
            if mode == "audio":
                path = download_audio(
                    video_url, cfg, audio_format=audio_format,
                    output_dir=str(playlist_subdir), on_progress=on_progress,
                )
            else:
                path = download_video(
                    video_url, cfg, quality=quality,
                    output_dir=str(playlist_subdir), on_progress=on_progress,
                )
            successes.append(path)
            if on_item:
                on_item(pos, total, title, "done")
        except DownloadError as exc:
            log.warning("Playlist item failed (%s): %s", title, exc)
            failures.append((title, str(exc)))
            if on_item:
                on_item(pos, total, title, "failed")

    log.info(
        "Playlist download finished: %d succeeded, %d failed (of %d)",
        len(successes), len(failures), total,
    )
    return successes, failures


def _safe_playlist_name(title: str) -> str:
    from utils.validator import sanitize_filename

    return sanitize_filename(title, max_length=100)
