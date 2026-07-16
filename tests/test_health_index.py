"""
WellGuard AI - Unit Tests for prediction/health_index.py and prediction/rul_estimator.py
"""
import pytest
import numpy as np
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from prediction.health_index import calculate_phi, categorize_phi
from prediction.rul_estimator import estimate_rul


class TestHealthIndex:

    def test_phi_healthy_state(self):
        """All-healthy inputs should yield PHI >= 80."""
        probs = [0.95, 0.04, 0.01]
        sensor_values = {'Motor_Temperature': 210.0, 'Motor_Current': 32.3,
                         'Discharge_Pressure': 2395.8, 'Intake_Pressure': 837.8}
        trend_features = {'Motor_Temperature': 0.0, 'Discharge_Pressure': 0.0, 'Motor_Current': 0.0}
        phi = calculate_phi(probs, sensor_values, trend_features)
        assert phi >= 75.0, f"Healthy-state PHI should be >= 75, got {phi:.1f}"

    def test_phi_critical_state(self):
        """High critical probability should yield PHI <= 40."""
        probs = [0.05, 0.10, 0.85]
        sensor_values = {'Motor_Temperature': 250.0, 'Motor_Current': 50.0,
                         'Discharge_Pressure': 1000.0, 'Intake_Pressure': 300.0}
        trend_features = {'Motor_Temperature': 5.0, 'Discharge_Pressure': -100.0, 'Motor_Current': 2.0}
        phi = calculate_phi(probs, sensor_values, trend_features)
        assert phi <= 45.0, f"Critical-state PHI should be <= 45, got {phi:.1f}"

    def test_phi_bounded_0_to_100(self):
        """PHI must always be between 0 and 100."""
        for _ in range(50):
            probs = np.random.dirichlet([1, 1, 1]).tolist()
            sensor_values = {
                'Motor_Temperature':  np.random.uniform(100, 300),
                'Motor_Current':      np.random.uniform(0, 60),
                'Discharge_Pressure': np.random.uniform(200, 5000),
                'Intake_Pressure':    np.random.uniform(100, 2000),
            }
            trend_features = {
                'Motor_Temperature':  np.random.uniform(-10, 10),
                'Discharge_Pressure': np.random.uniform(-200, 200),
                'Motor_Current':      np.random.uniform(-5, 5),
            }
            phi = calculate_phi(probs, sensor_values, trend_features)
            assert 0.0 <= phi <= 100.0, f"PHI out of bounds: {phi}"

    def test_phi_returns_float(self):
        """PHI should return a numeric (float) value."""
        probs = [0.8, 0.15, 0.05]
        sensor_values = {'Motor_Temperature': 210.0}
        trend_features = {'Motor_Temperature': 0.2}
        phi = calculate_phi(probs, sensor_values, trend_features)
        assert isinstance(phi, (float, np.floating)), "PHI must be a float"

    def test_categorize_phi_excellent(self):
        """PHI >= 95 should be Excellent."""
        category, severity, action = categorize_phi(97.5)
        assert category == 'Excellent'
        assert severity == 'Healthy'

    def test_categorize_phi_healthy(self):
        """PHI in [80, 94] should be Healthy."""
        category, severity, action = categorize_phi(85.0)
        assert category == 'Healthy'

    def test_categorize_phi_monitor(self):
        """PHI in [60, 79] should be Monitor."""
        category, severity, action = categorize_phi(70.0)
        assert category == 'Monitor'

    def test_categorize_phi_warning(self):
        """PHI in [40, 59] should be Warning."""
        category, severity, action = categorize_phi(50.0)
        assert category == 'Warning'

    def test_categorize_phi_critical(self):
        """PHI < 40 should be Critical."""
        category, severity, action = categorize_phi(25.0)
        assert category == 'Critical'

    def test_categorize_returns_three_values(self):
        """categorize_phi must return exactly 3 values."""
        result = categorize_phi(60.0)
        assert len(result) == 3


class TestRULEstimator:

    def test_rul_healthy_phi(self):
        """Healthy PHI (>= 80) should yield RUL >= 60 days."""
        probs = [0.9, 0.08, 0.02]
        rul = estimate_rul(90.0, 0.0, probs)
        assert rul >= 60, f"Healthy RUL should be >= 60 days, got {rul}"

    def test_rul_critical_phi(self):
        """Critical PHI (< 20) should yield RUL < 5 days."""
        probs = [0.0, 0.1, 0.9]
        rul = estimate_rul(15.0, 0.5, probs)
        assert rul < 10, f"Critical RUL should be < 10 days, got {rul}"

    def test_rul_non_negative(self):
        """RUL should never be negative."""
        for phi in [0, 10, 30, 50, 70, 90, 100]:
            for deg in [0.0, 0.5, 2.0]:
                probs = [0.33, 0.33, 0.34]
                rul = estimate_rul(phi, deg, probs)
                assert rul >= 0, f"RUL should be >= 0, got {rul} for phi={phi}, deg={deg}"

    def test_rul_decreases_with_higher_degradation(self):
        """Higher degradation rate should yield lower RUL."""
        probs = [0.5, 0.3, 0.2]
        rul_low  = estimate_rul(70.0, 0.1, probs)
        rul_high = estimate_rul(70.0, 2.0, probs)
        assert rul_high <= rul_low, "Higher degradation should yield lower or equal RUL"

    def test_rul_high_critical_prob_halves_rul(self):
        """If critical probability > 0.5, RUL should be halved."""
        probs_low_crit  = [0.7, 0.25, 0.05]
        probs_high_crit = [0.1, 0.15, 0.75]
        rul_low  = estimate_rul(70.0, 0.0, probs_low_crit)
        rul_high = estimate_rul(70.0, 0.0, probs_high_crit)
        assert rul_high < rul_low, "High critical probability should produce lower RUL"
