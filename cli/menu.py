"""
The main menu loop and per-option screen handlers.

Each `_handle_*` method is a self-contained screen: it gathers input via
cli/prompts.py, calls into the downloader/database layers, and renders
results via cli/ui.py. All exceptions from the downloader layer are caught
here so the app never crashes — every failure becomes a friendly panel.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import (
    AUDIO_FORMATS,
    AUDIO_QUALITIES,
    COOKIE_BROWSERS,
    LANGUAGES,
    THEMES,
    VIDEO_QUALITIES,
    Config,
)
from database.history import HistoryDB
from database.models import DownloadStatus, DownloadType, HistoryRecord
from downloader.audio import download_audio
from downloader.base import DownloadError
from downloader.playlist import download_playlist, estimate_playlist_size, get_playlist_info
from downloader.subtitles import download_subtitles, list_available_subtitles
from downloader.thumbnail import download_thumbnail
from downloader.video import download_video, get_video_info
from utils.filesystem import ffmpeg_available, has_enough_space, human_size
from utils.helpers import now_iso
from utils.logger import get_logger
from utils.validator import URLType, classify_url, parse_index_range

from cli import ui
from cli.prompts import (
    prompt_choice,
    prompt_confirm,
    prompt_directory,
    prompt_range_spec,
    prompt_text,
    prompt_url,
)

log = get_logger("cli.menu")

VERSION = "1.0.0"

MENU_ITEMS = [
    ("1", "Download Video"),
    ("2", "Download Audio (MP3)"),
    ("3", "Download Playlist"),
    ("4", "Download Thumbnail"),
    ("5", "Show Video Information"),
    ("6", "Download Subtitles"),
    ("7", "Download Channel Videos"),
    ("8", "Settings"),
    ("9", "Download History"),
    ("10", "About"),
    ("11", "Exit"),
]


class App:
    def __init__(self, console: Console):
        self.console = console
        self.cfg = Config.load()
        self.db = HistoryDB()

    # ---- main loop ---------------------------------------------------

    def run(self) -> None:
        while True:
            self._render_menu()
            choice = prompt_text(self.console, "Select an option (1-11)")
            handler = {
                "1": self._handle_download_video,
                "2": self._handle_download_audio,
                "3": self._handle_download_playlist,
                "4": self._handle_download_thumbnail,
                "5": self._handle_show_info,
                "6": self._handle_download_subtitles,
                "7": self._handle_download_channel,
                "8": self._handle_settings,
                "9": self._handle_history,
                "10": self._handle_about,
                "11": self._handle_exit,
            }.get(choice.strip())

            if handler is None:
                ui.show_warning(self.console, "Please enter a number between 1 and 11.")
                continue

            try:
                if handler() is False:  # exit sentinel
                    break
            except KeyboardInterrupt:
                ui.show_warning(self.console, "Operation canceled.")
            except DownloadError as exc:
                ui.show_error(self.console, str(exc), detail=exc.detail)
                self._maybe_show_cookie_diagnostic(exc)
            except Exception as exc:  # pragma: no cover - last line of defense
                log.exception("Unhandled error in menu handler")
                ui.show_error(self.console, f"Something went wrong: {exc}")

            self.console.print()

    def _render_menu(self) -> None:
        self.console.rule("[brand]TubeForge[/brand]", style="panel.border")
        table = Table.grid(padding=(0, 3))
        table.add_column()
        table.add_column()
        rows = [(f"[menu.number]{n}.[/menu.number] [menu.label]{label}[/menu.label]") for n, label in MENU_ITEMS]
        # two-column layout
        for i in range(0, len(rows), 2):
            pair = rows[i : i + 2]
            table.add_row(*pair) if len(pair) == 2 else table.add_row(pair[0], "")
        self.console.print(Panel(table, title="[title]Main Menu[/title]", border_style="panel.border"))

    # ---- 1. Download Video -------------------------------------------

    def _handle_download_video(self):
        url = prompt_url(self.console)
        info = self._fetch_with_spinner(url)
        self.console.print(ui.video_info_panel(info))

        quality = prompt_choice(self.console, "Select video quality", VIDEO_QUALITIES, default=self.cfg.video_quality)
        out_dir = prompt_directory(self.console, "Output directory", self.cfg.download_folder)

        estimated = info.estimated_size()
        if not has_enough_space(out_dir, estimated):
            if not prompt_confirm(self.console, "Estimated size may exceed free disk space. Continue anyway?", default=False):
                return

        path = self._run_download(
            lambda progress_cb: download_video(url, self.cfg, quality=quality, output_dir=out_dir, on_progress=progress_cb),
            description=info.title,
        )
        if path:
            self._record_history(info, DownloadType.VIDEO, path, out_dir)
            ui.show_success(self.console, f"Saved to {path}")

    # ---- 2. Download Audio -------------------------------------------

    def _handle_download_audio(self):
        if not ffmpeg_available():
            ui.show_error(
                self.console,
                "FFmpeg is required for audio extraction but was not found on PATH. "
                "See the README's FFmpeg setup section.",
            )
            return

        url = prompt_url(self.console)
        info = self._fetch_with_spinner(url)
        self.console.print(ui.video_info_panel(info))

        audio_format = prompt_choice(self.console, "Select audio format", AUDIO_FORMATS, default=self.cfg.audio_format)
        quality = prompt_choice(self.console, "Select audio quality", AUDIO_QUALITIES, default=self.cfg.audio_quality)
        out_dir = prompt_directory(self.console, "Output directory", self.cfg.download_folder)

        path = self._run_download(
            lambda progress_cb: download_audio(
                url, self.cfg, audio_format=audio_format, quality=quality, output_dir=out_dir, on_progress=progress_cb
            ),
            description=info.title,
        )
        if path:
            self._record_history(info, DownloadType.AUDIO, path, out_dir)
            ui.show_success(self.console, f"Saved to {path}")

    # ---- 3. Download Playlist ----------------------------------------

    def _handle_download_playlist(self):
        url = prompt_url(self.console, label="Paste YouTube playlist URL")
        classified = classify_url(url)
        if classified.kind not in (URLType.PLAYLIST, URLType.VIDEO):
            ui.show_error(self.console, "That URL doesn't appear to contain a playlist.")
            return

        with self.console.status("[info]Fetching playlist metadata...[/info]", spinner="dots"):
            info = get_playlist_info(url, self.cfg)

        self.console.print(ui.playlist_table(info))
        est_size = estimate_playlist_size(info)
        self.console.print(
            f"[dim]{len(info.entries)} videos found. "
            f"Estimated total size: {human_size(est_size) if est_size else 'Unknown'}[/dim]"
        )

        scope = prompt_choice(self.console, "Download scope", ["Entire playlist", "Selected videos / range"], default="Entire playlist")
        if scope == "Entire playlist":
            indices = list(range(len(info.entries)))
        else:
            spec = prompt_range_spec(self.console, len(info.entries))
            indices = parse_index_range(spec, len(info.entries))

        if not indices:
            ui.show_warning(self.console, "No videos selected.")
            return

        mode = prompt_choice(self.console, "Download as", ["video", "audio"], default="video")
        quality = self.cfg.video_quality
        audio_format = self.cfg.audio_format
        if mode == "video":
            quality = prompt_choice(self.console, "Select video quality", VIDEO_QUALITIES, default=self.cfg.video_quality)
        else:
            audio_format = prompt_choice(self.console, "Select audio format", AUDIO_FORMATS, default=self.cfg.audio_format)

        out_dir = prompt_directory(self.console, "Output directory", self.cfg.download_folder)

        def on_item(pos, total, title, status):
            symbol = {"starting": "…", "done": "✔", "failed": "✖"}.get(status, "")
            self.console.print(f"[dim]({pos}/{total})[/dim] {symbol} {title}")

        with ui.build_download_progress(self.console) as progress:
            task_id = progress.add_task(f"Playlist: {info.title}", total=len(indices))

            def on_progress(d: dict):
                if d.get("status") == "finished":
                    progress.update(task_id, advance=1)

            successes, failures = download_playlist(
                info, self.cfg, indices, mode=mode, quality=quality, audio_format=audio_format,
                output_dir=out_dir, on_item=on_item, on_progress=on_progress,
            )

        for path in successes:
            self._record_history(info, DownloadType.PLAYLIST, Path(path), out_dir)

        if successes:
            ui.show_success(self.console, f"{len(successes)} video(s) downloaded successfully.")
        if failures:
            detail = "\n".join(f"• {title}: {msg}" for title, msg in failures[:10])
            ui.show_warning(self.console, f"{len(failures)} video(s) failed:\n{detail}")

    # ---- 4. Download Thumbnail ----------------------------------------

    def _handle_download_thumbnail(self):
        url = prompt_url(self.console)
        info = self._fetch_with_spinner(url)
        out_dir = prompt_directory(self.console, "Output directory", self.cfg.download_folder)
        with self.console.status("[info]Downloading thumbnail...[/info]", spinner="dots"):
            path = download_thumbnail(url, self.cfg, output_dir=out_dir)
        self._record_history(info, DownloadType.THUMBNAIL, path, out_dir)
        ui.show_success(self.console, f"Thumbnail saved to {path}")

    # ---- 5. Show Video Information -------------------------------------

    def _handle_show_info(self):
        url = prompt_url(self.console)
        info = self._fetch_with_spinner(url)
        self.console.print(ui.video_info_panel(info))
        if info.is_playlist:
            self.console.print(ui.playlist_table(info))

    # ---- 6. Download Subtitles -----------------------------------------

    def _handle_download_subtitles(self):
        url = prompt_url(self.console)
        with self.console.status("[info]Checking available subtitles...[/info]", spinner="dots"):
            available = list_available_subtitles(url, self.cfg)

        if not available["manual"] and not available["auto"]:
            ui.show_warning(self.console, "No subtitles are available for this video.")
            return

        self.console.print(f"[dim]Manual: {', '.join(available['manual']) or 'none'}[/dim]")
        self.console.print(f"[dim]Auto-generated: {', '.join(available['auto']) or 'none'}[/dim]")

        langs_raw = prompt_text(self.console, "Language codes (comma-separated)", "en")
        languages = [l.strip() for l in langs_raw.split(",") if l.strip()]
        include_auto = prompt_confirm(self.console, "Include auto-generated captions if manual unavailable?", default=True)
        out_dir = prompt_directory(self.console, "Output directory", self.cfg.download_folder)

        with self.console.status("[info]Downloading subtitles...[/info]", spinner="dots"):
            files = download_subtitles(url, self.cfg, languages, include_auto=include_auto, output_dir=out_dir)

        if files:
            ui.show_success(self.console, "Downloaded:\n" + "\n".join(str(f) for f in files))
        else:
            ui.show_warning(self.console, "No subtitle files were produced for the requested languages.")

    # ---- 7. Download Channel Videos ------------------------------------

    def _handle_download_channel(self):
        url = prompt_url(self.console, label="Paste YouTube channel URL")
        classified = classify_url(url)
        if classified.kind not in (URLType.CHANNEL, URLType.PLAYLIST):
            ui.show_warning(
                self.console,
                "This doesn't look like a channel URL — treating it as a playlist/videos feed and attempting to fetch anyway.",
            )
        channel_videos_url = url if url.rstrip("/").endswith(("videos", "streams", "shorts")) else url.rstrip("/") + "/videos"

        with self.console.status("[info]Fetching channel video list (this can take a while for large channels)...[/info]", spinner="dots"):
            info = get_playlist_info(channel_videos_url, self.cfg)

        self.console.print(ui.playlist_table(info))
        spec = prompt_range_spec(self.console, len(info.entries))
        indices = parse_index_range(spec, len(info.entries))
        if not indices:
            ui.show_warning(self.console, "No videos selected.")
            return

        mode = prompt_choice(self.console, "Download as", ["video", "audio"], default="video")
        out_dir = prompt_directory(self.console, "Output directory", self.cfg.download_folder)

        with ui.build_download_progress(self.console) as progress:
            task_id = progress.add_task(f"Channel: {info.title}", total=len(indices))

            def on_progress(d: dict):
                if d.get("status") == "finished":
                    progress.update(task_id, advance=1)

            successes, failures = download_playlist(
                info, self.cfg, indices, mode=mode, output_dir=out_dir, on_progress=on_progress,
            )

        for path in successes:
            self._record_history(info, DownloadType.CHANNEL, Path(path), out_dir)
        if successes:
            ui.show_success(self.console, f"{len(successes)} video(s) downloaded from channel.")
        if failures:
            ui.show_warning(self.console, f"{len(failures)} video(s) failed.")

    # ---- 8. Settings ----------------------------------------------------

    def _handle_settings(self):
        self.console.print(Panel(self._settings_table(), title="[title]Current Settings[/title]", border_style="panel.border"))
        field = prompt_choice(
            self.console,
            "What would you like to change?",
            [
                "Download folder", "Video quality", "Audio quality", "Audio format",
                "Theme", "Concurrent downloads", "Filename template", "Proxy", "Language",
                "Cookie Source", "Update yt-dlp", "Back",
            ],
            default="Back",
        )
        if field == "Back":
            return
        if field == "Update yt-dlp":
            self._handle_update_ytdlp()
            return

        if field == "Download folder":
            self.cfg.download_folder = prompt_directory(self.console, "New download folder", self.cfg.download_folder)
        elif field == "Video quality":
            self.cfg.video_quality = prompt_choice(self.console, "Video quality", VIDEO_QUALITIES, default=self.cfg.video_quality)
        elif field == "Audio quality":
            self.cfg.audio_quality = prompt_choice(self.console, "Audio quality", AUDIO_QUALITIES, default=self.cfg.audio_quality)
        elif field == "Audio format":
            self.cfg.audio_format = prompt_choice(self.console, "Audio format", AUDIO_FORMATS, default=self.cfg.audio_format)
        elif field == "Theme":
            self.cfg.theme = prompt_choice(self.console, "Theme", THEMES, default=self.cfg.theme)
            from cli.theme import get_theme
            self.console.push_theme(get_theme(self.cfg.theme))
        elif field == "Concurrent downloads":
            raw = prompt_text(self.console, "Concurrent downloads (1-10)", str(self.cfg.concurrent_downloads))
            self.cfg.concurrent_downloads = max(1, min(10, int(raw) if raw.isdigit() else self.cfg.concurrent_downloads))
        elif field == "Filename template":
            self.cfg.filename_template = prompt_text(self.console, "yt-dlp filename template", self.cfg.filename_template)
        elif field == "Proxy":
            self.cfg.proxy = prompt_text(self.console, "Proxy URL (blank to disable)", self.cfg.proxy)
        elif field == "Language":
            self.cfg.language = prompt_choice(self.console, "Language", LANGUAGES, default=self.cfg.language)
        elif field == "Cookie Source":
            self.console.print(
                "[dim]Choose 'none' for no authentication, a browser name to read its logged-in "
                "session cookies, or 'file' to point at an exported cookies.txt.[/dim]"
            )
            choice = prompt_choice(self.console, "Cookie source", COOKIE_BROWSERS, default=self.cfg.cookie_source)
            self.cfg.cookie_source = choice
            if choice == "file":
                self.cfg.cookie_file_path = prompt_text(
                    self.console, "Path to cookies.txt", self.cfg.cookie_file_path or str(Path.home() / "cookies.txt")
                )

        self.cfg.save()
        ui.show_success(self.console, "Settings updated.")

    def _handle_update_ytdlp(self) -> None:
        """Run 'pip install -U yt-dlp' from inside the app.

        Outdated yt-dlp is the single most common cause of YouTube's
        sign-in/bot-check errors, since YouTube changes its site frequently
        and yt-dlp ships near-daily fixes for it.
        """
        import subprocess
        import sys as _sys

        with self.console.status("[info]Updating yt-dlp (pip install -U yt-dlp)...[/info]", spinner="dots"):
            try:
                result = subprocess.run(
                    [_sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                    capture_output=True, text=True, timeout=120,
                )
            except Exception as exc:
                ui.show_error(self.console, f"Could not run pip: {exc}")
                return

        if result.returncode == 0:
            last_line = next((l for l in reversed(result.stdout.strip().splitlines()) if l.strip()), "Done.")
            ui.show_success(self.console, f"yt-dlp updated.\n{last_line}\n\nRestart TubeForge for the update to take effect.")
        elif "externally-managed-environment" in result.stderr:
            ui.show_error(
                self.console,
                "Your system Python blocks direct pip installs (PEP 668). Fix by either:\n"
                "  • Running TubeForge inside a virtual environment (see README → Installation), or\n"
                "  • Running manually: pip install --upgrade yt-dlp --break-system-packages",
            )
        else:
            ui.show_error(self.console, f"pip install failed:\n{result.stderr.strip()[-500:]}")

    def _settings_table(self) -> Table:
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold", justify="right")
        table.add_column()
        for key, value in self.cfg.as_dict().items():
            table.add_row(key.replace("_", " ").title(), str(value) if value != "" else "(none)")
        return table

    # ---- 9. Download History --------------------------------------------

    def _handle_history(self):
        action = prompt_choice(self.console, "History", ["View recent", "Search", "Delete entry", "Export CSV", "Statistics", "Back"], default="View recent")
        if action == "Back":
            return
        if action == "View recent":
            self.console.print(ui.history_table(self.db.all(limit=50)))
        elif action == "Search":
            query = prompt_text(self.console, "Search term")
            self.console.print(ui.history_table(self.db.search(query)))
        elif action == "Delete entry":
            self.console.print(ui.history_table(self.db.all(limit=50)))
            raw_id = prompt_text(self.console, "Entry ID to delete")
            if raw_id.isdigit() and self.db.delete(int(raw_id)):
                ui.show_success(self.console, f"Deleted history entry {raw_id}.")
            else:
                ui.show_warning(self.console, "Entry not found.")
        elif action == "Export CSV":
            out = prompt_text(self.console, "Export path", str(Path.home() / "tubeforge_history.csv"))
            path = self.db.export_csv(out)
            ui.show_success(self.console, f"Exported history to {path}")
        elif action == "Statistics":
            self.console.print(ui.stats_panel(self.db.stats()))

    # ---- 10. About -------------------------------------------------------

    def _handle_about(self):
        self.console.print(ui.about_panel(VERSION))
        self.console.print(ui.system_info_panel())

    # ---- 11. Exit ----------------------------------------------------

    def _handle_exit(self):
        if prompt_confirm(self.console, "Exit TubeForge?", default=True):
            self.console.print("[brand]Goodbye! 👋[/brand]")
            return False
        return None

    # ---- shared helpers ----------------------------------------------

    def _fetch_with_spinner(self, url: str):
        with self.console.status("[info]Fetching metadata...[/info]", spinner="dots"):
            return get_video_info(url, self.cfg)

    def _run_download(self, download_call, description: str):
        with ui.build_download_progress(self.console) as progress:
            task_id = progress.add_task(description, total=100)

            def on_progress(d: dict):
                status = d.get("status")
                if status == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate")
                    downloaded = d.get("downloaded_bytes", 0)
                    if total:
                        progress.update(task_id, total=total, completed=downloaded)
                elif status == "finished":
                    progress.update(task_id, completed=progress.tasks[0].total or 100)

            try:
                return download_call(on_progress)
            except DownloadError as exc:
                progress.stop()
                ui.show_error(self.console, str(exc), detail=exc.detail)
                self._maybe_show_cookie_diagnostic(exc)
                return None

    def _maybe_show_cookie_diagnostic(self, exc: DownloadError) -> None:
        """
        When a bot-check / sign-in error happens, show exactly which cookie
        setting is currently active so it's obvious whether the config is
        being applied at all, versus a browser that yielded zero usable
        cookies (a very common silent failure).
        """
        if "bot-check" not in str(exc) and "sign-in" not in str(exc).lower():
            return

        source = self.cfg.cookie_source
        if source == "none":
            ui.show_info(
                self.console,
                "Cookie Source is currently set to 'none' — that's why no cookies were sent. "
                "Go to Settings → Cookie Source and pick your browser, or 'file' with a cookies.txt.",
                title="Diagnostic",
            )
        elif source == "file":
            path_ok = Path(self.cfg.cookie_file_path).expanduser().exists() if self.cfg.cookie_file_path else False
            status = "found" if path_ok else "NOT FOUND"
            ui.show_info(
                self.console,
                f"Cookie Source is set to 'file' → {self.cfg.cookie_file_path or '(empty)'} ({status}). "
                + ("" if path_ok else "That file doesn't exist — export a fresh cookies.txt and update the path in Settings."),
                title="Diagnostic",
            )
        else:
            ui.show_info(
                self.console,
                f"Cookie Source is set to '{source}', but yt-dlp still reports zero cookies used. "
                "This usually means that browser has no YouTube login session, or its cookie "
                "store couldn't be decrypted on this OS. Try: (1) log into YouTube in that exact "
                "browser and fully close it before retrying, or (2) switch to Settings → Cookie "
                "Source → file and use an exported cookies.txt instead (more reliable on Linux).",
                title="Diagnostic",
            )

    def _record_history(self, info, dtype: DownloadType, path: Path, out_dir: str) -> None:
        try:
            size = path.stat().st_size if path.exists() else 0
        except OSError:
            size = 0
        self.db.add(
            HistoryRecord(
                id=None,
                title=getattr(info, "title", path.stem),
                url=getattr(info, "webpage_url", ""),
                date=now_iso(),
                size_bytes=size,
                dtype=dtype.value,
                output_path=str(path),
                duration_seconds=int(getattr(info, "duration", 0) or 0),
                status=DownloadStatus.COMPLETED.value,
            )
        )
