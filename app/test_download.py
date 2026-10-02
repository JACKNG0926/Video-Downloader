from pathlib import Path
import yt_dlp


# ============================================================
# Project Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TOOLS_DIR = BASE_DIR / "tools"

DENO_EXE = TOOLS_DIR / "deno" / "deno.exe"
FFMPEG_DIR = TOOLS_DIR / "ffmpeg" / "bin"

FFMPEG_EXE = FFMPEG_DIR / "ffmpeg.exe"
FFPROBE_EXE = FFMPEG_DIR / "ffprobe.exe"

DOWNLOAD_DIR = BASE_DIR / "downloads"


# ============================================================
# Utility Functions
# ============================================================

def format_size(size):
    """Convert bytes to a readable size."""

    if not size:
        return "Unknown"

    size = float(size)

    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} PB"


def format_duration(seconds):
    """Convert seconds to HH:MM:SS or MM:SS."""

    if seconds is None:
        return "Unknown"

    seconds = int(seconds)

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    return f"{minutes:02}:{seconds:02}"


def short_codec(codec):
    """Make codec names easier to read."""

    if not codec or codec == "none":
        return "-"

    codec = codec.lower()

    replacements = {
        "avc1": "H.264",
        "av01": "AV1",
        "vp09": "VP9",
        "vp9": "VP9",
        "vp8": "VP8",
        "hev1": "H.265",
        "hvc1": "H.265",
        "mp4a": "AAC",
        "opus": "Opus",
        "vorbis": "Vorbis",
    }

    for key, value in replacements.items():
        if key in codec:
            return value

    return codec[:12]


def get_resolution(fmt):
    """Return resolution text."""

    height = fmt.get("height")
    width = fmt.get("width")

    if height:
        return f"{height}p"

    if width:
        return f"{width}w"

    return "-"


def get_video_codec(fmt):
    return short_codec(fmt.get("vcodec"))


def get_audio_codec(fmt):
    return short_codec(fmt.get("acodec"))


def get_hdr(fmt):
    dynamic_range = fmt.get("dynamic_range")

    if not dynamic_range:
        return "SDR"

    return str(dynamic_range)


def get_size(fmt):
    return format_size(
        fmt.get("filesize")
        or fmt.get("filesize_approx")
    )


def is_video(fmt):
    return fmt.get("vcodec") not in (None, "none")


def is_audio(fmt):
    return fmt.get("acodec") not in (None, "none")


def is_video_only(fmt):
    return is_video(fmt) and not is_audio(fmt)


def is_audio_only(fmt):
    return is_audio(fmt) and not is_video(fmt)


def is_combined(fmt):
    return is_video(fmt) and is_audio(fmt)


# ============================================================
# Environment Check
# ============================================================

def check_environment():
    print("=" * 78)
    print("ENVIRONMENT CHECK")
    print("=" * 78)

    all_ok = True

    # Python / yt-dlp
    try:
        print(f"[OK] yt-dlp {yt_dlp.version.__version__}")
    except Exception:
        print("[ERROR] yt-dlp unavailable")
        all_ok = False

    # Deno
    if DENO_EXE.exists():
        print("[OK] Deno found")
        print(f"     {DENO_EXE}")
    else:
        print("[ERROR] Deno not found")
        print(f"        Expected: {DENO_EXE}")
        all_ok = False

    # FFmpeg
    if FFMPEG_EXE.exists():
        print("[OK] FFmpeg found")
        print(f"     {FFMPEG_EXE}")
    else:
        print("[ERROR] FFmpeg not found")
        print(f"        Expected: {FFMPEG_EXE}")
        all_ok = False

    # FFprobe
    if FFPROBE_EXE.exists():
        print("[OK] FFprobe found")
        print(f"[OK] FFprobe found")
    else:
        print("[WARNING] FFprobe not found")

    print("=" * 78)

    return all_ok


# ============================================================
# yt-dlp Options
# ============================================================

def get_base_options():
    """Return common yt-dlp configuration."""

    return {
        "quiet": False,
        "no_warnings": False,
        "verbose": True,
        "skip_download": True,

        # Project-local FFmpeg
        "ffmpeg_location": str(FFMPEG_DIR),

        # Project-local Deno
        "js_runtimes": {
            "deno": {
                "path": str(DENO_EXE)
            }
        },

        # V1: do not process playlists
        "noplaylist": True,
    }


# ============================================================
# Analyze URL
# ============================================================

def analyze_url(url):
    """Extract metadata and formats without downloading."""

    options = get_base_options()

    try:
        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        return info

    except Exception as error:
        print("\n" + "=" * 78)
        print("ANALYSIS FAILED")
        print("=" * 78)
        print(error)

        return None


# ============================================================
# Display Basic Information
# ============================================================

def show_media_info(info):

    print("\n" + "=" * 78)
    print("MEDIA INFORMATION")
    print("=" * 78)

    print(f"Title       : {info.get('title', 'Unknown')}")
    print(f"Uploader    : {info.get('uploader', 'Unknown')}")
    print(f"Duration    : {format_duration(info.get('duration'))}")
    print(f"Extractor   : {info.get('extractor_key', 'Unknown')}")
    print(f"Video ID    : {info.get('id', 'Unknown')}")
    print(f"Format Count: {len(info.get('formats', []))}")


# ============================================================
# Sort Functions
# ============================================================

def video_sort_key(fmt):
    """Sort video formats from better to worse."""

    height = fmt.get("height") or 0
    fps = fmt.get("fps") or 0
    filesize = (
        fmt.get("filesize")
        or fmt.get("filesize_approx")
        or 0
    )

    return (
        height,
        fps,
        filesize,
    )


def audio_sort_key(fmt):
    """Sort audio formats from better to worse."""

    abr = fmt.get("abr") or 0
    asr = fmt.get("asr") or 0
    filesize = (
        fmt.get("filesize")
        or fmt.get("filesize_approx")
        or 0
    )

    return (
        abr,
        asr,
        filesize,
    )


def combined_sort_key(fmt):
    """Sort combined formats."""

    height = fmt.get("height") or 0
    fps = fmt.get("fps") or 0
    filesize = (
        fmt.get("filesize")
        or fmt.get("filesize_approx")
        or 0
    )

    return (
        height,
        fps,
        filesize,
    )


# ============================================================
# Display Video-only Formats
# ============================================================

def show_video_formats(formats):

    video_formats = [
        fmt
        for fmt in formats
        if is_video_only(fmt)
    ]

    video_formats.sort(
        key=video_sort_key,
        reverse=True
    )

    print("\n" + "=" * 78)
    print("VIDEO-ONLY FORMATS")
    print("=" * 78)

    print(
        f"{'ID':<8}"
        f"{'EXT':<7}"
        f"{'RES':<8}"
        f"{'FPS':<7}"
        f"{'CODEC':<10}"
        f"{'HDR':<10}"
        f"{'SIZE':<12}"
    )

    print("-" * 78)

    for fmt in video_formats:

        print(
            f"{str(fmt.get('format_id', '-')):<8}"
            f"{str(fmt.get('ext', '-')):<7}"
            f"{get_resolution(fmt):<8}"
            f"{str(fmt.get('fps') or '-'): <7}"
            f"{get_video_codec(fmt):<10}"
            f"{get_hdr(fmt):<10}"
            f"{get_size(fmt):<12}"
        )


# ============================================================
# Display Audio-only Formats
# ============================================================

def show_audio_formats(formats):

    audio_formats = [
        fmt
        for fmt in formats
        if is_audio_only(fmt)
    ]

    audio_formats.sort(
        key=audio_sort_key,
        reverse=True
    )

    print("\n" + "=" * 78)
    print("AUDIO-ONLY FORMATS")
    print("=" * 78)

    print(
        f"{'ID':<8}"
        f"{'EXT':<7}"
        f"{'CODEC':<10}"
        f"{'BITRATE':<12}"
        f"{'SAMPLE':<12}"
        f"{'LANG':<10}"
        f"{'SIZE':<12}"
    )

    print("-" * 78)

    for fmt in audio_formats:

        abr = fmt.get("abr")

        bitrate = (
            f"{abr:.0f}k"
            if abr
            else "-"
        )

        asr = fmt.get("asr")

        sample_rate = (
            f"{asr} Hz"
            if asr
            else "-"
        )

        language = (
            fmt.get("language")
            or "-"
        )

        print(
            f"{str(fmt.get('format_id', '-')):<8}"
            f"{str(fmt.get('ext', '-')):<7}"
            f"{get_audio_codec(fmt):<10}"
            f"{bitrate:<12}"
            f"{sample_rate:<12}"
            f"{str(language):<10}"
            f"{get_size(fmt):<12}"
        )


# ============================================================
# Display Combined Formats
# ============================================================

def show_combined_formats(formats):

    combined_formats = [
        fmt
        for fmt in formats
        if is_combined(fmt)
    ]

    combined_formats.sort(
        key=combined_sort_key,
        reverse=True
    )

    print("\n" + "=" * 78)
    print("VIDEO + AUDIO FORMATS")
    print("=" * 78)

    print(
        f"{'ID':<8}"
        f"{'EXT':<7}"
        f"{'RES':<8}"
        f"{'FPS':<7}"
        f"{'VIDEO':<10}"
        f"{'AUDIO':<10}"
        f"{'SIZE':<12}"
    )

    print("-" * 78)

    for fmt in combined_formats:

        print(
            f"{str(fmt.get('format_id', '-')):<8}"
            f"{str(fmt.get('ext', '-')):<7}"
            f"{get_resolution(fmt):<8}"
            f"{str(fmt.get('fps') or '-'): <7}"
            f"{get_video_codec(fmt):<10}"
            f"{get_audio_codec(fmt):<10}"
            f"{get_size(fmt):<12}"
        )


# ============================================================
# Format Analysis Summary
# ============================================================

def show_format_summary(formats):

    video_count = sum(
        1 for fmt in formats
        if is_video_only(fmt)
    )

    audio_count = sum(
        1 for fmt in formats
        if is_audio_only(fmt)
    )

    combined_count = sum(
        1 for fmt in formats
        if is_combined(fmt)
    )

    print("\n" + "=" * 78)
    print("FORMAT SUMMARY")
    print("=" * 78)

    print(f"Video-only : {video_count}")
    print(f"Audio-only : {audio_count}")
    print(f"Combined   : {combined_count}")


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 78)
    print("                    UNIVERSAL VIDEO DOWNLOADER")
    print("                              V1")
    print("=" * 78)

    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    if not check_environment():
        print("\nEnvironment check failed.")
        return

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    url = input("\nEnter video URL: ").strip()

    if not url:
        print("[ERROR] URL cannot be empty.")
        return

    # --------------------------------------------------------
    # Analyze
    # --------------------------------------------------------

    print("\nAnalyzing media...")
    print("Please wait.\n")

    info = analyze_url(url)

    if not info:
        return

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    show_media_info(info)

    # --------------------------------------------------------
    # Formats
    # --------------------------------------------------------

    formats = info.get("formats", [])

    show_format_summary(formats)

    show_combined_formats(formats)

    show_video_formats(formats)

    show_audio_formats(formats)

    # --------------------------------------------------------
    # End
    # --------------------------------------------------------

    print("\n" + "=" * 78)
    print("ANALYSIS COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()