from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import yt_dlp

from config import Config
from downloader.base import DownloadError, ProgressCallback, VideoInfo, base_opts, friendly_message, build_progress_hook, fetch_info
from downloader.base import _no_formats_message, _tail
from utils.logger import get_logger

log = get_logger("downloader.video")

_HEIGHT_MAP = {
    "2160p": 2160, "1440p": 1440, "1080p": 1080,
    "720p": 720, "480p": 480, "360p": 360,
}


def _format_selector(quality: str) -> str:
    """Build a yt-dlp -f format string for the requested quality label."""
    if quality in ("Best", "best"):
        return "bestvideo+bestaudio/best"
    if quality in ("Worst", "worst"):
        return "worstvideo+worstaudio/worst"
    height = _HEIGHT_MAP.get(quality)
    if height is None:
        return "bestvideo+bestaudio/best"
    return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"


def get_video_info(url: str, cfg: Config) -> VideoInfo:
    return fetch_info(url, cfg)


def download_video(
    url: str,
    cfg: Config,
    quality: str = "1080p",
    output_dir: Optional[str] = None,
    on_progress: Optional[ProgressCallback] = None,
    resume: bool = True,
) -> Path:
    """
    Download a single video at the requested quality.

    Returns the final file path on success. Raises DownloadError on failure;
    the CLI layer is responsible for catching this and rendering a friendly
    error panel (never a raw traceback).
    """
    opts = base_opts(cfg)
    opts["format"] = _format_selector(quality)
    opts["merge_output_format"] = "mp4"
    opts["continuedl"] = resume
    opts["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]

    if output_dir:
        outtmpl = str(Path(output_dir).expanduser() / cfg.filename_template)
    else:
        outtmpl = opts["outtmpl"]
    opts["outtmpl"] = outtmpl

    if cfg.embed_thumbnail:
        opts.setdefault("postprocessors", []).append({"key": "EmbedThumbnail"})
        opts["writethumbnail"] = True
    if cfg.write_metadata:
        opts.setdefault("postprocessors", []).append({"key": "FFmpegMetadata"})

    result_path: dict[str, Optional[str]] = {"path": None}

    def _hook(d: dict) -> None:
        if d.get("status") == "finished":
            result_path["path"] = d.get("filename")
        if on_progress:
            on_progress(d)

    opts["progress_hooks"] = [build_progress_hook(_hook)]

    log.info("Starting video download: %s (quality=%s)", url, quality)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = ydl.prepare_filename(info)
    except yt_dlp.utils.DownloadError as exc:
        exc_text = str(exc).lower()
        if "requested format is not available" in exc_text and opts["format"] != "best":
            # This particular video's available formats didn't intersect
            # with our height/codec filter (common with certain live
            # replays, some Shorts, or restricted-format videos). Retry
            # once with a plain "best" selector before giving up.
            log.warning("Format %r unavailable for %s, retrying with 'best'", opts["format"], url)
            captured_1 = opts["logger"].text()
            opts["format"] = "best"
            from downloader.base import _SilentLogger
            opts["logger"] = _SilentLogger()
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    final_path = ydl.prepare_filename(info)
            except yt_dlp.utils.DownloadError as exc2:
                log.error("Video download retry failed for %s: %s", url, exc2)
                combined_log = captured_1 + "\n" + opts["logger"].text()
                raise DownloadError(_no_formats_message(str(exc2), combined_log), cause=exc2, detail=_tail(combined_log)) from exc2
        elif "http error 403" in exc_text:
            # Sometimes transient/session-related — one quick automatic
            # retry before surfacing the PO-token explanation to the user.
            log.warning("Got HTTP 403 downloading %s, retrying once", url)
            time.sleep(2)
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    final_path = ydl.prepare_filename(info)
            except yt_dlp.utils.DownloadError as exc2:
                log.error("Video download retry after 403 failed for %s: %s", url, exc2)
                raise DownloadError(friendly_message(str(exc2)), cause=exc2) from exc2
        else:
            log.error("Video download failed for %s: %s", url, exc)
            raise DownloadError(friendly_message(str(exc)), cause=exc) from exc
    except Exception as exc:
        log.exception("Unexpected error downloading video %s", url)
        raise DownloadError(f"Unexpected error: {exc}", cause=exc) from exc

    resolved = Path(result_path["path"] or final_path)
    # yt-dlp reports the pre-merge filename sometimes; prefer the .mp4 sibling if present.
    mp4_candidate = resolved.with_suffix(".mp4")
    log.info("Video download complete: %s", mp4_candidate if mp4_candidate.exists() else resolved)
    return mp4_candidate if mp4_candidate.exists() else resolved
