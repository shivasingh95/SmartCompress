"""
UI Components Module
All Streamlit rendering functions: charts, cards, metrics, CSS.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Optional


# ── CSS ────────────────────────────────────────────────────────────────────────

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .main { background: #0a0e1a; }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1424 50%, #0a1520 100%);
    }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1a1f35 0%, #0f1628 100%);
        border: 1px solid rgba(99, 179, 237, 0.15);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .app-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #4facfe, #00f2fe, #43e97b, #38f9d7);
    }
    .app-header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 50%, #43e97b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem 0;
    }
    .app-header p {
        color: #8892a4;
        font-size: 1.05rem;
        margin: 0;
    }
    .badge-row {
        display: flex;
        gap: 0.6rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    .badge {
        background: rgba(79, 172, 254, 0.1);
        border: 1px solid rgba(79, 172, 254, 0.3);
        color: #4facfe;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Metric cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1f35 0%, #0f1628 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: rgba(79, 172, 254, 0.4); }
    .metric-card .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e8eaf0;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    .metric-card .metric-label {
        font-size: 0.78rem;
        color: #6b7280;
        margin-top: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-card.highlight {
        border-color: rgba(79, 172, 254, 0.4);
        background: linear-gradient(135deg, #1a2540 0%, #0f1a30 100%);
    }
    .metric-card .metric-val.positive { color: #43e97b; }
    .metric-card .metric-val.accent   { color: #4facfe; }

    /* Info / file card */
    .info-card {
        background: #131827;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
    }
    .info-card h4 {
        color: #8892a4;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 0 0.75rem 0;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.35rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        font-size: 0.9rem;
    }
    .info-row:last-child { border-bottom: none; }
    .info-row .key   { color: #6b7280; }
    .info-row .value { color: #cbd5e1; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }

    /* Advisor card */
    .advisor-card {
        background: linear-gradient(135deg, #1a2030 0%, #0f1624 100%);
        border: 1px solid rgba(67, 233, 123, 0.25);
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
    }
    .advisor-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        border-radius: 14px 14px 0 0;
        background: linear-gradient(90deg, #43e97b, #38f9d7);
    }
    .advisor-headline {
        font-size: 1.15rem;
        font-weight: 600;
        color: #e8eaf0;
        margin-bottom: 0.3rem;
    }
    .advisor-summary {
        font-size: 0.85rem;
        color: #6b7280;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 1rem;
    }
    .rec-item {
        background: rgba(67, 233, 123, 0.07);
        border-left: 3px solid #43e97b;
        padding: 0.5rem 0.75rem;
        border-radius: 0 6px 6px 0;
        margin: 0.4rem 0;
        font-size: 0.88rem;
        color: #c8d8c8;
    }
    .warn-item {
        background: rgba(251, 191, 36, 0.07);
        border-left: 3px solid #fbbf24;
        padding: 0.5rem 0.75rem;
        border-radius: 0 6px 6px 0;
        margin: 0.4rem 0;
        font-size: 0.88rem;
        color: #d4c090;
    }
    .confidence-tag {
        display: inline-block;
        background: rgba(79, 172, 254, 0.15);
        border: 1px solid rgba(79, 172, 254, 0.4);
        color: #4facfe;
        font-size: 0.72rem;
        padding: 0.15rem 0.6rem;
        border-radius: 10px;
        font-family: 'JetBrains Mono', monospace;
        margin-left: 0.5rem;
    }

    /* Feature list */
    .feature-list { margin-top: 0.5rem; }
    .feature-item {
        background: #131827;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 0.4rem 0;
        font-size: 0.9rem;
        color: #c8d0dc;
    }

    /* Bandwidth table */
    .bw-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        margin-top: 0.5rem;
    }
    .bw-table th {
        background: #1a1f35;
        color: #8892a4;
        padding: 0.6rem 1rem;
        text-align: left;
        font-weight: 500;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .bw-table td {
        padding: 0.55rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        color: #cbd5e1;
    }
    .bw-table tr:hover td { background: rgba(255,255,255,0.02); }
    .bw-table .saved-col { color: #43e97b; font-family: 'JetBrains Mono', monospace; }
    .bw-table .time-col  { font-family: 'JetBrains Mono', monospace; }
    .bw-saving-bar {
        background: rgba(67, 233, 123, 0.15);
        border-radius: 4px;
        height: 6px;
        margin-top: 3px;
    }
    .bw-saving-fill {
        background: linear-gradient(90deg, #43e97b, #38f9d7);
        border-radius: 4px;
        height: 6px;
    }

    /* CDN cost card */
    .cdn-card {
        background: linear-gradient(135deg, #1a2030, #0f1624);
        border: 1px solid rgba(79, 172, 254, 0.2);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-top: 1rem;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 5rem 2rem;
        color: #4b5563;
    }
    .empty-icon { font-size: 4rem; margin-bottom: 1rem; }
    .empty-title { font-size: 1.3rem; color: #6b7280; font-weight: 500; }
    .empty-sub { font-size: 0.9rem; color: #4b5563; margin-top: 0.5rem; }

    /* Override Streamlit defaults */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #0a0e1a;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        padding: 0.75rem 2rem;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.4);
    }

    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────

def render_header():
    st.markdown("""
    <div class="app-header">
        <h1>🎛️ SmartCompress AI</h1>
        <p>Production-grade multimedia compression with intelligent analysis</p>
        <div class="badge-row">
            <span class="badge">🤖 AI Advisor</span>
            <span class="badge">📡 Bandwidth Sim</span>
            <span class="badge">🎞️ Scene Analysis</span>
            <span class="badge">📊 ROI Score</span>
            <span class="badge">H.264 · MP3 · AAC</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── File Info Card ─────────────────────────────────────────────────────────────

def render_file_info_card(info: dict, label: str = ""):
    title = f"{label} File" if label else "File Info"
    rows = ""

    rows += f'<div class="info-row"><span class="key">Filename</span><span class="value">{info.get("filename", "—")}</span></div>'
    rows += f'<div class="info-row"><span class="key">Format</span><span class="value">{info.get("format", "—")} / {info.get("codec", "—")}</span></div>'
    rows += f'<div class="info-row"><span class="key">File Size</span><span class="value">{info.get("size_mb", 0):.3f} MB</span></div>'
    rows += f'<div class="info-row"><span class="key">Duration</span><span class="value">{_fmt_duration(info.get("duration", 0))}</span></div>'
    rows += f'<div class="info-row"><span class="key">Bitrate</span><span class="value">{info.get("bitrate_kbps", 0)} kbps</span></div>'

    if info.get("type") == "video":
        rows += f'<div class="info-row"><span class="key">Resolution</span><span class="value">{info.get("resolution", "—")}</span></div>'
        rows += f'<div class="info-row"><span class="key">Frame Rate</span><span class="value">{info.get("fps", 0)} fps</span></div>'
    elif info.get("type") == "audio":
        rows += f'<div class="info-row"><span class="key">Sample Rate</span><span class="value">{info.get("sample_rate", 0):,} Hz</span></div>'
        rows += f'<div class="info-row"><span class="key">Channels</span><span class="value">{"Stereo" if info.get("channels") == 2 else "Mono"}</span></div>'

    st.markdown(f"""
    <div class="info-card">
        <h4>{title}</h4>
        {rows}
    </div>
    """, unsafe_allow_html=True)


# ── Advisor Card ───────────────────────────────────────────────────────────────

def render_advisor_card(advice):
    recs_html = "".join(
        f'<div class="rec-item">✅ {r}</div>' for r in advice.recommendations
    )
    warns_html = "".join(
        f'<div class="warn-item">⚠️ {w}</div>' for w in advice.warnings
    )
    optimal_items = " · ".join(
        f"<b>{k}</b>: {v}" for k, v in advice.optimal_settings.items()
    )

    st.markdown(f"""
    <div class="advisor-card">
        <div class="advisor-headline">
            🧠 AI Smart Advisor
            <span class="confidence-tag">Confidence: {advice.confidence}</span>
        </div>
        <div class="advisor-summary">{advice.headline} — {advice.summary}</div>
        {recs_html}
        {warns_html}
        {'<div class="rec-item">⚙️ Optimal: ' + optimal_items + '</div>' if optimal_items else ''}
    </div>
    """, unsafe_allow_html=True)


# ── Metrics Row ────────────────────────────────────────────────────────────────

def render_metrics_row(pre: dict, post: dict, elapsed: float):
    orig_mb = pre.get("size_mb", 0)
    comp_mb = post.get("size_mb", 0)
    ratio = round(orig_mb / comp_mb, 2) if comp_mb > 0 else 0
    saved_mb = round(orig_mb - comp_mb, 3)
    saved_pct = round((saved_mb / orig_mb) * 100, 1) if orig_mb > 0 else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("📁 Original Size", f"{orig_mb:.2f} MB")
    with col2:
        st.metric("📦 Compressed Size", f"{comp_mb:.2f} MB", delta=f"-{saved_mb:.2f} MB")
    with col3:
        st.metric("🗜️ Compression Ratio", f"{ratio}×")
    with col4:
        st.metric("💾 Space Saved", f"{saved_pct}%")
    with col5:
        st.metric("⏱️ Time Taken", f"{elapsed:.1f}s")
    with col6:
        bitrate_after = post.get("bitrate_kbps", 0)
        st.metric("📡 Output Bitrate", f"{bitrate_after} kbps")


# ── Compression Chart ──────────────────────────────────────────────────────────

def render_compression_chart(pre: dict, post: dict):
    orig = pre.get("size_mb", 0)
    comp = post.get("size_mb", 0)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Original",
        x=["File Size (MB)"],
        y=[orig],
        marker=dict(
            color="rgba(79, 172, 254, 0.85)",
            line=dict(color="#4facfe", width=1.5),
        ),
        text=[f"{orig:.2f} MB"],
        textposition="outside",
        textfont=dict(color="#cbd5e1", size=13, family="JetBrains Mono"),
        width=0.35,
    ))

    fig.add_trace(go.Bar(
        name="Compressed",
        x=["File Size (MB)"],
        y=[comp],
        marker=dict(
            color="rgba(67, 233, 123, 0.85)",
            line=dict(color="#43e97b", width=1.5),
        ),
        text=[f"{comp:.2f} MB"],
        textposition="outside",
        textfont=dict(color="#cbd5e1", size=13, family="JetBrains Mono"),
        width=0.35,
    ))

    fig.update_layout(
        barmode="group",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#8892a4"),
        legend=dict(
            orientation="h",
            y=1.1,
            x=0,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=40, b=20, l=10, r=10),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            ticksuffix=" MB",
            tickfont=dict(family="JetBrains Mono"),
        ),
        height=320,
    )

    st.plotly_chart(fig, use_container_width=True)


# ── ROI Gauge ──────────────────────────────────────────────────────────────────

def render_roi_gauge(roi: dict):
    score = roi.get("score", 0)
    label = roi.get("label", "N/A")

    color_map = {
        "Excellent": "#43e97b",
        "Good": "#4facfe",
        "Fair": "#fbbf24",
        "Poor": "#f87171",
    }
    color = color_map.get(label, "#6b7280")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"ROI: {label}", "font": {"color": "#8892a4", "size": 14, "family": "Space Grotesk"}},
        number={"suffix": "/100", "font": {"color": color, "size": 36, "family": "JetBrains Mono"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#4b5563", "tickfont": {"color": "#6b7280"}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40],  "color": "rgba(248,113,113,0.1)"},
                {"range": [40, 60], "color": "rgba(251,191,36,0.1)"},
                {"range": [60, 80], "color": "rgba(79,172,254,0.1)"},
                {"range": [80, 100],"color": "rgba(67,233,123,0.1)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#8892a4"),
        height=260,
        margin=dict(t=30, b=10, l=20, r=20),
    )

    breakdown = roi.get("breakdown", {})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""
    <div style="font-size:0.8rem; color:#6b7280; text-align:center; font-family:'JetBrains Mono', monospace;">
        Size Reduction: <b style="color:#43e97b">{roi.get('size_reduction_pct', 0)}%</b> &nbsp;|&nbsp;
        Ratio: <b style="color:#4facfe">{roi.get('compression_ratio', 0)}×</b>
    </div>
    """, unsafe_allow_html=True)


# ── Bandwidth Table ────────────────────────────────────────────────────────────

def render_bandwidth_table(bw_data: dict):
    networks = bw_data.get("networks", [])
    cdn = bw_data.get("cdn", {})

    rows_html = ""
    for n in networks:
        pct = n["saving_pct"]
        bar_width = min(100, pct)
        rows_html += f"""
        <tr>
            <td>{n['emoji']} {n['network']}</td>
            <td style="color:#6b7280;font-size:0.78rem;">{n['typical_use']}</td>
            <td class="time-col">{n['original_time']}</td>
            <td class="time-col">{n['compressed_time']}</td>
            <td class="saved-col">
                {n['time_saved']} ({pct}%)
                <div class="bw-saving-bar"><div class="bw-saving-fill" style="width:{bar_width}%"></div></div>
            </td>
        </tr>
        """

    st.markdown(f"""
    <table class="bw-table">
        <thead>
            <tr>
                <th>Network</th>
                <th>Use Case</th>
                <th>Original Download</th>
                <th>Compressed Download</th>
                <th>Time Saved</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    # CDN Cost Card
    st.markdown(f"""
    <div class="cdn-card">
        <div style="font-size:0.85rem;color:#8892a4;margin-bottom:0.75rem;">
            💰 <b style="color:#cbd5e1">CDN Cost Savings Projection</b>
            <span style="font-family:'JetBrains Mono';font-size:0.75rem;margin-left:0.5rem;">
                ({cdn.get('deliveries_assumed', 0):,} deliveries/month assumed)
            </span>
        </div>
        <div style="display:flex;gap:2rem;flex-wrap:wrap;">
            <div>
                <div style="font-size:1.4rem;font-weight:700;color:#f87171;font-family:'JetBrains Mono'">
                    ${cdn.get('monthly_original_usd', 0):.2f}
                </div>
                <div style="font-size:0.75rem;color:#6b7280">Original Monthly CDN</div>
            </div>
            <div>
                <div style="font-size:1.4rem;font-weight:700;color:#43e97b;font-family:'JetBrains Mono'">
                    ${cdn.get('monthly_compressed_usd', 0):.2f}
                </div>
                <div style="font-size:0.75rem;color:#6b7280">Compressed Monthly CDN</div>
            </div>
            <div>
                <div style="font-size:1.4rem;font-weight:700;color:#4facfe;font-family:'JetBrains Mono'">
                    ${cdn.get('monthly_saving_usd', 0):.2f}/mo
                </div>
                <div style="font-size:0.75rem;color:#6b7280">Monthly Savings</div>
            </div>
            <div>
                <div style="font-size:1.4rem;font-weight:700;color:#00f2fe;font-family:'JetBrains Mono'">
                    ${cdn.get('annual_saving_usd', 0):.2f}/yr
                </div>
                <div style="font-size:0.75rem;color:#6b7280">Annual Savings</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Utility ────────────────────────────────────────────────────────────────────

def _fmt_duration(seconds: float) -> str:
    if seconds <= 0:
        return "—"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}m {s:02d}s" if m > 0 else f"{s}s"
