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

# 📊 Feature Comparison

| Feature | TubeForge |
|----------|:---------:|
| Interactive Terminal UI | ✅ |
| High Quality Downloads | ✅ |
| Playlist Downloads | ✅ |
| Channel Downloads | ✅ |
| Audio Extraction | ✅ |
| MP3 Conversion | ✅ |
| Subtitle Downloads | ✅ |
| Thumbnail Downloads | ✅ |
| Download History | ✅ |
| SQLite Database | ✅ |
| Theme Support | ✅ |
| Persistent Settings | ✅ |
| Progress Bars | ✅ |
| Logging System | ✅ |
| FFmpeg Integration | ✅ |
| Cross Platform | ✅ |
| Modular Architecture | ✅ |
| Open Source | ✅ |

---

# 📜 Logging

TubeForge includes a built-in logging system designed to simplify debugging and troubleshooting.

Logs include:

- Application startup
- Download status
- Errors and exceptions
- FFmpeg output
- yt-dlp messages
- Configuration changes

Log files are stored inside:

```
logs/
```

---

# 🗂 Download History

Every successful download is automatically stored in the local SQLite database.

Stored information includes:

- Video Title
- Original URL
- Download Date
- Download Type
- Selected Quality
- File Path

This makes it easy to keep track of previously downloaded media.

---

# 🧩 Architecture

```
                 User
                   │
                   ▼
          Interactive CLI
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
 Menu System              Configuration
      │                         │
      ▼                         ▼
 Download Engine          Settings Manager
      │
      ▼
      yt-dlp
      │
      ▼
    FFmpeg
      │
      ▼
 Downloads Folder
      │
      ▼
 SQLite History Database
```

---

# ⚠ Error Handling

TubeForge gracefully handles many common situations, including:

- Invalid URLs
- Network failures
- Missing FFmpeg
- Unsupported websites
- Playlist errors
- Interrupted downloads
- Permission errors
- Existing files
- Invalid configuration

Whenever possible, meaningful error messages are displayed to help users resolve issues quickly.

---

# ❓ Frequently Asked Questions

### Does TubeForge require FFmpeg?

Only for audio extraction, format conversion, and stream merging.

---

### Can I download playlists?

Yes.

TubeForge fully supports playlist downloads.

---

### Can I download an entire YouTube channel?

Yes.

Channel downloads are supported through yt-dlp.

---

### Is TubeForge cross-platform?

Yes.

Windows, Linux, and macOS are supported.

---

### Where are downloaded files stored?

By default:

```
downloads/
```

This location can be changed in the configuration.

---

### Is my data sent anywhere?

No.

Everything runs locally on your computer.

---

# 🔧 Troubleshooting

## FFmpeg not found

Install FFmpeg and ensure it is available in your system PATH.

---

## Python command not found

Verify Python is installed correctly:

```bash
python --version
```

or

```bash
python3 --version
```

---

## Permission denied

Run the terminal with appropriate permissions or choose another output directory.

---

## Download failed

Possible reasons:

- Invalid URL
- Private content
- Internet connection
- Website restrictions
- Outdated yt-dlp

Update dependencies using:

```bash
pip install -U yt-dlp
```

---

# 🛣 Roadmap

## Completed

- Interactive CLI
- Download Videos
- Download Audio
- Playlist Support
- Channel Support
- Subtitle Downloads
- Thumbnail Downloads
- SQLite History
- Logging
- Themes
- Persistent Settings
- FFmpeg Integration

---

## Planned

- Download Queue
- Multi-threaded Downloads
- Automatic Updates
- Plugin System
- Localization
- Download Scheduler
- Built-in Media Player
- GUI Version
- Portable Build
- Export History
- Batch URL Import

---

# 🤝 Contributing

Contributions are always welcome.

If you'd like to contribute:

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push your branch.
5. Open a Pull Request.

Please make sure your code follows the project's style guidelines and includes appropriate documentation where necessary.

---

# 💡 Code Style

This project follows:

- PEP 8
- Modular Design
- Readable Code
- Meaningful Naming
- Consistent Formatting
- Reusable Components

---

# ❤️ Acknowledgements

Special thanks to the amazing open-source projects that make TubeForge possible.

- Python
- yt-dlp
- Rich
- FFmpeg
- Prompt Toolkit
- SQLite

Without these projects, TubeForge would not exist.

---

# 📄 License

This project is licensed under the MIT License.

See the LICENSE file for more information.

---

# ⭐ Support the Project

If you found this project useful:

⭐ Star the repository

🍴 Fork the project

🐞 Report bugs

💡 Suggest new features

🤝 Contribute with Pull Requests

Every contribution is greatly appreciated.

---

<div align="center">

## 🚀 TubeForge

Modern • Fast • Beautiful • Open Source

Built with ❤️ using Python, Rich, yt-dlp and FFmpeg.

If you like this project, don't forget to ⭐ star the repository.

</div>