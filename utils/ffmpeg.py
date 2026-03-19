"""Helpers for using the bundled ffmpeg binary from imageio-ffmpeg."""

import os
from pathlib import Path

import imageio_ffmpeg


def configure_bundled_ffmpeg() -> str:
    """Expose imageio-ffmpeg's bundled binary through PATH and env vars."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = str(Path(ffmpeg_exe).parent)

    current_path = os.environ.get("PATH", "")
    path_parts = [part for part in current_path.split(os.pathsep) if part]
    normalized_parts = {
        os.path.normcase(os.path.normpath(part))
        for part in path_parts
    }
    normalized_ffmpeg_dir = os.path.normcase(os.path.normpath(ffmpeg_dir))

    if normalized_ffmpeg_dir not in normalized_parts:
        os.environ["PATH"] = os.pathsep.join([ffmpeg_dir, *path_parts]) if path_parts else ffmpeg_dir

    os.environ.setdefault("IMAGEIO_FFMPEG_EXE", ffmpeg_exe)
    return ffmpeg_exe
