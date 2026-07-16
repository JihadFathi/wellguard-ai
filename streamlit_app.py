"""
Predictive maintenance of Electrical submersible pump using AI
Main Single-Page Streamlit Application
"""
import streamlit as st
import os
import sys
import pandas as pd
import time
import datetime

# ── Path setup ────────────────────────────────────────────────────────
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

# ── Import UI Components ──────────────────────────────────────────────
from ui.components.charts import (
    load_css, render_kpi_card, render_status_badge,
    phi_gauge, probability_donut, phi_trend_chart,
    sensor_trend_chart, render_recommendation_card, render_sensor_table
)

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="صيانة المضخات الغاطسة بالذكاء الاصطناعي",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px 0;">
        <div style="font-size:2.5rem">🛢️</div>
        <div style="font-size:1.2rem;font-weight:800;color:#00B4D8;line-height:1.4;">صيانة المضخات الغاطسة<br>بالذكاء الاصطناعي</div>
        <div style="font-size:0.75rem;color:#8892A4;letter-spacing:1px;margin-top:8px;">
            Predictive maintenance of ESP
        </div>
    </div>
    <hr style="border-color:rgba(0,180,216,0.2);margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="color:#8892A4;font-size:0.9rem;text-align:right;line-height:1.7;">
        هذا النظام يتيح لك التنبؤ بأعطال المضخات الغاطسة (ESP) مسبقاً باستخدام الذكاء الاصطناعي.<br>
        قم برفع ملف البيانات (Excel أو CSV) وسيقوم النظام فوراً بـ:
        <ul>
            <li>تنظيف البيانات</li>
            <li>استخراج الميزات</li>
            <li>توقع حالة المضخة</li>
            <li>إعطاء توصيات للصيانة</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="border-color:rgba(0,180,216,0.2);margin:12px 0;">
    <div style="color:#8892A4;font-size:0.75rem;text-align:center;">
        الإصدار 1.0 &nbsp;|&nbsp; بئر B-167
    </div>
    """, unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:20px 20px 40px 20px;">
    <h1 style="font-size:2.5rem;font-weight:900;color:#E8EAF6;margin:0;">
        التنبؤ بأعطال <span style="color:#00B4D8;">المضخات الغاطسة</span> بالذكاء الاصطناعي
    </h1>
    <p style="color:#8892A4;font-size:1.1rem;max-width:600px;margin:16px auto 0 auto;line-height:1.7;">
        نظام ذكي يعتمد على نماذج التعلم الآلي (Random Forest & LightGBM) لتحليل بيانات الحساسات والتنبؤ باحتمالية تعطل المضخة قبل حدوثها لتوفير تكاليف الصيانة.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Upload Section ────────────────────────────────────────────────────
st.markdown('<div class="section-header">📤 رفع ملف بيانات الحساسات</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "اسحب وأفلت ملف بيانات المضخة هنا",
    type=['xlsx', 'csv', 'xls'],
    label_visibility='collapsed'
)

st.markdown("""
<div style="background:rgba(0,180,216,0.06);border:1px dashed rgba(0,180,216,0.3);border-radius:12px;padding:14px 18px;margin-top:8px;">
    <div style="color:#00B4D8;font-size:0.9rem;font-weight:600;margin-bottom:6px">📋 الأعمدة المطلوبة في الملف</div>
    <div style="color:#8892A4;font-size:0.85rem;line-height:1.8">
        • <b style="color:#B0B8C8">Timestamp</b> — عمود الوقت والتاريخ<br>
        • <b style="color:#B0B8C8">Motor_Temperature</b> — حرارة المحرك (°F)<br>
        • <b style="color:#B0B8C8">Motor_Current</b> — تيار المحرك (Amperes)<br>
        • <b style="color:#B0B8C8">Discharge_Pressure</b> — ضغط التفريغ (psia)<br>
        • <b style="color:#B0B8C8">Intake_Pressure</b> — ضغط السحب (psia)
    </div>
</div>
""", unsafe_allow_html=True)

if uploaded_file is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚙️ جاري التحليل...</div>', unsafe_allow_html=True)

    progress = st.progress(0, text="قراءة الملف...")
    time.sleep(0.3)

    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            xl = pd.ExcelFile(uploaded_file)
            sheet = xl.sheet_names[0]
            # Try parsing with header on row 0 first
            df_raw = xl.parse(sheet)
            # If standard columns not found, try row 1
            if 'Motor_Temperature' not in df_raw.columns and 'Motor_Current' not in df_raw.columns:
                df_raw = xl.parse(sheet, header=1)

        progress.progress(25, text="تم تحميل الملف. جاري التحقق من الأعمدة...")
        time.sleep(0.3)

        progress.progress(50, text="جاري تنظيف البيانات واستخراج الميزات...")
        time.sleep(0.3)

        from preprocessing.cleaner import clean_data
        from preprocessing.feature_engineer import engineer_features

        df_clean = clean_data(df_raw)
        df_feat  = engineer_features(df_clean)
        
        progress.progress(75, text="جاري تشغيل نماذج الذكاء الاصطناعي...")
        time.sleep(0.3)

        from prediction.predictor import PumpPredictor
        predictor = PumpPredictor()
        df_results = predictor.predict_batch(df_feat)
        
        progress.progress(100, text="✅ اكتمل التحليل!")

        # Get latest predictions
        last = df_results.iloc[-1]
        phi    = float(last.get('health_index', 0))
        label  = last.get('predicted_label', 'Unknown')
        
        # Translate Label to Arabic
        lbl_map = {'Critical': 'عطل حرج', 'Warning': 'تحذير', 'Healthy': 'سليمة'}
        label_ar = lbl_map.get(label, label)

        rul    = int(last.get('rul_days', 0))
        status = last.get('health_status', 'Unknown')

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

        # Probabilities
        probs = [0.0, 0.0, 0.0]
        if 'prob_0' in last:
            probs = [float(last['prob_0']), float(last['prob_1']), float(last['prob_2'])]
        else:
            if label == 'Critical': probs = [0.1, 0.2, 0.7]
            elif label == 'Warning': probs = [0.2, 0.6, 0.2]
            else: probs = [0.8, 0.15, 0.05]

        from prediction.recommendation_engine import get_recommendations
        primary_rec, all_recs = get_recommendations(sensor_values, trend_features)
        if not all_recs: all_recs = [primary_rec]

        st.success(f"✅ تمت معالجة الملف بنجاح! تم تحليل **{len(df_raw):,}** قراءة زمنية.")
        st.markdown("<hr>", unsafe_allow_html=True)

        # ─── Results Section ────────────────────────────────────────────
        st.markdown('<div class="section-header">⚡ الحالة الحالية للمضخة (أحدث قراءة)</div>', unsafe_allow_html=True)

        phi_color = "#2ECC71" if phi >= 80 else ("#00B4D8" if phi >= 60 else ("#F39C12" if phi >= 40 else "#E74C3C"))
        
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">💉</div>
                <div class="kpi-value" style="color:{phi_color};">{phi:.1f}%</div>
                <div class="kpi-label">مؤشر الصحة (PHI)</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📡</div>
                <div class="kpi-value" style="font-size:1.6rem;color:#E8EAF6;">{label_ar}</div>
                <div class="kpi-label">تنبؤ الذكاء الاصطناعي</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            rul_color = "#2ECC71" if rul >= 30 else ("#F39C12" if rul >= 7 else "#E74C3C")
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">⏱️</div>
                <div class="kpi-value" style="color:{rul_color};">{rul}</div>
                <div class="kpi-label">العمر المتبقي (أيام)</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🛢️</div>
                <div class="kpi-value" style="font-size:1.6rem;color:#E8EAF6;">B-167</div>
                <div class="kpi-label">معرف البئر</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ─── Charts ─────────────────────────
        st.markdown('<div class="section-header">📊 الرسوم البيانية التوضيحية</div>', unsafe_allow_html=True)
        col_gauge, col_donut = st.columns(2, gap="medium")
        with col_gauge:
            st.plotly_chart(phi_gauge(phi, status), width='stretch', config={'displayModeBar': False}, key="gauge_main")
        with col_donut:
            st.plotly_chart(probability_donut(probs), width='stretch', config={'displayModeBar': False}, key="donut_main")

        # ─── Trend ─────────────────────────
        history_phi = df_results['health_index'].tolist() if 'health_index' in df_results.columns else None
        if history_phi and len(history_phi) > 5:
            st.markdown('<div class="section-header">📈 التغير الزمني لمؤشر الصحة</div>', unsafe_allow_html=True)
            ts = df_results['Timestamp'].tolist() if 'Timestamp' in df_results.columns else list(range(len(history_phi)))
            fig_trend = phi_trend_chart(ts, history_phi)
            st.plotly_chart(fig_trend, width='stretch', config={'displayModeBar': True}, key="trend_main")

        # ─── Sensor Status Table ───────────────────────────────────
        st.markdown('<div class="section-header">📟 قراءات الحساسات الفعلية</div>', unsafe_allow_html=True)
        render_sensor_table(sensor_values, trend_features)

        # ─── Recommendations ──────────────────────────────────────
        st.markdown('<div class="section-header">🔔 توصيات الصيانة الذكية</div>', unsafe_allow_html=True)
        
        # Translate recommendations to Arabic if they are standard English texts
        for rec in all_recs:
            if "Stop the pump immediately" in rec.get('description', ''):
                rec['title'] = "إيقاف المضخة فوراً"
                rec['description'] = "أوقف المضخة فوراً لمنع حدوث احتراق في المحرك بناءً على القراءات الحرجة."
                rec['priority_lbl'] = "P1 - طارئ"
                rec['response_time'] = "< ساعة واحدة"
            elif "Schedule maintenance" in rec.get('description', ''):
                rec['title'] = "جدولة صيانة وقائية"
                rec['description'] = "هناك بوادر تدهور في أداء المضخة، يرجى جدولة فحص وقائي."
                rec['priority_lbl'] = "P2 - عالي"
                rec['response_time'] = "< 7 أيام"
            elif "Continue monitoring" in rec.get('description', ''):
                rec['title'] = "استمرار المراقبة"
                rec['description'] = "المضخة تعمل في النطاق الطبيعي، يرجى الاستمرار في المراقبة الدورية."
                rec['priority_lbl'] = "P4 - منخفض"
                rec['response_time'] = "روتيني"
            render_recommendation_card(rec)

    except Exception as e:
        progress.progress(100, text="❌ حدث خطأ")
        st.error(f"❌ فشل في تحليل الملف: {e}")
