from dataclasses import dataclass
from typing import Callable, Optional

from core.download_task import (
    DownloadState,
)

from core.format_manager import (
    build_format_selector,
)

from services.ytdlp_service import (
    YTDLPService,
)


@dataclass
class DownloadRequest:
    """Information required to start a download."""

    url: str

    output_dir: str

    output_format: str

    max_height: Optional[int] = None


@dataclass
class DownloadResult:
    """Result of a download operation."""

    state: DownloadState

    output_dir: str

    format_selector: Optional[str] = None

    error: Optional[str] = None


class DownloadManager:

    def __init__(
        self,
        service: YTDLPService,

        state_callback: Optional[
            Callable[[DownloadState], None]
        ] = None,

        progress_callback: Optional[
            Callable[[int, str], None]
        ] = None,

        cancellation_token=None,
    ):

        self.service = service

        self.state_callback = (
            state_callback
        )

        self.progress_callback = (
            progress_callback
        )

        self.cancellation_token = (
            cancellation_token
        )

        self.state = (
            DownloadState.PENDING
        )

    # ========================================================
    # State
    # ========================================================

    def _set_state(
        self,
        state: DownloadState,
    ):

        self.state = state

        if self.state_callback:

            self.state_callback(
                state
            )

    # ========================================================
    # Download
    # ========================================================

    def download(
        self,
        request: DownloadRequest,
        info: dict,
    ) -> DownloadResult:

        try:

            # ------------------------------------------------
            # Check cancellation before starting
            # ------------------------------------------------

            if (
                self.cancellation_token
                and self.cancellation_token.is_cancelled()
            ):

                self._set_state(
                    DownloadState.CANCELLED
                )

                return DownloadResult(
                    state=DownloadState.CANCELLED,
                    output_dir=request.output_dir,
                )

            # ------------------------------------------------
            # Select formats
            # ------------------------------------------------

            output_format = (
                request.output_format
                .lower()
            )

            (
                selector,
                _video,
                _audio,
            ) = build_format_selector(
                info=info,
                max_height=request.max_height,
                output_format=output_format,
            )

            # ------------------------------------------------
            # Download
            # ------------------------------------------------

            self._set_state(
                DownloadState.DOWNLOADING
            )

            self.service.download(
                url=request.url,

                format_selector=selector,

                output_dir=request.output_dir,

                output_format=output_format,

                progress_callback=(
                    self.progress_callback
                ),

                postprocessor_callback=(
                    self._postprocessor_hook
                ),

                cancellation_token=(
                    self.cancellation_token
                ),
            )

            # ------------------------------------------------
            # Complete
            # ------------------------------------------------

            self._set_state(
                DownloadState.COMPLETED
            )

            return DownloadResult(
                state=DownloadState.COMPLETED,
                output_dir=request.output_dir,
                format_selector=selector,
            )

        except Exception as exc:

            # ------------------------------------------------
            # Cancellation is not a normal failure
            # ------------------------------------------------

            from yt_dlp.utils import (
                DownloadCancelled,
            )

            if isinstance(
                exc,
                DownloadCancelled,
            ):

                self._set_state(
                    DownloadState.CANCELLED
                )

                return DownloadResult(
                    state=DownloadState.CANCELLED,
                    output_dir=request.output_dir,
                    format_selector=selector
                    if "selector" in locals()
                    else None,
                )

            # ------------------------------------------------
            # Normal failure
            # ------------------------------------------------

            self._set_state(
                DownloadState.FAILED
            )

            return DownloadResult(
                state=DownloadState.FAILED,
                output_dir=request.output_dir,
                format_selector=(
                    selector
                    if "selector" in locals()
                    else None
                ),
                error=str(exc),
            )

    # ========================================================
    # Post-processing
    # ========================================================

    def _postprocessor_hook(
        self,
        data: dict,
    ):

        status = data.get(
            "status"
        )

        if status == "started":

            self._set_state(
                DownloadState.PROCESSING
            )

        elif status == "finished":

            self._set_state(
                DownloadState.PROCESSING
            )