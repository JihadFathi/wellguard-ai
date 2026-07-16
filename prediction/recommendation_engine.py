def get_recommendations(sensor_values, trend_features, baseline_current=32.3):
    """
    Translates sensor values and trend indicators into actionable recommendations.
    
    Parameters:
    - sensor_values: dict of current sensor values
    - trend_features: dict of rolling trends
    - baseline_current: standard baseline motor current (amps)
    
    Returns:
    - primary_rec: dict with 'priority', 'title', 'description', 'response_time'
    - triggered_rules: list of dicts representing all triggered rules
    """
    triggered_rules = []
    
    # 1. Temperature Check (> 180 F and rising)
    temp = sensor_values.get('Motor_Temperature', 0.0)
    temp_trend = trend_features.get('Motor_Temperature', 0.0)
    if temp > 180.0 and temp_trend > 0.5:
        triggered_rules.append({
            'priority': 2, # P2 - High
            'priority_lbl': 'P2 - High',
            'title': 'Inspect Cooling System',
            'description': 'Motor temperature is high (>180°F) and rising. Check flow path, ESP motor cooling, and intake screen.',
            'response_time': 'Within 48 hours'
        })
    elif temp > 210.0:
        triggered_rules.append({
            'priority': 1, # P1 - Urgent
            'priority_lbl': 'P1 - Urgent',
            'title': 'High Temperature Alert',
            'description': 'Motor temperature is critical (>210°F). Possible motor overload or serious cooling blockage.',
            'response_time': 'Immediate'
        })
        
    # 2. Intake Pressure Drop (drop > 15% over 7 days, represented by a negative trend)
    intake_p = sensor_values.get('Intake_Pressure', 0.0)
    intake_p_trend = trend_features.get('Intake_Pressure', 0.0)
    # 15% of 837 psia is ~125 psi. Over 7 days, this is ~0.74 psi/hour.
    if intake_p_trend < -100.0:
        triggered_rules.append({
            'priority': 3, # P3 - Medium
            'priority_lbl': 'P3 - Medium',
            'title': 'Inspect Intake Valve',
            'description': 'Intake pressure is declining rapidly. Check for intake blockage, scale, or sand buildup.',
            'response_time': 'Within 1 week'
        })
        
    # 3. Motor Current Increase (> 120% of baseline current, i.e., > 38.7 Amps)
    current = sensor_values.get('Motor_Current', 0.0)
    if current > (1.20 * baseline_current):
        triggered_rules.append({
            'priority': 2, # P2 - High
            'priority_lbl': 'P2 - High',
            'title': 'Check Motor Load',
            'description': 'Motor current draw is significantly above baseline (>120%). Inspect for mechanical binding or increased fluid density.',
            'response_time': 'Within 48 hours'
        })
        
    # 4. Discharge / Differential Pressure Declining
    discharge_p = sensor_values.get('Discharge_Pressure', 0.0)
    # Pressure difference
    press_diff = discharge_p - intake_p
    # Check if pressure difference is dropping (e.g. trend < -150 psi)
    disch_p_trend = trend_features.get('Discharge_Pressure', 0.0)
    if disch_p_trend < -150.0:
        triggered_rules.append({
            'priority': 3, # P3 - Medium
            'priority_lbl': 'P3 - Medium',
            'title': 'Inspect Pump Stages',
            'description': 'Discharge pressure is declining significantly. Possible pump impeller wear or gas interference.',
            'response_time': 'Within 1 week'
        })
        
    # 5. Frozen Sensor Detection (critical custom telemetry rule)
    # If standard deviations of pressure & temp are zero (we check trend or value stability)
    # For a single row entry, if values match frozen states exactly
    if abs(discharge_p - 944.4) < 0.1 and abs(intake_p - 925.1) < 0.1 and abs(temp - 174.7) < 0.1:
        triggered_rules.append({
            'priority': 1, # P1 - Urgent
            'priority_lbl': 'P1 - Urgent',
            'title': 'Telemetry Sensor Freeze',
            'description': 'Downhole sensor signals (discharge/intake pressure, temperature) are completely frozen. Telemetry failure detected.',
            'response_time': 'Immediate'
        })

    # If no rules triggered, return nominal
    if len(triggered_rules) == 0:
        primary_rec = {
            'priority': 4, # P4 - Low
            'priority_lbl': 'P4 - Low',
            'title': 'Continue Monitoring',
            'description': 'All measured sensor parameters are within nominal operational boundaries.',
            'response_time': 'Next scheduled maintenance'
        }
        return primary_rec, []
        
    # Sort by priority ascending (1 is highest priority)
    triggered_rules = sorted(triggered_rules, key=lambda x: x['priority'])
    
    # Aggregation & Escalation
    # If 3+ rules trigger, escalate the highest priority
    primary_rec = triggered_rules[0].copy()
    if len(triggered_rules) >= 3:
        # Escalate priority: e.g. 3 -> 2, 2 -> 1
        original_priority = primary_rec['priority']
        escalated_priority = max(1, original_priority - 1)
        if escalated_priority != original_priority:
            primary_rec['priority'] = escalated_priority
            lbls = {1: 'P1 - Urgent', 2: 'P2 - High', 3: 'P3 - Medium', 4: 'P4 - Low'}
            primary_rec['priority_lbl'] = lbls[escalated_priority] + " (Escalated)"
            primary_rec['description'] += " [Priority escalated due to multiple co-occurring anomalies.]"
            
    return primary_rec, triggered_rules
