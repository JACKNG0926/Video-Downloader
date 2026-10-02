from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DownloadState(Enum):
    PENDING = "Pending"
    ANALYZING = "Analyzing"
    DOWNLOADING = "Downloading"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass
class DownloadTask:
    """Represents one download task."""

    url: str

    output_dir: str

    output_format: str

    max_height: Optional[int] = None

    state: DownloadState = DownloadState.PENDING

    title: str = "Unknown"

    error: Optional[str] = None

    def set_state(
        self,
        state: DownloadState,
    ):
        self.state = state