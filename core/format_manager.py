from typing import Optional


def is_video_only(fmt: dict) -> bool:
    """Return True if the format contains video but no audio."""

    return (
        fmt.get("vcodec") not in (None, "none")
        and fmt.get("acodec") in (None, "none")
        and fmt.get("height") is not None
    )


def is_audio_only(fmt: dict) -> bool:
    """Return True if the format contains audio but no video."""

    return (
        fmt.get("acodec") not in (None, "none")
        and fmt.get("vcodec") in (None, "none")
    )


def is_combined(fmt: dict) -> bool:
    """Return True if the format contains both video and audio."""

    return (
        fmt.get("vcodec") not in (None, "none")
        and fmt.get("acodec") not in (None, "none")
    )


def get_available_resolutions(
    info: dict,
) -> list[int]:
    """Return available video resolutions."""

    resolutions = {
        fmt.get("height")
        for fmt in info.get("formats", [])
        if is_video_only(fmt)
        and fmt.get("height") is not None
    }

    return sorted(
        resolutions,
        reverse=True,
    )


def _video_codec_score(
    fmt: dict,
    output_format: str,
) -> int:
    """
    Score a video format based on the requested
    output container.
    """

    codec = (
        fmt.get("vcodec")
        or ""
    ).lower()

    extension = (
        fmt.get("ext")
        or ""
    ).lower()

    score = 0

    if output_format == "mp4":

        # H.264 is preferred for MP4 compatibility.
        if (
            "avc1" in codec
            or "h264" in codec
        ):
            score += 100

        if extension == "mp4":
            score += 30

    elif output_format == "mkv":

        # MKV accepts a wider range of codecs.
        score += 10

    return score


def _audio_codec_score(
    fmt: dict,
    output_format: str,
) -> int:
    """
    Score an audio format based on the requested
    output container.
    """

    codec = (
        fmt.get("acodec")
        or ""
    ).lower()

    extension = (
        fmt.get("ext")
        or ""
    ).lower()

    score = 0

    if output_format == "mp4":

        # AAC is preferred for MP4 compatibility.
        if (
            "mp4a" in codec
            or "aac" in codec
        ):
            score += 100

        if extension == "m4a":
            score += 30

    elif output_format == "mkv":

        # Opus is perfectly reasonable for MKV.
        if "opus" in codec:
            score += 30

    return score


def select_video(
    info: dict,
    max_height: Optional[int],
    output_format: str,
) -> Optional[dict]:
    """
    Select the most suitable video-only format.

    The selected format prioritizes:
    1. Resolution
    2. Container/codec compatibility
    3. FPS
    4. Bitrate
    """

    formats = [
        fmt
        for fmt in info.get("formats", [])
        if is_video_only(fmt)
    ]

    if not formats:
        return None

    # --------------------------------------------------------
    # Apply resolution limit
    # --------------------------------------------------------

    if max_height is not None:

        filtered = [
            fmt
            for fmt in formats
            if (fmt.get("height") or 0)
            <= max_height
        ]

        if filtered:
            formats = filtered

    # --------------------------------------------------------
    # Scoring
    # --------------------------------------------------------

    def score(fmt: dict):

        height = (
            fmt.get("height")
            or 0
        )

        fps = (
            fmt.get("fps")
            or 0
        )

        bitrate = (
            fmt.get("tbr")
            or 0
        )

        codec_score = _video_codec_score(
            fmt,
            output_format,
        )

        return (
            height,
            codec_score,
            fps,
            bitrate,
        )

    return max(
        formats,
        key=score,
    )


def select_audio(
    info: dict,
    output_format: str,
) -> Optional[dict]:
    """
    Select the most suitable audio-only format.

    The selected format prioritizes:
    1. Codec/container compatibility
    2. Bitrate
    3. Sample rate
    """

    formats = [
        fmt
        for fmt in info.get("formats", [])
        if is_audio_only(fmt)
    ]

    if not formats:
        return None

    def score(fmt: dict):

        bitrate = (
            fmt.get("abr")
            or 0
        )

        sample_rate = (
            fmt.get("asr")
            or 0
        )

        codec_score = _audio_codec_score(
            fmt,
            output_format,
        )

        return (
            codec_score,
            bitrate,
            sample_rate,
        )

    return max(
        formats,
        key=score,
    )


def build_format_selector(
    info: dict,
    max_height: Optional[int],
    output_format: str,
):
    """
    Build a yt-dlp format selector.

    Returns:
        selector
        selected_video
        selected_audio
    """

    output_format = output_format.lower()

    video = select_video(
        info=info,
        max_height=max_height,
        output_format=output_format,
    )

    audio = select_audio(
        info=info,
        output_format=output_format,
    )

    if video is None:
        raise ValueError(
            "No suitable video format was found."
        )

    if audio is None:
        raise ValueError(
            "No suitable audio format was found."
        )

    video_id = video.get(
        "format_id"
    )

    audio_id = audio.get(
        "format_id"
    )

    if not video_id:
        raise ValueError(
            "Selected video format has no format ID."
        )

    if not audio_id:
        raise ValueError(
            "Selected audio format has no format ID."
        )

    selector = (
        f"{video_id}+{audio_id}"
    )

    return (
        selector,
        video,
        audio,
    )