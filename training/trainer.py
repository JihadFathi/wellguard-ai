import pandas as pd
import numpy as np
import os
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import classification_report, f1_score, recall_score

# Try to import XGBoost and LightGBM
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    import lightgbm as lgb
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

# Import preprocessing pipeline
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.cleaner import load_raw_data, clean_data
from preprocessing.feature_engineer import engineer_features
from preprocessing.labeler import assign_labels

def prepare_training_data(raw_path):
    df_raw = load_raw_data(raw_path)
    df_clean = clean_data(df_raw)
    df_feat = engineer_features(df_clean)
    df_labeled = assign_labels(df_feat)
    
    # Filter out transient rows
    df_filtered = df_labeled[df_labeled['Is_Transient'] == False].reset_index(drop=True)
    
    # Target columns to drop from feature list
    non_feature_cols = [
        'Timestamp', 'Well_ID', 'Event', 'Quality for Event Compute',
        'Classification', 'Severity', 'Symptom', 'Probable Cause',
        'Shutdown_Cause', 'Shutdown Cause', 'Recommendation', 
        'label', 'time_to_failure', 'RUL_hours', 'Is_Transient'
    ]
    
    feature_cols = [c for c in df_filtered.columns if c not in non_feature_cols]
    
    X = df_filtered[feature_cols].copy()
    for col in X.columns:
        if X[col].isnull().any():
            X[col] = X[col].fillna(0.0)
            
    y = df_filtered['label'].copy()
    
    label_map = {'Healthy': 0, 'Warning': 1, 'Critical': 2}
    y_encoded = y.map(label_map)
    
    return X, y_encoded, feature_cols, df_filtered

def split_and_scale_data(X, y):
    """
    Splits the data using a stratified split to ensure representation of all classes in train, val, and test.
    """
    # 70% train, 30% temp (which will be split into 15% val and 15% test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )
    
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert back to DataFrame
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
    X_val_scaled = pd.DataFrame(X_val_scaled, columns=X.columns)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)
    
    return X_train_scaled, y_train, X_val_scaled, y_val, X_test_scaled, y_test, scaler

def train_and_evaluate_models(X_train, y_train, X_val, y_val):
    sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=15, class_weight='balanced', random_state=42)
    }
    
    if XGB_AVAILABLE:
        models['XGBoost'] = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric='mlogloss')
    if LGBM_AVAILABLE:
        models['LightGBM'] = lgb.LGBMClassifier(n_estimators=100, max_depth=8, learning_rate=0.1, class_weight='balanced', random_state=42, verbose=-1)
        
    models['Gradient Boosting'] = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    
    best_score = -1
    best_model_name = None
    best_model = None
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        try:
            if name in ['XGBoost', 'Gradient Boosting']:
                model.fit(X_train, y_train, sample_weight=sample_weights)
            else:
                model.fit(X_train, y_train)
                
            val_preds = model.predict(X_val)
            
            macro_f1 = f1_score(y_val, val_preds, average='macro')
            critical_recall = recall_score(y_val, val_preds, labels=[2], average='macro')
            
            print(f"{name} Validation Macro F1: {macro_f1:.4f} | Critical Class Recall: {critical_recall:.4f}")
            results[name] = {'macro_f1': macro_f1, 'critical_recall': critical_recall, 'model': model}
            
            selection_score = 0.5 * macro_f1 + 0.5 * critical_recall
            if selection_score > best_score:
                best_score = selection_score
                best_model_name = name
                best_model = model
                
        except Exception as e:
            print(f"Error training {name}: {e}")
            
    print(f"\n--> Best model selected: {best_model_name}")
    return best_model, best_model_name, results

def save_artifacts(model, scaler, feature_cols, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    
    with open(os.path.join(target_dir, 'best_model.pkl'), 'wb') as f:
        pickle.dump(model, f)
        
    with open(os.path.join(target_dir, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
        
    config = {
        'feature_names': feature_cols,
        'label_map': {'Healthy': 0, 'Warning': 1, 'Critical': 2},
        'reverse_label_map': {0: 'Healthy', 1: 'Warning', 2: 'Critical'}
    }
    config_dir = os.path.join(os.path.dirname(target_dir), 'configs')
    os.makedirs(config_dir, exist_ok=True)
    with open(os.path.join(config_dir, 'model_configs.json'), 'w') as f:
        json.dump(config, f, indent=4)
        
    print(f"Artifacts saved successfully in {target_dir}")

def run_pipeline():
    raw_path = r"d:\مشروع التبؤ بصيانة مضخات النفط\Oil Pump Health Monitoring System\DataSet\Data_Export_Selected_B_167_01_Jan_2025_000000_01_Jul_2025_000000 (2).xlsx"
    target_dir = r"d:\مشروع التبؤ بصيانة مضخات النفط\Oil Pump Health Monitoring System\Project\models\trained"
    
    print("Preparing training data...")
    X, y, feature_cols, df_labeled = prepare_training_data(raw_path)
    
    print("\nSplitting and scaling...")
    X_train, y_train, X_val, y_val, X_test, y_test, scaler = split_and_scale_data(X, y)
    
    print("\nTraining and comparing models...")
    best_model, best_name, results = train_and_evaluate_models(X_train, y_train, X_val, y_val)
    
    test_preds = best_model.predict(X_test)
    print("\n=== Final Test Set Evaluation (Best Model: {}) ===".format(best_name))
    print(classification_report(y_test, test_preds, target_names=['Healthy', 'Warning', 'Critical']))
    
    save_artifacts(best_model, scaler, feature_cols, target_dir)

if __name__ == "__main__":
    run_pipeline()
