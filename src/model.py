"""
ML Model Module
XGBoost-based phishing detection model
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')


class PhishingModel:
    """XGBoost model for phishing detection"""
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.metrics = {}
        
    def train(self, X, y):
        """
        Train the phishing detection model
        
        Args:
            X: Feature DataFrame
            y: Labels (0=benign, 1=phishing)
        
        Returns:
            Dict with training metrics
        """
        self.feature_names = list(X.columns)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Initialize XGBoost classifier
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        
        # Train
        print("\nTraining XGBoost model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        self.metrics = {
            'roc_auc': roc_auc_score(y_test, y_prob),
            'pr_auc': average_precision_score(y_test, y_prob),
            'test_accuracy': (y_pred == y_test).mean(),
            'phishing_precision': None,
            'phishing_recall': None
        }
        
        # Get classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        if '1' in report:
            self.metrics['phishing_precision'] = report['1']['precision']
            self.metrics['phishing_recall'] = report['1']['recall']
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='roc_auc')
        self.metrics['cv_roc_auc_mean'] = cv_scores.mean()
        self.metrics['cv_roc_auc_std'] = cv_scores.std()
        
        print(f"\n[METRICS] Model Performance:")
        print(f"  ROC-AUC: {self.metrics['roc_auc']:.4f}")
        print(f"  PR-AUC: {self.metrics['pr_auc']:.4f}")
        print(f"  Test Accuracy: {self.metrics['test_accuracy']:.4f}")
        print(f"  CV ROC-AUC: {self.metrics['cv_roc_auc_mean']:.4f} (+/- {self.metrics['cv_roc_auc_std']*2:.4f})")
        
        return self.metrics
    
    def predict(self, X):
        """Predict labels for new data"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Predict probabilities for new data"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict_proba(X)
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        importance = self.model.feature_importances_
        feature_imp = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return feature_imp
    
    def save(self, model_dir='models'):
        """Save model to disk"""
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        
        # Save model
        joblib.dump(self.model, f'{model_dir}/xgboost_model.pkl')
        
        # Save feature names
        joblib.dump(self.feature_names, f'{model_dir}/feature_names.pkl')
        
        # Save metrics
        joblib.dump(self.metrics, f'{model_dir}/metrics.pkl')
        
        print(f"\n[SAVED] Model saved to {model_dir}/")
        print(f"   - xgboost_model.pkl")
        print(f"   - feature_names.pkl")
        print(f"   - metrics.pkl")
    
    def load(self, model_dir='models'):
        """Load model from disk"""
        self.model = joblib.load(f'{model_dir}/xgboost_model.pkl')
        self.feature_names = joblib.load(f'{model_dir}/feature_names.pkl')
        self.metrics = joblib.load(f'{model_dir}/metrics.pkl')
        print(f"📂 Model loaded from {model_dir}/")
        return self
