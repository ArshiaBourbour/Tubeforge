"""
Subtitle/closed-caption download logic (manual + auto-generated captions).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yt_dlp

from config import Config
from downloader.base import DownloadError, base_opts, fetch_info, friendly_message
from utils.logger import get_logger

log = get_logger("downloader.subtitles")


def list_available_subtitles(url: str, cfg: Config) -> dict[str, list[str]]:
    """Return {'manual': [lang codes...], 'auto': [lang codes...]} for a video."""
    opts = base_opts(cfg)
    opts.update({"skip_download": True, "listsubtitles": True})
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as exc:
        raise DownloadError(friendly_message(str(exc)), cause=exc) from exc

    manual = sorted((data or {}).get("subtitles", {}).keys())
    auto = sorted((data or {}).get("automatic_captions", {}).keys())
    return {"manual": manual, "auto": auto}


def download_subtitles(
    url: str,
    cfg: Config,
    languages: list[str],
    include_auto: bool = True,
    sub_format: str = "srt",
    output_dir: Optional[str] = None,
) -> list[Path]:
    """Download subtitle files only (no video/audio) for the given languages."""
    opts = base_opts(cfg)
    outtmpl_dir = Path(output_dir).expanduser() if output_dir else Path(cfg.download_folder).expanduser()
    opts["outtmpl"] = str(outtmpl_dir / cfg.filename_template)
    opts.update(
        {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": include_auto,
            "subtitleslangs": languages or ["en"],
            "subtitlesformat": sub_format,
        }
    )

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            base_name = Path(ydl.prepare_filename(info)).with_suffix("")
    except yt_dlp.utils.DownloadError as exc:
        raise DownloadError(friendly_message(str(exc)), cause=exc) from exc
    except Exception as exc:
        raise DownloadError(f"Unexpected error downloading subtitles: {exc}", cause=exc) from exc

    found = list(base_name.parent.glob(f"{base_name.name}*.{sub_format}"))
    log.info("Downloaded %d subtitle file(s) for %s", len(found), url)
    return found
