import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
import os

def evaluate_predictions(y_true, y_pred, y_prob=None, model_name="Model"):
    """
    Computes standard classification evaluation metrics.
    """
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision_macro': precision_score(y_true, y_pred, average='macro'),
        'recall_macro': recall_score(y_true, y_pred, average='macro'),
        'f1_macro': f1_score(y_true, y_pred, average='macro'),
        'f1_critical': f1_score(y_true, y_pred, labels=[2], average='macro'),
        'recall_critical': recall_score(y_true, y_pred, labels=[2], average='macro')
    }
    
    if y_prob is not None:
        try:
            # Multi-class ROC-AUC
            metrics['roc_auc'] = roc_auc_score(y_true, y_prob, multi_class='ovr', average='macro')
        except Exception:
            metrics['roc_auc'] = np.nan
            
    print(f"=== Evaluation Metrics for {model_name} ===")
    for k, v in metrics.items():
        print(f"{k.replace('_', ' ').title()}: {v:.4f}")
        
    return metrics

def plot_confusion_matrix(y_true, y_pred, output_path=None):
    """
    Plots confusion matrix and saves it as an image.
    """
    cm = confusion_matrix(y_true, y_pred)
    labels = ['Healthy', 'Warning', 'Critical']
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def get_feature_importances(model, feature_names):
    """
    Extracts feature importances from a tree-based model.
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)
        return feat_imp
    return None

def plot_feature_importances(feat_imp, top_n=20, output_path=None):
    """
    Plots the top N features by importance.
    """
    plt.figure(figsize=(10, 6))
    feat_imp.head(top_n).plot(kind='barh')
    plt.gca().invert_yaxis()
    plt.title(f'Top {top_n} Feature Importances')
    plt.xlabel('Importance Score')
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()
