import os
import pickle
import json
import pandas as pd
import numpy as np

# Import preprocessing pipelines
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.cleaner import clean_data
from preprocessing.feature_engineer import engineer_features
from prediction.health_index import calculate_phi, categorize_phi
from prediction.rul_estimator import estimate_rul
from prediction.recommendation_engine import get_recommendations

class PumpPredictor:
    """
    Main inference predictor for WellGuard AI pump health monitoring system.
    """
    def __init__(self, models_dir=None):
        if models_dir is None:
            # Default directory
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'trained')
            
        self.models_dir = models_dir
        self.model_path = os.path.join(models_dir, 'best_model.pkl')
        self.scaler_path = os.path.join(models_dir, 'scaler.pkl')
        self.config_path = os.path.join(os.path.dirname(models_dir), 'configs', 'model_configs.json')
        
        # Load artifacts
        self.load_artifacts()

    def load_artifacts(self):
        """Loads serialized model, scaler, and config files."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            raise FileNotFoundError(f"Trained model artifacts not found in {self.models_dir}. Please run training first.")
            
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        with open(self.scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
            
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            
        self.feature_names = self.config['feature_names']
        self.reverse_label_map = {int(k): v for k, v in self.config['reverse_label_map'].items()}

    def predict_single(self, sensor_values, trend_features):
        """
        Runs prediction on a single instance of current sensor inputs.
        
        Parameters:
        - sensor_values: dict of {'sensor_name': value}
        - trend_features: dict of {'sensor_name': trend_value}
        
        Returns:
        - dict containing full prediction details.
        """
        # Create a single row DataFrame of the raw inputs
        # Combine sensor_values and trend_features into a dictionary
        input_data = {}
        # Fill in raw sensor values
        for k, v in sensor_values.items():
            input_data[k] = v
            
        # We need to construct the full engineered feature set
        # Since we cannot easily run rolling operations on a single row,
        # we construct the engineered features manually or fallback to baselines
        engineered_inputs = {}
        
        # Calculate Pressure Differentials
        discharge_p = sensor_values.get('Discharge_Pressure', 0.0)
        intake_p = sensor_values.get('Intake_Pressure', 0.0)
        engineered_inputs['Pressure_Difference'] = discharge_p - intake_p
        engineered_inputs['Pressure_Ratio'] = discharge_p / (intake_p + 1e-5)
        
        # Voltage-Current Ratio
        current = sensor_values.get('Motor_Current', 0.0)
        engineered_inputs['Voltage_Current_Ratio'] = 480.0 / (current + 1e-5)
        
        # Set rolling features to their current values (means) or general stats
        for col in ['Motor_Current', 'Discharge_Pressure', 'Intake_Pressure', 'Motor_Temperature']:
            val = sensor_values.get(col, 0.0)
            # Fill rolling means
            for w in ['3h', '6h', '12h', '24h']:
                engineered_inputs[f'{col}_mean_{w}'] = val
                engineered_inputs[f'{col}_min_{w}'] = val
                engineered_inputs[f'{col}_max_{w}'] = val
                # Std dev is zero if we have no history, or standard historical std dev if known
                engineered_inputs[f'{col}_std_{w}'] = 0.0
                
        # Fill trend features
        engineered_inputs['Temp_Trend'] = trend_features.get('Motor_Temperature', 0.0)
        engineered_inputs['Temp_Acceleration'] = 0.0
        engineered_inputs['Pressure_Trend'] = trend_features.get('Discharge_Pressure', 0.0)
        engineered_inputs['Current_Trend'] = trend_features.get('Motor_Current', 0.0)
        
        # Change rates
        for col in ['Motor_Current', 'Discharge_Pressure', 'Intake_Pressure', 'Motor_Temperature']:
            engineered_inputs[f'{col}_change_rate_1h'] = trend_features.get(col, 0.0)
            
        # Hours since restart
        engineered_inputs['Hours_Since_Restart'] = sensor_values.get('Hours_Since_Restart', 24.0)
        
        # Interaction features
        temp = sensor_values.get('Motor_Temperature', 0.0)
        engineered_inputs['Temp_x_Current'] = temp * current
        engineered_inputs['Temp_x_Pressure_Ratio'] = temp / (engineered_inputs['Pressure_Ratio'] + 1e-5)
        
        # Build the final array in the exact feature ordering
        feature_vector = []
        for name in self.feature_names:
            val = engineered_inputs.get(name, 0.0)
            feature_vector.append(val)
            
        # Reshape for scaling — wrap in DataFrame to avoid sklearn feature-name warning
        feature_df = pd.DataFrame([feature_vector], columns=self.feature_names)
        
        # Scale and predict
        scaled_vector = self.scaler.transform(feature_df)
        pred_df = pd.DataFrame(scaled_vector, columns=self.feature_names)
        pred_class = self.model.predict(pred_df)[0]
        
        # Get probability
        if hasattr(self.model, 'predict_proba'):
            probs = self.model.predict_proba(pred_df)[0]
        else:
            # Fallback uniform
            probs = np.array([0.0, 0.0, 0.0])
            probs[pred_class] = 1.0
            
        # Get label
        label = self.reverse_label_map.get(pred_class, 'Unknown')
        
        # Calculate Pump Health Index (PHI)
        phi = calculate_phi(probs, sensor_values, trend_features)
        status, severity_class, action = categorize_phi(phi)
        
        # Calculate Remaining Useful Life (RUL)
        # Compute degradation rate: standard default or dynamically checked
        # Let's assume degradation rate is 0 unless temp/pressure trend is high
        temp_trend = trend_features.get('Motor_Temperature', 0.0)
        degradation_rate = 0.0
        if temp_trend > 0.5:
            # Temperature rise degrades health
            degradation_rate += 0.1
        if trend_features.get('Discharge_Pressure', 0.0) < -10.0:
            # Pressure drop degrades health
            degradation_rate += 0.2
            
        rul_days = estimate_rul(phi, degradation_rate, probs)
        
        # Get recommendations
        rec_summary, triggered_recs = get_recommendations(sensor_values, trend_features)
        
        return {
            'label': label,
            'probabilities': probs.tolist(),
            'health_index': phi,
            'status': status,
            'action': action,
            'rul_days': rul_days,
            'primary_recommendation': rec_summary,
            'all_triggered_recommendations': triggered_recs
        }

    def predict_batch(self, df):
        """
        Runs prediction pipeline on an entire batch dataset.
        
        Parameters:
        - df: Raw DataFrame containing sensor reading columns.
        
        Returns:
        - df_out: DataFrame with prepended health predictions, PHI, RUL, and recommendations.
        """
        # 1. Clean and engineer features
        df_clean = clean_data(df)
        df_feat = engineer_features(df_clean)
        
        # 2. Extract features matching feature names
        X = df_feat[self.feature_names].copy()
        # Fill missing values
        for col in X.columns:
            if X[col].isnull().any():
                X[col] = X[col].fillna(0.0)
                
        # 3. Scale and predict
        X_scaled = self.scaler.transform(X)
        preds = self.model.predict(X_scaled)
        
        if hasattr(self.model, 'predict_proba'):
            probs = self.model.predict_proba(X_scaled)
        else:
            probs = np.zeros((len(df_feat), 3))
            for i, p in enumerate(preds):
                probs[i, p] = 1.0
                
        # Map predictions to label names
        pred_labels = [self.reverse_label_map[p] for p in preds]
        
        # 4. Calculate PHI and RUL for each row in batch
        phi_scores = []
        rul_forecasts = []
        status_labels = []
        action_labels = []
        
        for i in range(len(df_feat)):
            row = df_feat.iloc[i]
            
            # Construct dict for current sensor values and trend features
            sensor_vals = {
                'Motor_Temperature': row.get('Motor_Temperature', 0.0),
                'Motor_Current': row.get('Motor_Current', 0.0),
                'Discharge_Pressure': row.get('Discharge_Pressure', 0.0),
                'Intake_Pressure': row.get('Intake_Pressure', 0.0)
            }
            
            trend_vals = {
                'Motor_Temperature': row.get('Temp_Trend', 0.0),
                'Discharge_Pressure': row.get('Pressure_Trend', 0.0),
                'Motor_Current': row.get('Current_Trend', 0.0)
            }
            
            # PHI
            phi = calculate_phi(probs[i], sensor_vals, trend_vals)
            status, severity_class, action = categorize_phi(phi)
            
            # RUL
            # Dynamic degradation rate
            deg_rate = 0.0
            if trend_vals['Motor_Temperature'] > 0.5:
                deg_rate += 0.1
            if trend_vals['Discharge_Pressure'] < -10.0:
                deg_rate += 0.2
                
            rul = estimate_rul(phi, deg_rate, probs[i])
            
            phi_scores.append(phi)
            rul_forecasts.append(rul)
            status_labels.append(status)
            action_labels.append(action)
            
        # Append to output dataframe
        df_out = df_feat.copy()
        df_out['predicted_label'] = pred_labels
        df_out['health_index'] = phi_scores
        df_out['health_status'] = status_labels
        df_out['action_recommendation'] = action_labels
        df_out['rul_days'] = rul_forecasts
        
        return df_out
