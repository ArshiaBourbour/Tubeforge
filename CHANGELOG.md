# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-07-17

### Added
- Initial public release of TubeForge.
- Animated ASCII splash screen and colorful two-column main menu.
- Video downloads with resolution selection (360p–4K), FFmpeg remuxing to MP4, and resume support.
- Audio extraction to MP3, WAV, AAC, FLAC, M4A, and Opus with configurable bitrate.
- Playlist downloads: entire playlist, index range (`1,3,5-8`), or hand-picked selection.
- Channel video downloads (uploads feed) with the same range-selection UX as playlists.
- Standalone thumbnail downloader.
- Subtitle downloader supporting manual and auto-generated captions in any language.
- Video Information screen (title, uploader, duration, upload date, resolutions, estimated size).
- Persistent JSON-backed Settings (download folder, quality/format defaults, theme, concurrency, filename template, proxy, language).
- SQLite-backed Download History with search, delete, CSV export, and aggregate statistics.
- Clipboard URL auto-detection when pasting links.
- Five built-in color themes: Midnight, Dracula, Solarized, Nord, Mono.
- Live Rich progress bars with percentage, speed, ETA, and per-item playlist status.
- Friendly, non-crashing error handling for age-restricted/private/removed videos, network failures, SSL errors, and missing FFmpeg.
- Rotating log file at `~/.tubeforge/logs/tubeforge.log`.
- Clean architecture: `cli/`, `downloader/`, `database/`, and `utils/` layers with no cross-layer leakage.

### Known Limitations
- No cookie/authentication support yet for age-restricted or member-only content.
- Batch operations (playlist/channel) report per-item failures rather than pre-validating every entry up front.
