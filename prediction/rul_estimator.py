def estimate_rul(phi, degradation_rate, class_probs):
    """
    Estimates the Remaining Useful Life (RUL) of the pump in days.
    
    Parameters:
    - phi: Pump Health Index (0-100)
    - degradation_rate: PHI points lost per hour (positive float).
    - class_probs: list/array of [P(Healthy), P(Warning), P(Critical)]
    """
    # 1. Base RUL from PHI (in days)
    if phi >= 80.0:
        base_rul_days = (phi - 50.0) * 2.0  # Healthy: 60 to 100 days
    elif phi >= 60.0:
        base_rul_days = (phi - 40.0) * 1.0  # Monitor: 20 to 60 days
    elif phi >= 40.0:
        base_rul_days = (phi - 20.0) * 0.5  # Warning: 5 to 20 days
    else:
        base_rul_days = phi * 0.1  # Critical: 0 to 5 days
        
    # 2. Adjust by degradation rate (if active)
    # If degradation_rate > 0, calculate how many hours remain before PHI hits 0, and convert to days
    if degradation_rate > 0.0:
        estimated_remaining_days = (phi / degradation_rate) / 24.0
        base_rul_days = min(base_rul_days, estimated_remaining_days)
        
    # 3. Adjust by model classification probabilities
    critical_prob = class_probs[2]
    if critical_prob > 0.5:
        # Halve RUL if Critical probability is high
        base_rul_days *= 0.5
        
    return max(0, int(round(base_rul_days)))
