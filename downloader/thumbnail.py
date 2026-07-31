"""
Thumbnail download logic — fetches the best-quality thumbnail image
without touching video/audio streams.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yt_dlp

from config import Config
from downloader.base import DownloadError, base_opts, friendly_message
from utils.logger import get_logger

log = get_logger("downloader.thumbnail")


def download_thumbnail(url: str, cfg: Config, output_dir: Optional[str] = None) -> Path:
    """Download only the video's best thumbnail image. Returns the saved file path."""
    opts = base_opts(cfg)
    outtmpl_dir = Path(output_dir).expanduser() if output_dir else Path(cfg.download_folder).expanduser()
    opts["outtmpl"] = str(outtmpl_dir / cfg.filename_template)
    opts.update(
        {
            "skip_download": True,
            "writethumbnail": True,
        }
    )

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            base_name = Path(ydl.prepare_filename(info)).with_suffix("")
    except yt_dlp.utils.DownloadError as exc:
        raise DownloadError(friendly_message(str(exc)), cause=exc) from exc
    except Exception as exc:
        raise DownloadError(f"Unexpected error downloading thumbnail: {exc}", cause=exc) from exc

    for ext in ("jpg", "jpeg", "png", "webp"):
        candidate = base_name.with_suffix(f".{ext}")
        if candidate.exists():
            log.info("Thumbnail saved: %s", candidate)
            return candidate

    # Fall back: search directory for any newly created image with matching stem.
    matches = list(base_name.parent.glob(f"{base_name.name}*.*"))
    image_matches = [m for m in matches if m.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
    if image_matches:
        return image_matches[0]

    raise DownloadError("Thumbnail file could not be located after download.")
