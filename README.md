# Video Downloader

A simple Windows desktop video downloader built with Python and PySide6.

## Features

- Analyze media URLs
- Select video quality
- Select output format
- MP4 / MKV output
- Download queue
- Sequential downloads
- Cancel queue
- Download progress tracking
- Dark-themed graphical interface
- No terminal window required

## Screenshots

Add application screenshots here.

## Development Requirements

- Windows 10 / Windows 11
- Python 3.13
- PySide6 6.11.2
- yt-dlp 2026.8.19
- yt-dlp-ejs
- FFmpeg
- Deno

The released Windows application is packaged with PyInstaller and does not require Python to be installed separately.

## Build from Source

### 1. Create a virtual environment

From the project root:

```powershell
python -m venv .venv
```

### 2. Activate the virtual environment

In PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal should show something similar to:

```text
(.venv) PS C:\Users\<username>\Desktop\Video Downloader>
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Build the application

```powershell
python -m PyInstaller `
    --clean `
    --noconfirm `
    --windowed `
    --name "Video Downloader" `
    --icon ".\assets\video-downloader.ico" `
    --paths "." `
    --collect-all yt_dlp `
    --collect-all yt_dlp_ejs `
    ".\launcher.py"
```

The generated application will be located at:

```text
dist\Video Downloader\
```

## Running from Source

With the virtual environment activated:

```powershell
python -m app.main
```

## Download Location

By default, downloaded files are saved to:

```text
%USERPROFILE%\Downloads\Video Downloader
```

On Windows, this normally resolves to:

```text
C:\Users\<username>\Downloads\Video Downloader
```

## Project Structure

```text
Video Downloader/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── gui.py
├── core/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── cancellation.py
│   ├── download_manager.py
│   ├── download_queue.py
│   ├── download_task.py
│   ├── format_manager.py
│   └── queue_runner.py
├── services/
│   ├── __init__.py
│   └── ytdlp_service.py
├── tools/
│   ├── deno/
│   │   └── deno.exe
│   └── ffmpeg/
│       └── bin/
│           ├── ffmpeg.exe
│           └── ffprobe.exe
├── assets/
│   └── video-downloader.ico
├── launcher.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Third-Party Components

Video Downloader uses third-party software including:

- PySide6 / Qt
- yt-dlp
- yt-dlp-ejs
- FFmpeg
- Deno

Please refer to the respective projects for their licenses and terms.

## Disclaimer

Video Downloader is intended for downloading content that you have permission to download.

Users are responsible for complying with applicable laws, copyright requirements, and the terms of service of the websites they use.

This project does not provide functionality intended to bypass DRM or other access controls.

## License

The source code license for Video Downloader is specified in `LICENSE`.
