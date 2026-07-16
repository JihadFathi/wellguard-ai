"""
WellGuard AI — Main Streamlit Application
Compatible with Streamlit Community Cloud (multi-page app structure).
"""
import streamlit as st
import os
import sys

# ── Path setup ────────────────────────────────────────────────────────
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

# ── CSS Loader ────────────────────────────────────────────────────────
def _load_css():
    css_path = os.path.join(APP_DIR, "ui", "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="WellGuard AI | Predictive Maintenance",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "**WellGuard AI** — ESP Pump Predictive Maintenance System"
    }
)

_load_css()

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px 0;">
        <div style="font-size:2.5rem">🛢️</div>
        <div style="font-size:1.4rem;font-weight:800;color:#00B4D8;letter-spacing:1px;">WellGuard AI</div>
        <div style="font-size:0.75rem;color:#8892A4;letter-spacing:2px;text-transform:uppercase;margin-top:4px;">
            Predictive Maintenance
        </div>
    </div>
    <hr style="border-color:rgba(0,180,216,0.2);margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("### 🗂️ Navigation")
    pages = {
        "🏠  Home":               "streamlit_app",
        "📊  Wells Overview":      "pages/1_dashboard",
        "📁  Upload Dataset":      "pages/2_upload",
        "✏️  Manual Entry":        "pages/3_manual_entry",
        "🔬  Analysis Results":    "pages/4_analysis",
        "🕰️  History":             "pages/5_history",
        "⚙️  Settings":            "pages/6_settings",
    }
    # Use query param for simple routing
    for label, page_key in pages.items():
        st.page_link(f"pages/{page_key.split('/')[-1]}.py" if "/" in page_key else "streamlit_app.py",
                     label=label)

    st.markdown("""
    <hr style="border-color:rgba(0,180,216,0.2);margin:12px 0;">
    <div style="color:#8892A4;font-size:0.75rem;text-align:center;">
        v1.0.0 &nbsp;|&nbsp; Well B-167
    </div>
    """, unsafe_allow_html=True)

# ── Home Page ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:60px 20px 40px 20px;">
    <div style="font-size:4rem;margin-bottom:16px;">🛢️</div>
    <h1 style="font-size:3rem;font-weight:900;color:#E8EAF6;margin:0;letter-spacing:-1px;">
        WellGuard <span style="color:#00B4D8;">AI</span>
    </h1>
    <p style="color:#8892A4;font-size:1.15rem;max-width:560px;margin:16px auto 0 auto;line-height:1.7;">
        Intelligent Predictive Maintenance for Electrical Submersible Pumps.<br>
        Monitor, predict, and prevent ESP pump failures before they happen.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Quick-Action Cards ────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4, gap="medium")
cards = [
    ("📊", "Wells Overview",  "Monitor all active wells"),
    ("📁", "Upload Data",     "Process sensor exports"),
    ("🔬", "Analyze",         "Run predictions & reports"),
    ("📄", "PDF Report",      "Export maintenance brief"),
]
for col, (icon, title, desc) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value" style="font-size:1.3rem;">{title}</div>
            <div class="kpi-label">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── System Features ───────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">⚡ System Capabilities</div>', unsafe_allow_html=True)

features = [
    ("🤖", "AI Classification",   "Multi-class health state prediction using Random Forest & LightGBM with 100% critical recall on B-167 dataset."),
    ("🔢", "Health Index (PHI)",  "Real-time Pump Health Index 0–100 combining model probabilities, sensor z-scores, and degradation trends."),
    ("📅", "RUL Forecasting",     "Remaining Useful Life in days, dynamically adjusted by current degradation rate and failure probability."),
    ("🔔", "Smart Alerts",        "Threshold-based P1–P4 recommendation engine with multi-rule escalation for actionable maintenance guidance."),
    ("📊", "Interactive Charts",  "Time-series sensor trends, PHI history, and failure probability visualization powered by Plotly."),
    ("📄", "PDF Reports",         "Professional 7-page maintenance reports with charts, sensor tables, AI findings, and recommendations."),
]
rows = [features[i:i+3] for i in range(0, len(features), 3)]
for row in rows:
    cols = st.columns(3, gap="medium")
    for col, (icon, title, desc) in zip(cols, row):
        with col:
            st.markdown(f"""
            <div class="well-card" style="min-height:160px;">
                <div style="font-size:2rem;margin-bottom:8px">{icon}</div>
                <div style="color:#00B4D8;font-weight:700;font-size:1rem;margin-bottom:6px">{title}</div>
                <div style="color:#8892A4;font-size:0.85rem;line-height:1.5">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Model Status Banner ───────────────────────────────────────────────
model_path = os.path.join(APP_DIR, "models", "trained", "best_model.pkl")
model_exists = os.path.exists(model_path)

if model_exists:
    st.success("✅ **AI Model Loaded** — Random Forest classifier (Macro F1: 1.000 | Critical Recall: 1.000) ready for inference.")
else:
    st.warning("⚠️ **No trained model found.** Use the Settings page to trigger retraining, or upload a dataset first.")

st.markdown("""
<br>
<div style="text-align:center;color:#5A6478;font-size:0.8rem;padding:20px 0;">
    WellGuard AI &nbsp;|&nbsp; ESP Predictive Maintenance System &nbsp;|&nbsp; Well B-167
</div>
""", unsafe_allow_html=True)
