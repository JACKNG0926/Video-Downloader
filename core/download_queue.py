from collections import deque
from typing import Optional

from core.download_manager import (
    DownloadManager,
    DownloadRequest,
)

from core.download_task import (
    DownloadState,
    DownloadTask,
)

class DownloadQueue:
    """FIFO queue for download tasks."""

    def __init__(self):
        self._queue = deque()

    def add(
        self,
        task: DownloadTask,
    ):
        """Add a task to the queue."""

        self._queue.append(task)

    def remove(
        self,
        task: DownloadTask,
    ) -> bool:
        """Remove a task from the queue."""

        try:
            self._queue.remove(task)
            return True

        except ValueError:
            return False

    def next_task(
        self,
    ) -> Optional[DownloadTask]:
        """
        Return and remove the next pending task.

        Kept for low-level queue usage and testing.
        """

        for task in self._queue:

            if task.state == DownloadState.PENDING:

                self._queue.remove(task)

                return task

        return None

    def pending_tasks(self) -> list[DownloadTask]:
        """Return all pending tasks without removing them."""

        return [
            task
            for task in self._queue
            if task.state == DownloadState.PENDING
        ]

    def all_tasks(self) -> list[DownloadTask]:
        """Return all tasks in queue order."""

        return list(self._queue)

    def clear(self):
        """Clear all tasks."""

        self._queue.clear()

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def has_pending(self) -> bool:
        return any(
            task.state == DownloadState.PENDING
            for task in self._queue
        )

    def __len__(self):
        return len(self._queue)