from __future__ import annotations

from pathlib import Path
from typing import Optional

import yt_dlp

from config import Config
from downloader.base import DownloadError, ProgressCallback, base_opts, build_progress_hook, friendly_message
from utils.filesystem import ffmpeg_available
from utils.logger import get_logger

log = get_logger("downloader.audio")

_QUALITY_MAP = {
    "320kbps": "320", "256kbps": "256", "192kbps": "192", "128kbps": "128", "Best": "0",
}


def download_audio(
    url: str,
    cfg: Config,
    audio_format: str = "mp3",
    quality: str = "192kbps",
    output_dir: Optional[str] = None,
    on_progress: Optional[ProgressCallback] = None,
) -> Path:
    """Download and convert a video's audio track. Returns the final file path."""
    if not ffmpeg_available():
        raise DownloadError(
            "FFmpeg was not found on your system PATH. Audio conversion requires "
            "FFmpeg — please install it and try again (see README's FFmpeg setup section)."
        )

    opts = base_opts(cfg)
    opts["format"] = "bestaudio/best"

    outtmpl_dir = Path(output_dir).expanduser() if output_dir else Path(cfg.download_folder).expanduser()
    opts["outtmpl"] = str(outtmpl_dir / cfg.filename_template)

    preferred_quality = _QUALITY_MAP.get(quality, "192")
    opts["postprocessors"] = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": preferred_quality,
        }
    ]
    if cfg.embed_thumbnail and audio_format == "mp3":
        opts["writethumbnail"] = True
        opts["postprocessors"].append({"key": "EmbedThumbnail"})
    if cfg.write_metadata:
        opts["postprocessors"].append({"key": "FFmpegMetadata"})

    result_path: dict[str, Optional[str]] = {"path": None}

    def _hook(d: dict) -> None:
        if d.get("status") == "finished":
            result_path["path"] = d.get("filename")
        if on_progress:
            on_progress(d)

    opts["progress_hooks"] = [build_progress_hook(_hook)]

    log.info("Starting audio download: %s (%s @ %s)", url, audio_format, quality)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_path = Path(ydl.prepare_filename(info))
    except yt_dlp.utils.DownloadError as exc:
        log.error("Audio download failed for %s: %s", url, exc)
        raise DownloadError(friendly_message(str(exc)), cause=exc) from exc
    except Exception as exc:
        log.exception("Unexpected error downloading audio %s", url)
        raise DownloadError(f"Unexpected error: {exc}", cause=exc) from exc

    final_path = raw_path.with_suffix(f".{audio_format}")
    log.info("Audio download complete: %s", final_path if final_path.exists() else raw_path)
    return final_path if final_path.exists() else raw_path
