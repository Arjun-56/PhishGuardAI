"""
Explainability Module
Provides SHAP-based explanations for predictions
"""

import pandas as pd
import numpy as np
import shap
import warnings
warnings.filterwarnings('ignore')


class URLExplainer:
    """Generate explanations for URL predictions using SHAP"""
    
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self._setup_explainer()
    
    def _setup_explainer(self):
        """Initialize SHAP explainer"""
        try:
            # Try TreeExplainer for tree-based models
            self.explainer = shap.TreeExplainer(self.model)
        except:
            # Fallback to KernelExplainer
            self.explainer = None
    
    def explain(self, url, features, prediction_prob):
        """
        Generate explanation for a prediction
        
        Args:
            url: The URL being analyzed
            features: Dict of extracted features
            prediction_prob: Probability of phishing (0-1)
        
        Returns:
            Dict with explanation details
        """
        # Create feature DataFrame
        X = pd.DataFrame([features])[self.feature_names]
        
        # Get feature importance
        top_factors = self._get_top_factors(features, prediction_prob)
        
        # Generate human-readable summary
        summary = self._generate_summary(url, prediction_prob, top_factors)
        
        return {
            'top_factors': top_factors,
            'summary': summary,
            'risk_score': prediction_prob,
            'url': url
        }
    
    def _get_top_factors(self, features, prediction_prob):
        """Get top contributing features"""
        factors = []
        
        # Feature descriptions and risk assessment
        feature_descriptions = {
            'url_length': ('URL Length', 'Very long URLs are often used to hide malicious content'),
            'domain_length': ('Domain Length', 'Unusually long domains may be suspicious'),
            'subdomain_count': ('Number of Subdomains', 'Multiple subdomains can indicate phishing'),
            'path_depth': ('Path Depth', 'Deep paths may hide malicious scripts'),
            'has_https': ('HTTPS Security', 'HTTPS provides encryption (positive indicator)'),
            'has_http': ('HTTP (no SSL)', 'Unencrypted connection is less secure'),
            'suspicious_keywords': ('Suspicious Keywords', 'Words like "login" or "verify" in URLs are red flags'),
            'has_ip_address': ('IP Address in URL', 'URLs with IP addresses instead of domains are suspicious'),
            'is_shortened': ('URL Shortener', 'Shortened URLs can hide the true destination'),
            'has_brand_name': ('Brand Name Present', 'Brand names in non-official domains may be impersonation'),
            'has_suspicious_tld': ('Suspicious Domain Extension', 'Some TLDs are frequently used for malicious sites'),
            'entropy': ('Domain Randomness', 'High randomness suggests auto-generated malicious domains'),
            'dot_count': ('Dot Count', 'Excessive dots can indicate subdomain abuse'),
            'hyphen_count': ('Hyphen Count', 'Many hyphens are sometimes used in phishing domains'),
            'digit_count': ('Digit Count', 'Many digits in domain names can be suspicious'),
        }
        
        # Score each feature based on its risk contribution
        for feature, value in features.items():
            if feature not in self.feature_names:
                continue
                
            impact = 0
            description = feature_descriptions.get(feature, (feature, 'No description available'))[1]
            display_name = feature_descriptions.get(feature, (feature, ''))[0]
            
            # Calculate impact based on feature type and value
            if feature == 'url_length' and value > 75:
                impact = min((value - 50) / 100, 1.0)
            elif feature == 'domain_length' and value > 30:
                impact = min((value - 20) / 50, 1.0)
            elif feature == 'subdomain_count' and value > 2:
                impact = min(value / 5, 1.0)
            elif feature == 'path_depth' and value > 3:
                impact = min(value / 8, 1.0)
            elif feature == 'suspicious_keywords' and value > 0:
                impact = min(value * 0.3, 1.0)
            elif feature == 'has_ip_address' and value == 1:
                impact = 0.8
            elif feature == 'is_shortened' and value == 1:
                impact = 0.5
            elif feature == 'has_suspicious_tld' and value == 1:
                impact = 0.7
            elif feature == 'entropy' and value > 4.0:
                impact = min((value - 3) / 2, 1.0)
            elif feature == 'has_http' and value == 1:
                impact = 0.3
            elif feature == 'has_https' and value == 0:
                impact = 0.2
            
            if impact > 0:
                factors.append({
                    'feature': display_name,
                    'value': value,
                    'impact': impact,
                    'description': description
                })
        
        # Sort by impact
        factors.sort(key=lambda x: abs(x['impact']), reverse=True)
        
        return factors
    
    def _generate_summary(self, url, risk_score, factors):
        """Generate human-readable summary"""
        if risk_score > 0.7:
            risk_level = "HIGH RISK"
            summary = f"This URL has been flagged as {risk_level} with {risk_score*100:.1f}% confidence. "
        elif risk_score > 0.4:
            risk_level = "MEDIUM RISK"
            summary = f"This URL shows {risk_level} with {risk_score*100:.1f}% confidence. "
        else:
            risk_level = "LOW RISK"
            summary = f"This URL appears to be {risk_level} with {risk_score*100:.1f}% confidence. "
        
        if factors:
            summary += "Key indicators: "
            indicator_list = [f"{f['feature']} ({f['description']})" for f in factors[:3]]
            summary += "; ".join(indicator_list) + "."
        else:
            summary += "No significant risk indicators detected."
        
        return summary
