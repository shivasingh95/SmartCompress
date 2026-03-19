"""
Audio Processing Module
Uses pydub (with imageio-ffmpeg bundled codec) + librosa for analysis.
No system FFmpeg installation required — everything via pip.
"""

import warnings
from pathlib import Path

import librosa
import numpy as np

from utils.ffmpeg import configure_bundled_ffmpeg

_BUNDLED_FFMPEG = configure_bundled_ffmpeg()

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        message="Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work",
        category=RuntimeWarning,
        module="pydub.utils",
    )
    from pydub import AudioSegment
    from pydub.silence import detect_leading_silence

AudioSegment.converter = _BUNDLED_FFMPEG
AudioSegment.ffmpeg = _BUNDLED_FFMPEG


class AudioProcessor:
    """
    Compresses WAV → MP3 using pydub with imageio-ffmpeg's bundled codec.
    No system FFmpeg needed — imageio-ffmpeg ships its own binary via pip.
    """

    SUPPORTED_FORMATS = {".wav"}
    VALID_BITRATES     = {"64k", "128k", "192k", "256k", "320k"}

    def compress(
        self,
        input_path: str,
        bitrate: str  = "128k",
        normalize: bool = True,
        trim_silence: bool = False,
        out_dir: str  = "temp",
    ) -> str:
        """
        Compress WAV to MP3.
        Returns path to output MP3.
        """
        self._validate(input_path)
        if bitrate not in self.VALID_BITRATES:
            raise ValueError(f"Invalid bitrate. Choose from {self.VALID_BITRATES}")

        audio = AudioSegment.from_wav(input_path)

        if trim_silence:
            audio = self._trim_silence(audio)

        if normalize:
            audio = self._normalize(audio)

        out_path = self._output_path(input_path, ".mp3", out_dir)
        audio.export(out_path, format="mp3", bitrate=bitrate)
        return out_path

    def get_intelligence(self, input_path: str) -> dict:
        """
        Deep audio analysis using librosa:
        silence ratio, RMS energy, spectral centroid, tempo estimate.
        """
        try:
            y, sr = librosa.load(input_path, sr=None, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            # RMS energy
            rms = float(np.sqrt(np.mean(y ** 2)))

            # Silence ratio (frames below threshold)
            frame_rms   = librosa.feature.rms(y=y)[0]
            thresh      = 0.01
            silence_ratio = float(np.mean(frame_rms < thresh))

            # Spectral centroid (brightness)
            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

            # Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            tempo = float(tempo) if tempo else 0.0

            # Dynamic range
            peak = float(np.max(np.abs(y))) if len(y) > 0 else 0.0
            dynamic_range_db = round(20 * np.log10(peak / (rms + 1e-9)), 2) if rms > 0 else 0

            return {
                "available"        : True,
                "silence_ratio"    : round(silence_ratio, 3),
                "rms_energy"       : round(rms, 4),
                "peak_amplitude"   : round(peak, 4),
                "dynamic_range_db" : dynamic_range_db,
                "spectral_centroid": round(centroid, 1),
                "tempo_bpm"        : round(tempo, 1),
                "sample_rate"      : sr,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ── Private helpers ────────────────────────────────────────────────────────

    def _trim_silence(self, audio: AudioSegment) -> AudioSegment:
        start = detect_leading_silence(audio, silence_threshold=-40)
        end   = detect_leading_silence(audio.reverse(), silence_threshold=-40)
        end_i = len(audio) - end
        return audio[start:end_i] if end_i > start else audio

    def _normalize(self, audio: AudioSegment, target_dbfs: float = -14.0) -> AudioSegment:
        change = target_dbfs - audio.dBFS
        return audio.apply_gain(change)

    @staticmethod
    def _validate(path: str):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if p.suffix.lower() not in AudioProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Only WAV files are supported. Got: {p.suffix}")

    @staticmethod
    def _output_path(input_path: str, ext: str, out_dir: str) -> str:
        stem = Path(input_path).stem
        out  = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        return str(out / f"{stem}_compressed{ext}")
