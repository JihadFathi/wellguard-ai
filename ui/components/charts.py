"""
WellGuard AI - Reusable UI Components
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np


def load_css():
    """Loads the main CSS stylesheet."""
    import os
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'styles', 'main.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_kpi_card(icon: str, value: str, label: str, color: str = "#00B4D8"):
    """Renders a styled KPI metric card."""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value" style="color:{color};">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str):
    """Renders a colored status badge based on status string."""
    status_map = {
        'Excellent': ('badge-healthy',  '🟢'),
        'Healthy':   ('badge-healthy',  '🟢'),
        'Monitor':   ('badge-monitor',  '🔵'),
        'Warning':   ('badge-warning',  '🟡'),
        'Critical':  ('badge-critical', '🔴'),
    }
    cls, icon = status_map.get(status, ('badge-monitor', '⚪'))
    st.markdown(f"""
    <span class="badge {cls}">{icon} {status}</span>
    """, unsafe_allow_html=True)


def phi_gauge(phi_value: float, status: str = 'Healthy') -> go.Figure:
    """
    Creates a premium Plotly gauge chart for the Pump Health Index.
    """
    # Color based on PHI value
    if phi_value >= 80:
        bar_color = "#2ECC71"
        text_color = "#2ECC71"
    elif phi_value >= 60:
        bar_color = "#00B4D8"
        text_color = "#00B4D8"
    elif phi_value >= 40:
        bar_color = "#F39C12"
        text_color = "#F39C12"
    else:
        bar_color = "#E74C3C"
        text_color = "#E74C3C"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=phi_value,
        number={
            'font': {'size': 52, 'color': text_color, 'family': 'Inter, sans-serif'},
            'suffix': '%'
        },
        title={
            'text': f"Pump Health Index<br><b style='color:{text_color};font-size:14px'>{status}</b>",
            'font': {'size': 14, 'color': '#8892A4', 'family': 'Inter, sans-serif'}
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': '#2A3F5F',
                'tickfont': {'color': '#8892A4', 'size': 11}
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': 'rgba(13,31,60,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 39],   'color': 'rgba(231,76,60,0.15)'},
                {'range': [40, 59],  'color': 'rgba(243,156,18,0.15)'},
                {'range': [60, 79],  'color': 'rgba(0,180,216,0.15)'},
                {'range': [80, 94],  'color': 'rgba(46,204,113,0.15)'},
                {'range': [95, 100], 'color': 'rgba(46,204,113,0.25)'},
            ],
            'threshold': {
                'line': {'color': '#FFFFFF', 'width': 3},
                'thickness': 0.8,
                'value': phi_value
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#E8EAF6'},
        height=320,
        margin=dict(l=30, r=30, t=30, b=10),
    )
    return fig


def probability_donut(probs: list) -> go.Figure:
    """
    Creates a Plotly donut chart for failure class probabilities.
    """
    labels = ['Healthy', 'Warning', 'Critical']
    colors = ['#2ECC71', '#F39C12', '#E74C3C']
    values = [round(p * 100, 1) for p in probs]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color='#0A1628', width=2)),
        textinfo='label+percent',
        textfont=dict(color='#E8EAF6', size=12),
        hovertemplate="<b>%{label}</b><br>Probability: %{value:.1f}%<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#E8EAF6'},
        showlegend=True,
        legend=dict(
            font=dict(color='#8892A4', size=11),
            bgcolor='rgba(0,0,0,0)',
            orientation='h',
            x=0.15, y=-0.05
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=280,
        annotations=[dict(
            text=f"<b>{values[0]:.0f}%</b><br>Healthy",
            x=0.5, y=0.5,
            font=dict(size=14, color='#2ECC71'),
            showarrow=False
        )]
    )
    return fig


def phi_trend_chart(timestamps, phi_values) -> go.Figure:
    """
    Creates a PHI historical trend line chart.
    """
    # Color gradient for line based on health state
    colors_map = []
    for v in phi_values:
        if v >= 80:    colors_map.append('#2ECC71')
        elif v >= 60:  colors_map.append('#00B4D8')
        elif v >= 40:  colors_map.append('#F39C12')
        else:          colors_map.append('#E74C3C')

    fig = go.Figure()

    # Reference bands
    fig.add_hrect(y0=95, y1=100, fillcolor="rgba(46,204,113,0.06)", line_width=0, annotation_text="Excellent", annotation_position="right")
    fig.add_hrect(y0=80, y1=95,  fillcolor="rgba(46,204,113,0.04)", line_width=0, annotation_text="Healthy",   annotation_position="right")
    fig.add_hrect(y0=60, y1=80,  fillcolor="rgba(0,180,216,0.05)",  line_width=0, annotation_text="Monitor",   annotation_position="right")
    fig.add_hrect(y0=40, y1=60,  fillcolor="rgba(243,156,18,0.06)", line_width=0, annotation_text="Warning",   annotation_position="right")
    fig.add_hrect(y0=0,  y1=40,  fillcolor="rgba(231,76,60,0.06)",  line_width=0, annotation_text="Critical",  annotation_position="right")

    fig.add_trace(go.Scatter(
        x=timestamps,
        y=phi_values,
        mode='lines',
        line=dict(color='#00B4D8', width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(0,180,216,0.08)',
        name='PHI',
        hovertemplate="<b>%{x}</b><br>PHI: <b>%{y:.1f}%</b><extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#E8EAF6'},
        yaxis=dict(
            range=[0, 105],
            gridcolor='rgba(255,255,255,0.05)',
            title='Health Index (%)',
            title_font={'color': '#8892A4'}
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            title='Timestamp',
            title_font={'color': '#8892A4'}
        ),
        hovermode='x unified',
        margin=dict(l=20, r=60, t=20, b=40),
        height=350,
        showlegend=False
    )
    return fig


def sensor_trend_chart(timestamps, sensor_data: dict) -> go.Figure:
    """
    Creates a multi-sensor trend chart.
    """
    SENSOR_COLORS = {
        'Motor_Temperature':  '#E74C3C',
        'Motor_Current':      '#F39C12',
        'Discharge_Pressure': '#00B4D8',
        'Intake_Pressure':    '#2ECC71',
    }
    SENSOR_LABELS = {
        'Motor_Temperature':  'Motor Temp (°F)',
        'Motor_Current':      'Motor Current (A)',
        'Discharge_Pressure': 'Discharge Pressure (psi)',
        'Intake_Pressure':    'Intake Pressure (psi)',
    }

    fig = go.Figure()

    for sensor, values in sensor_data.items():
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=values,
            mode='lines',
            name=SENSOR_LABELS.get(sensor, sensor),
            line=dict(color=SENSOR_COLORS.get(sensor, '#FFFFFF'), width=1.8),
            hovertemplate=f"<b>{SENSOR_LABELS.get(sensor, sensor)}</b><br>%{{x}}<br>Value: <b>%{{y:.2f}}</b><extra></extra>"
        ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#E8EAF6'},
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(
            bgcolor='rgba(13,31,60,0.7)',
            bordercolor='rgba(0,180,216,0.3)',
            borderwidth=1,
            font=dict(color='#8892A4', size=11)
        ),
        hovermode='x unified',
        margin=dict(l=20, r=20, t=20, b=40),
        height=380,
    )
    return fig


def render_recommendation_card(rec: dict):
    """Renders a colored recommendation card based on priority."""
    priority_map = {
        1: ('alert-urgent', '🚨', '#E74C3C'),
        2: ('alert-high',   '⚠️', '#F39C12'),
        3: ('alert-medium', '🔵', '#00B4D8'),
        4: ('alert-low',    '✅', '#2ECC71'),
    }
    p = rec.get('priority', 4)
    css_cls, icon, color = priority_map.get(p, priority_map[4])
    st.markdown(f"""
    <div class="alert-box {css_cls}">
        <div style="font-size:1.4rem">{icon}</div>
        <div>
            <div style="color:{color};font-weight:700;font-size:0.95rem">{rec.get('priority_lbl','P4 - Low')} — {rec.get('title','')}</div>
            <div style="color:#B0B8C8;font-size:0.88rem;margin-top:4px">{rec.get('description','')}</div>
            <div style="color:#8892A4;font-size:0.82rem;margin-top:4px">⏱ Response time: <b style="color:{color}">{rec.get('response_time','')}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sensor_table(sensor_values: dict, trend_values: dict, baselines: dict = None):
    """Renders a styled sensor values table with status indicators."""
    default_baselines = {
        'Motor_Temperature':  {'value': 210.0, 'unit': '°F',  'high': 220.0, 'low': 150.0},
        'Motor_Current':      {'value': 32.3,  'unit': 'A',   'high': 38.8,  'low': 10.0},
        'Discharge_Pressure': {'value': 2395.8,'unit': 'psi', 'high': 3000.0,'low': 500.0},
        'Intake_Pressure':    {'value': 837.8, 'unit': 'psi', 'high': 1200.0,'low': 200.0},
    }
    if baselines is None:
        baselines = default_baselines

    labels = {
        'Motor_Temperature':  'Motor Temperature',
        'Motor_Current':      'Motor Current',
        'Discharge_Pressure': 'Discharge Pressure',
        'Intake_Pressure':    'Intake Pressure',
    }

    for sensor, val in sensor_values.items():
        if sensor not in labels:
            continue
        b = baselines.get(sensor, {})
        baseline_val = b.get('value', 0)
        unit = b.get('unit', '')
        high = b.get('high', float('inf'))
        low  = b.get('low',  0)
        trend = trend_values.get(sensor, 0.0)

        # Status color
        if low <= val <= high:
            status_color = "#2ECC71"
            status_icon  = "✅"
        elif val > high:
            status_color = "#E74C3C"
            status_icon  = "🔴"
        else:
            status_color = "#F39C12"
            status_icon  = "🟡"

        trend_arrow = "→"
        trend_color = "#8892A4"
        if trend > 0.5:
            trend_arrow = "↑"
            trend_color = "#E74C3C"
        elif trend < -0.5:
            trend_arrow = "↓"
            trend_color = "#00B4D8"

        st.markdown(f"""
        <div class="sensor-row">
            <div>
                <div class="sensor-name">{labels[sensor]}</div>
                <div style="color:#5A6478;font-size:0.75rem">Baseline: {baseline_val} {unit}</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px">
                <span class="sensor-value">{val:.1f} {unit}</span>
                <span style="color:{trend_color};font-size:1.2rem">{trend_arrow}</span>
                <span style="font-size:1.1rem">{status_icon}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
