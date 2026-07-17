"""
Color themes for TubeForge's Rich-based interface.

Each theme maps semantic style names (used throughout cli/ui.py and
cli/menu.py) to concrete colors, so switching themes in Settings
re-colors the entire app without touching any rendering code.
"""

from __future__ import annotations

from rich.theme import Theme

THEMES: dict[str, Theme] = {
    "midnight": Theme(
        {
            "brand": "bold bright_cyan",
            "accent": "bright_magenta",
            "title": "bold white",
            "subtitle": "grey70",
            "success": "bold green",
            "error": "bold red",
            "warning": "bold yellow",
            "info": "bright_blue",
            "menu.number": "bold bright_cyan",
            "menu.label": "white",
            "panel.border": "bright_cyan",
            "progress.bar": "bright_magenta",
            "table.header": "bold bright_cyan",
            "dim": "grey50",
        }
    ),
    "dracula": Theme(
        {
            "brand": "bold magenta",
            "accent": "bright_magenta",
            "title": "bold pink1",
            "subtitle": "grey70",
            "success": "bold green",
            "error": "bold red",
            "warning": "bold yellow",
            "info": "bright_cyan",
            "menu.number": "bold magenta",
            "menu.label": "white",
            "panel.border": "magenta",
            "progress.bar": "bright_magenta",
            "table.header": "bold magenta",
            "dim": "grey50",
        }
    ),
    "solarized": Theme(
        {
            "brand": "bold yellow",
            "accent": "bright_yellow",
            "title": "bold wheat1",
            "subtitle": "grey70",
            "success": "bold green",
            "error": "bold red",
            "warning": "bold orange1",
            "info": "cyan",
            "menu.number": "bold yellow",
            "menu.label": "wheat1",
            "panel.border": "yellow",
            "progress.bar": "yellow",
            "table.header": "bold yellow",
            "dim": "grey50",
        }
    ),
    "nord": Theme(
        {
            "brand": "bold blue",
            "accent": "bright_blue",
            "title": "bold steel_blue1",
            "subtitle": "grey70",
            "success": "bold green",
            "error": "bold red",
            "warning": "bold yellow",
            "info": "bright_cyan",
            "menu.number": "bold blue",
            "menu.label": "white",
            "panel.border": "blue",
            "progress.bar": "blue",
            "table.header": "bold blue",
            "dim": "grey50",
        }
    ),
    "mono": Theme(
        {
            "brand": "bold white",
            "accent": "bold white",
            "title": "bold white",
            "subtitle": "grey70",
            "success": "bold white",
            "error": "bold white underline",
            "warning": "bold white",
            "info": "white",
            "menu.number": "bold white",
            "menu.label": "grey78",
            "panel.border": "white",
            "progress.bar": "white",
            "table.header": "bold white",
            "dim": "grey50",
        }
    ),
}


def get_theme(name: str) -> Theme:
    return THEMES.get(name, THEMES["midnight"])
