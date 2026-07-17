"""
Animated startup splash screen and small reusable spinner/typewriter effects.
"""

from __future__ import annotations

import time
from pathlib import Path

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.txt"


def _load_logo() -> str:
    try:
        return LOGO_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "TubeForge"


def show_splash(console: Console, version: str = "1.0.0", fast: bool = False) -> None:
    """
    Render an animated splash: the logo fades/builds in line by line, then a
    short 'initializing' progress flourish, before handing off to the main menu.

    `fast=True` skips animation delays (used for --no-splash / CI environments).
    """
    logo_lines = _load_logo().splitlines()
    delay = 0.0 if fast else 0.035

    with Live(console=console, refresh_per_second=30, screen=False) as live:
        rendered = ""
        for line in logo_lines:
            rendered += line + "\n"
            live.update(_splash_panel(rendered, console))
            if delay:
                time.sleep(delay)

        stages = [
            "Initializing core modules...",
            "Loading configuration...",
            "Preparing download engine...",
            "Checking FFmpeg availability...",
            "Ready.",
        ]
        for stage in stages:
            live.update(_splash_panel(rendered, console, status=stage))
            if not fast:
                time.sleep(0.25)


def _splash_panel(logo_text: str, console: Console, status: str | None = None) -> Panel:
    body = Text(logo_text, style="brand", justify="center")
    if status:
        body.append("\n" + status, style="dim")
    body.append("\n\nModern Terminal YouTube Downloader", style="subtitle")
    return Panel(
        Align.center(body, vertical="middle"),
        border_style="panel.border",
        padding=(1, 4),
        title="[title]TubeForge[/title]",
        subtitle=f"[dim]v{'{}'.format('1.0.0')}[/dim]",
    )


def spinner_step(console: Console, message: str, seconds: float = 0.6) -> None:
    """A short-lived spinner for quick operations (e.g. 'Connecting...')."""
    with console.status(f"[info]{message}[/info]", spinner="dots"):
        time.sleep(seconds)
