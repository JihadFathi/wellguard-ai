import pandas as pd
import numpy as np
import os

def assign_labels(df, critical_days=3, warning_days=10):
    """
    Assigns multi-class failure labels and continuous RUL target variables to the dataset.
    
    Labels:
    - 'Critical' (0 to critical_days before failure)
    - 'Warning' (critical_days to warning_days before failure)
    - 'Healthy' (> warning_days before failure)
    
    Also identifies transient startup periods (first 48 hours after a Pump Start event)
    so they can be excluded from training.
    """
    df = df.copy()
    
    # Ensure Timestamp is datetime in UTC
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    else:
        raise ValueError("Timestamp column is required for labeling.")
        
    # Identify failure/stop timestamps
    # B-167 has specific shutdown dates:
    # 1. 2025-06-19 08:46:01 (Manual Stop/Electrical issues)
    # 2. 2025-06-29 10:29:01 (VSD Internal Trip)
    # Let's detect these dynamically from the 'Event' column or 'Shutdown Cause'
    failure_dates = []
    
    # Let's find rows where Event is 'Pump Stop' or Shutdown Cause is not null
    if 'Event' in df.columns:
        stop_rows = df[df['Event'] == 'Pump Stop']
        failure_dates = stop_rows['Timestamp'].tolist()
        
    # If no failure dates found dynamically, hardcode B-167 known shutdown dates as fallback
    if len(failure_dates) == 0:
        failure_dates = [
            pd.to_datetime('2025-06-19 08:46:01').tz_localize('UTC'),
            pd.to_datetime('2025-06-29 10:29:01').tz_localize('UTC')
        ]
        
    # Calculate time to next failure in hours for each row
    df['time_to_failure'] = np.inf
    
    for f_date in failure_dates:
        # Convert f_date to pandas Timestamp with UTC
        f_date = pd.to_datetime(f_date)
        if f_date.tzinfo is None:
            f_date = f_date.tz_localize('UTC')
            
        time_diff = (f_date - df['Timestamp']).dt.total_seconds() / 3600.0
        # We only look at records BEFORE the failure date (time_diff >= 0)
        mask = (time_diff >= 0) & (time_diff < df['time_to_failure'])
        df.loc[mask, 'time_to_failure'] = time_diff[mask]

    # Assign labels based on windows (in hours)
    critical_hours = critical_days * 24
    warning_hours = warning_days * 24
    
    df['label'] = 'Healthy'
    df.loc[df['time_to_failure'] <= warning_hours, 'label'] = 'Warning'
    df.loc[df['time_to_failure'] <= critical_hours, 'label'] = 'Critical'
    
    # Assign continuous RUL label (cap at 90 days = 2160 hours)
    df['RUL_hours'] = df['time_to_failure'].clip(upper=2160)

    # Identify transient startup periods (first 48 hours after a Pump Start event)
    df['Is_Transient'] = False
    
    start_dates = []
    if 'Event' in df.columns:
        start_rows = df[df['Event'] == 'Pump Start']
        start_dates = start_rows['Timestamp'].tolist()
        
    # Mark rows falling within 48 hours after any start date
    for s_date in start_dates:
        s_date = pd.to_datetime(s_date)
        if s_date.tzinfo is None:
            s_date = s_date.tz_localize('UTC')
            
        time_diff_start = (df['Timestamp'] - s_date).dt.total_seconds() / 3600.0
        # 0 to 48 hours after startup
        mask_transient = (time_diff_start >= 0) & (time_diff_start <= 48.0)
        df.loc[mask_transient, 'Is_Transient'] = True
        
    return df

if __name__ == "__main__":
    from cleaner import load_raw_data, clean_data
    from feature_engineer import engineer_features
    
    raw_path = r"d:\مشروع التبؤ بصيانة مضخات النفط\Oil Pump Health Monitoring System\DataSet\Data_Export_Selected_B_167_01_Jan_2025_000000_01_Jul_2025_000000 (2).xlsx"
    if os.path.exists(raw_path):
        df_raw = load_raw_data(raw_path)
        df_clean = clean_data(df_raw)
        df_feat = engineer_features(df_clean)
        df_labeled = assign_labels(df_feat)
        
        print("Labeled shape:", df_labeled.shape)
        print("Label distributions:\n", df_labeled['label'].value_counts())
        print("Transient rows count:", df_labeled['Is_Transient'].sum())
    else:
        print("File path does not exist.")
