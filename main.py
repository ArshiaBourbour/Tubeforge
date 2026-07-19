from __future__ import annotations

import sys

from rich.console import Console

from cli.animations import show_splash
from cli.menu import App
from cli.theme import get_theme
from config import Config
from utils.logger import get_logger

log = get_logger("main")


def main() -> int:
    fast = "--no-splash" in sys.argv

    cfg = Config.load()
    console = Console(theme=get_theme(cfg.theme))

    try:
        show_splash(console, fast=fast)
        app = App(console)
        app.run()
    except KeyboardInterrupt:
        console.print("\n[warning]Interrupted. Goodbye![/warning]")
        return 0
    except Exception as exc:
        log.exception("Fatal error")
        console.print(f"\n[error]A fatal error occurred: {exc}[/error]")
        console.print("[dim]Check ~/.tubeforge/logs/tubeforge.log for details.[/dim]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
