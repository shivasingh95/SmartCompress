"""
Media Analyzer Module
Extracts metadata using pure Python libraries only.
Audio: soundfile | Video: moviepy
"""

from pathlib import Path

import soundfile as sf

try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip


class MediaAnalyzer:

    # ── Audio ──────────────────────────────────────────────────────────────────

    def analyze_audio(self, path: str) -> dict:
        p          = Path(path)
        size_bytes = p.stat().st_size
        size_mb    = round(size_bytes / (1024 ** 2), 3)

        duration    = 0
        sample_rate = 0
        channels    = 0
        bitrate_kbps= 0
        codec       = p.suffix.lstrip(".").upper()

        try:
            audio_info   = sf.info(path)
            duration     = round(float(audio_info.duration), 2)
            sample_rate  = int(audio_info.samplerate or 0)
            channels     = int(audio_info.channels or 0)
            codec        = audio_info.subtype or codec
            bitrate_kbps = round((size_bytes * 8) / (duration * 1000), 1) if duration > 0 else 0
        except Exception:
            pass

        return {
            "type"        : "audio",
            "path"        : str(path),
            "filename"    : p.name,
            "format"      : p.suffix.lstrip(".").upper(),
            "codec"       : codec,
            "size_bytes"  : size_bytes,
            "size_mb"     : size_mb,
            "duration"    : duration,
            "bitrate_kbps": bitrate_kbps,
            "sample_rate" : sample_rate,
            "channels"    : channels,
        }

    # ── Video ──────────────────────────────────────────────────────────────────

    def analyze_video(self, path: str) -> dict:
        p          = Path(path)
        size_bytes = p.stat().st_size
        size_mb    = round(size_bytes / (1024 ** 2), 3)

        width = height = fps = duration = frame_count = 0
        bitrate_kbps = 0

        try:
            clip         = VideoFileClip(path)
            width        = clip.w
            height       = clip.h
            fps          = round(clip.fps, 2)
            duration     = round(clip.duration, 2)
            frame_count  = int(fps * duration)
            bitrate_kbps = round((size_bytes * 8) / (duration * 1000), 1) if duration > 0 else 0
            clip.close()
        except Exception:
            pass

        return {
            "type"        : "video",
            "path"        : str(path),
            "filename"    : p.name,
            "format"      : p.suffix.lstrip(".").upper(),
            "codec"       : "H.264",
            "size_bytes"  : size_bytes,
            "size_mb"     : size_mb,
            "duration"    : duration,
            "width"       : width,
            "height"      : height,
            "resolution"  : f"{width}×{height}",
            "fps"         : fps,
            "bitrate_kbps": bitrate_kbps,
        }

    # ── ROI Score ──────────────────────────────────────────────────────────────

    def compute_roi_score(self, pre: dict, post: dict) -> dict:
        if pre["size_bytes"] == 0:
            return {"score": 0, "label": "N/A", "breakdown": {}}

        size_reduction = 1.0 - (post["size_bytes"] / pre["size_bytes"])
        size_score     = min(100, size_reduction * 150)

        pre_br  = pre.get("bitrate_kbps",  1) or 1
        post_br = post.get("bitrate_kbps", 1) or 1
        quality_score = min(100, (post_br / pre_br) * 120)

        penalty = 25 if size_reduction > 0.9 else (40 if size_reduction < 0.05 else 0)
        score   = max(0, min(100, round(size_score * 0.6 + quality_score * 0.4 - penalty)))
        label   = "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor"

        return {
            "score"              : score,
            "label"              : label,
            "size_reduction_pct" : round(size_reduction * 100, 1),
            "compression_ratio"  : round(pre["size_bytes"] / max(post["size_bytes"], 1), 2),
            "breakdown": {
                "size_score"   : round(size_score, 1),
                "quality_score": round(quality_score, 1),
                "penalty"      : penalty,
            },
        }
