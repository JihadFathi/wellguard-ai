import pandas as pd
import numpy as np
import os

# Standard Column Mapping
COLUMN_MAPPING = {
    'Date (Africa/Tripoli)': 'Timestamp',
    'Well': 'Well_ID',
    'Average Amps (Amps)': 'Motor_Current',
    'Discharge Pressure (psia)': 'Discharge_Pressure',
    'Drive Frequency (Hz)': 'Drive_Frequency',
    'Intake Pressure (psia)': 'Intake_Pressure',
    'Motor Temperature (°F)': 'Motor_Temperature'
}

REVERSE_COLUMN_MAPPING = {v: k for k, v in COLUMN_MAPPING.items()}

def load_raw_data(file_path):
    """
    Loads raw Excel/CSV dataset and renames columns to standard internal names.
    """
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path, sheet_name=0)
    else:
        df = pd.read_csv(file_path)
    
    # Rename matching columns
    df = df.rename(columns=COLUMN_MAPPING)
    return df

def clean_data(df, threshold=0.15):
    """
    Executes the data cleaning pipeline:
    1. Deduplication
    2. Chronological sorting
    3. Date parsing & timezone UTC conversion
    4. Handling missing values
    5. Capping outliers using IQR
    6. Boundary validation
    """
    df = df.copy()
    
    # 1. Deduplication
    if 'Timestamp' in df.columns and 'Well_ID' in df.columns:
        df = df.drop_duplicates(subset=['Well_ID', 'Timestamp'], keep='last')
    
    # 2. Date parsing & UTC conversion
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        # If timezone information is present, convert/localize to UTC, else assign UTC
        if df['Timestamp'].dt.tz is not None:
            df['Timestamp'] = df['Timestamp'].dt.tz_convert('UTC')
        else:
            df['Timestamp'] = df['Timestamp'].dt.tz_localize('UTC')
            
    # 3. Sort chronologically
    if 'Well_ID' in df.columns and 'Timestamp' in df.columns:
        df = df.sort_values(by=['Well_ID', 'Timestamp']).reset_index(drop=True)
    elif 'Timestamp' in df.columns:
        df = df.sort_values(by='Timestamp').reset_index(drop=True)

    # Critical columns for checking missing rates
    critical_cols = ['Motor_Current', 'Discharge_Pressure', 'Intake_Pressure', 'Motor_Temperature']
    
    # Drop columns not in df
    critical_cols = [c for c in critical_cols if c in df.columns]
    
    # Drop rows where missing data exceeds threshold in critical columns
    for col in critical_cols:
        missing_pct = df[col].isnull().sum() / len(df)
        if missing_pct > threshold:
            df = df.dropna(subset=[col])
            
    # 4. Missing Values Treatment
    # Forward fill gradual temperature & drive frequency
    for col in ['Motor_Temperature', 'Drive_Frequency']:
        if col in df.columns:
            df[col] = df[col].ffill().bfill()
            
    # Interpolation for Intake & Discharge Pressure
    for col in ['Intake_Pressure', 'Discharge_Pressure']:
        if col in df.columns:
            df[col] = df[col].interpolate(method='linear').ffill().bfill()
            
    # Rolling mean for Motor Current
    if 'Motor_Current' in df.columns:
        # Using rolling window of 5 to smooth and fill missing
        df['Motor_Current'] = df['Motor_Current'].fillna(
            df['Motor_Current'].rolling(window=5, min_periods=1, center=True).mean()
        )
        df['Motor_Current'] = df['Motor_Current'].ffill().bfill()

    # 5. Outlier Detection and Capping using IQR
    # Limit capping only to dynamic period or apply reasonable bounds
    sensor_cols = ['Motor_Current', 'Discharge_Pressure', 'Intake_Pressure', 'Motor_Temperature']
    sensor_cols = [c for c in sensor_cols if c in df.columns]
    
    for col in sensor_cols:
        # Check standard deviation. If it is too low (e.g. frozen), don't do IQR capping
        if df[col].std() > 0.01:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            
            # Additional safety: don't cap values if it clips normal startup or shutdown states
            # For motor temperature, physical limits are ~100 to 250 F.
            # Let's ensure physical sanity bounds override IQR if IQR is too narrow
            if col == 'Motor_Temperature':
                lower = max(lower, 50.0)
                upper = min(upper, 300.0)
            elif col == 'Motor_Current':
                lower = max(lower, 0.0)
                upper = min(upper, 100.0)
            elif col == 'Discharge_Pressure' or col == 'Intake_Pressure':
                lower = max(lower, 0.0)
                upper = min(upper, 6000.0)
                
            df[col] = df[col].clip(lower, upper)

    # 6. Physical Boundary Validation
    if 'Motor_Temperature' in df.columns:
        # Temperature cannot be negative or absurdly high
        df = df[(df['Motor_Temperature'] >= 32.0) & (df['Motor_Temperature'] <= 350.0) | df['Motor_Temperature'].isnull()]
    if 'Motor_Current' in df.columns:
        df = df[(df['Motor_Current'] >= 0.0) & (df['Motor_Current'] <= 150.0) | df['Motor_Current'].isnull()]
    if 'Intake_Pressure' in df.columns:
        df = df[(df['Intake_Pressure'] >= 0.0) & (df['Intake_Pressure'] <= 6000.0) | df['Intake_Pressure'].isnull()]
    if 'Discharge_Pressure' in df.columns:
        df = df[(df['Discharge_Pressure'] >= 0.0) & (df['Discharge_Pressure'] <= 6000.0) | df['Discharge_Pressure'].isnull()]

    return df.reset_index(drop=True)

if __name__ == "__main__":
    # Test script run
    raw_path = r"d:\مشروع التبؤ بصيانة مضخات النفط\Oil Pump Health Monitoring System\DataSet\Data_Export_Selected_B_167_01_Jan_2025_000000_01_Jul_2025_000000 (2).xlsx"
    if os.path.exists(raw_path):
        df_raw = load_raw_data(raw_path)
        print("Raw shape:", df_raw.shape)
        df_clean = clean_data(df_raw)
        print("Clean shape:", df_clean.shape)
        print("Nulls after clean:\n", df_clean.isnull().sum())
    else:
        print("File path does not exist.")
