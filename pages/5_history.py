"""
WellGuard AI - Page 5: Prediction History
"""
import streamlit as st
import sys
import os
import pandas as pd
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.charts import load_css

st.set_page_config(page_title="History | WellGuard AI", page_icon="🕰️", layout="wide")
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
    <h1 style="color:#E8EAF6;font-size:2rem;font-weight:800;margin:0;">🕰️ Prediction History</h1>
    <p style="color:#8892A4;margin-top:4px">Browse and search previous health analyses and PDF reports.</p>
</div>
""", unsafe_allow_html=True)

# ─── Retrieve history ─────────────────────────────────────────────────
history = st.session_state.get('history', [])

if len(history) == 0:
    st.info("""
    📭 No prediction history yet.

    Run a prediction from **Manual Entry** or **Upload Dataset**, then navigate to **Analysis Results**
    and generate a report — it will appear here automatically.
    """)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📁 Upload Dataset", width='stretch'):
            st.switch_page("pages/2_upload.py")
    with col_b:
        if st.button("✏️ Manual Entry", width='stretch'):
            st.switch_page("pages/3_manual_entry.py")
    st.stop()

# ─── Filters ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Filter History</div>', unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns(3)

all_wells  = sorted(list(set(h['well_id'] for h in history)))
all_states = sorted(list(set(h['status'] for h in history)))

with col_f1:
    filter_well = st.multiselect("Well ID", all_wells, default=all_wells)
with col_f2:
    filter_status = st.multiselect("Health Status", all_states, default=all_states)
with col_f3:
    filter_src = st.multiselect("Source", ["Manual Entry Result", "Batch Upload Result"],
                                default=["Manual Entry Result", "Batch Upload Result"])

# Apply filters
filtered = [
    h for h in history
    if h['well_id'] in filter_well
    and h['status'] in filter_status
    and h['source'] in filter_src
]

# ─── Summary Stats ────────────────────────────────────────────────────
st.markdown(f"""
<div style="color:#8892A4;font-size:0.85rem;margin:12px 0">
    Showing <b style="color:#00B4D8">{len(filtered)}</b> of <b style="color:#00B4D8">{len(history)}</b> records
</div>
""", unsafe_allow_html=True)

# ─── History Table ────────────────────────────────────────────────────
if filtered:
    df_hist = pd.DataFrame(filtered)
    df_hist = df_hist.rename(columns={
        'timestamp': 'Timestamp',
        'well_id':   'Well ID',
        'phi':       'PHI (%)',
        'label':     'Predicted Label',
        'rul':       'RUL (days)',
        'status':    'Status',
        'source':    'Analysis Source',
        'report':    'Report File'
    })

    def color_status(val):
        if val == 'Critical':  return 'color: #E74C3C; font-weight: bold'
        elif val == 'Warning': return 'color: #F39C12; font-weight: bold'
        elif val == 'Monitor': return 'color: #00B4D8; font-weight: bold'
        elif val == 'Healthy': return 'color: #2ECC71; font-weight: bold'
        return ''

    styled_df = df_hist.style.applymap(color_status, subset=['Status', 'Predicted Label'])

    st.dataframe(
        styled_df,
        width='stretch',
        height=min(60 + 40 * len(df_hist), 600),
        column_config={
            'PHI (%)': st.column_config.ProgressColumn(
                "PHI (%)", min_value=0, max_value=100, format="%.1f"
            ),
            'RUL (days)': st.column_config.NumberColumn("RUL (days)", format="%d days"),
        }
    )

    # ─── Export history as CSV ────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = df_hist.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Export History as CSV",
        data=csv_data,
        file_name=f"wellguard_history_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # ─── History Cards ────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Detailed Records</div>', unsafe_allow_html=True)
    for h in reversed(filtered[-10:]):  # Show last 10
        phi = h['phi']
        phi_color = "#2ECC71" if phi >= 80 else ("#00B4D8" if phi >= 60 else ("#F39C12" if phi >= 40 else "#E74C3C"))
        status = h['status']
        badge_cls = {'Critical': 'badge-critical', 'Warning': 'badge-warning',
                     'Monitor': 'badge-monitor', 'Healthy': 'badge-healthy'}.get(status, 'badge-monitor')

        st.markdown(f"""
        <div class="well-card" style="padding:16px 20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <div>
                    <span style="color:#00B4D8;font-weight:700">🛢️ {h['well_id']}</span>
                    <span style="color:#5A6478;font-size:0.8rem;margin-left:12px">{h['timestamp']}</span>
                </div>
                <span class="badge {badge_cls}">{status}</span>
            </div>
            <div style="display:flex;gap:24px;margin-top:12px;flex-wrap:wrap">
                <div>
                    <span style="color:#8892A4;font-size:0.78rem">PHI</span><br>
                    <span style="color:{phi_color};font-weight:700;font-size:1.3rem">{phi:.1f}%</span>
                </div>
                <div>
                    <span style="color:#8892A4;font-size:0.78rem">State</span><br>
                    <span style="color:#E8EAF6;font-weight:700">{h['label']}</span>
                </div>
                <div>
                    <span style="color:#8892A4;font-size:0.78rem">RUL</span><br>
                    <span style="color:#E8EAF6;font-weight:700">{h['rul']} days</span>
                </div>
                <div>
                    <span style="color:#8892A4;font-size:0.78rem">Source</span><br>
                    <span style="color:#E8EAF6;font-size:0.85rem">{h['source']}</span>
                </div>
                {f'<div><span style="color:#8892A4;font-size:0.78rem">Report</span><br><span style="color:#00B4D8;font-size:0.82rem">📄 {h.get("report","")}</span></div>' if h.get('report') else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── Clear History ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear All History", type="secondary"):
        st.session_state['history'] = []
        st.rerun()


