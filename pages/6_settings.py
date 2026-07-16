"""
WellGuard AI - Page 6: Settings & Configuration
"""
import streamlit as st
import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.charts import load_css

st.set_page_config(page_title="Settings | WellGuard AI", page_icon="⚙️", layout="wide")
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
    <h1 style="color:#E8EAF6;font-size:2rem;font-weight:800;margin:0;">⚙️ Settings & Configuration</h1>
    <p style="color:#8892A4;margin-top:4px">Customize alert thresholds, well parameters, and system configuration.</p>
</div>
""", unsafe_allow_html=True)

# ─── Tab Layout ───────────────────────────────────────────────────────
tab_thresh, tab_well, tab_model, tab_system = st.tabs([
    "🔔 Alert Thresholds",
    "🛢️ Well Parameters",
    "🤖 Model Configuration",
    "⚙️ System Settings"
])

# ─── Tab 1: Alert Thresholds ──────────────────────────────────────────
with tab_thresh:
    st.markdown('<div class="section-header">🌡️ Temperature Thresholds</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        temp_warn = st.slider(
            "Warning Temperature (°F)",
            min_value=150, max_value=250, step=5,
            value=st.session_state.get('thresh_temp_warn', 180),
            help="Motor temperature level that triggers a P2-High warning alert"
        )
        st.session_state['thresh_temp_warn'] = temp_warn
    with col_t2:
        temp_crit = st.slider(
            "Critical Temperature (°F)",
            min_value=180, max_value=300, step=5,
            value=st.session_state.get('thresh_temp_crit', 210),
            help="Motor temperature level that triggers a P1-Urgent critical alert"
        )
        st.session_state['thresh_temp_crit'] = temp_crit

    st.markdown('<div class="section-header">⚡ Current Thresholds</div>', unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        baseline_current = st.number_input(
            "Baseline Motor Current (A)",
            min_value=5.0, max_value=100.0, step=0.1,
            value=st.session_state.get('thresh_baseline_current', 32.3),
            help="Normal operating motor current for this well (Amperes)"
        )
        st.session_state['thresh_baseline_current'] = baseline_current
    with col_c2:
        current_pct = st.slider(
            "High Current Alert Threshold (%)",
            min_value=105, max_value=150, step=5,
            value=st.session_state.get('thresh_current_pct', 120),
            help="Percentage above baseline current that triggers an alert"
        )
        st.session_state['thresh_current_pct'] = current_pct
    st.markdown(f"""
    <div style="background:rgba(0,180,216,0.06);border-radius:8px;padding:10px 14px;color:#8892A4;font-size:0.85rem">
        Alert triggers when current exceeds: <b style="color:#00B4D8">{baseline_current * current_pct / 100:.1f} A</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📊 PHI Threshold Bands</div>', unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        phi_warn_lower = st.number_input("Warning PHI Lower Bound", min_value=20, max_value=70, value=40)
    with col_p2:
        phi_monitor_lower = st.number_input("Monitor PHI Lower Bound", min_value=40, max_value=85, value=60)
    with col_p3:
        phi_healthy_lower = st.number_input("Healthy PHI Lower Bound", min_value=60, max_value=95, value=80)

    st.markdown("""
    <div style="background:rgba(13,31,60,0.8);border:1px solid rgba(0,180,216,0.2);border-radius:12px;padding:16px;margin-top:12px">
        <div style="display:flex;gap:0;border-radius:6px;overflow:hidden;height:24px">
            <div style="flex:{};background:#E74C3C;display:flex;align-items:center;justify-content:center;color:white;font-size:0.7rem;font-weight:700">Critical</div>
            <div style="flex:{};background:#F39C12;display:flex;align-items:center;justify-content:center;color:white;font-size:0.7rem;font-weight:700">Warning</div>
            <div style="flex:{};background:#00B4D8;display:flex;align-items:center;justify-content:center;color:white;font-size:0.7rem;font-weight:700">Monitor</div>
            <div style="flex:{};background:#2ECC71;display:flex;align-items:center;justify-content:center;color:white;font-size:0.7rem;font-weight:700">Healthy</div>
            <div style="flex:5;background:rgba(46,204,113,0.7);display:flex;align-items:center;justify-content:center;color:white;font-size:0.7rem;font-weight:700">Excellent</div>
        </div>
    </div>
    """.format(phi_warn_lower, phi_monitor_lower - phi_warn_lower, phi_healthy_lower - phi_monitor_lower, 95 - phi_healthy_lower), unsafe_allow_html=True)

# ─── Tab 2: Well Parameters ───────────────────────────────────────────
with tab_well:
    st.markdown('<div class="section-header">🛢️ Well B-167 Design Parameters</div>', unsafe_allow_html=True)
    st.info("These values are sourced from the B-167 ESP Design Sheet (8-DEC-2024). They are used as constant baselines since only 4 production test records are available.")

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        water_cut = st.slider("Water Cut (%)", 0, 100, 63, help="Water cut from production test data")
        gor = st.number_input("GOR (scf/stb)", min_value=0, max_value=5000, value=330, help="Gas-to-Oil Ratio")
        sbhp = st.number_input("SBHP (psig)", min_value=500, max_value=5000, value=2100, help="Static Bottom Hole Pressure")
    with col_w2:
        pump_type = st.text_input("Pump Type", value="S2000N", help="ESP pump model designation")
        hp = st.number_input("Motor HP", min_value=5, max_value=1000, value=150, help="Motor rated horsepower")
        voltage = st.number_input("Supply Voltage (V)", min_value=100, max_value=5000, value=480)

    st.markdown("<br>", unsafe_allow_html=True)
    col_save, _ = st.columns([1, 4])
    with col_save:
        if st.button("💾 Save Well Parameters", type="primary", width='stretch'):
            st.session_state['well_params'] = {
                'water_cut': water_cut, 'gor': gor, 'sbhp': sbhp,
                'pump_type': pump_type, 'hp': hp, 'voltage': voltage
            }
            st.success("✅ Well parameters saved to session.")

# ─── Tab 3: Model Configuration ───────────────────────────────────────
with tab_model:
    st.markdown('<div class="section-header">🤖 Model Settings</div>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        critical_days = st.slider(
            "Critical Label Window (days)",
            min_value=1, max_value=14, value=3,
            help="Days before shutdown to label as 'Critical'. Default: 3 days for B-167."
        )
        warning_days = st.slider(
            "Warning Label Window (days)",
            min_value=3, max_value=60, value=10,
            help="Days before shutdown to label as 'Warning'. Default: 10 days for B-167."
        )
    with col_m2:
        phi_model_weight = st.slider(
            "PHI — Model Score Weight (%)",
            min_value=20, max_value=80, value=60,
            help="Weight of model classification probabilities in PHI calculation."
        )
        phi_sensor_weight = st.slider(
            "PHI — Sensor Deviation Weight (%)",
            min_value=10, max_value=60, value=25,
            help="Weight of normalized sensor z-scores in PHI calculation."
        )
        phi_trend_weight = 100 - phi_model_weight - phi_sensor_weight
        st.metric("PHI — Trend Score Weight (%)", phi_trend_weight)

    if phi_trend_weight < 0:
        st.error("⚠️ Weight sum exceeds 100%. Reduce Model or Sensor weights.")
    else:
        st.success(f"✅ Total weight: {phi_model_weight + phi_sensor_weight + phi_trend_weight}%")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Retrain Model with New Labels", type="secondary"):
        try:
            with st.spinner("Training model... this may take a minute."):
                import subprocess
                result = subprocess.run(
                    ["python", os.path.join(PROJECT_ROOT, "training", "trainer.py")],
                    capture_output=True, text=True, timeout=300
                )
            if result.returncode == 0:
                st.success("✅ Model retrained successfully!")
                st.code(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            else:
                st.error(f"❌ Training failed:\n{result.stderr[-1000:]}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ─── Tab 4: System Settings ───────────────────────────────────────────
with tab_system:
    st.markdown('<div class="section-header">📂 File Paths</div>', unsafe_allow_html=True)

    config_dir = os.path.join(PROJECT_ROOT, 'models', 'configs')
    trained_dir = os.path.join(PROJECT_ROOT, 'models', 'trained')
    reports_dir = os.path.join(PROJECT_ROOT, 'reports', 'generated')

    model_exists  = os.path.exists(os.path.join(trained_dir, 'best_model.pkl'))
    scaler_exists = os.path.exists(os.path.join(trained_dir, 'scaler.pkl'))
    config_exists = os.path.exists(os.path.join(config_dir, 'model_configs.json'))

    st.markdown(f"""
    <div style="background:rgba(13,31,60,0.9);border:1px solid rgba(0,180,216,0.2);border-radius:12px;padding:16px 20px;">
        <div style="display:grid;gap:10px">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="color:#8892A4;font-size:0.88rem">Trained Model (best_model.pkl)</span>
                <span style="color:{'#2ECC71' if model_exists else '#E74C3C'};font-weight:700">
                    {'✅ Found' if model_exists else '❌ Not Found'}
                </span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="color:#8892A4;font-size:0.88rem">Feature Scaler (scaler.pkl)</span>
                <span style="color:{'#2ECC71' if scaler_exists else '#E74C3C'};font-weight:700">
                    {'✅ Found' if scaler_exists else '❌ Not Found'}
                </span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="color:#8892A4;font-size:0.88rem">Model Config (model_configs.json)</span>
                <span style="color:{'#2ECC71' if config_exists else '#E74C3C'};font-weight:700">
                    {'✅ Found' if config_exists else '❌ Not Found'}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not model_exists:
        st.warning("""
        ⚠️ No trained model found. To train the model:
        ```bash
        $env:PYTHONHOME=$null; & "C:\\ProgramData\\anaconda3\\python.exe" training/trainer.py
        ```
        Run this from the `Project/` directory.
        """)

    if config_exists:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔑 Model Feature Configuration</div>', unsafe_allow_html=True)
        try:
            with open(os.path.join(config_dir, 'model_configs.json'), 'r') as f:
                config = json.load(f)
            st.json(config)
        except Exception as e:
            st.error(f"Could not load config: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🗑️ Session Management</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🗑️ Clear All Session Data", type="secondary", width='stretch'):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ Session cleared.")
            st.rerun()
    with col_s2:
        session_keys = list(st.session_state.keys())
        st.markdown(f"""
        <div style="background:rgba(13,31,60,0.6);border-radius:8px;padding:10px 14px;color:#8892A4;font-size:0.82rem">
            Active session keys: <b style="color:#00B4D8">{len(session_keys)}</b><br>
            {', '.join(session_keys[:8])}{'...' if len(session_keys) > 8 else ''}
        </div>
        """, unsafe_allow_html=True)


