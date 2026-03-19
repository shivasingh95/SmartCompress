"""
Smart Multimedia Compression & Analyzer System
Pure Python — no system FFmpeg required.
Uses: moviepy · pydub · soundfile · imageio-ffmpeg (all via pip)
"""

import streamlit as st
import os
import time
import tempfile
from pathlib import Path

st.set_page_config(
    page_title="SmartCompress AI",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


# ── Dep check (pure pip — no system tools) ────────────────────────────────────
@st.cache_resource
def check_deps() -> tuple[bool, list]:
    missing = []
    try:
        import moviepy
    except ImportError:
        missing.append("moviepy")
    try:
        import pydub
    except ImportError:
        missing.append("pydub")
    try:
        import soundfile
    except ImportError:
        missing.append("soundfile")
    try:
        import plotly
    except ImportError:
        missing.append("plotly")
    return len(missing) == 0, missing

deps_ok, missing_deps = check_deps()

if not deps_ok:
    st.error(f"❌ Missing packages: `{', '.join(missing_deps)}`")
    st.code("pip install -r requirements.txt", language="bash")
    st.stop()
    raise SystemExit

from utils.audio       import AudioProcessor
from utils.video       import VideoProcessor
from utils.analyzer    import MediaAnalyzer
from utils.intelligence import SmartAdvisor
from utils.bandwidth   import BandwidthSimulator
from utils.ui_components import (
    render_header, render_metrics_row, render_compression_chart,
    render_bandwidth_table, render_roi_gauge, render_file_info_card,
    render_advisor_card, apply_custom_css,
)

apply_custom_css()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ SmartCompress AI")
    st.markdown("---")
    st.success("✅ No system dependencies required", icon="🐍")
    st.markdown("---")
    st.markdown("### ⚙️ Processing Settings")

    media_type = st.radio("Media Type", ["🎵 Audio", "🎬 Video"], horizontal=False)
    st.markdown("---")

    if "Audio" in media_type:
        st.markdown("#### Audio Compression")
        bitrate = st.select_slider(
            "Output Bitrate",
            options=["64k", "128k", "192k", "256k", "320k"],
            value="128k",
        )
        normalize_audio = st.toggle("Normalize Volume", value=True)
        remove_silence  = st.toggle("Trim Silence",     value=False)
    else:
        st.markdown("#### Video Compression")
        quality_preset = st.select_slider(
            "Quality Preset",
            options=["Ultra Low (CRF 40)", "Low (CRF 35)", "Medium (CRF 28)",
                     "High (CRF 20)", "Ultra High (CRF 15)"],
            value="Medium (CRF 28)",
        )
        crf_map = {
            "Ultra Low (CRF 40)": 40, "Low (CRF 35)": 35, "Medium (CRF 28)": 28,
            "High (CRF 20)": 20,      "Ultra High (CRF 15)": 15,
        }
        crf = crf_map[quality_preset]
        resolution_scale = st.select_slider(
            "Resolution Scale",
            options=["25%", "50%", "75%", "100%"],
            value="100%",
        )
        scale_map = {"25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
        res_scale = scale_map[resolution_scale]

    st.markdown("---")
    simulate_bandwidth = st.toggle("Show Bandwidth Analysis", value=True)
    st.markdown("---")
    st.caption("SmartCompress AI v3.0 · Pure Python Edition")


# ── Main Layout ───────────────────────────────────────────────────────────────
render_header()

col_upload, col_info = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("### 📂 Upload Media File")
    accepted   = [".wav"] if "Audio" in media_type else [".mp4", ".avi"]
    accept_str = ", ".join(accepted)
    uploaded   = st.file_uploader(
        f"Drop your file here · Supported: `{accept_str}`",
        type=[x.lstrip(".") for x in accepted],
        key="uploader",
    )

with col_info:
    st.markdown("### 🧠 Pure Python Stack")
    st.markdown("""
    <div class="feature-list">
        <div class="feature-item">🐍 <strong>moviepy</strong> — Video encode/decode (bundled codec)</div>
        <div class="feature-item">🎵 <strong>pydub</strong> — Audio compression to MP3</div>
        <div class="feature-item">📊 <strong>soundfile</strong> — Audio metadata & signal analysis</div>
        <div class="feature-item">🤖 <strong>AI Smart Advisor</strong> — Content-aware recommendations</div>
        <div class="feature-item">📡 <strong>Bandwidth + CDN Simulator</strong> — Real-world impact</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


def save_upload(uf) -> tuple[Path, bytes]:
    data   = uf.getvalue()
    suffix = Path(uf.name).suffix.lower()
    tmp    = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=TEMP_DIR)
    tmp.write(data)
    tmp.close()
    return Path(tmp.name), data


def cleanup(*paths):
    for p in paths:
        try:
            if p and Path(p).exists():
                os.remove(p)
        except Exception:
            pass


# ── Processing ────────────────────────────────────────────────────────────────
if uploaded is not None:
    input_path, input_bytes = save_upload(uploaded)
    output_path = None
    output_bytes = b""

    try:
        analyzer = MediaAnalyzer()
        advisor  = SmartAdvisor()

        with st.spinner("🔍 Analyzing media..."):
            if "Audio" in media_type:
                pre_info = analyzer.analyze_audio(str(input_path))
                advice   = advisor.advise_audio(pre_info)
            else:
                pre_info = analyzer.analyze_video(str(input_path))
                advice   = advisor.advise_video(pre_info)

        render_advisor_card(advice)
        st.markdown("---")
        st.markdown("### 📋 Original File Analysis")
        render_file_info_card(pre_info, "Original")
        st.markdown("---")

        btn_col, _ = st.columns([1, 2])
        with btn_col:
            run_btn = st.button("🚀 Compress & Analyze", type="primary", use_container_width=True)

        if run_btn:
            bar    = st.progress(0, text="Starting compression...")
            status = st.empty()
            t0     = time.time()

            try:
                if "Audio" in media_type:
                    proc = AudioProcessor()
                    bar.progress(20, text="🎵 Loading audio...")
                    bar.progress(50, text="⚙️ Encoding MP3...")
                    output_path = proc.compress(
                        str(input_path), bitrate=bitrate,
                        normalize=normalize_audio, trim_silence=remove_silence,
                        out_dir=str(TEMP_DIR),
                    )
                    bar.progress(80, text="📊 Analyzing output...")
                    post_info = analyzer.analyze_audio(output_path)

                else:
                    proc = VideoProcessor()
                    bar.progress(10, text="🎬 Reading video metadata...")
                    bar.progress(30, text="🎞️ Analyzing scene complexity...")
                    complexity  = proc.analyze_scene_complexity(str(input_path))
                    bar.progress(50, text="⚙️ Encoding H.264 video...")
                    status.info("⏳ Video encoding takes 30–120s depending on file size. Please wait...")
                    output_path = proc.compress(
                        str(input_path), crf=crf, scale=res_scale, out_dir=str(TEMP_DIR),
                    )
                    bar.progress(85, text="📊 Analyzing output...")
                    status.empty()
                    post_info = analyzer.analyze_video(output_path)
                    post_info["scene_complexity"] = complexity

                output_bytes = Path(output_path).read_bytes()
                elapsed = time.time() - t0
                bar.progress(100, text="✅ Done!")
                status.empty()

            except Exception as e:
                bar.empty()
                status.error(f"❌ Compression failed: {e}")
                st.stop()

            # ── Dashboard ─────────────────────────────────────────────────────
            st.markdown("---")
            st.markdown("### 📊 Compression Results")
            render_metrics_row(pre_info, post_info, elapsed)
            st.markdown("---")

            ch_col, g_col = st.columns([3, 2], gap="large")
            with ch_col:
                st.markdown("#### 📈 Size Comparison")
                render_compression_chart(pre_info, post_info)
            with g_col:
                st.markdown("#### 🏆 Compression ROI Score")
                roi = analyzer.compute_roi_score(pre_info, post_info)
                render_roi_gauge(roi)

            st.markdown("---")

            if simulate_bandwidth:
                st.markdown("### 📡 Bandwidth & CDN Simulator")
                bw = BandwidthSimulator()
                render_bandwidth_table(bw.simulate(pre_info["size_bytes"], post_info["size_bytes"]))
                st.markdown("---")

            # ── Preview ───────────────────────────────────────────────────────
            st.markdown("### ▶️ Before vs After Preview")
            l, r = st.columns(2, gap="large")

            if "Audio" in media_type:
                with l:
                    st.markdown("**Original WAV**")
                    st.audio(input_bytes)
                with r:
                    st.markdown("**Compressed MP3**")
                    st.audio(output_bytes)
            else:
                with l:
                    st.markdown("**Original**")
                    st.video(input_bytes)
                with r:
                    st.markdown("**Compressed**")
                    st.video(output_bytes)

            st.markdown("---")
            st.markdown("### 💾 Download")
            ext     = ".mp3" if "Audio" in media_type else ".mp4"
            dl_name = f"compressed_{Path(uploaded.name).stem}{ext}"
            st.download_button(
                label     = f"⬇️ Download {dl_name}",
                data      = output_bytes,
                file_name = dl_name,
                mime      = "audio/mpeg" if "Audio" in media_type else "video/mp4",
                type      = "primary",
            )

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
    finally:
        if output_path:
            cleanup(output_path)
        cleanup(str(input_path))

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🎛️</div>
        <div class="empty-title">Upload a media file to get started</div>
        <div class="empty-sub">WAV audio · MP4 / AVI video — no system tools required</div>
    </div>
    """, unsafe_allow_html=True)
