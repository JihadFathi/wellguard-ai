import numpy as np

# Baseline Statistics for Well B-167 (from dynamic period)
BASELINES = {
    'Motor_Temperature': {'mean': 210.0, 'std': 0.3},
    'Motor_Current': {'mean': 32.3, 'std': 0.15},
    'Discharge_Pressure': {'mean': 2395.8, 'std': 9.0},
    'Intake_Pressure': {'mean': 837.8, 'std': 7.0}
}

def calculate_phi(model_probs, sensor_values, trend_features):
    """
    Computes the Pump Health Index (PHI) from 0 to 100.
    
    Parameters:
    - model_probs: list/array of [P(Healthy), P(Warning), P(Critical)]
    - sensor_values: dict of {'sensor_name': current_value}
    - trend_features: dict of {'sensor_name': current_trend}
    """
    # 1. Model-based score (0-100)
    # Healthy (Prob * 100) + Warning (Prob * 60) + Critical (Prob * 20)
    model_score = model_probs[0] * 100.0 + model_probs[1] * 60.0 + model_probs[2] * 20.0
    
    # 2. Sensor Deviation Score (z-score based)
    sensor_scores = []
    for sensor, val in sensor_values.items():
        if sensor in BASELINES:
            mean = BASELINES[sensor]['mean']
            std = BASELINES[sensor]['std']
            z = (val - mean) / (std + 1e-5)
            # score = 1 / (1 + |z|)
            score = 1.0 / (1.0 + abs(z))
            sensor_scores.append(score)
            
    if len(sensor_scores) > 0:
        sensor_score = np.mean(sensor_scores) * 100.0
    else:
        sensor_score = 100.0
        
    # 3. Trend Score
    # Negative trends (e.g. rising temp, falling pressure diff) reduce the trend score.
    # We assign:
    # - Temp trend > 2 F -> negative impact (-1.0)
    # - Pressure trend < -50 psi -> negative impact (-1.0)
    # - Current trend > 1 Amp -> negative impact (-1.0)
    # Else -> nominal (0.0 or 1.0)
    trend_scores_list = []
    
    if 'Motor_Temperature' in trend_features:
        temp_t = trend_features['Motor_Temperature']
        # Rising temperature is bad
        trend_scores_list.append(-1.0 if temp_t > 1.0 else 1.0)
        
    if 'Discharge_Pressure' in trend_features:
        pres_t = trend_features['Discharge_Pressure']
        # Falling discharge pressure is bad
        trend_scores_list.append(-1.0 if pres_t < -10.0 else 1.0)
        
    if 'Motor_Current' in trend_features:
        curr_t = trend_features['Motor_Current']
        # Rising current is bad
        trend_scores_list.append(-1.0 if curr_t > 0.5 else 1.0)
        
    if len(trend_scores_list) > 0:
        # Normalize mean of [-1, 1] to [0, 100]
        # (1 + mean) / 2 * 100
        trend_score = (1.0 + np.mean(trend_scores_list)) / 2.0 * 100.0
    else:
        trend_score = 100.0
        
    # 4. Weighted combination
    phi = 0.60 * model_score + 0.25 * sensor_score + 0.15 * trend_score
    
    return np.clip(phi, 0.0, 100.0)

def categorize_phi(phi):
    """
    Categorizes the Pump Health Index (PHI) into status and maintenance action.
    """
    if phi >= 95.0:
        return 'Excellent', 'Healthy', 'No action needed'
    elif phi >= 80.0:
        return 'Healthy', 'Healthy', 'Continue monitoring'
    elif phi >= 60.0:
        return 'Monitor', 'Warning', 'Increase monitoring frequency'
    elif phi >= 40.0:
        return 'Warning', 'Warning', 'Plan maintenance intervention'
    else:
        return 'Critical', 'Critical', 'Immediate intervention required'
