from threading import Event


class CancellationToken:
    """Thread-safe cancellation signal."""

    def __init__(self):
        self._event = Event()

    def cancel(self):
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()