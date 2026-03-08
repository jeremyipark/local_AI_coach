import hashlib
import subprocess
from pathlib import Path
import uuid


BROWSER_NATIVE_CODECS = {"h264", "hevc", "av1", "vp9"}


def _probe_codec(video_path: Path) -> str | None:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "default=nw=1:nk=1",
        str(video_path),
    ]

    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return None

    codec = result.stdout.strip().splitlines()
    return codec[0] if codec else None


def _cache_path(video_path: Path, cache_dir: Path) -> Path:
    digest = hashlib.sha1(
        f"{video_path.resolve()}::{video_path.stat().st_mtime_ns}".encode("utf-8")
    ).hexdigest()
    return cache_dir / f"{digest}.mp4"


def _transcode_to_h264(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file first so interrupted jobs never leave a bad cached artifact.
    tmp_output = output_path.with_name(f"{output_path.stem}.{uuid.uuid4().hex}.tmp.mp4")
    if tmp_output.exists():
        tmp_output.unlink()

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        # Keep review output lightweight for fast first load on local CPU.
        "-vf",
        "scale=if(gt(iw\\,1920)\\,1920\\,iw):-2:flags=bicubic",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "30",
        "-pix_fmt",
        "yuv420p",
        "-profile:v",
        "main",
        "-movflags",
        "+faststart",
        "-an",
        str(tmp_output),
    ]

    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        tail = stderr[-800:] if len(stderr) > 800 else stderr
        raise RuntimeError(
            "ffmpeg transcode failed. "
            "Source may be corrupted or not decodable. "
            f"Details: {tail}"
        )

    # Validate transcode output before exposing it.
    if _probe_codec(tmp_output) != "h264":
        raise RuntimeError("Transcode output is invalid (expected h264 stream).")

    if output_path.exists():
        # Another request may have completed the same transcode concurrently.
        tmp_output.unlink(missing_ok=True)
        return

    tmp_output.replace(output_path)


def get_browser_playable_video_path(video_path: Path, cache_dir: Path) -> Path:
    """Return original path when browser-safe, otherwise cached H.264 transcode."""

    codec = _probe_codec(video_path)
    if codec and codec.lower() in BROWSER_NATIVE_CODECS:
        return video_path

    cached = _cache_path(video_path, cache_dir)
    if cached.exists():
        # Rebuild stale/partial cache files if they are not decodable.
        if _probe_codec(cached) == "h264":
            return cached
        cached.unlink(missing_ok=True)

    if cached.exists():
        return cached

    _transcode_to_h264(video_path, cached)
    return cached
