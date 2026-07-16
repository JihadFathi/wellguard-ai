"""
WellGuard AI - Main Streamlit Application Entry Point
"""

import streamlit as st
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.charts import load_css

# ─── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="WellGuard AI | Predictive Maintenance",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "**WellGuard AI** — Intelligent ESP Pump Predictive Maintenance System"
    }
)

# ─── Load Global CSS ──────────────────────────────────────────────────
load_css()

# ─── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <div style="font-size:2.5rem">🛢️</div>
        <div style="font-size:1.4rem; font-weight:800; color:#00B4D8; letter-spacing:1px;">WellGuard AI</div>
        <div style="font-size:0.75rem; color:#8892A4; letter-spacing:2px; text-transform:uppercase; margin-top:4px;">
            Predictive Maintenance
        </div>
    </div>
    <hr style="border-color:rgba(0,180,216,0.2); margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("### 🗂️ Navigation")
    st.page_link("ui/app.py",                    label="🏠  Home / Dashboard",     icon=None)
    st.page_link("ui/pages/1_dashboard.py",       label="📊  Wells Overview",        icon=None)
    st.page_link("ui/pages/2_upload.py",          label="📁  Upload Dataset",        icon=None)
    st.page_link("ui/pages/3_manual_entry.py",    label="✏️  Manual Entry",          icon=None)
    st.page_link("ui/pages/4_analysis.py",        label="🔬  Analysis Results",      icon=None)
    st.page_link("ui/pages/5_history.py",         label="🕰️  History",               icon=None)
    st.page_link("ui/pages/6_settings.py",        label="⚙️  Settings",              icon=None)

    st.markdown("""
    <hr style="border-color:rgba(0,180,216,0.2); margin:12px 0;">
    <div style="color:#8892A4; font-size:0.75rem; text-align:center;">
        v1.0.0 &nbsp;|&nbsp; Well B-167
    </div>
    """, unsafe_allow_html=True)

# ─── Home Page: Hero Section ──────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 60px 20px 40px 20px;">
    <div style="font-size:4rem; margin-bottom:16px;">🛢️</div>
    <h1 style="font-size:3rem; font-weight:900; color:#E8EAF6; margin:0; letter-spacing:-1px;">
        WellGuard <span style="color:#00B4D8;">AI</span>
    </h1>
    <p style="color:#8892A4; font-size:1.15rem; max-width:560px; margin:16px auto 0 auto; line-height:1.7;">
        Intelligent Predictive Maintenance for Electrical Submersible Pumps.<br>
        Monitor, predict, and prevent ESP pump failures before they happen.
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Quick-Action Cards ───────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    st.markdown("""
    <div class="kpi-card" style="cursor:pointer;">
        <div class="kpi-icon">📊</div>
        <div class="kpi-value" style="font-size:1.4rem;">Wells Overview</div>
        <div class="kpi-label">Monitor all active wells</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="kpi-card" style="cursor:pointer;">
        <div class="kpi-icon">📁</div>
        <div class="kpi-value" style="font-size:1.4rem;">Upload Data</div>
        <div class="kpi-label">Process sensor exports</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="kpi-card" style="cursor:pointer;">
        <div class="kpi-icon">🔬</div>
        <div class="kpi-value" style="font-size:1.4rem;">Analyze</div>
        <div class="kpi-label">Run predictions & reports</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown("""
    <div class="kpi-card" style="cursor:pointer;">
        <div class="kpi-icon">📄</div>
        <div class="kpi-value" style="font-size:1.4rem;">PDF Report</div>
        <div class="kpi-label">Export maintenance brief</div>
    </div>
    """, unsafe_allow_html=True)

# ─── System Features ──────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">⚡ System Capabilities</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)
features = [
    ("🤖", "AI Classification", "Multi-class health state prediction using XGBoost, LightGBM, and Random Forest ensemble models with high recall optimization."),
    ("🔢", "Health Index (PHI)", "Real-time Pump Health Index from 0–100 combining model probabilities, sensor deviations, and degradation trends."),
    ("📅", "RUL Forecasting", "Remaining Useful Life estimation in days, dynamically adjusted by current degradation rate curves."),
    ("🔔", "Smart Alerts", "Threshold-based recommendation engine with P1–P4 priority escalation for actionable maintenance guidance."),
    ("📊", "Interactive Charts", "Time-series sensor trends, PHI history, and failure probability visualization with Plotly."),
    ("📄", "PDF Reports", "Professional 7-page maintenance reports with charts, sensor tables, AI findings, and recommendations."),
]
for i, (icon, title, desc) in enumerate(features):
    col = [f1, f2, f3][i % 3]
    with col:
        st.markdown(f"""
        <div class="well-card" style="min-height:160px;">
            <div style="font-size:2rem;margin-bottom:8px">{icon}</div>
            <div style="color:#00B4D8;font-weight:700;font-size:1rem;margin-bottom:6px">{title}</div>
            <div style="color:#8892A4;font-size:0.85rem;line-height:1.5">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<br>
<div style="text-align:center;color:#5A6478;font-size:0.8rem;padding:20px 0;">
    WellGuard AI &nbsp;|&nbsp; ESP Predictive Maintenance System &nbsp;|&nbsp; Well B-167 Dataset
</div>
""", unsafe_allow_html=True)
