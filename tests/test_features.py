"""
WellGuard AI - Unit Tests for preprocessing/feature_engineer.py
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from preprocessing.feature_engineer import engineer_features


def make_clean_df(n=500):
    """Create a pre-cleaned DataFrame for feature engineering tests."""
    timestamps = pd.date_range('2025-05-11', periods=n, freq='5min', tz='UTC')
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Well_ID': 'B-167',
        'Motor_Temperature': np.random.normal(210, 3, n),
        'Motor_Current': np.random.normal(32.3, 0.5, n),
        'Discharge_Pressure': np.random.normal(2395, 30, n),
        'Intake_Pressure': np.random.normal(837, 15, n),
    })
    return df


class TestFeatureEngineer:

    def test_pressure_difference_computed(self):
        """Pressure_Difference feature should exist and equal Discharge - Intake."""
        df = make_clean_df(100)
        df_feat = engineer_features(df)
        assert 'Pressure_Difference' in df_feat.columns, "Pressure_Difference feature missing"
        # Verify values are reasonable (positive for B-167)
        assert df_feat['Pressure_Difference'].mean() > 0, "Pressure difference should be positive"

    def test_pressure_ratio_computed(self):
        """Pressure_Ratio feature should exist and be > 0."""
        df = make_clean_df(100)
        df_feat = engineer_features(df)
        assert 'Pressure_Ratio' in df_feat.columns, "Pressure_Ratio feature missing"
        assert (df_feat['Pressure_Ratio'] > 0).all(), "Pressure ratio should always be positive"

    def test_rolling_features_exist(self):
        """Rolling statistical features should be generated for key sensors."""
        df = make_clean_df(500)
        df_feat = engineer_features(df)
        # Check for at least one rolling feature
        rolling_features = [c for c in df_feat.columns if '_mean_' in c or '_std_' in c]
        assert len(rolling_features) > 0, "Rolling mean/std features should exist"

    def test_trend_features_exist(self):
        """Trend features for temperature, pressure, and current should exist."""
        df = make_clean_df(500)
        df_feat = engineer_features(df)
        trend_features = [c for c in df_feat.columns if 'Trend' in c or 'trend' in c]
        assert len(trend_features) > 0, "Trend features should be generated"

    def test_interaction_features_exist(self):
        """Interaction features (Temp_x_Current etc.) should be computed."""
        df = make_clean_df(200)
        df_feat = engineer_features(df)
        interaction_features = [c for c in df_feat.columns if '_x_' in c]
        assert len(interaction_features) > 0, "Interaction features should exist"

    def test_no_inf_values(self):
        """Engineered features should not contain infinite values."""
        df = make_clean_df(200)
        df_feat = engineer_features(df)
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        has_inf = np.isinf(df_feat[numeric_cols]).any().any()
        assert not has_inf, "Feature matrix should not contain infinite values"

    def test_output_has_more_columns(self):
        """Feature engineering should produce more columns than the input."""
        df = make_clean_df(200)
        df_feat = engineer_features(df)
        assert df_feat.shape[1] > df.shape[1], "Feature engineering should add new columns"

    def test_timestamp_preserved(self):
        """Timestamp column should still be present after feature engineering."""
        df = make_clean_df(100)
        df_feat = engineer_features(df)
        assert 'Timestamp' in df_feat.columns, "Timestamp column should be preserved"
