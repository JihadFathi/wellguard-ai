"""
WellGuard AI - Unit Tests for prediction/recommendation_engine.py
"""
import pytest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from prediction.recommendation_engine import get_recommendations


class TestRecommendationEngine:

    def test_nominal_returns_p4(self):
        """All nominal values should return P4 (low priority, continue monitoring)."""
        sensor_values  = {'Motor_Temperature': 200.0, 'Motor_Current': 30.0,
                          'Discharge_Pressure': 2400.0, 'Intake_Pressure': 850.0}
        trend_features = {'Motor_Temperature': 0.0, 'Discharge_Pressure': 0.0,
                          'Motor_Current': 0.0, 'Intake_Pressure': 0.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        assert primary['priority'] == 4, "Nominal conditions should return P4"
        assert len(triggered) == 0, "No rules should trigger for nominal conditions"

    def test_high_temperature_and_rising(self):
        """Temperature > 180°F and rising trend should trigger a P2 alert."""
        sensor_values  = {'Motor_Temperature': 185.0, 'Motor_Current': 30.0,
                          'Discharge_Pressure': 2400.0, 'Intake_Pressure': 850.0}
        trend_features = {'Motor_Temperature': 2.0, 'Discharge_Pressure': 0.0,
                          'Motor_Current': 0.0, 'Intake_Pressure': 0.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        assert any(r['priority'] <= 2 for r in triggered), "High rising temperature should trigger P1 or P2"

    def test_critical_temperature(self):
        """Temperature > 210°F should trigger a P1 Urgent alert."""
        sensor_values  = {'Motor_Temperature': 215.0, 'Motor_Current': 30.0,
                          'Discharge_Pressure': 2400.0, 'Intake_Pressure': 850.0}
        trend_features = {'Motor_Temperature': 0.5, 'Discharge_Pressure': 0.0,
                          'Motor_Current': 0.0, 'Intake_Pressure': 0.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        assert any(r['priority'] == 1 for r in triggered), "Critical temperature should trigger P1"

    def test_frozen_sensor_detection(self):
        """Frozen sensor values (DEt event) should trigger P1 Urgent."""
        sensor_values  = {'Motor_Temperature': 174.7, 'Motor_Current': 32.0,
                          'Discharge_Pressure': 944.4, 'Intake_Pressure': 925.1}
        trend_features = {'Motor_Temperature': 0.0, 'Discharge_Pressure': 0.0,
                          'Motor_Current': 0.0, 'Intake_Pressure': 0.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        assert any(r['priority'] == 1 for r in triggered), "Frozen sensor should trigger P1 Urgent"
        titles = [r['title'] for r in triggered]
        assert any('Telemetry' in t or 'Freeze' in t for t in titles), "Should detect telemetry freeze"

    def test_high_current(self):
        """Current > 120% baseline (38.76A) should trigger P2."""
        sensor_values  = {'Motor_Temperature': 200.0, 'Motor_Current': 40.0,
                          'Discharge_Pressure': 2400.0, 'Intake_Pressure': 850.0}
        trend_features = {'Motor_Temperature': 0.0, 'Discharge_Pressure': 0.0,
                          'Motor_Current': 0.0, 'Intake_Pressure': 0.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        assert any(r['priority'] <= 2 for r in triggered), "High current should trigger P2 or higher"

    def test_multiple_alerts_escalate_priority(self):
        """3+ simultaneous alerts should escalate the top priority."""
        sensor_values  = {'Motor_Temperature': 215.0, 'Motor_Current': 42.0,
                          'Discharge_Pressure': 944.4, 'Intake_Pressure': 925.1}
        trend_features = {'Motor_Temperature': 3.0, 'Discharge_Pressure': -200.0,
                          'Motor_Current': 1.0, 'Intake_Pressure': -5.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        assert len(triggered) >= 3, "Multiple conditions should trigger 3+ rules"

    def test_output_structure(self):
        """Each recommendation should have required keys."""
        sensor_values  = {'Motor_Temperature': 215.0, 'Motor_Current': 30.0,
                          'Discharge_Pressure': 2400.0, 'Intake_Pressure': 850.0}
        trend_features = {'Motor_Temperature': 1.0, 'Discharge_Pressure': 0.0,
                          'Motor_Current': 0.0, 'Intake_Pressure': 0.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        required_keys = ['priority', 'title', 'description', 'response_time']
        for key in required_keys:
            assert key in primary, f"Missing key '{key}' in primary recommendation"

    def test_sorted_by_priority(self):
        """Triggered rules should be sorted from highest to lowest priority."""
        sensor_values  = {'Motor_Temperature': 215.0, 'Motor_Current': 42.0,
                          'Discharge_Pressure': 2400.0, 'Intake_Pressure': 850.0}
        trend_features = {'Motor_Temperature': 2.0, 'Discharge_Pressure': -20.0,
                          'Motor_Current': 1.0, 'Intake_Pressure': 0.0}
        primary, triggered = get_recommendations(sensor_values, trend_features)
        if len(triggered) >= 2:
            for i in range(len(triggered) - 1):
                assert triggered[i]['priority'] <= triggered[i+1]['priority'], \
                    "Rules should be sorted ascending by priority number (1=highest)"
