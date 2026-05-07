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

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background-color: #f4f1ea;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Header */
.dashboard-header {
    background: linear-gradient(135deg, #2c4c3b 0%, #4a7c59 50%, #8fbc8f 100%);
    padding: 1.8rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 8px 32px rgba(46, 204, 113, 0.25);
}
.dashboard-header h1 {
    margin: 0; font-size: 1.8rem; font-weight: 700;
}
.dashboard-header p {
    margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.95rem;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #fcfbf8, #f4f1ea);
    border: 1px solid #e3e0d8;
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}
.kpi-icon { font-size: 1.6rem; }
.kpi-label { font-size: 0.75rem; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.3rem; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: #0d4f2b; margin-top: 0.1rem; }

/* Section */
.section-title {
    font-size: 1.15rem; font-weight: 600; color: #2c4c3b;
    border-left: 4px solid #8fbc8f; padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
}

/* Recommendation */
.rec-card {
    border-radius: 12px; padding: 1rem 1.2rem;
    margin-bottom: 0.6rem; border-left: 5px solid;
    font-size: 0.9rem;
}
.rec-warning { background: #fef3c7; border-color: #f59e0b; color: #92400e; }
.rec-danger  { background: #fee2e2; border-color: #ef4444; color: #991b1b; }
.rec-info    { background: #dbeafe; border-color: #3b82f6; color: #1e40af; }
.rec-success { background: #d1fae5; border-color: #10b981; color: #065f46; }

/* Footer */
.footer {
    text-align: center; padding: 1.5rem 0 0.5rem 0;
    color: #9ca3af; font-size: 0.8rem;
    border-top: 1px solid #e5e7eb; margin-top: 2rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #eceae1 0%, #f4f1ea 100%);
}
section[data-testid="stSidebar"] .stMarkdown h2 {
    color: #0d4f2b;
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
    "primary": "#8fbc8f", "secondary": "#7ab893", "accent": "#73a5c6",
    "warm": "#d9a05b", "danger": "#c96f6f", "purple": "#9581b3",
}

col1, col2 = st.columns(2)

with col1:
    fig_temp = px.line(
        df_sample, x="UAV_Timestamp", y="Temperature",
        title="🌡️ Temperature Over Time",
        labels={"UAV_Timestamp": "Waktu", "Temperature": "Temperature (norm)"},
    )
    fig_temp.update_traces(line=dict(color=chart_colors["warm"], width=1.5))
    fig_temp.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    fig_moist = px.line(
        df_sample, x="UAV_Timestamp", y="Moisture",
        title="💧 Moisture Over Time",
        labels={"UAV_Timestamp": "Waktu", "Moisture": "Moisture (norm)"},
    )
    fig_moist.update_traces(line=dict(color=chart_colors["accent"], width=1.5))
    fig_moist.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_moist, use_container_width=True)

# ──────────────────────────────────────────────
# CHARTS — DISTRIBUTION & CORRELATION
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">📊 Distribusi & Korelasi</p>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    action_counts = df["Action_Suggested"].value_counts().reset_index()
    action_counts.columns = ["Action", "Count"]
    color_map = {
        "Irrigate": "#73a5c6", "Monitor": "#8fbc8f",
        "Apply Fertilizer": "#d9a05b", "Apply Pesticide": "#c96f6f",
    }
    fig_bar = px.bar(
        action_counts, x="Action", y="Count", color="Action",
        title="🎯 Distribusi Action Suggested",
        color_discrete_map=color_map,
    )
    fig_bar.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400, showlegend=False,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
    )
    fig_bar.update_traces(marker_line_width=0, opacity=0.9)
    st.plotly_chart(fig_bar, use_container_width=True)

with col4:
    corr_cols = ["Temperature", "Humidity", "Moisture", "pH", "N", "P", "K",
                 "Energy_Consumed_mAh", "Latency_ms"]
    corr_matrix = df[corr_cols].corr()
    fig_heat = px.imshow(
        corr_matrix, text_auto=".2f",
        title="🔥 Heatmap Korelasi Fitur Utama",
        color_continuous_scale="Tealrose", aspect="auto",
        labels=dict(color="Korelasi"),
    )
    fig_heat.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
    )
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
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(size=10)),
    )
    st.plotly_chart(fig_box, use_container_width=True)

with col6:
    fig_scatter = px.scatter(
        df_sample, x="Temperature", y="Humidity",
        color="Action_Suggested", opacity=0.6,
        title="🔬 Scatter: Temperature vs Humidity",
        color_discrete_map=color_map,
        labels={"Temperature": "Temperature (norm)", "Humidity": "Humidity (norm)"},
    )
    fig_scatter.update_traces(marker=dict(size=4))
    fig_scatter.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(size=10)),
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
    fig_energy.update_traces(line=dict(color="#c96f6f", width=1.5))
    fig_energy.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=370,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_energy, use_container_width=True)

with col8:
    fig_latency = px.line(
        df_sample, x="UAV_Timestamp", y="Latency_ms",
        title="⏱️ Latency (ms) Trend",
        labels={"UAV_Timestamp": "Waktu", "Latency_ms": "Latency (norm)"},
    )
    fig_latency.update_traces(line=dict(color="#9581b3", width=1.5))
    fig_latency.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=370,
        title_font=dict(size=15), margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
    )
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
