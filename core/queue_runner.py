from typing import Callable, Optional

from core.cancellation import CancellationToken
from core.download_manager import (
    DownloadManager,
    DownloadRequest,
)
from core.download_queue import DownloadQueue
from core.download_task import (
    DownloadState,
    DownloadTask,
)
from services.ytdlp_service import YTDLPService


class QueueRunner:
    """
    Sequentially processes pending download tasks.

    Responsibilities:
    - Process tasks in FIFO order
    - Analyze each task before downloading
    - Create DownloadManager for each task
    - Report task state changes
    - Report download progress
    - Respect queue cancellation
    - Stop processing new tasks after cancellation
    """

    def __init__(
        self,
        service: YTDLPService,
        queue: DownloadQueue,
        task_callback: Optional[
            Callable[[DownloadTask], None]
        ] = None,
        progress_callback: Optional[
            Callable[[int, str], None]
        ] = None,
        cancellation_token: Optional[
            CancellationToken
        ] = None,
    ):
        self.service = service
        self.queue = queue

        self.task_callback = task_callback
        self.progress_callback = progress_callback

        self.cancellation_token = (
            cancellation_token
            or CancellationToken()
        )

    # ========================================================
    # Notification Helpers
    # ========================================================

    def _notify_task(
        self,
        task: DownloadTask,
    ):
        """Notify the UI/application about a task update."""

        if self.task_callback:
            self.task_callback(task)

    def _notify_progress(
        self,
        value: int,
        message: str,
    ):
        """Notify the UI/application about download progress."""

        if self.progress_callback:
            self.progress_callback(
                value,
                message,
            )

    # ========================================================
    # Cancellation
    # ========================================================

    def is_cancelled(self) -> bool:
        """Return whether queue cancellation was requested."""

        return self.cancellation_token.is_cancelled()

    # ========================================================
    # Run Queue
    # ========================================================

    def run(self) -> dict:
        """
        Process all pending tasks sequentially.

        Returns:
            {
                "completed": int,
                "failed": int,
                "cancelled": int,
            }

        Cancellation stops the currently active task when the
        underlying download operation observes the cancellation
        token. Pending tasks remain in the queue.
        """

        completed = 0
        failed = 0
        cancelled = 0

        # Take a snapshot of pending tasks.
        #
        # The tasks remain in the queue so that the GUI can continue
        # displaying their state.
        tasks = self.queue.pending_tasks()

        for task in tasks:

            # ------------------------------------------------
            # Stop starting new tasks after cancellation
            # ------------------------------------------------

            if self.is_cancelled():
                break

            try:

                # ============================================
                # ANALYZING
                # ============================================

                task.set_state(
                    DownloadState.ANALYZING
                )

                self._notify_task(task)

                # Check cancellation before starting analysis.
                if self.is_cancelled():

                    task.set_state(
                        DownloadState.CANCELLED
                    )

                    self._notify_task(task)

                    cancelled += 1

                    break

                # --------------------------------------------
                # Analyze URL
                # --------------------------------------------

                info = self.service.analyze(
                    task.url
                )

                # --------------------------------------------
                # Check cancellation after analysis
                # --------------------------------------------

                if self.is_cancelled():

                    task.set_state(
                        DownloadState.CANCELLED
                    )

                    self._notify_task(task)

                    cancelled += 1

                    break

                # --------------------------------------------
                # Update title
                # --------------------------------------------

                task.title = info.get(
                    "title",
                    "Unknown",
                )

                self._notify_task(task)

                # ============================================
                # DOWNLOAD MANAGER
                # ============================================

                def state_callback(
                    state,
                    current_task=task,
                ):
                    """
                    Update the current task state.

                    current_task is captured explicitly so the
                    callback remains associated with the correct
                    task.
                    """

                    current_task.set_state(
                        state
                    )

                    self._notify_task(
                        current_task
                    )

                manager = DownloadManager(
                    service=self.service,

                    state_callback=state_callback,

                    progress_callback=(
                        self._notify_progress
                    ),

                    cancellation_token=(
                        self.cancellation_token
                    ),
                )

                request = DownloadRequest(
                    url=task.url,

                    output_dir=task.output_dir,

                    output_format=(
                        task.output_format
                    ),

                    max_height=(
                        task.max_height
                    ),
                )

                # ============================================
                # DOWNLOAD
                # ============================================

                result = manager.download(
                    request=request,
                    info=info,
                )

                # --------------------------------------------
                # Update task result
                # --------------------------------------------

                task.set_state(
                    result.state
                )

                if result.error:
                    task.error = result.error

                self._notify_task(task)

                # ============================================
                # RESULT
                # ============================================

                if (
                    result.state
                    == DownloadState.COMPLETED
                ):

                    completed += 1

                elif (
                    result.state
                    == DownloadState.CANCELLED
                ):

                    cancelled += 1

                    # Stop the queue. Pending tasks remain
                    # untouched.
                    break

                else:

                    failed += 1

            except Exception as exc:

                # ============================================
                # UNEXPECTED ERROR
                # ============================================

                task.error = str(exc)

                task.set_state(
                    DownloadState.FAILED
                )

                failed += 1

                self._notify_task(task)

                # Do not stop the entire queue for a normal
                # task-specific failure.
                continue

        # ====================================================
        # Final Result
        # ====================================================

        return {
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
        }