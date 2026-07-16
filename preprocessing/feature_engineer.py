import pandas as pd
import numpy as np
import os

def engineer_features(df):
    """
    Computes engineered features from the cleaned time-series dataset:
    1. Differentials
    2. Statistical rolling features (means, std devs, min, max)
    3. Trend features (slopes & acceleration)
    4. Rate of change features
    5. Cumulative features (Runtime since restart)
    6. Interaction features
    """
    df = df.copy()
    
    # Ensure Timestamp is datetime
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # 1. Differential Features
    if 'Discharge_Pressure' in df.columns and 'Intake_Pressure' in df.columns:
        df['Pressure_Difference'] = df['Discharge_Pressure'] - df['Intake_Pressure']
        # Avoid division by zero
        df['Pressure_Ratio'] = df['Discharge_Pressure'] / (df['Intake_Pressure'] + 1e-5)
    
    # Custom conditional features (check if column exists)
    if 'Motor_Voltage' in df.columns and 'Motor_Current' in df.columns:
        df['Voltage_Current_Ratio'] = df['Motor_Voltage'] / (df['Motor_Current'] + 1e-5)
    else:
        # Mock voltage of 480V for WellGuard AI specs if not present
        df['Voltage_Current_Ratio'] = 480.0 / (df['Motor_Current'] + 1e-5)

    if 'Flow_Rate' in df.columns and 'Pressure_Difference' in df.columns:
        df['Flow_Pressure_Ratio'] = df['Flow_Rate'] / (df['Pressure_Difference'] + 1e-5)

    # 2. Rolling Window Statistical Features
    # Since data is 5-minute interval:
    # 3 hours = 36 rows
    # 6 hours = 72 rows
    # 12 hours = 144 rows
    # 24 hours = 288 rows
    windows = {
        '3h': 36,
        '6h': 72,
        '12h': 144,
        '24h': 288
    }
    
    sensor_cols = ['Motor_Current', 'Discharge_Pressure', 'Intake_Pressure', 'Motor_Temperature']
    sensor_cols = [c for c in sensor_cols if c in df.columns]
    
    for w_name, w_size in windows.items():
        for col in sensor_cols:
            df[f'{col}_mean_{w_name}'] = df[col].rolling(w_size, min_periods=1).mean()
            df[f'{col}_std_{w_name}'] = df[col].rolling(w_size, min_periods=1).std().fillna(0.0)
            df[f'{col}_min_{w_name}'] = df[col].rolling(w_size, min_periods=1).min()
            df[f'{col}_max_{w_name}'] = df[col].rolling(w_size, min_periods=1).max()
            
    # 3. Trend Features (using difference over windows)
    # Temperature Trend (24h)
    if 'Motor_Temperature' in df.columns:
        df['Temp_Trend'] = df['Motor_Temperature'] - df['Motor_Temperature'].shift(288)
        df['Temp_Trend'] = df['Temp_Trend'].ffill().bfill()
        # Temperature Acceleration (second derivative)
        df['Temp_Acceleration'] = df['Temp_Trend'] - df['Temp_Trend'].shift(288)
        df['Temp_Acceleration'] = df['Temp_Acceleration'].ffill().bfill()
        
    # Pressure Trend (12h)
    if 'Discharge_Pressure' in df.columns:
        df['Pressure_Trend'] = df['Discharge_Pressure'] - df['Discharge_Pressure'].shift(144)
        df['Pressure_Trend'] = df['Pressure_Trend'].ffill().bfill()
        
    # Current Trend (24h)
    if 'Motor_Current' in df.columns:
        df['Current_Trend'] = df['Motor_Current'] - df['Motor_Current'].shift(288)
        df['Current_Trend'] = df['Current_Trend'].ffill().bfill()

    # 4. Rate of Change Features (1 hour delta)
    for col in sensor_cols:
        df[f'{col}_change_rate_1h'] = df[col] - df[col].shift(12)
        df[f'{col}_change_rate_1h'] = df[f'{col}_change_rate_1h'].ffill().bfill()

    # 5. Cumulative Features: Hours Since Restart
    # The pump is running if Motor_Current > 5 (amps)
    is_running = df['Motor_Current'] > 5.0
    
    # Calculate cumulative run hours
    # Each row is 5 minutes = 5/60 hours = 0.0833 hours
    run_hours = []
    current_run = 0.0
    for val in is_running:
        if val:
            current_run += 0.08333333333333333
        else:
            current_run = 0.0
        run_hours.append(current_run)
    df['Hours_Since_Restart'] = run_hours
    
    # 6. Interaction Features
    if 'Motor_Temperature' in df.columns and 'Motor_Current' in df.columns:
        df['Temp_x_Current'] = df['Motor_Temperature'] * df['Motor_Current']
        
    if 'Discharge_Pressure' in df.columns and 'Motor_Temperature' in df.columns:
        df['Temp_x_Pressure_Ratio'] = df['Motor_Temperature'] / (df['Pressure_Ratio'] + 1e-5)

    return df

if __name__ == "__main__":
    from cleaner import load_raw_data, clean_data
    raw_path = r"d:\مشروع التبؤ بصيانة مضخات النفط\Oil Pump Health Monitoring System\DataSet\Data_Export_Selected_B_167_01_Jan_2025_000000_01_Jul_2025_000000 (2).xlsx"
    if os.path.exists(raw_path):
        df_raw = load_raw_data(raw_path)
        df_clean = clean_data(df_raw)
        df_feat = engineer_features(df_clean)
        print("Features shape:", df_feat.shape)
        print("Example computed columns:\n", [c for c in df_feat.columns if c not in df_clean.columns][:10])
    else:
        print("File path does not exist.")
