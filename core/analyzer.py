from dataclasses import dataclass

from services.ytdlp_service import YTDLPService


@dataclass
class MediaInfo:
    """Normalized media information."""

    title: str
    uploader: str
    duration: int | None
    source: str
    video_id: str
    format_count: int
    raw_info: dict


class MediaAnalyzer:
    """Application-level media analysis."""

    def __init__(
        self,
        service: YTDLPService,
    ):
        self.service = service

    def analyze(
        self,
        url: str,
    ) -> MediaInfo:
        """Analyze a media URL."""

        info = self.service.analyze(url)

        return MediaInfo(
            title=info.get(
                "title",
                "Unknown",
            ),
            uploader=info.get(
                "uploader",
                "Unknown",
            ),
            duration=info.get(
                "duration",
            ),
            source=info.get(
                "extractor_key",
                "Unknown",
            ),
            video_id=info.get(
                "id",
                "Unknown",
            ),
            format_count=len(
                info.get(
                    "formats",
                    [],
                )
            ),
            raw_info=info,
        )