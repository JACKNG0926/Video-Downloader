import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(
        sys.executable
    ).resolve().parent
else:
    BASE_DIR = Path(
        __file__
    ).resolve().parent.parent

from typing import Callable, Optional

import yt_dlp
from yt_dlp.utils import DownloadCancelled




TOOLS_DIR = BASE_DIR / "tools"

DENO_EXE = TOOLS_DIR / "deno" / "deno.exe"
FFMPEG_DIR = TOOLS_DIR / "ffmpeg" / "bin"

DOWNLOAD_DIR = Path.home() / "Downloads" / "Video Downloader"

# ============================================================
# Formatting Helpers
# ============================================================

def format_bytes(value) -> str:
    """Convert bytes to a readable string."""

    if value is None:
        return "-"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "-"

    units = [
        "B",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
    ]

    for unit in units:

        if value < 1024:
            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{value:.1f} PiB"


def format_duration(seconds) -> str:
    """Convert seconds to HH:MM:SS."""

    if seconds is None:
        return "--:--"

    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "--:--"

    hours, remainder = divmod(
        seconds,
        3600,
    )

    minutes, seconds = divmod(
        remainder,
        60,
    )

    if hours:
        return (
            f"{hours:02}:"
            f"{minutes:02}:"
            f"{seconds:02}"
        )

    return (
        f"{minutes:02}:"
        f"{seconds:02}"
    )


# ============================================================
# YT-DLP Service
# ============================================================

class YTDLPService:
    """Service layer for yt-dlp operations."""

    def __init__(self):
        self._validate_tools()

    # ========================================================
    # Dependency Validation
    # ========================================================

    def _validate_tools(self):

        if not DENO_EXE.exists():

            raise FileNotFoundError(
                f"Deno not found:\n{DENO_EXE}"
            )

        if not (
            FFMPEG_DIR / "ffmpeg.exe"
        ).exists():

            raise FileNotFoundError(
                "FFmpeg not found:\n"
                f"{FFMPEG_DIR / 'ffmpeg.exe'}"
            )

    # ========================================================
    # Base Options
    # ========================================================

    def _base_options(self):

        return {
            "quiet": True,
            "no_warnings": True,

            "ffmpeg_location": str(
                FFMPEG_DIR
            ),

            "js_runtimes": {
                "deno": {
                    "path": str(
                        DENO_EXE
                    )
                }
            },

            "noplaylist": True,
        }

    # ========================================================
    # Analyze
    # ========================================================

    def analyze(
        self,
        url: str,
    ) -> dict:

        options = self._base_options()

        options["skip_download"] = True

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            return ydl.extract_info(
                url,
                download=False,
            )

    # ========================================================
    # Download
    # ========================================================

    def download(
        self,
        url: str,
        format_selector: str,
        output_dir: str,
        output_format: str,
        progress_callback: Optional[
            Callable[[int, str], None]
        ] = None,
        postprocessor_callback: Optional[
            Callable[[dict], None]
        ] = None,
        cancellation_token=None,
    ):
        """
        Download media using yt-dlp.

        Progress is calculated from raw numeric byte values
        instead of yt-dlp's ANSI-colored display strings.
        """

        output_path = Path(
            output_dir
        )

        output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        options = self._base_options()

        # ====================================================
        # Progress Hook
        # ====================================================

        def progress_hook(data):

            # ------------------------------------------------
            # Cancellation
            # ------------------------------------------------

            if (
                cancellation_token
                and cancellation_token.is_cancelled()
            ):

                raise DownloadCancelled()

            # ------------------------------------------------
            # No callback
            # ------------------------------------------------

            if progress_callback is None:
                return

            status = data.get(
                "status"
            )

            # ------------------------------------------------
            # Downloading
            # ------------------------------------------------

            if status == "downloading":

                downloaded = (
                    data.get(
                        "downloaded_bytes"
                    )
                    or 0
                )

                total = (
                    data.get(
                        "total_bytes"
                    )
                    or data.get(
                        "total_bytes_estimate"
                    )
                )

                speed = data.get(
                    "speed"
                )

                eta_seconds = data.get(
                    "eta"
                )

                # --------------------------------------------
                # Calculate percentage
                # --------------------------------------------

                if total:

                    try:

                        percent = (
                            downloaded
                            / total
                            * 100
                        )

                    except (
                        TypeError,
                        ZeroDivisionError,
                    ):

                        percent = 0

                else:

                    percent = 0

                percent = max(
                    0,
                    min(
                        100,
                        percent,
                    )
                )

                # --------------------------------------------
                # Speed
                # --------------------------------------------

                if speed:

                    speed_text = (
                        f"{format_bytes(speed)}/s"
                    )

                else:

                    speed_text = "-"

                # --------------------------------------------
                # ETA
                # --------------------------------------------

                eta_text = format_duration(
                    eta_seconds
                )

                # --------------------------------------------
                # Display message
                # --------------------------------------------

                if total:

                    message = (
                        f"{percent:.1f}%  •  "
                        f"{format_bytes(downloaded)} / "
                        f"{format_bytes(total)}  •  "
                        f"{speed_text}  •  "
                        f"ETA {eta_text}"
                    )

                else:

                    message = (
                        f"{format_bytes(downloaded)}  •  "
                        f"{speed_text}  •  "
                        f"ETA {eta_text}"
                    )

                # --------------------------------------------
                # Send numeric percentage to GUI
                # --------------------------------------------

                progress_callback(
                    int(percent),
                    message,
                )

            # ------------------------------------------------
            # Download Finished
            # ------------------------------------------------

            elif status == "finished":

                progress_callback(
                    100,
                    "Download finished. "
                    "Processing media...",
                )

        # ====================================================
        # Postprocessor Hook
        # ====================================================

        def postprocessor_hook(data):

            if postprocessor_callback:

                postprocessor_callback(
                    data
                )

        # ====================================================
        # yt-dlp Options
        # ====================================================

        options.update({

            "format": format_selector,

            "merge_output_format":
                output_format,

            "outtmpl": str(
                output_path
                / "%(title)s [%(id)s].%(ext)s"
            ),

            "retries": 10,

            "fragment_retries": 10,

            "continuedl": True,

            "progress_hooks": [
                progress_hook
            ],

            "postprocessor_hooks": [
                postprocessor_hook
            ],

        })

        # ====================================================
        # Execute
        # ====================================================

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            return ydl.download(
                [url]
            )