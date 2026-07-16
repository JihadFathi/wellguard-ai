"""
WellGuard AI - Page 4: Analysis Results
"""
import streamlit as st
import sys
import os
import pandas as pd
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.charts import (
    load_css, phi_gauge, probability_donut,
    phi_trend_chart, render_recommendation_card, render_sensor_table
)

st.set_page_config(page_title="Analysis Results | WellGuard AI", page_icon="🔬", layout="wide")
load_css()

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 10px 0;">
        <div style="font-size:2rem">🛢️</div>
        <div style="font-size:1.3rem;font-weight:800;color:#00B4D8;">WellGuard AI</div>
    </div>
    <hr style="border-color:rgba(0,180,216,0.2);">
    """, unsafe_allow_html=True)
    st.page_link("streamlit_app.py",                    label="🏠  Home")
    st.page_link("pages/1_dashboard.py",       label="📊  Wells Overview")
    st.page_link("pages/2_upload.py",          label="📁  Upload Dataset")
    st.page_link("pages/3_manual_entry.py",    label="✏️  Manual Entry")
    st.page_link("pages/4_analysis.py",        label="🔬  Analysis Results")
    st.page_link("pages/5_history.py",         label="🕰️  History")
    st.page_link("pages/6_settings.py",        label="⚙️  Settings")

st.markdown("""
<div style="padding:24px 0 16px 0;">
    <h1 style="color:#E8EAF6;font-size:2rem;font-weight:800;margin:0;">🔬 Analysis Results</h1>
    <p style="color:#8892A4;margin-top:4px">Detailed AI-powered health assessment and recommendations.</p>
</div>
""", unsafe_allow_html=True)

# ─── Check for available results ──────────────────────────────────────
has_manual = 'manual_result' in st.session_state
has_batch  = 'df_results' in st.session_state

if not has_manual and not has_batch:
    st.info("ℹ️ No analysis results yet. Please use **Upload Dataset** or **Manual Entry** to run a prediction first.")
    col_u, col_m = st.columns(2)
    with col_u:
        if st.button("📁 Upload Dataset", width='stretch'):
            st.switch_page("pages/2_upload.py")
    with col_m:
        if st.button("✏️ Manual Entry", width='stretch'):
            st.switch_page("pages/3_manual_entry.py")
    st.stop()

# ─── Determine Source ─────────────────────────────────────────────────
mode_options = []
if has_manual: mode_options.append("Manual Entry Result")
if has_batch:  mode_options.append("Batch Upload Result")

if len(mode_options) > 1:
    selected_mode = st.radio("📌 Select Analysis Source:", mode_options, horizontal=True)
else:
    selected_mode = mode_options[0]

well_id = st.session_state.get('well_id', 'B-167')

if selected_mode == "Manual Entry Result":
    result         = st.session_state['manual_result']
    sensor_values  = st.session_state['manual_sensor']
    trend_features = st.session_state['manual_trend']
    phi    = result['health_index']
    label  = result['label']
    rul    = result['rul_days']
    status = result['status']
    action = result['action']
    probs  = result['probabilities']
    primary_rec  = result['primary_recommendation']
    all_recs     = result.get('all_triggered_recommendations', [primary_rec])
    history_phi  = None  # No history for single prediction

else:  # Batch
    df_results  = st.session_state['df_results']
    df_clean    = st.session_state.get('df_clean', pd.DataFrame())

    # Use last row as the "current" prediction
    last = df_results.iloc[-1]
    phi    = st.session_state.get('last_phi', float(last.get('health_index', 0)))
    label  = st.session_state.get('last_label', last.get('predicted_label', 'Unknown'))
    rul    = st.session_state.get('last_rul', int(last.get('rul_days', 0)))
    status = st.session_state.get('last_status', last.get('health_status', 'Unknown'))
    action = st.session_state.get('last_action', 'Continue Monitoring')
    probs  = [0.6, 0.3, 0.1]  # approximation if not stored

    sensor_values = {
        'Motor_Temperature':  float(last.get('Motor_Temperature', 0)),
        'Motor_Current':      float(last.get('Motor_Current', 0)),
        'Discharge_Pressure': float(last.get('Discharge_Pressure', 0)),
        'Intake_Pressure':    float(last.get('Intake_Pressure', 0)),
    }
    trend_features = {
        'Motor_Temperature':  float(last.get('Temp_Trend', 0)),
        'Discharge_Pressure': float(last.get('Pressure_Trend', 0)),
        'Motor_Current':      float(last.get('Current_Trend', 0)),
        'Intake_Pressure':    0.0,
    }

    # Build recommendation for display
    from prediction.recommendation_engine import get_recommendations
    primary_rec, all_recs = get_recommendations(sensor_values, trend_features)
    if not all_recs:
        all_recs = [primary_rec]

    # PHI history
    if 'health_index' in df_results.columns:
        history_phi = df_results['health_index'].tolist()
    else:
        history_phi = None

# ─── COLOR CONFIG ─────────────────────────────────────────────────────
phi_color = "#2ECC71" if phi >= 80 else ("#00B4D8" if phi >= 60 else ("#F39C12" if phi >= 40 else "#E74C3C"))

# ─── Section 1: Key Metrics ────────────────────────────────────────────
st.markdown('<div class="section-header">⚡ Current Health Snapshot</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💉</div>
        <div class="kpi-value" style="color:{phi_color};">{phi:.1f}%</div>
        <div class="kpi-label">Health Index (PHI)</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📡</div>
        <div class="kpi-value" style="font-size:1.6rem;color:#E8EAF6;">{label}</div>
        <div class="kpi-label">Predicted State</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    rul_color = "#2ECC71" if rul >= 30 else ("#F39C12" if rul >= 7 else "#E74C3C")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-value" style="color:{rul_color};">{rul}</div>
        <div class="kpi-label">Remaining Useful Life (days)</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🛢️</div>
        <div class="kpi-value" style="font-size:1.6rem;color:#E8EAF6;">{well_id}</div>
        <div class="kpi-label">Well Identifier</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 2: PHI Gauge + Probability Donut ─────────────────────────
st.markdown('<div class="section-header">📊 Health Visualization</div>', unsafe_allow_html=True)
col_gauge, col_donut = st.columns(2, gap="medium")
with col_gauge:
    st.plotly_chart(phi_gauge(phi, status), width='stretch', config={'displayModeBar': False}, key="analysis_gauge")
with col_donut:
    st.plotly_chart(probability_donut(probs), width='stretch', config={'displayModeBar': False}, key="analysis_donut")

# ─── Section 3: PHI History (batch only) ─────────────────────────────
if history_phi and len(history_phi) > 5:
    st.markdown('<div class="section-header">📈 PHI Historical Trend</div>', unsafe_allow_html=True)
    if 'df_results' in st.session_state and 'Timestamp' in st.session_state['df_results'].columns:
        ts = st.session_state['df_results']['Timestamp'].tolist()
    else:
        import numpy as np
        ts = list(range(len(history_phi)))
    fig_trend = phi_trend_chart(ts, history_phi)
    st.plotly_chart(fig_trend, width='stretch', config={'displayModeBar': True}, key="analysis_trend")

# ─── Section 4: Sensor Status Table ───────────────────────────────────
st.markdown('<div class="section-header">📟 Sensor Status</div>', unsafe_allow_html=True)
render_sensor_table(sensor_values, trend_features)

# ─── Section 5: Recommendations ──────────────────────────────────────
st.markdown('<div class="section-header">🔔 Maintenance Recommendations</div>', unsafe_allow_html=True)
for rec in all_recs:
    render_recommendation_card(rec)

# ─── Section 6: PDF Report Export ────────────────────────────────────
st.markdown('<div class="section-header">📄 Export PDF Report</div>', unsafe_allow_html=True)
st.markdown("""
<div style="background:rgba(0,180,216,0.06);border:1px solid rgba(0,180,216,0.2);border-radius:12px;padding:16px 20px;margin-bottom:16px">
    <div style="color:#00B4D8;font-weight:600;margin-bottom:6px">📋 Report Contents</div>
    <div style="color:#8892A4;font-size:0.85rem;line-height:1.8">
        The generated PDF report includes:<br>
        • Cover page with well information and diagnosis summary<br>
        • Executive summary with primary recommendations<br>
        • Health Dashboard with PHI gauge and probability charts<br>
        • Real-time sensor values vs baseline analysis table<br>
        • Key AI findings and anomaly detection results<br>
        • Detailed maintenance recommendations with priority levels<br>
        • Glossary and model confidence metrics
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("📄 Generate & Download PDF Report", type="primary", width='content'):
    try:
        from prediction.report_generator import PDFReportGenerator
        import base64

        with st.spinner("🔧 Generating PDF report..."):
            result_pkg = {
                'health_index': phi,
                'label': label,
                'status': status,
                'rul_days': rul,
                'action': action,
                'probabilities': probs,
                'primary_recommendation': primary_rec,
                'all_triggered_recommendations': all_recs
            }
            gen = PDFReportGenerator()
            pdf_path = gen.build_pdf(well_id, result_pkg, sensor_values, trend_features)

        # Read and offer download
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        st.success(f"✅ Report generated: `{os.path.basename(pdf_path)}`")
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf",
            type="primary"
        )

        # Save to history
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        st.session_state['history'].append({
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'well_id': well_id,
            'phi': phi,
            'label': label,
            'rul': rul,
            'status': status,
            'source': selected_mode,
            'report': os.path.basename(pdf_path)
        })

    except ImportError:
        st.error("❌ ReportLab library not installed. Run: `pip install reportlab`")
    except Exception as e:
        st.error(f"❌ Report generation failed: {e}")


