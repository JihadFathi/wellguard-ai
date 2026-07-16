"""
WellGuard AI - Page 2: Upload Dataset
"""
import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.charts import load_css, phi_trend_chart, sensor_trend_chart

st.set_page_config(page_title="Upload Dataset | WellGuard AI", page_icon="📁", layout="wide")
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
    <h1 style="color:#E8EAF6;font-size:2rem;font-weight:800;margin:0;">📁 Upload Sensor Dataset</h1>
    <p style="color:#8892A4;margin-top:4px">Upload your ESP sensor export file for batch analysis.</p>
</div>
""", unsafe_allow_html=True)

# ─── Upload Area ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">📤 File Upload</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drag & drop your sensor export file here",
    type=['xlsx', 'csv', 'xls'],
    help="Supports: Excel (.xlsx, .xls) and CSV (.csv) formats. Expected columns: Timestamp, Motor_Temperature, Motor_Current, Discharge_Pressure, Intake_Pressure, etc.",
    label_visibility='visible'
)

st.markdown("""
<div style="background:rgba(0,180,216,0.06);border:1px dashed rgba(0,180,216,0.3);border-radius:12px;padding:14px 18px;margin-top:8px">
    <div style="color:#00B4D8;font-size:0.85rem;font-weight:600;margin-bottom:6px">📋 Expected File Format</div>
    <div style="color:#8892A4;font-size:0.82rem;line-height:1.8">
        • <b style="color:#B0B8C8">Timestamp</b> — datetime column (UTC or local)<br>
        • <b style="color:#B0B8C8">Motor_Temperature</b> — Motor winding temperature (°F)<br>
        • <b style="color:#B0B8C8">Motor_Current</b> — Motor current draw (Amperes)<br>
        • <b style="color:#B0B8C8">Discharge_Pressure</b> — Pump discharge pressure (psia)<br>
        • <b style="color:#B0B8C8">Intake_Pressure</b> — Pump intake pressure (psia)<br>
        • <b style="color:#B0B8C8">Event</b> (optional) — Event classification column
    </div>
</div>
""", unsafe_allow_html=True)

if uploaded_file is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚙️ Processing</div>', unsafe_allow_html=True)

    progress = st.progress(0, text="Reading file...")
    time.sleep(0.3)

    # ─── Load File ────────────────────────────────────────────────────
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            xl = pd.ExcelFile(uploaded_file)
            sheet = xl.sheet_names[0]
            df_raw = xl.parse(sheet)
            if 'Motor_Temperature' not in df_raw.columns and 'Motor_Current' not in df_raw.columns:
                df_raw = xl.parse(sheet, header=1)

        progress.progress(25, text="File loaded. Validating schema...")
        time.sleep(0.3)

        # ─── Schema Validation ────────────────────────────────────────
        required_cols = ['Motor_Temperature', 'Motor_Current', 'Discharge_Pressure', 'Intake_Pressure']
        # Try to find timestamp column
        ts_candidates = [c for c in df_raw.columns if 'time' in c.lower() or 'date' in c.lower() or 'timestamp' in str(c).lower()]

        missing = [c for c in required_cols if c not in df_raw.columns]

        if missing:
            st.warning(f"⚠️ The following expected columns were not found: `{', '.join(missing)}`")
            st.info("The file may use different column names. Proceeding with available columns for preview...")

        progress.progress(50, text="Cleaning and processing data...")
        time.sleep(0.3)

        # ─── Run preprocessing pipeline ───────────────────────────────
        try:
            from preprocessing.cleaner import clean_data
            from preprocessing.feature_engineer import engineer_features

            df_clean = clean_data(df_raw)
            df_feat  = engineer_features(df_clean)
            progress.progress(75, text="Running AI predictions...")
            time.sleep(0.3)

            # Try to run predictor
            try:
                from prediction.predictor import PumpPredictor
                predictor = PumpPredictor()
                df_results = predictor.predict_batch(df_feat)
                progress.progress(100, text="✅ Complete!")

                # Store results in session state
                avg_phi = df_results['health_index'].mean()
                last_phi = df_results['health_index'].iloc[-1]
                last_label = df_results['predicted_label'].iloc[-1]
                last_rul   = df_results['rul_days'].iloc[-1]
                last_status = df_results['health_status'].iloc[-1]
                last_action = df_results['action_recommendation'].iloc[-1]

                st.session_state['df_results']   = df_results
                st.session_state['df_clean']     = df_clean
                st.session_state['last_phi']     = float(last_phi)
                st.session_state['last_label']   = last_label
                st.session_state['last_rul']     = int(last_rul)
                st.session_state['last_status']  = last_status
                st.session_state['last_action']  = last_action
                st.session_state['well_id']      = 'B-167'

            except FileNotFoundError:
                progress.progress(100, text="⚠️ No trained model found — showing data preview only.")
                st.warning("⚠️ No trained model found in `models/trained/`. Run `training/trainer.py` first.")
                df_results = df_feat.copy()
                st.session_state['df_clean'] = df_clean

        except Exception as e:
            progress.progress(100, text="⚠️ Preprocessing error — showing raw preview.")
            st.warning(f"Preprocessing pipeline error: {e}")
            df_results = df_raw.copy()

        # ─── File Preview ─────────────────────────────────────────────
        st.success(f"✅ File processed: **{uploaded_file.name}** | **{len(df_raw):,}** rows × **{df_raw.shape[1]}** columns")

        st.markdown('<div class="section-header">📋 Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(
            df_raw.head(50).astype(str).style.set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#0D1F3C'), ('color', '#00B4D8')]},
                {'selector': 'td', 'props': [('background-color', '#071020'), ('color', '#E8EAF6')]},
            ]),
            width='stretch', height=280
        )

        st.markdown(f"""
        <div style="display:flex;gap:20px;flex-wrap:wrap;margin:12px 0">
            <div style="background:rgba(13,31,60,0.8);border:1px solid rgba(0,180,216,0.2);border-radius:8px;padding:12px 20px">
                <span style="color:#8892A4;font-size:0.8rem">Total Rows</span><br>
                <span style="color:#00B4D8;font-weight:700;font-size:1.2rem">{len(df_raw):,}</span>
            </div>
            <div style="background:rgba(13,31,60,0.8);border:1px solid rgba(0,180,216,0.2);border-radius:8px;padding:12px 20px">
                <span style="color:#8892A4;font-size:0.8rem">Columns</span><br>
                <span style="color:#00B4D8;font-weight:700;font-size:1.2rem">{df_raw.shape[1]}</span>
            </div>
            <div style="background:rgba(13,31,60,0.8);border:1px solid rgba(0,180,216,0.2);border-radius:8px;padding:12px 20px">
                <span style="color:#8892A4;font-size:0.8rem">Missing Values</span><br>
                <span style="color:#F39C12;font-weight:700;font-size:1.2rem">{df_raw.isnull().sum().sum():,}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── Sensor Trend Charts ──────────────────────────────────────
        if 'df_clean' in st.session_state:
            df_c = st.session_state['df_clean']
            sensor_cols = [c for c in ['Motor_Temperature', 'Motor_Current', 'Discharge_Pressure', 'Intake_Pressure'] if c in df_c.columns]

            if 'Timestamp' in df_c.columns and len(sensor_cols) > 0:
                st.markdown('<div class="section-header">📈 Sensor Trend Overview</div>', unsafe_allow_html=True)
                sensor_data = {col: df_c[col].tolist() for col in sensor_cols}
                fig = sensor_trend_chart(df_c['Timestamp'].tolist(), sensor_data)
                st.plotly_chart(fig, width='stretch', config={'displayModeBar': True}, key="upload_trend")

        # ─── Navigate to analysis ─────────────────────────────────────
        if 'df_results' in st.session_state:
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("🎯 Data processed successfully! Navigate to **Analysis Results** for full predictions.")
            col_btn = st.columns([1, 1, 3])
            with col_btn[0]:
                if st.button("🔬 View Analysis", type="primary", width='stretch'):
                    st.switch_page("pages/4_analysis.py")

    except Exception as e:
        progress.progress(100, text="❌ Error")
        st.error(f"❌ Failed to read file: {e}")
        st.info("Please ensure the file is a valid Excel or CSV sensor export.")


