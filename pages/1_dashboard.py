"""
WellGuard AI - Page 1: Wells Overview Dashboard
"""
import streamlit as st
import sys
import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.charts import (
    load_css, render_kpi_card, render_status_badge,
    phi_gauge, phi_trend_chart, sensor_trend_chart, render_recommendation_card
)

st.set_page_config(page_title="Wells Overview | WellGuard AI", page_icon="📊", layout="wide")
load_css()

# ─── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 10px 0;">
        <div style="font-size:2rem">🛢️</div>
        <div style="font-size:1.3rem;font-weight:800;color:#00B4D8;">WellGuard AI</div>
    </div>
    <hr style="border-color:rgba(0,180,216,0.2);">
    """, unsafe_allow_html=True)
    st.markdown("### 🗂️ Navigation")
    st.page_link("streamlit_app.py",                    label="🏠  Home")
    st.page_link("pages/1_dashboard.py",       label="📊  Wells Overview")
    st.page_link("pages/2_upload.py",          label="📁  Upload Dataset")
    st.page_link("pages/3_manual_entry.py",    label="✏️  Manual Entry")
    st.page_link("pages/4_analysis.py",        label="🔬  Analysis Results")
    st.page_link("pages/5_history.py",         label="🕰️  History")
    st.page_link("pages/6_settings.py",        label="⚙️  Settings")

# ─── Header ───────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:24px 0 16px 0;">
    <h1 style="color:#E8EAF6;font-size:2rem;font-weight:800;margin:0;">
        📊 Wells Overview Dashboard
    </h1>
    <p style="color:#8892A4;margin-top:4px">Real-time health monitoring for all active ESP wells.</p>
</div>
""", unsafe_allow_html=True)

# ─── Load session state or generate mock data ─────────────────────────
# If batch predictions have been stored (from upload page), use them.
# Otherwise display a sample well card.

if 'batch_results' not in st.session_state:
    # Mock example for demonstration
    mock_wells = [
        {'well_id': 'B-167', 'phi': 72.3, 'status': 'Monitor', 'rul': 18, 'label': 'Warning',
         'probs': [0.25, 0.60, 0.15], 'last_update': '2025-06-15 08:00'},
    ]
else:
    mock_wells = st.session_state.batch_results

# ─── Fleet KPI Summary ────────────────────────────────────────────────
st.markdown('<div class="section-header">Fleet Status Summary</div>', unsafe_allow_html=True)

total  = len(mock_wells)
crits  = sum(1 for w in mock_wells if w['status'] == 'Critical')
warns  = sum(1 for w in mock_wells if w['status'] in ('Warning', 'Monitor'))
healths= total - crits - warns
avg_phi= np.mean([w['phi'] for w in mock_wells]) if mock_wells else 0

c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1: render_kpi_card("🛢️", str(total), "Total Wells Monitored", "#00B4D8")
with c2: render_kpi_card("🟢", str(healths), "Healthy Wells", "#2ECC71")
with c3: render_kpi_card("🟡", str(warns), "Warnings / Monitor", "#F39C12")
with c4: render_kpi_card("🔴", str(crits), "Critical Wells", "#E74C3C")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Fleet Average PHI ────────────────────────────────────────────────
st.markdown('<div class="section-header">Fleet Average Health Index</div>', unsafe_allow_html=True)
col_g, col_info = st.columns([1, 2])
with col_g:
    st.plotly_chart(phi_gauge(avg_phi, 'Monitor'), width='stretch', config={'displayModeBar': False})
with col_info:
    st.markdown(f"""
    <div style="padding:20px 0;">
        <div style="color:#8892A4;font-size:0.85rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
            Fleet Average PHI
        </div>
        <div style="color:#00B4D8;font-size:3rem;font-weight:900;">{avg_phi:.1f}%</div>
        <div style="margin-top:16px;color:#B0B8C8;font-size:0.9rem;line-height:1.7">
            <b>{crits}</b> well(s) are in <span style="color:#E74C3C">Critical</span> state.<br>
            <b>{warns}</b> well(s) require <span style="color:#F39C12">attention</span>.<br>
            <b>{healths}</b> well(s) operating <span style="color:#2ECC71">normally</span>.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Well Cards ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">Individual Well Status</div>', unsafe_allow_html=True)

for well in mock_wells:
    phi  = well['phi']
    stat = well['status']
    if phi >= 80:   bar_color, badge_cls = "#2ECC71", "badge-healthy"
    elif phi >= 60: bar_color, badge_cls = "#00B4D8", "badge-monitor"
    elif phi >= 40: bar_color, badge_cls = "#F39C12", "badge-warning"
    else:           bar_color, badge_cls = "#E74C3C", "badge-critical"

    anim_cls = "critical-pulse" if stat == 'Critical' else ""

    with st.container():
        st.markdown(f"""
        <div class="well-card {anim_cls}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
                <div>
                    <div style="font-size:1.3rem;font-weight:800;color:#E8EAF6">🛢️ {well['well_id']}</div>
                    <div style="color:#8892A4;font-size:0.82rem;margin-top:2px">Last Updated: {well.get('last_update', 'N/A')}</div>
                </div>
                <span class="badge {badge_cls}">{stat}</span>
            </div>
            <div style="margin-top:16px;display:flex;gap:32px;flex-wrap:wrap">
                <div>
                    <div style="color:#8892A4;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px">Health Index</div>
                    <div style="color:{bar_color};font-size:1.8rem;font-weight:900">{phi:.1f}%</div>
                </div>
                <div>
                    <div style="color:#8892A4;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px">RUL Estimate</div>
                    <div style="color:#E8EAF6;font-size:1.8rem;font-weight:900">{well['rul']} <span style="font-size:1rem">days</span></div>
                </div>
                <div>
                    <div style="color:#8892A4;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px">Predicted State</div>
                    <div style="color:#E8EAF6;font-size:1.4rem;font-weight:700">{well['label']}</div>
                </div>
            </div>
            <div style="margin-top:14px;background:rgba(0,0,0,0.25);border-radius:6px;height:8px;overflow:hidden">
                <div style="width:{phi}%;height:100%;background:{bar_color};border-radius:6px;transition:width 0.8s ease"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"🔍 Detailed Analysis for {well['well_id']}"):
            gc, pc = st.columns(2)
            with gc:
                st.plotly_chart(phi_gauge(phi, stat), width='stretch', config={'displayModeBar': False})
            with pc:
                from ui.components.charts import probability_donut
                st.plotly_chart(probability_donut(well['probs']), width='stretch', config={'displayModeBar': False})

st.markdown("""
<div style="text-align:center;color:#5A6478;font-size:0.8rem;padding:30px 0 10px 0;">
    Use <b>Upload Dataset</b> to load your sensor export and populate this dashboard with real data.
</div>
""", unsafe_allow_html=True)


