"""
Smart AI Advisor Module
Content-aware compression recommendations. No external dependencies.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Advice:
    headline       : str
    summary        : str
    recommendations: List[str]
    warnings       : List[str]
    optimal_settings: dict
    confidence     : str  # "High" | "Medium" | "Low"


class SmartAdvisor:
    """Rule-based expert system for compression guidance."""

    def advise_audio(self, info: dict) -> Advice:
        duration    = info.get("duration",     0)
        sample_rate = info.get("sample_rate",  44100)
        channels    = info.get("channels",     2)
        size_mb     = info.get("size_mb",      0)
        recs, warns, optimal = [], [], {}
        confidence = "High"

        if duration > 0 and size_mb > 0:
            raw_kbps = (size_mb * 8 * 1024) / duration
            if raw_kbps > 1200:
                content_type = "Studio / Uncompressed WAV"
                recs.append("128k–192k MP3 gives excellent quality with 8–12× size reduction")
                optimal["bitrate"] = "128k"
            elif raw_kbps > 600:
                content_type = "High-Quality Audio"
                recs.append("192k–256k MP3 recommended to preserve fidelity")
                optimal["bitrate"] = "192k"
            else:
                content_type = "Standard Quality Audio"
                recs.append("128k MP3 is sufficient for this source quality")
                optimal["bitrate"] = "128k"
        else:
            content_type = "Audio File"
            optimal["bitrate"] = "128k"
            confidence = "Low"

        if channels == 1:
            recs.append("Mono audio detected — 64k–96k is sufficient for speech/podcast")
            optimal["bitrate"] = "64k"

        if sample_rate > 48000:
            recs.append(f"{sample_rate}Hz detected — resampling to 44.1kHz saves space without audible loss")
        elif sample_rate < 22050:
            warns.append(f"Low sample rate ({sample_rate}Hz) — audio quality may already be degraded")

        if duration > 600:
            warns.append("File longer than 10 minutes — consider splitting for web delivery")
        if duration < 5:
            warns.append("Very short file — compression gains may be minimal")

        optimal["normalize"]     = True
        optimal["trim_silence"]  = duration > 30

        return Advice(
            headline        = f"Detected: {content_type}",
            summary         = f"{duration:.1f}s · {channels}ch · {sample_rate}Hz · {size_mb:.2f}MB",
            recommendations = recs,
            warnings        = warns,
            optimal_settings= optimal,
            confidence      = confidence,
        )

    def advise_video(self, info: dict) -> Advice:
        width    = info.get("width",        0)
        height   = info.get("height",       0)
        fps      = info.get("fps",          0)
        duration = info.get("duration",     0)
        size_mb  = info.get("size_mb",      0)
        bitrate  = info.get("bitrate_kbps", 0)
        recs, warns, optimal = [], [], {}
        confidence = "High"

        if height >= 2160:
            res_label, optimal["crf"] = "4K Ultra HD",    22
            recs.append("4K source — CRF 20–22 for archival, CRF 28 for web delivery")
        elif height >= 1080:
            res_label, optimal["crf"] = "Full HD 1080p",  23
            recs.append("1080p source — CRF 23 provides the best quality/size balance")
        elif height >= 720:
            res_label, optimal["crf"] = "HD 720p",        25
            recs.append("720p source — CRF 25 is optimal for web streaming")
        elif height > 0:
            res_label, optimal["crf"] = "SD Resolution",  28
            warns.append("Low resolution — aggressive compression may cause blocking artifacts")
        else:
            res_label, optimal["crf"] = "Unknown",        28
            confidence = "Low"

        if fps > 60:
            recs.append(f"{fps}fps detected — dropping to 30fps halves size with minimal perceptual loss")
        elif fps < 24 and fps > 0:
            warns.append(f"Low frame rate ({fps}fps) — may appear choppy after re-encoding")

        if bitrate > 20000:
            recs.append("Very high source bitrate — expect 5–10× file size reduction")
        elif bitrate < 500 and bitrate > 0:
            warns.append("Low source bitrate — compression gains may be limited")

        if duration > 3600:
            warns.append("Video exceeds 1 hour — processing will take significant time")
        if duration < 10:
            warns.append("Very short clip — encoding overhead reduces efficiency")

        if width > 1920:
            recs.append("Consider 50% scale for web — saves bandwidth with minimal visual difference")
            optimal["scale"] = 0.5
        else:
            optimal["scale"] = 1.0

        return Advice(
            headline        = f"Detected: {res_label} @ {fps}fps",
            summary         = f"{info.get('resolution','N/A')} · {duration:.1f}s · {size_mb:.2f}MB · ~{bitrate}kbps",
            recommendations = recs,
            warnings        = warns,
            optimal_settings= optimal,
            confidence      = confidence,
        )
