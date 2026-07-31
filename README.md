<div align="center">

# 🎬 TubeForge

### Modern • Fast • Powerful • Cross-Platform YouTube Downloader

A feature-rich terminal-based YouTube downloader built with **Python**, **yt-dlp**, and **Rich**, offering a beautiful interactive CLI, playlist and channel support, subtitle downloads, audio extraction, download history, configurable settings, and seamless FFmpeg integration.

---

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Rich](https://img.shields.io/badge/Rich-Terminal_UI-FAE742?style=for-the-badge&logo=python&logoColor=black)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Latest-FF0000?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Supported-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Prompt Toolkit](https://img.shields.io/badge/Prompt%20Toolkit-CLI-4B8BBE?style=for-the-badge)

![Windows](https://img.shields.io/badge/Windows-Supported-0078D6?style=for-the-badge&logo=windows)
![Linux](https://img.shields.io/badge/Linux-Supported-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/macOS-Supported-000000?style=for-the-badge&logo=apple)

![License](https://img.shields.io/github/license/YOUR_USERNAME/YOUR_REPOSITORY?style=for-the-badge)
![Release](https://img.shields.io/github/v/release/YOUR_USERNAME/YOUR_REPOSITORY?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/YOUR_REPOSITORY?style=for-the-badge)
![Forks](https://img.shields.io/github/forks/YOUR_USERNAME/YOUR_REPOSITORY?style=for-the-badge)
![Issues](https://img.shields.io/github/issues/YOUR_USERNAME/YOUR_REPOSITORY?style=for-the-badge)
![Contributors](https://img.shields.io/github/contributors/YOUR_USERNAME/YOUR_REPOSITORY?style=for-the-badge)

![Open Source](https://img.shields.io/badge/Open%20Source-Yes-success?style=for-the-badge)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-success?style=for-the-badge)
![Made With Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)
![CLI](https://img.shields.io/badge/Interface-Terminal-blueviolet?style=for-the-badge)

</div>

---

# ✨ Features

## 🎥 Video Downloads

- Download videos in the highest available quality
- Download specific resolutions
- Download private videos using cookies
- Merge separate video and audio streams automatically
- Support for hundreds of websites powered by yt-dlp

---

## 🎵 Audio Downloads

- Extract audio from videos
- Convert to MP3 using FFmpeg
- Preserve metadata whenever possible
- High-quality audio extraction

---

## 📺 Playlist Support

- Download complete playlists
- Download selected videos
- Resume interrupted playlist downloads
- Automatic numbering

---

## 📡 Channel Downloads

- Download an entire channel
- Download latest uploads
- Batch downloading
- Organized folder structure

---

## 💬 Subtitle Support

- Download subtitles
- Download auto-generated subtitles
- Multiple language support
- Save subtitles separately

---

## 🖼 Thumbnail Downloads

- Download video thumbnails
- Keep original resolution
- Automatic naming

---

## 📜 Download History

- SQLite-powered history
- Search previous downloads
- Store metadata
- Persistent records

---

## ⚙ Settings

- Persistent configuration
- Default output folder
- Preferred quality
- Theme selection
- Audio preferences

---

## 🎨 Beautiful Terminal Interface

- Rich-powered UI
- Colored menus
- Progress bars
- Live download status
- Interactive prompts

---

## 📝 Logging

- Detailed logs
- Error reporting
- Debug information
- Easy troubleshooting

---

## 🌍 Cross Platform

- Windows
- Linux
- macOS

---

# 🚀 Why TubeForge?

Unlike basic download scripts, TubeForge provides a complete terminal experience.

✔ Beautiful interactive interface

✔ Download history

✔ Theme support

✔ Configuration system

✔ Playlist management

✔ Channel downloading

✔ Subtitle downloading

✔ FFmpeg integration

✔ SQLite database

✔ Rich progress bars

✔ Easy to use

✔ Clean architecture

✔ Modular source code

✔ Beginner friendly

✔ Open Source

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core Language |
| yt-dlp | Download Engine |
| Rich | Terminal UI |
| FFmpeg | Audio/Video Processing |
| SQLite | Download History |
| Prompt Toolkit | Interactive CLI |
| Pyperclip | Clipboard Support |
| Logging | Logs & Debugging |

---

# 📦 Project Highlights

- Modern architecture
- Clean codebase
- Modular design
- Easy maintenance
- Extensible
- Lightweight
- Fast
- Reliable
- Open Source
- Cross-platform

# 📋 Requirements

Before running TubeForge, make sure the following software is installed on your system.

| Requirement | Version |
|------------|---------|
| Python | 3.10 or newer |
| pip | Latest |
| FFmpeg | Required for audio conversion |
| Git | Optional |

---

# 📥 Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git

cd YOUR_REPOSITORY
```

---

## Create Virtual Environment

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install FFmpeg

### Windows

Download FFmpeg from:

https://ffmpeg.org/download.html

or

```powershell
winget install Gyan.FFmpeg
```

---

### macOS

```bash
brew install ffmpeg
```

---

### Ubuntu / Debian

```bash
sudo apt update

sudo apt install ffmpeg
```

---

## Verify Installation

```bash
ffmpeg -version
```

---

# ▶ Quick Start

Launch TubeForge

```bash
python main.py
```

or

```bash
python3 main.py
```

---

# 🎮 Usage

After launching the application you'll be presented with an interactive menu.

Simply:

1. Choose a download option
2. Paste a video or playlist URL
3. Select desired quality
4. Wait for download to complete

That's it!

---

# 📂 Project Structure

```
TubeForge/
│
├── cli/
│   ├── animations.py
│   ├── menu.py
│   ├── prompts.py
│   ├── theme.py
│   └── ui.py
│
├── database/
│   ├── history.py
│   └── models.py
│
├── downloads/
│
├── logs/
│
├── settings/
│   └── config.json
│
├── utils/
│   ├── filesystem.py
│   ├── helpers.py
│   ├── logger.py
│   └── validator.py
│
├── main.py
├── config.py
├── requirements.txt
└── README.md
```

---

# ⚙ Configuration

TubeForge stores its configuration in

```
settings/config.json
```

Configuration includes

- Default download directory
- Preferred quality
- Audio settings
- Theme
- Download behavior
- FFmpeg preferences

All settings persist between sessions.

---

# 📜 Download History

TubeForge automatically stores downloaded media information using SQLite.

History includes

- Video title
- URL
- Download date
- Media type
- Resolution
- Output location

This allows users to review previous downloads without downloading the same content repeatedly.

---

# 📁 Output Directory

Downloaded files are saved inside

```
downloads/
```

unless another output directory is configured.

---

# 🖥 Supported Platforms

| Platform | Status |
|-----------|--------|
| Windows | ✅ |
| Linux | ✅ |
| macOS | ✅ |

---

# 🔒 Privacy

TubeForge does not:

- Collect analytics
- Track users
- Send telemetry
- Upload downloaded content
- Require online accounts

Everything runs locally on your machine.

---

# ⚡ Performance

TubeForge is optimized for

- Fast downloads
- Low memory usage
- Responsive interface
- Efficient playlist processing
- Reliable FFmpeg integration

---