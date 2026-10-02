from core.download_queue import DownloadQueue
from core.download_task import (
    DownloadState,
    DownloadTask,
)


def main():

    queue = DownloadQueue()

    task1 = DownloadTask(
        url="https://example.com/video1",
        output_dir="downloads",
        output_format="mp4",
        max_height=720,
    )

    task2 = DownloadTask(
        url="https://example.com/video2",
        output_dir="downloads",
        output_format="mp4",
        max_height=1080,
    )

    task3 = DownloadTask(
        url="https://example.com/video3",
        output_dir="downloads",
        output_format="mkv",
        max_height=None,
    )

    queue.add(task1)
    queue.add(task2)
    queue.add(task3)

    print("Queue size:", len(queue))

    while not queue.is_empty():

        task = queue.next_task()

        if task is None:
            break

        print()
        print("Processing:")
        print(f"URL: {task.url}")
        print(f"Quality: {task.max_height}")
        print(f"Format: {task.output_format}")

        task.set_state(
            DownloadState.DOWNLOADING
        )

        print(
            "State:",
            task.state.value,
        )

        task.set_state(
            DownloadState.COMPLETED
        )

        print(
            "State:",
            task.state.value,
        )

    print()
    print("Queue finished.")


if __name__ == "__main__":
    main()