"""
Reusable Rich UI building blocks shared by every menu screen: message panels,
tables, progress bars bound to yt-dlp hooks, the system-info sidebar, and the
in-app log viewer.
"""

from __future__ import annotations

from typing import Optional

from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table
from rich.text import Text

from database.models import HistoryRecord
from downloader.base import VideoInfo
from utils.filesystem import human_duration, human_size
from utils.helpers import system_info


def show_success(console: Console, message: str, title: str = "Success") -> None:
    console.print(Panel(f"[success]✔ {message}[/success]", title=title, border_style="success", expand=False))


def show_error(console: Console, message: str, title: str = "Error") -> None:
    console.print(Panel(f"[error]✖ {message}[/error]", title=title, border_style="error", expand=False))


def show_warning(console: Console, message: str, title: str = "Warning") -> None:
    console.print(Panel(f"[warning]⚠ {message}[/warning]", title=title, border_style="warning", expand=False))


def show_info(console: Console, message: str, title: str = "Info") -> None:
    console.print(Panel(f"[info]ℹ {message}[/info]", title=title, border_style="info", expand=False))


def video_info_panel(info: VideoInfo) -> Panel:
    """Render metadata (title, uploader, duration, resolutions, size) as a panel."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold", justify="right")
    table.add_column()

    table.add_row("Title", Text(info.title, style="title"))
    table.add_row("Uploader", info.uploader)
    table.add_row("Duration", human_duration(info.duration))
    table.add_row("Upload Date", _format_date(info.upload_date))
    if info.view_count is not None:
        table.add_row("Views", f"{info.view_count:,}")
    if info.is_playlist:
        table.add_row("Playlist Videos", str(info.playlist_count or len(info.entries)))
    else:
        resolutions = info.available_resolutions()
        table.add_row("Available Resolutions", ", ".join(resolutions) or "Unknown")
        table.add_row("Estimated Size (best)", human_size(info.estimated_size()))

    return Panel(table, title="[title]Video Information[/title]", border_style="panel.border")


def _format_date(raw: Optional[str]) -> str:
    if not raw or len(raw) != 8:
        return "Unknown"
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"


def playlist_table(info: VideoInfo) -> Table:
    table = Table(title=f"Playlist: {info.title}", header_style="table.header", expand=True)
    table.add_column("#", justify="right", width=4)
    table.add_column("Title", overflow="ellipsis", max_width=60)
    table.add_column("Duration", justify="right", width=10)
    for i, entry in enumerate(info.entries, start=1):
        title = entry.get("title") or "Untitled"
        duration = human_duration(entry.get("duration"))
        table.add_row(str(i), title, duration)
    return table


def history_table(records: list[HistoryRecord]) -> Table:
    table = Table(title="Download History", header_style="table.header", expand=True)
    table.add_column("ID", justify="right", width=5)
    table.add_column("Title", overflow="ellipsis", max_width=40)
    table.add_column("Type", width=10)
    table.add_column("Size", justify="right", width=10)
    table.add_column("Duration", justify="right", width=10)
    table.add_column("Date", width=19)
    table.add_column("Status", width=10)
    for r in records:
        status_style = "success" if r.status == "completed" else "error"
        table.add_row(
            str(r.id), r.title, r.dtype, human_size(r.size_bytes),
            human_duration(r.duration_seconds), r.date,
            f"[{status_style}]{r.status}[/{status_style}]",
        )
    return table


def stats_panel(stats: dict) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold", justify="right")
    table.add_column()
    table.add_row("Total Downloads", str(stats["total"]))
    table.add_row("Total Size", human_size(stats["total_bytes"]))
    table.add_row("Total Duration", human_duration(stats["total_seconds"]))
    for dtype, count in stats.get("by_type", {}).items():
        table.add_row(f"  {dtype.title()}", str(count))
    return Panel(table, title="[title]Download Statistics[/title]", border_style="panel.border")


def system_info_panel() -> Panel:
    info = system_info()
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold", justify="right")
    table.add_column()
    for key, value in info.items():
        table.add_row(key, value)
    return Panel(table, title="[title]System Info[/title]", border_style="panel.border")


def build_download_progress(console: Console) -> Progress:
    """A rich Progress bar preconfigured with speed/ETA/percentage columns,
    used for video/audio/playlist downloads (bound to yt-dlp progress hooks).

    IMPORTANT: must receive the app's themed Console instance — otherwise
    Progress creates its own default Console (no theme), and semantic style
    names like "progress.bar" get misinterpreted as literal color names.
    """
    return Progress(
        SpinnerColumn(style="accent"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, style="dim", complete_style="progress.bar"),
        "[progress.percentage]{task.percentage:>3.0f}%",
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def log_viewer_panel(lines: list[str], max_lines: int = 25) -> Panel:
    tail = lines[-max_lines:]
    text = Text("".join(tail) or "No log entries yet.", style="dim")
    return Panel(text, title="[title]Log Viewer (tail)[/title]", border_style="panel.border")


def about_panel(version: str) -> Panel:
    body = Group(
        Text("TubeForge", style="brand", justify="center"),
        Text(f"Version {version}", style="subtitle", justify="center"),
        Text(""),
        Text("A modern, terminal-based YouTube downloader built on yt-dlp,", justify="center"),
        Text("Rich, and Prompt Toolkit.", justify="center"),
        Text(""),
        Text("License: MIT", style="dim", justify="center"),
        Text("https://github.com/ArshiaBourbour/TubeForge", style="info", justify="center"),
    )
    return Panel(body, title="[title]About[/title]", border_style="panel.border", padding=(1, 4))
