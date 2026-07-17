"""
Data models used by the SQLite-backed download history.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DownloadType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    PLAYLIST = "playlist"
    THUMBNAIL = "thumbnail"
    SUBTITLE = "subtitle"
    CHANNEL = "channel"


class DownloadStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    PARTIAL = "partial"


@dataclass
class HistoryRecord:
    id: int | None
    title: str
    url: str
    date: str
    size_bytes: int
    dtype: str
    output_path: str
    duration_seconds: int
    status: str = DownloadStatus.COMPLETED.value

    def as_row(self) -> tuple:
        return (
            self.title,
            self.url,
            self.date,
            self.size_bytes,
            self.dtype,
            self.output_path,
            self.duration_seconds,
            self.status,
        )
