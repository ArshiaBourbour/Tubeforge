"""
User input prompts: URL entry (with clipboard auto-detection), quality/format
selection, directory selection, and confirmation dialogs. Built on
prompt_toolkit for line editing (history, arrow keys) and Rich for styling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console

from utils.validator import URLType, classify_url

try:
    import pyperclip  # type: ignore[import-untyped]

    _HAS_CLIPBOARD = True
except Exception:  # pragma: no cover - clipboard access is optional/platform-dependent
    _HAS_CLIPBOARD = False

_url_session: PromptSession = PromptSession(history=InMemoryHistory())
_text_session: PromptSession = PromptSession()


def detect_clipboard_url() -> Optional[str]:
    """Return a YouTube URL sitting in the clipboard, if any (best-effort)."""
    if not _HAS_CLIPBOARD:
        return None
    try:
        content = pyperclip.paste()
    except Exception:
        return None
    if content and classify_url(content.strip()).kind != URLType.INVALID:
        return content.strip()
    return None


def prompt_url(console: Console, label: str = "Paste YouTube URL") -> str:
    """Prompt for a URL, offering an auto-detected clipboard link as a suggestion."""
    clipboard_url = detect_clipboard_url()
    if clipboard_url:
        console.print(f"[dim]📋 Detected YouTube URL in clipboard: {clipboard_url}[/dim]")
        use_it = _text_session.prompt("Use this URL? [Y/n]: ").strip().lower()
        if use_it in ("", "y", "yes"):
            return clipboard_url

    while True:
        url = _url_session.prompt(f"{label}: ").strip()
        if not url:
            console.print("[warning]Please enter a URL, or press Ctrl+C to cancel.[/warning]")
            continue
        info = classify_url(url)
        if info.kind == URLType.INVALID:
            console.print("[error]That doesn't look like a valid YouTube URL. Try again.[/error]")
            continue
        return url


def prompt_choice(console: Console, label: str, options: list[str], default: Optional[str] = None) -> str:
    """Numbered choice prompt, e.g. quality/format/theme selection."""
    console.print(f"[title]{label}[/title]")
    for i, opt in enumerate(options, start=1):
        marker = " (default)" if opt == default else ""
        console.print(f"  [menu.number]{i}.[/menu.number] [menu.label]{opt}{marker}[/menu.label]")

    completer = WordCompleter([str(i) for i in range(1, len(options) + 1)] + options)
    while True:
        raw = PromptSession(completer=completer).prompt("> ").strip()
        if not raw and default:
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        if raw in options:
            return raw
        console.print("[error]Invalid choice, please enter a listed number or name.[/error]")


def prompt_text(console: Console, label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    raw = _text_session.prompt(f"{label}{suffix}: ").strip()
    return raw or default


def prompt_directory(console: Console, label: str, default: str) -> str:
    while True:
        raw = prompt_text(console, label, default)
        path = Path(raw).expanduser()
        try:
            path.mkdir(parents=True, exist_ok=True)
            return str(path)
        except OSError as exc:
            console.print(f"[error]Could not use that directory: {exc}[/error]")


def prompt_confirm(console: Console, label: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    raw = _text_session.prompt(f"{label} {suffix}: ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")


def prompt_range_spec(console: Console, count: int) -> str:
    console.print(
        f"[dim]Enter indices (e.g. 1,3,5-8) out of {count} videos, "
        "or press Enter for the entire playlist.[/dim]"
    )
    return _text_session.prompt("> ").strip()
