# TubeForge

A modern, terminal-based YouTube downloader with a polished, interactive TUI — built on [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [Rich](https://github.com/Textualize/rich).

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

```
 _____     _          ______
|_   _|   | |         |  ___|
  | |_   _| |__   ___  | |_ ___  _ __ __ _  ___
  | | | | | '_ \ / _ \ |  _/ _ \| '__/ _` |/ _ \
  | | |_| | |_) |  __/ | || (_) | | | (_| |  __/
  \_/\__,_|_.__/ \___| \_| \___/|_|  \__, |\___|
                                      __/ |
                                     |___/
```

## Features

- **Animated splash screen** and a colorful, two-column main menu
- **Video downloads** with selectable resolution (360p–4K), format conversion, and resume support
- **Audio extraction** to MP3, WAV, AAC, FLAC, M4A, or Opus via FFmpeg
- **Playlist downloads** — entire playlist, a specific range (`1,3,5-8`), or hand-picked videos
- **Channel downloads** — pull every video (or a selection) from a channel's uploads
- **Thumbnail downloader** — grabs the best-quality thumbnail as a standalone image
- **Subtitle downloader** — manual or auto-generated captions, any language, SRT format
- **Video information viewer** — title, uploader, duration, upload date, resolutions, estimated size
- **Persistent Settings** (JSON) — download folder, quality defaults, theme, concurrency, filename template, proxy, language
- **Download History** (SQLite) — search, delete entries, export to CSV, view aggregate statistics
- **Clipboard URL detection** — auto-suggests a YouTube link found in your clipboard
- **Five built-in themes** — Midnight, Dracula, Solarized, Nord, and Mono
- **Live progress bars** — percentage, transfer speed, ETA, and completed-file counts
- **Graceful error handling** — age-restricted/private/removed videos, network failures, and missing FFmpeg never crash the app
- **Rotating log file** with an in-app log viewer for troubleshooting
- **Clean architecture** — fully separated CLI, downloader, database, and utility layers

## Screenshots

> _Add screenshots or terminal recordings (e.g. via [asciinema](https://asciinema.org/)) here._

| Main Menu | Video Info | Download Progress |
|---|---|---|
| `screenshots/menu.png` | `screenshots/info.png` | `screenshots/progress.png` |

## Requirements

- Python 3.12 or newer
- [FFmpeg](https://ffmpeg.org/) (required for audio extraction and video remuxing)
- A terminal with 256-color / true-color support for the full visual experience

## FFmpeg Setup

TubeForge shells out to `ffmpeg` for audio conversion, thumbnail embedding, and metadata writing. It must be discoverable on your system `PATH`.

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
1. Download a build from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) or `winget install ffmpeg`
2. Add the `bin` folder to your system `PATH`
3. Verify with `ffmpeg -version` in a new terminal

If FFmpeg is missing, TubeForge will detect this and show a clear in-app warning before attempting audio downloads — it will not crash.

## Installation

```bash
git clone https://github.com/ArshiaBourbour/TubeForge.git
cd TubeForge
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Skip the startup animation (useful in CI or slower terminals):

```bash
python main.py --no-splash
```

Then navigate the numbered main menu:

```
1.  Download Video              2.  Download Audio (MP3)
3.  Download Playlist           4.  Download Thumbnail
5.  Show Video Information      6.  Download Subtitles
7.  Download Channel Videos     8.  Settings
9.  Download History            10. About
11. Exit
```

Paste a YouTube URL when prompted — TubeForge validates it, fetches metadata, and walks you through quality/format/output-folder selection before showing a live progress bar.

### Playlist range syntax

When downloading part of a playlist or channel, enter indices like:

```
1,3,5-8
```

This selects videos 1, 3, 5, 6, 7, and 8 from the listing shown above the prompt.

## Configuration

Settings are stored at `~/.tubeforge/config.json` and can be edited via the in-app **Settings** menu or by hand:

| Setting | Description |
|---|---|
| `download_folder` | Default output directory |
| `video_quality` | Default resolution (e.g. `1080p`, `Best`) |
| `audio_quality` | Default bitrate (e.g. `192kbps`) |
| `audio_format` | Default audio container (`mp3`, `wav`, `aac`, `flac`, `m4a`, `opus`) |
| `theme` | `midnight`, `dracula`, `solarized`, `nord`, or `mono` |
| `concurrent_downloads` | Parallel fragment downloads (1–10) |
| `filename_template` | yt-dlp output template, e.g. `%(title)s.%(ext)s` |
| `proxy` | Optional proxy URL |
| `language` | Interface language code (`en`, `fa`) |

Download history lives in a separate SQLite database at `~/.tubeforge/history.db`.

## Folder Structure

```
tubeforge/
├── main.py                 # Entry point
├── config.py                # Config dataclass + JSON persistence
├── cli/
│   ├── menu.py               # Main menu loop & per-option screens
│   ├── theme.py              # Rich color themes
│   ├── animations.py         # Splash screen & spinners
│   ├── prompts.py            # Input prompts (prompt_toolkit)
│   └── ui.py                 # Panels, tables, progress bars
├── downloader/
│   ├── base.py               # Shared yt-dlp plumbing & error translation
│   ├── video.py               # Video downloads
│   ├── audio.py               # Audio extraction
│   ├── playlist.py            # Playlist/channel batch downloads
│   ├── subtitles.py           # Subtitle downloads
│   └── thumbnail.py           # Thumbnail downloads
├── database/
│   ├── history.py             # SQLite history store
│   └── models.py              # Data models
├── settings/
│   └── config.json            # Shipped default configuration
├── utils/
│   ├── validator.py           # URL classification & sanitization
│   ├── logger.py              # Rotating file logger
│   ├── filesystem.py          # Size formatting, disk space, FFmpeg checks
│   └── helpers.py             # Misc small utilities
├── assets/
│   └── logo.txt                # ASCII logo
├── downloads/                  # Default output location
├── requirements.txt
└── README.md
```

## Known Limitations

This is a first stable release (`v1.0.0`). A few things to be upfront about:

- **YouTube's "SABR streaming" rollout (2026):** YouTube is currently forcing a newer streaming protocol that, for some videos, strips download URLs from the standard web client's formats — this is a widespread, actively-tracked yt-dlp/YouTube issue (see [yt-dlp#12482](https://github.com/yt-dlp/yt-dlp/issues/12482)) affecting many downloaders right now, not something specific to this app.
- **"n challenge solving failed" / JS runtime errors:** Related to the above, YouTube's playback signature challenge now requires yt-dlp's separate `yt-dlp-ejs` package (included in `requirements.txt`) *plus* a JavaScript runtime like Node.js on PATH. If you still see this error after installing both, run `pip install -U yt-dlp yt-dlp-ejs` — this part of yt-dlp is under active development and updates frequently. See [the EJS wiki](https://github.com/yt-dlp/yt-dlp/wiki/EJS).
- Keep yt-dlp itself updated too (`pip install -U yt-dlp`) — the project patches around YouTube's changes frequently.
- Downloading requires network access to YouTube; the app cannot verify the yt-dlp extractor still matches YouTube's current site structure — if YouTube changes something, update yt-dlp.
- Age-restricted, private, and members-only videos require authentication via Settings → Cookie Source (browser cookies or an exported `cookies.txt`).
- Very large channels/playlists are fetched via `extract_flat`, which is fast but doesn't pre-validate every entry's availability — some entries may fail individually during batch download (TubeForge reports these as partial failures rather than aborting the whole batch).

## Contributing

Issues and pull requests are welcome. Please keep changes modular and consistent with the existing clean-architecture layout (`cli/` never talks to `yt-dlp` directly — it goes through `downloader/`).

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes with clear messages
4. Open a pull request

## License

Released under the [MIT License](LICENSE).
