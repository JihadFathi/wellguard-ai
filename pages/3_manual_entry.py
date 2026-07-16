"""
WellGuard AI - Page 3: Manual Sensor Entry
"""
import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.charts import load_css, render_kpi_card

st.set_page_config(page_title="Manual Entry | WellGuard AI", page_icon="✏️", layout="wide")
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
    <h1 style="color:#E8EAF6;font-size:2rem;font-weight:800;margin:0;">✏️ Manual Sensor Entry</h1>
    <p style="color:#8892A4;margin-top:4px">Enter current sensor readings manually to run a quick health prediction.</p>
</div>
""", unsafe_allow_html=True)

# ─── Quick-Fill Button ────────────────────────────────────────────────
col_fill, col_fill2 = st.columns([1, 4])
with col_fill:
    quick_fill = st.button("⚡ Quick Fill (B-167 Baseline)", type="secondary", width='stretch')
with col_fill2:
    frozen_fill = st.button("🧊 Quick Fill (Frozen Sensor Scenario)", type="secondary", width='stretch')

# Defaults
defaults = {
    'well_id': 'B-167',
    'motor_temp': 210.0,
    'motor_current': 32.3,
    'discharge_pressure': 2395.8,
    'intake_pressure': 837.8,
    'hours_since_restart': 240.0,
    'temp_trend': 0.0,
    'current_trend': 0.0,
    'pressure_trend': 0.0,
    'intake_trend': 0.0,
}

if quick_fill:
    for k, v in defaults.items():
        st.session_state[f'input_{k}'] = v
    st.success("✅ Baseline values for Well B-167 loaded.")

if frozen_fill:
    frozen = dict(defaults)
    frozen.update({
        'discharge_pressure': 944.4,
        'intake_pressure': 925.1,
        'motor_temp': 174.7,
        'motor_current': 32.0,
    })
    for k, v in frozen.items():
        st.session_state[f'input_{k}'] = v
    st.warning("🧊 Frozen sensor scenario loaded — simulates telemetry failure (DEt event).")

# ─── Input Form ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">📡 Current Sensor Readings</div>', unsafe_allow_html=True)

with st.form("manual_entry_form", clear_on_submit=False):
    c_info, c_sensors = st.columns([1, 2])

    with c_info:
        st.markdown("**Well Information**")
        well_id = st.text_input(
            "Well Identifier",
            value=st.session_state.get('input_well_id', 'B-167'),
            help="Enter the well identifier (e.g., B-167)"
        )
        hours_since_restart = st.number_input(
            "Hours Since Last Restart",
            min_value=0.0, max_value=9000.0, step=1.0,
            value=float(st.session_state.get('input_hours_since_restart', 240.0)),
            help="Cumulative hours the pump has been running since last restart"
        )

    with c_sensors:
        st.markdown("**Primary Sensor Values**")
        col_a, col_b = st.columns(2)
        with col_a:
            motor_temp = st.number_input(
                "Motor Temperature (°F)",
                min_value=50.0, max_value=350.0, step=0.1,
                value=float(st.session_state.get('input_motor_temp', 210.0)),
                help="Downhole motor winding temperature"
            )
            motor_current = st.number_input(
                "Motor Current (A)",
                min_value=0.0, max_value=100.0, step=0.1,
                value=float(st.session_state.get('input_motor_current', 32.3)),
                help="Motor current draw in Amperes"
            )
        with col_b:
            discharge_pressure = st.number_input(
                "Discharge Pressure (psia)",
                min_value=0.0, max_value=10000.0, step=1.0,
                value=float(st.session_state.get('input_discharge_pressure', 2395.8)),
                help="Pump discharge pressure in psia"
            )
            intake_pressure = st.number_input(
                "Intake Pressure (psia)",
                min_value=0.0, max_value=5000.0, step=1.0,
                value=float(st.session_state.get('input_intake_pressure', 837.8)),
                help="Pump intake pressure in psia"
            )

    st.markdown('<div class="section-header">📉 Trend Indicators (per hour)</div>', unsafe_allow_html=True)
    st.caption("Enter the rate of change per hour for each sensor (positive = rising, negative = falling).")

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        temp_trend = st.number_input(
            "Temp Trend (°F/hr)",
            min_value=-50.0, max_value=50.0, step=0.1,
            value=float(st.session_state.get('input_temp_trend', 0.0))
        )
    with col_t2:
        current_trend = st.number_input(
            "Current Trend (A/hr)",
            min_value=-20.0, max_value=20.0, step=0.01,
            value=float(st.session_state.get('input_current_trend', 0.0))
        )
    with col_t3:
        pressure_trend = st.number_input(
            "Discharge P Trend (psi/hr)",
            min_value=-500.0, max_value=500.0, step=0.5,
            value=float(st.session_state.get('input_pressure_trend', 0.0))
        )
    with col_t4:
        intake_trend = st.number_input(
            "Intake P Trend (psi/hr)",
            min_value=-500.0, max_value=500.0, step=0.5,
            value=float(st.session_state.get('input_intake_trend', 0.0))
        )

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🔬 Run Health Prediction", type="primary", width='stretch')

# ─── Prediction ───────────────────────────────────────────────────────
if submitted:
    sensor_values = {
        'Motor_Temperature': motor_temp,
        'Motor_Current': motor_current,
        'Discharge_Pressure': discharge_pressure,
        'Intake_Pressure': intake_pressure,
        'Hours_Since_Restart': hours_since_restart,
    }
    trend_features = {
        'Motor_Temperature': temp_trend,
        'Motor_Current': current_trend,
        'Discharge_Pressure': pressure_trend,
        'Intake_Pressure': intake_trend,
    }

    try:
        from prediction.predictor import PumpPredictor
        with st.spinner("🤖 Running AI analysis..."):
            predictor = PumpPredictor()
            result = predictor.predict_single(sensor_values, trend_features)

        # Store in session state for the analysis page
        st.session_state['manual_result']  = result
        st.session_state['manual_sensor']  = sensor_values
        st.session_state['manual_trend']   = trend_features
        st.session_state['well_id']        = well_id
        st.session_state['last_phi']       = result['health_index']
        st.session_state['last_label']     = result['label']
        st.session_state['last_rul']       = result['rul_days']
        st.session_state['last_status']    = result['status']
        st.session_state['last_action']    = result['action']

        # Quick summary
        phi    = result['health_index']
        label  = result['label']
        rul    = result['rul_days']
        status = result['status']

        if phi >= 80:   phi_color = "#2ECC71"
        elif phi >= 60: phi_color = "#00B4D8"
        elif phi >= 40: phi_color = "#F39C12"
        else:           phi_color = "#E74C3C"

        st.success("✅ Prediction complete!")
        st.markdown(f"""
        <div style="background:rgba(13,31,60,0.95);border:1px solid rgba(0,180,216,0.3);border-radius:16px;padding:24px;margin-top:12px">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px">
                <div>
                    <div style="color:#8892A4;font-size:0.8rem;letter-spacing:1px;text-transform:uppercase">Health Index</div>
                    <div style="color:{phi_color};font-size:3rem;font-weight:900">{phi:.1f}%</div>
                    <div style="color:#8892A4;font-size:0.85rem">Status: <b style="color:{phi_color}">{status}</b></div>
                </div>
                <div>
                    <div style="color:#8892A4;font-size:0.8rem;letter-spacing:1px;text-transform:uppercase">Predicted State</div>
                    <div style="color:#E8EAF6;font-size:2rem;font-weight:800">{label}</div>
                </div>
                <div>
                    <div style="color:#8892A4;font-size:0.8rem;letter-spacing:1px;text-transform:uppercase">Est. RUL</div>
                    <div style="color:#E8EAF6;font-size:2rem;font-weight:800">{rul} <span style="font-size:1rem">days</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 View Full Analysis →", type="primary"):
            st.switch_page("pages/4_analysis.py")

    except FileNotFoundError:
        st.error("❌ Trained model not found. Please run `training/trainer.py` first to train the model.")
    except Exception as e:
        st.error(f"❌ Prediction error: {e}")


