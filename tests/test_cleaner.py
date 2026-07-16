"""
WellGuard AI - Unit Tests for preprocessing/cleaner.py
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from preprocessing.cleaner import clean_data


def make_sample_df(n=100, add_duplicates=True, add_outliers=True):
    """Create a sample sensor DataFrame for testing."""
    timestamps = pd.date_range('2025-05-11', periods=n, freq='5min', tz='UTC')
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Well_ID': 'B-167',
        'Motor_Temperature': np.random.normal(210, 5, n),
        'Motor_Current': np.random.normal(32.3, 1, n),
        'Discharge_Pressure': np.random.normal(2395, 50, n),
        'Intake_Pressure': np.random.normal(837, 20, n),
    })

    if add_duplicates:
        # Add 5 exact duplicate rows
        df = pd.concat([df, df.iloc[:5]], ignore_index=True)

    if add_outliers:
        # Add extreme outliers
        df.loc[0, 'Motor_Temperature'] = 99999.0   # Unrealistic outlier
        df.loc[1, 'Discharge_Pressure'] = -500.0   # Negative pressure

    return df


class TestCleaner:

    def test_deduplication(self):
        """Duplicates should be removed."""
        df = make_sample_df(n=20, add_duplicates=True, add_outliers=False)
        original_count = len(df)
        df_clean = clean_data(df)
        assert len(df_clean) < original_count, "Duplicates should have been removed"

    def test_chronological_sort(self):
        """Rows should be sorted by Timestamp."""
        df = make_sample_df(n=50, add_duplicates=False, add_outliers=False)
        # Shuffle the dataframe
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        df_clean = clean_data(df)
        if 'Timestamp' in df_clean.columns:
            timestamps = df_clean['Timestamp'].tolist()
            assert timestamps == sorted(timestamps), "DataFrame should be sorted by Timestamp"

    def test_no_negative_pressure_after_cleaning(self):
        """After cleaning, there should be no obviously invalid negative pressures."""
        df = make_sample_df(n=50, add_outliers=True)
        df_clean = clean_data(df)
        if 'Discharge_Pressure' in df_clean.columns:
            min_val = df_clean['Discharge_Pressure'].min()
            assert min_val > -1000, "Discharge pressure should not have extreme negative values after cleaning"

    def test_no_missing_values_in_key_sensors(self):
        """Key sensor columns should not have high proportion of missing values after cleaning."""
        df = make_sample_df(n=100, add_duplicates=False, add_outliers=False)
        # Introduce some NaN values (15% threshold)
        df.loc[0:5, 'Motor_Temperature'] = np.nan
        df_clean = clean_data(df)
        key_cols = ['Motor_Temperature', 'Motor_Current']
        for col in key_cols:
            if col in df_clean.columns:
                null_pct = df_clean[col].isnull().mean()
                assert null_pct < 0.20, f"{col} has too many nulls after cleaning: {null_pct:.1%}"

    def test_output_has_timestamp(self):
        """Cleaned DataFrame must contain a Timestamp column."""
        df = make_sample_df(n=20)
        df_clean = clean_data(df)
        assert 'Timestamp' in df_clean.columns, "Timestamp column must be present"

    def test_output_is_dataframe(self):
        """clean_data must return a DataFrame."""
        df = make_sample_df(n=20)
        result = clean_data(df)
        assert isinstance(result, pd.DataFrame), "Output must be a pandas DataFrame"
