"""
Flask Web Application for PhishGuard AI
Connects the beautiful frontend with the ML backend
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from src.features import URLFeatureExtractor
from src.brand_detector import BrandDetector
from src.explainer import URLExplainer
from src.maintenance import is_maintenance_mode, get_maintenance_status
import warnings
import os
from pathlib import Path

warnings.filterwarnings('ignore')

app = Flask(__name__, static_folder='static')

# Load ML components
def load_components():
    """Load model and components"""
    try:
        model = joblib.load('models/xgboost_model.pkl')
        feature_names = joblib.load('models/feature_names.pkl')
        brand_detector = BrandDetector()
        explainer = URLExplainer(model, feature_names)
        return model, feature_names, brand_detector, explainer
    except FileNotFoundError:
        print("⚠️ Model not found. Please run `python scripts/train_model.py` first.")
        return None, None, None, None

# Global components
model, feature_names, brand_detector, explainer = load_components()

@app.route('/')
def index():
    """Serve the main page"""
    # Check maintenance mode
    if is_maintenance_mode():
        return render_template('maintenance.html', status=get_maintenance_status())
    
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_url():
    """Analyze URL endpoint"""
    try:
        # Check maintenance mode
        if is_maintenance_mode():
            return jsonify({
                'status': 'maintenance',
                'icon': 'fas fa-tools',
                'text': 'System Maintenance',
                'details': 'PhishGuard is updating with fresh threat data. Please try again in a few minutes.'
            })
        
        # Check if model is loaded
        if model is None:
            return jsonify({
                'status': 'error',
                'icon': 'fas fa-exclamation-circle',
                'text': 'Service Unavailable',
                'details': 'AI model is not available. Please contact administrator.'
            })
        
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'status': 'error',
                'icon': 'fas fa-exclamation-circle',
                'text': 'Invalid Input',
                'details': 'Please enter a valid URL.'
            })
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Whitelist of known legitimate domains
        legitimate_domains = [
            'flipkart.com', 'amazon.com', 'amazon.in', 'google.com', 'youtube.com',
            'facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com',
            'microsoft.com', 'apple.com', 'netflix.com', 'spotify.com',
            'github.com', 'stackoverflow.com', 'wikipedia.org', 'reddit.com',
            'ebay.com', 'walmart.com', 'target.com', 'bestbuy.com',
            'myntra.com', 'snapdeal.com', 'paytm.com', 'phonepe.com'
        ]
        
        # Check if domain is in whitelist
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower().replace('www.', '')
        
        if any(domain.endswith(legit_domain) for legit_domain in legitimate_domains):
            return jsonify({
                'status': 'safe',
                'icon': 'fas fa-check-circle',
                'text': 'Verified Safe Domain',
                'details': f'This is a legitimate website ({domain}). The URL may have tracking parameters but the domain is trusted.',
                'risk_score': '0.0%',
                'brand_warning': False,
                'explanation': 'Domain is in our whitelist of verified legitimate websites.'
            })
        
        # Extract features
        extractor = URLFeatureExtractor()
        features = extractor.extract_single(url)
        
        # Predict
        X = pd.DataFrame([features])[feature_names]
        risk_prob = model.predict_proba(X)[0][1]
        
        # Brand check
        brand_result = brand_detector.check_url(url)
        
        # Get explanation
        explanation = explainer.explain(url, features, risk_prob)
        
        # Determine result status
        if risk_prob > 0.7:
            status = 'phishing'
            icon = 'fas fa-skull-crossbones'
            text = 'Phishing Detected!'
            details = f'High risk ({risk_prob*100:.1f}% confidence). This URL shows strong indicators of phishing.'
        elif risk_prob > 0.4:
            status = 'suspicious'
            icon = 'fas fa-exclamation-triangle'
            text = 'Potentially Unsafe'
            details = f'Medium risk ({risk_prob*100:.1f}% confidence). This URL has suspicious characteristics.'
        else:
            status = 'safe'
            icon = 'fas fa-check-circle'
            text = 'Safe to Proceed'
            details = f'Low risk ({risk_prob*100:.1f}% confidence). This URL appears legitimate.'
        
        # Add brand warning if detected
        if brand_result['is_suspicious']:
            if status == 'safe':
                status = 'suspicious'
                icon = 'fas fa-exclamation-triangle'
                text = 'Brand Impersonation Detected'
            details += f' Brand impersonation detected: {brand_result["matched_brand"]} ({brand_result["reason"]}).'
        
        # Add top risk factors
        risk_factors = []
        for factor in explanation['top_factors'][:3]:
            if factor['impact'] > 0:
                risk_factors.append(factor['feature'])
        
        if risk_factors:
            details += f' Key concerns: {", ".join(risk_factors)}.'
        
        # Build detailed explanation with SHAP-style breakdown
        detailed_explanation = explanation['summary']
        if len(detailed_explanation) > 300:
            detailed_explanation = detailed_explanation[:297] + '...'
        
        # Add top factors with impact scores
        factors_data = []
        for factor in explanation['top_factors'][:5]:
            factors_data.append({
                'feature': factor['feature'],
                'description': factor['description'],
                'impact': factor['impact']
            })
        
        return jsonify({
            'status': status,
            'icon': icon,
            'text': text,
            'details': details,
            'risk_score': f'{risk_prob*100:.1f}%',
            'brand_warning': brand_result['is_suspicious'],
            'explanation': detailed_explanation,
            'top_factors': factors_data,
            'features_analyzed': len(features)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'icon': 'fas fa-exclamation-circle',
            'text': 'Analysis Failed',
            'details': f'An error occurred during analysis: {str(e)}'
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'maintenance_mode': is_maintenance_mode()
    })

if __name__ == '__main__':
    # Create templates directory
    Path('templates').mkdir(exist_ok=True)
    
    # Check if running in production (AWS, Render, Railway, etc.)
    import os
    is_production = os.environ.get('RENDER') or os.environ.get('RAILWAY') or os.environ.get('AWS_REGION')
    port = int(os.environ.get('PORT', 5000))
    
    if not is_production:
        print("🚀 Starting PhishGuard AI Web Server...")
        print(f"🌐 Access at: http://localhost:{port}")
        print("🛡️ Ready to protect users!")
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        # Production: gunicorn handles the server
        print("🚀 PhishGuard AI starting in production mode...")
        app.run(debug=False, host='0.0.0.0', port=port)
