"""
🌾 Smart Agriculture IoT Dashboard
Dashboard monitoring lengkap untuk usaha tani kecil berbasis IoT.
Menampilkan data sensor, rekomendasi cerdas, dan monitoring perangkat.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="🌾 Smart Agriculture IoT Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ──────────────────────────────────────────────
   PALETTE (Agriculture / Earth + Sky)
   ──────────────────────────────────────────────
   --bg-0       : #07120e   (deepest base)
   --bg-1       : #0f1d18   (surface)
   --bg-2       : #16271f   (elevated surface)
   --border     : #234539   (subtle border)
   --border-2   : #2f5b49   (active border)
   --text-1     : #eaf5ee   (primary text)
   --text-2     : #b6cdc1   (secondary text)
   --text-3     : #7d9588   (muted)
   --green-1    : #10b981   (primary brand)
   --green-2    : #34d399
   --green-3    : #6ee7b7
   --sky        : #38bdf8   (water / irrigate)
   --amber      : #f59e0b   (sun / fertilizer)
   --rose       : #fb7185   (alert / pesticide)
   --violet     : #a78bfa   (latency / signal)
*/

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #eaf5ee;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Header */
.dashboard-header {
    background:
        radial-gradient(circle at 0% 0%, rgba(52, 211, 153, 0.18) 0%, transparent 55%),
        radial-gradient(circle at 100% 100%, rgba(56, 189, 248, 0.12) 0%, transparent 55%),
        linear-gradient(135deg, #0f1d18 0%, #16271f 60%, #1c3328 100%);
    padding: 1.8rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: #eaf5ee;
    border: 1px solid #234539;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
}
.dashboard-header h1 {
    margin: 0; font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(90deg, #6ee7b7 0%, #34d399 60%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.dashboard-header p {
    margin: 0.4rem 0 0 0; font-size: 0.95rem;
    color: #b6cdc1;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #16271f 0%, #0f1d18 100%);
    border: 1px solid #234539;
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: #2f5b49;
    box-shadow: 0 10px 28px rgba(16, 185, 129, 0.18);
}
.kpi-icon { font-size: 1.6rem; }
.kpi-label {
    font-size: 0.72rem; color: #7d9588; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.6px; margin-top: 0.35rem;
}
.kpi-value {
    font-size: 1.5rem; font-weight: 700; color: #6ee7b7;
    margin-top: 0.15rem;
}

/* Section */
.section-title {
    font-size: 1.15rem; font-weight: 600; color: #eaf5ee;
    border-left: 4px solid #10b981; padding-left: 0.8rem;
    margin: 1.6rem 0 1rem 0;
}

/* Recommendation */
.rec-card {
    border-radius: 12px; padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    border: 1px solid; border-left-width: 5px;
    font-size: 0.9rem;
    backdrop-filter: blur(2px);
}
.rec-card strong { display: block; margin-bottom: 0.25rem; font-size: 0.95rem; }
.rec-warning {
    background: rgba(245, 158, 11, 0.10);
    border-color: rgba(245, 158, 11, 0.35);
    border-left-color: #f59e0b;
    color: #fde7b8;
}
.rec-danger  {
    background: rgba(251, 113, 133, 0.10);
    border-color: rgba(251, 113, 133, 0.35);
    border-left-color: #fb7185;
    color: #fcd5db;
}
.rec-info    {
    background: rgba(56, 189, 248, 0.10);
    border-color: rgba(56, 189, 248, 0.35);
    border-left-color: #38bdf8;
    color: #cfeaff;
}
.rec-success {
    background: rgba(16, 185, 129, 0.10);
    border-color: rgba(16, 185, 129, 0.35);
    border-left-color: #10b981;
    color: #c8f1de;
}

/* Footer */
.footer {
    text-align: center; padding: 1.5rem 0 0.5rem 0;
    color: #7d9588; font-size: 0.8rem;
    border-top: 1px solid #234539; margin-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load and preprocess the agriculture dataset."""
    # Try multiple possible paths
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "DATASET", "Agriculture_Preprocessed_for_Dashboard.csv"),
        os.path.join(os.path.dirname(__file__), "dataset", "Agriculture_Preprocessed_for_Dashboard.csv"),
        "DATASET/Agriculture_Preprocessed_for_Dashboard.csv",
        "dataset/Agriculture_Preprocessed_for_Dashboard.csv",
    ]

    df = None
    for path in possible_paths:
        try:
            df = pd.read_csv(path)
            break
        except FileNotFoundError:
            continue

    if df is None:
        st.error("❌ File dataset tidak ditemukan! Pastikan file 'Agriculture_Preprocessed_for_Dashboard.csv' berada di folder DATASET/")
        st.stop()

    # Parse timestamps
    for col in ["UAV_Timestamp", "Migration_Timestamp"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


try:
    df_raw = load_data()
except Exception as e:
    st.error(f"❌ Gagal memuat dataset: {e}")
    st.stop()

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>🌾 Smart Agriculture IoT Dashboard</h1>
    <p>Monitoring real-time sensor pertanian, rekomendasi cerdas &amp; analisis perangkat IoT untuk usaha tani kecil</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SIDEBAR FILTERS
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filter Data")
    st.markdown("---")

    # Action filter
    actions = sorted(df_raw["Action_Suggested"].dropna().unique().tolist())
    selected_actions = st.multiselect(
        "🎯 Action Suggested",
        options=actions,
        default=actions,
        help="Pilih jenis aksi yang ingin ditampilkan"
    )

    st.markdown("---")

    # Temperature range
    temp_min, temp_max = float(df_raw["Temperature"].min()), float(df_raw["Temperature"].max())
    temp_range = st.slider(
        "🌡️ Range Temperature",
        min_value=temp_min, max_value=temp_max,
        value=(temp_min, temp_max),
        step=0.01, format="%.2f"
    )

    # Moisture range
    moist_min, moist_max = float(df_raw["Moisture"].min()), float(df_raw["Moisture"].max())
    moisture_range = st.slider(
        "💧 Range Moisture",
        min_value=moist_min, max_value=moist_max,
        value=(moist_min, moist_max),
        step=0.01, format="%.2f"
    )

    # pH range
    ph_min, ph_max = float(df_raw["pH"].min()), float(df_raw["pH"].max())
    ph_range = st.slider(
        "🧪 Range pH",
        min_value=ph_min, max_value=ph_max,
        value=(ph_min, ph_max),
        step=0.01, format="%.2f"
    )

    st.markdown("---")
    st.markdown(f"📊 **Total data:** `{len(df_raw):,}` baris")

# Apply filters
df = df_raw[
    (df_raw["Action_Suggested"].isin(selected_actions)) &
    (df_raw["Temperature"].between(temp_range[0], temp_range[1])) &
    (df_raw["Moisture"].between(moisture_range[0], moisture_range[1])) &
    (df_raw["pH"].between(ph_range[0], ph_range[1]))
].copy()

st.sidebar.markdown(f"✅ **Data terfilter:** `{len(df):,}` baris")

if df.empty:
    st.warning("⚠️ Tidak ada data yang sesuai filter. Silakan sesuaikan filter di sidebar.")
    st.stop()

# ──────────────────────────────────────────────
# KPI SECTION
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">📊 Key Performance Indicators</p>', unsafe_allow_html=True)

def render_kpi(icon, label, value):
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>"""

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(render_kpi("🌡️", "Avg Temperature", f"{df['Temperature'].mean():.3f}"), unsafe_allow_html=True)
with k2:
    st.markdown(render_kpi("💨", "Avg Humidity", f"{df['Humidity'].mean():.3f}"), unsafe_allow_html=True)
with k3:
    st.markdown(render_kpi("💧", "Avg Moisture", f"{df['Moisture'].mean():.3f}"), unsafe_allow_html=True)
with k4:
    st.markdown(render_kpi("🧪", "Avg pH", f"{df['pH'].mean():.3f}"), unsafe_allow_html=True)
with k5:
    st.markdown(render_kpi("⏱️", "Avg Latency", f"{df['Latency_ms'].mean():.3f}"), unsafe_allow_html=True)
with k6:
    st.markdown(render_kpi("🔋", "Avg Energy", f"{df['Energy_Consumed_mAh'].mean():.3f}"), unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CHARTS — SENSOR ANALYSIS
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">📈 Analisis Sensor Lingkungan</p>', unsafe_allow_html=True)

# Sample data for performance (large dataset)
sample_size = min(5000, len(df))
df_sample = df.sample(n=sample_size, random_state=42).sort_values("UAV_Timestamp") if len(df) > sample_size else df.sort_values("UAV_Timestamp")

chart_colors = {
    "primary":   "#34d399",  # green
    "secondary": "#6ee7b7",  # mint
    "accent":    "#38bdf8",  # sky / water
    "warm":      "#f59e0b",  # amber / sun
    "danger":    "#fb7185",  # rose
    "purple":    "#a78bfa",  # violet
}

# Konsisten: setiap "Action" dipetakan ke warna semantik
color_map = {
    "Irrigate":         "#38bdf8",  # air → biru langit
    "Monitor":          "#34d399",  # normal → hijau
    "Apply Fertilizer": "#f59e0b",  # pupuk → amber
    "Apply Pesticide":  "#fb7185",  # peringatan → rose
}

# Layout default seragam untuk semua chart
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#eaf5ee", family="Inter"),
    title_font=dict(size=15, color="#eaf5ee"),
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis=dict(showgrid=False, zeroline=False, color="#b6cdc1"),
    yaxis=dict(gridcolor="rgba(234,245,238,0.08)", zeroline=False, color="#b6cdc1"),
)

col1, col2 = st.columns(2)

with col1:
    fig_temp = px.line(
        df_sample, x="UAV_Timestamp", y="Temperature",
        title="🌡️ Temperature Over Time",
        labels={"UAV_Timestamp": "Waktu", "Temperature": "Temperature (norm)"},
    )
    fig_temp.update_traces(line=dict(color=chart_colors["warm"], width=1.8))
    fig_temp.update_layout(height=380, **PLOT_LAYOUT)
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    fig_moist = px.line(
        df_sample, x="UAV_Timestamp", y="Moisture",
        title="💧 Moisture Over Time",
        labels={"UAV_Timestamp": "Waktu", "Moisture": "Moisture (norm)"},
    )
    fig_moist.update_traces(line=dict(color=chart_colors["accent"], width=1.8))
    fig_moist.update_layout(height=380, **PLOT_LAYOUT)
    st.plotly_chart(fig_moist, use_container_width=True)

# ──────────────────────────────────────────────
# CHARTS — DISTRIBUTION & CORRELATION
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">📊 Distribusi & Korelasi</p>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    action_counts = df["Action_Suggested"].value_counts().reset_index()
    action_counts.columns = ["Action", "Count"]
    fig_bar = px.bar(
        action_counts, x="Action", y="Count", color="Action",
        title="🎯 Distribusi Action Suggested",
        color_discrete_map=color_map,
    )
    fig_bar.update_layout(height=400, showlegend=False, **PLOT_LAYOUT)
    fig_bar.update_traces(marker_line_width=0, opacity=0.95)
    st.plotly_chart(fig_bar, use_container_width=True)

with col4:
    corr_cols = ["Temperature", "Humidity", "Moisture", "pH", "N", "P", "K",
                 "Energy_Consumed_mAh", "Latency_ms"]
    corr_matrix = df[corr_cols].corr()
    fig_heat = px.imshow(
        corr_matrix, text_auto=".2f",
        title="🔥 Heatmap Korelasi Fitur Utama",
        color_continuous_scale=[
            [0.0, "#fb7185"],   # negatif kuat → rose
            [0.25, "#7d3a48"],
            [0.5, "#0f1d18"],   # netral → background
            [0.75, "#1f6b52"],
            [1.0, "#34d399"],   # positif kuat → green
        ],
        color_continuous_midpoint=0,
        zmin=-1, zmax=1,
        aspect="auto",
        labels=dict(color="Korelasi"),
    )
    fig_heat.update_layout(height=400, **PLOT_LAYOUT)
    st.plotly_chart(fig_heat, use_container_width=True)

# ──────────────────────────────────────────────
# CHARTS — BOXPLOT & SCATTER
# ──────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    fig_box = px.box(
        df, y="Moisture", color="Action_Suggested",
        title="📦 Boxplot Moisture per Action",
        color_discrete_map=color_map,
    )
    fig_box.update_layout(
        height=400, **PLOT_LAYOUT,
    )
    fig_box.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.35,
                    xanchor="center", x=0.5, font=dict(size=10, color="#b6cdc1")),
    )
    st.plotly_chart(fig_box, use_container_width=True)

with col6:
    fig_scatter = px.scatter(
        df_sample, x="Temperature", y="Humidity",
        color="Action_Suggested", opacity=0.65,
        title="🔬 Scatter: Temperature vs Humidity",
        color_discrete_map=color_map,
        labels={"Temperature": "Temperature (norm)", "Humidity": "Humidity (norm)"},
    )
    fig_scatter.update_traces(marker=dict(size=4, line=dict(width=0)))
    fig_scatter.update_layout(height=400, **PLOT_LAYOUT)
    fig_scatter.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.35,
                    xanchor="center", x=0.5, font=dict(size=10, color="#b6cdc1")),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ──────────────────────────────────────────────
# SMART RECOMMENDATION
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">🧠 Smart Recommendation</p>', unsafe_allow_html=True)

MOISTURE_THRESHOLD = 0.3
PH_THRESHOLD = 0.3
LATENCY_THRESHOLD = 0.7

avg_moisture = df["Moisture"].mean()
avg_ph = df["pH"].mean()
avg_latency = df["Latency_ms"].mean()
avg_energy = df["Energy_Consumed_mAh"].mean()

recommendations = []
if avg_moisture < MOISTURE_THRESHOLD:
    recommendations.append(("warning", "💧", "Irrigation Needed",
        f"Rata-rata Moisture ({avg_moisture:.3f}) di bawah threshold ({MOISTURE_THRESHOLD}). "
        "Segera lakukan irigasi untuk menjaga kelembapan tanah."))
if avg_ph < PH_THRESHOLD:
    recommendations.append(("danger", "🧪", "Soil Treatment Needed",
        f"Rata-rata pH ({avg_ph:.3f}) di bawah threshold ({PH_THRESHOLD}). "
        "Pertimbangkan pengapuran atau perlakuan tanah untuk menyeimbangkan pH."))
if avg_latency > LATENCY_THRESHOLD:
    recommendations.append(("info", "⏱️", "Device Optimization Required",
        f"Rata-rata Latency ({avg_latency:.3f}) melebihi threshold ({LATENCY_THRESHOLD}). "
        "Periksa koneksi jaringan dan optimasi perangkat IoT."))
if avg_energy > 0.7:
    recommendations.append(("danger", "🔋", "High Energy Consumption",
        f"Rata-rata konsumsi energi ({avg_energy:.3f}) sangat tinggi. "
        "Pertimbangkan mode hemat daya atau penggantian baterai."))

if not recommendations:
    recommendations.append(("success", "✅", "Semua Parameter Normal",
        "Semua indikator berada dalam batas normal. Sistem berjalan optimal!"))

rec_cols = st.columns(min(len(recommendations), 2))
for i, (style, icon, title, msg) in enumerate(recommendations):
    with rec_cols[i % 2]:
        st.markdown(f"""
        <div class="rec-card rec-{style}">
            <strong>{icon} {title}</strong><br>
            <span style="font-size:0.85rem;">{msg}</span>
        </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DEVICE MONITORING
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">🔌 Device Monitoring</p>', unsafe_allow_html=True)

col7, col8 = st.columns(2)

with col7:
    fig_energy = px.line(
        df_sample, x="UAV_Timestamp", y="Energy_Consumed_mAh",
        title="🔋 Energy Consumed (mAh) Trend",
        labels={"UAV_Timestamp": "Waktu", "Energy_Consumed_mAh": "Energy (norm)"},
    )
    fig_energy.update_traces(line=dict(color=chart_colors["danger"], width=1.8))
    fig_energy.update_layout(height=370, **PLOT_LAYOUT)
    st.plotly_chart(fig_energy, use_container_width=True)

with col8:
    fig_latency = px.line(
        df_sample, x="UAV_Timestamp", y="Latency_ms",
        title="⏱️ Latency (ms) Trend",
        labels={"UAV_Timestamp": "Waktu", "Latency_ms": "Latency (norm)"},
    )
    fig_latency.update_traces(line=dict(color=chart_colors["purple"], width=1.8))
    fig_latency.update_layout(height=370, **PLOT_LAYOUT)
    st.plotly_chart(fig_latency, use_container_width=True)

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("""
<div class="footer">
    🌾 <strong>Smart Agriculture IoT Dashboard</strong> — Universitas Siliwangi | Semester 6 - IoT<br>
    Built with ❤️ using Streamlit & Plotly | © 2025
</div>
""", unsafe_allow_html=True)
