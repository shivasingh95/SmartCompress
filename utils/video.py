"""
Video Processing Module
Uses moviepy (which bundles its own ffmpeg via imageio-ffmpeg).
No system FFmpeg installation required — pip install moviepy handles everything.
"""

from pathlib import Path

import numpy as np

# moviepy uses imageio-ffmpeg's pip-installed binary — no system install needed
from utils.ffmpeg import configure_bundled_ffmpeg

configure_bundled_ffmpeg()

try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip


def _resize_clip(clip, new_size: tuple[int, int]):
    """Handle the resize API differences between MoviePy v1 and v2."""
    if hasattr(clip, "resized"):
        return clip.resized(new_size=new_size)
    if hasattr(clip, "resize"):
        return clip.resize(new_size)
    raise AttributeError("MoviePy resize API not available for this clip.")


class VideoProcessor:
    """
    Compresses video using moviepy write_videofile with libx264 / aac codec.
    imageio-ffmpeg provides the codec binary automatically on all platforms.
    """

    SUPPORTED_FORMATS = {".mp4", ".avi"}

    def compress(
        self,
        input_path: str,
        crf: int       = 28,
        scale: float   = 1.0,
        out_dir: str   = "temp",
        audio_bitrate: str = "128k",
    ) -> str:
        """
        Compress video. CRF is mapped to moviepy bitrate tiers since
        moviepy uses target bitrate rather than CRF directly.
        Returns path to output MP4.
        """
        self._validate(input_path)
        out_path = self._output_path(input_path, out_dir)

        # Map CRF → approximate bitrate string for moviepy
        video_bitrate = self._crf_to_bitrate(crf)

        clip = VideoFileClip(input_path)

        if scale < 1.0:
            new_w = int(clip.w * scale) & ~1
            new_h = int(clip.h * scale) & ~1
            clip  = _resize_clip(clip, (new_w, new_h))

        clip.write_videofile(
            out_path,
            codec        = "libx264",
            audio_codec  = "aac",
            bitrate      = video_bitrate,
            audio_bitrate= audio_bitrate,
            preset       = "fast",
            logger       = None,   # suppress moviepy console output
            temp_audiofile= str(Path(out_dir) / "_tmp_audio.m4a"),
        )
        clip.close()
        return out_path

    def get_metadata(self, input_path: str) -> dict:
        """Extract video metadata using moviepy (no system tools needed)."""
        try:
            clip = VideoFileClip(input_path)
            meta = {
                "width"      : clip.w,
                "height"     : clip.h,
                "fps"        : round(clip.fps, 2),
                "duration"   : round(clip.duration, 2),
                "frame_count": int(clip.fps * clip.duration),
            }
            clip.close()
            return meta
        except Exception as e:
            return {"width": 0, "height": 0, "fps": 0, "duration": 0,
                    "frame_count": 0, "error": str(e)}

    def analyze_scene_complexity(self, input_path: str, n_samples: int = 24) -> dict:
        """
        Sample frames and measure inter-frame pixel difference using PIL/numpy.
        Returns motion complexity score 0–100 and content label.
        """
        try:
            clip         = VideoFileClip(input_path)
            duration     = clip.duration
            sample_times = np.linspace(0.5, max(0.5, duration - 0.5), n_samples)
            diffs        = []
            prev_arr     = None

            for t in sample_times:
                try:
                    frame = clip.get_frame(t)                   # numpy uint8 H×W×3
                    gray  = np.mean(frame, axis=2).astype(np.float32)
                    if prev_arr is not None:
                        diffs.append(float(np.mean(np.abs(gray - prev_arr))))
                    prev_arr = gray
                except Exception:
                    continue

            clip.close()

            if not diffs:
                return {"available": True, "score": 0, "label": "Unknown"}

            avg_diff = float(np.mean(diffs))
            score    = min(100, int(avg_diff * 4))

            if score < 20:
                label, crf_adj = "Low Motion (Screencast / Slides)", +5
            elif score < 50:
                label, crf_adj = "Moderate Motion (Interview / Talk)", +2
            elif score < 75:
                label, crf_adj = "High Motion (Sports / Action)", -3
            else:
                label, crf_adj = "Very High Motion (Fast Action)", -6

            return {
                "available"     : True,
                "score"         : score,
                "label"         : label,
                "crf_adjustment": crf_adj,
                "avg_frame_diff": round(avg_diff, 3),
            }
        except Exception as e:
            return {"available": True, "score": 0, "label": f"Error: {e}"}

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _crf_to_bitrate(crf: int) -> str:
        """Map CRF value to an approximate target bitrate string."""
        if crf <= 15:  return "8000k"
        if crf <= 20:  return "4000k"
        if crf <= 25:  return "2000k"
        if crf <= 28:  return "1200k"
        if crf <= 35:  return "600k"
        return "300k"

    @staticmethod
    def _validate(path: str):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if p.suffix.lower() not in VideoProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {p.suffix}. Use MP4 or AVI.")

    @staticmethod
    def _output_path(input_path: str, out_dir: str) -> str:
        stem = Path(input_path).stem
        out  = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        return str(out / f"{stem}_compressed.mp4")
