"""
Flask Web Application for PhishGuard AI
Connects the beautiful frontend with the ML backend
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from src.llm_analyzer import LLMAnalyzer
from src.features import URLFeatureExtractor
from src.brand_detector import BrandDetector
from src.explainer import URLExplainer
from src.maintenance import is_maintenance_mode, get_maintenance_status
import warnings
import os
from pathlib import Path

warnings.filterwarnings('ignore')

app = Flask(__name__, static_folder='static')

# Load both LLM and XGBoost components
def load_components():
    """Load LLM analyzer and XGBoost model"""
    llm_analyzer = None
    model = None
    feature_names = None
    brand_detector = None
    explainer = None
    
    # Load LLM Analyzer
    try:
        llm_analyzer = LLMAnalyzer()
        print("✅ LLM Analyzer loaded successfully")
    except Exception as e:
        print(f"❌ Error loading LLM Analyzer: {e}")
        print("⚠️ Make sure GROQ_API_KEY environment variable is set")
    
    # Load XGBoost Model
    try:
        model = joblib.load('models/xgboost_model.pkl')
        
        # Fix XGBoost version compatibility
        if hasattr(model, 'use_label_encoder'):
            delattr(model, 'use_label_encoder')
        
        feature_names = joblib.load('models/feature_names.pkl')
        brand_detector = BrandDetector()
        explainer = URLExplainer(model, feature_names)
        print("✅ XGBoost Model loaded successfully")
    except FileNotFoundError:
        print("⚠️ XGBoost Model not found. Please run `python train_model.py` first.")
    
    return llm_analyzer, model, feature_names, brand_detector, explainer

# Global components
llm_analyzer, model, feature_names, brand_detector, explainer = load_components()

@app.route('/')
def index():
    """Serve the main page"""
    # Check maintenance mode
    if is_maintenance_mode():
        return render_template('maintenance.html', status=get_maintenance_status())
    
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_url():
    """Analyze URL endpoint using Hybrid LLM + XGBoost approach"""
    try:
        # Check maintenance mode
        if is_maintenance_mode():
            return jsonify({
                'status': 'maintenance',
                'icon': 'fas fa-tools',
                'text': 'System Maintenance',
                'details': 'PhishGuard is updating with fresh threat data. Please try again in a few minutes.'
            })
        
        # Check if at least one analyzer is loaded
        if llm_analyzer is None and model is None:
            return jsonify({
                'status': 'error',
                'icon': 'fas fa-exclamation-circle',
                'text': 'Service Unavailable',
                'details': 'Neither LLM Analyzer nor XGBoost Model is available.'
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
        
        # Validate URL format - reject random text
        # Check if it looks like a URL or domain (contains at least one dot)
        if '.' not in url:
            return jsonify({
                'status': 'error',
                'icon': 'fas fa-exclamation-circle',
                'text': 'Invalid Input',
                'details': 'Please give in URL format (e.g., google.com or https://google.com)'
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
                'risk_score': '0.0',
                'brand_warning': False,
                'explanation': 'Domain is in our whitelist of verified legitimate websites.',
                'top_factors': [],
                'features_analyzed': 'Hybrid LLM + XGBoost'
            })
        
        # HYBRID ANALYSIS LOGIC
        llm_result = None
        xgboost_result = None
        final_status = 'suspicious'
        final_risk_score = 50
        final_reason = 'Analysis complete'
        
        # Step 1: LLM Analysis (if available)
        if llm_analyzer:
            try:
                llm_result = llm_analyzer.analyze_url(url)
                llm_risk = llm_result.get('risk_score', 50)
                
                # If LLM says safe (risk < 30%), trust it (LLM is conservative for safe URLs)
                if llm_risk < 30:
                    return jsonify({
                        'status': 'safe',
                        'icon': 'fas fa-check-circle',
                        'text': 'Safe to Proceed',
                        'details': llm_result.get('reason', 'LLM analysis indicates this URL is legitimate'),
                        'risk_score': f"{llm_risk}",
                        'brand_warning': False,
                        'explanation': llm_result.get('reason', ''),
                        'top_factors': [{'feature': factor, 'description': factor, 'impact': 0} for factor in llm_result.get('key_factors', [])],
                        'features_analyzed': 'Hybrid LLM + XGBoost'
                    })
            except Exception as e:
                print(f"LLM analysis failed: {e}")
        
        # Step 2: XGBoost Analysis (if available and LLM says suspicious)
        if model and feature_names:
            try:
                extractor = URLFeatureExtractor()
                features = extractor.extract_single(url)
                X = pd.DataFrame([features])[feature_names]
                
                # Apply label reversal fix
                risk_prob = model.predict_proba(X)[0][1]
                risk_prob = 1 - risk_prob  # FIX: Reverse the label reversal
                
                xgboost_risk = risk_prob * 100
                xgboost_result = {'risk_score': xgboost_risk}
                
                # Brand check
                brand_result = brand_detector.check_url(url)
                
                # Step 3: Decision Matrix
                if llm_result and xgboost_result:
                    llm_risk = llm_result.get('risk_score', 50)
                    
                    # Decision matrix logic
                    if llm_risk < 30:
                        final_status = 'safe'
                        final_risk_score = llm_risk
                        final_reason = llm_result.get('reason', 'LLM confirms safe')
                    elif llm_risk < 70 and xgboost_risk < 40:
                        final_status = 'safe'
                        final_risk_score = (llm_risk + xgboost_risk) / 2
                        final_reason = f"Both systems indicate safe (LLM: {llm_risk}%, XGBoost: {xgboost_risk:.1f}%)"
                    elif llm_risk < 70 and 40 <= xgboost_risk < 70:
                        final_status = 'suspicious'
                        final_risk_score = (llm_risk + xgboost_risk) / 2
                        final_reason = f"Systems disagree - conservative (LLM: {llm_risk}%, XGBoost: {xgboost_risk:.1f}%)"
                    elif llm_risk < 70 and xgboost_risk >= 70:
                        final_status = 'phishing'
                        final_risk_score = xgboost_risk
                        final_reason = f"XGBoost confident phishing (LLM: {llm_risk}%, XGBoost: {xgboost_risk:.1f}%)"
                    elif llm_risk >= 70 and xgboost_risk < 40:
                        final_status = 'suspicious'
                        final_risk_score = (llm_risk + xgboost_risk) / 2
                        final_reason = f"Systems disagree - conservative (LLM: {llm_risk}%, XGBoost: {xgboost_risk:.1f}%)"
                    elif llm_risk >= 70 and 40 <= xgboost_risk < 70:
                        final_status = 'phishing'
                        final_risk_score = (llm_risk + xgboost_risk) / 2
                        final_reason = f"Both systems indicate phishing (LLM: {llm_risk}%, XGBoost: {xgboost_risk:.1f}%)"
                    else:  # Both >= 70
                        final_status = 'phishing'
                        final_risk_score = max(llm_risk, xgboost_risk)
                        final_reason = f"Both systems confident phishing (LLM: {llm_risk}%, XGBoost: {xgboost_risk:.1f}%)"
                    
                    # Add brand warning if detected
                    if brand_result.get('is_suspicious', False):
                        if final_status == 'safe':
                            final_status = 'suspicious'
                        final_reason += f" Brand impersonation detected: {brand_result.get('matched_brand', 'unknown')}"
                    
                elif xgboost_result:  # Only XGBoost available
                    if xgboost_risk < 40:
                        final_status = 'safe'
                        final_risk_score = xgboost_risk
                        final_reason = f"XGBoost indicates safe ({xgboost_risk:.1f}%)"
                    elif xgboost_risk < 70:
                        final_status = 'suspicious'
                        final_risk_score = xgboost_risk
                        final_reason = f"XGBoost indicates suspicious ({xgboost_risk:.1f}%)"
                    else:
                        final_status = 'phishing'
                        final_risk_score = xgboost_risk
                        final_reason = f"XGBoost indicates phishing ({xgboost_risk:.1f}%)"
                    
                    # Add brand warning if detected
                    if brand_result.get('is_suspicious', False):
                        if final_status == 'safe':
                            final_status = 'suspicious'
                        final_reason += f" Brand impersonation detected: {brand_result.get('matched_brand', 'unknown')}"
                
            except Exception as e:
                print(f"XGBoost analysis failed: {e}")
        
        # Step 4: If only LLM available and it said suspicious
        if llm_result and not xgboost_result:
            llm_risk = llm_result.get('risk_score', 50)
            if llm_risk < 40:
                final_status = 'safe'
                final_risk_score = llm_risk
            elif llm_risk < 70:
                final_status = 'suspicious'
                final_risk_score = llm_risk
            else:
                final_status = 'phishing'
                final_risk_score = llm_risk
            final_reason = llm_result.get('reason', 'LLM analysis')
        
        # Map status to icon and text
        icon_mapping = {
            'safe': 'fas fa-check-circle',
            'suspicious': 'fas fa-exclamation-triangle',
            'phishing': 'fas fa-skull-crossbones'
        }
        
        text_mapping = {
            'safe': 'Safe to Proceed',
            'suspicious': 'Potentially Unsafe',
            'phishing': 'Phishing Detected!'
        }
        
        # Use LLM explanation if available, otherwise use final_reason
        if llm_result and llm_result.get('reason'):
            explanation_text = llm_result.get('reason')
            explanation_factors = [{'feature': factor, 'description': factor, 'impact': 0} for factor in llm_result.get('key_factors', [])]
        else:
            explanation_text = final_reason
            explanation_factors = []
        
        return jsonify({
            'status': final_status,
            'icon': icon_mapping.get(final_status, 'fas fa-exclamation-triangle'),
            'text': text_mapping.get(final_status, 'Potentially Unsafe'),
            'details': final_reason,
            'risk_score': f"{final_risk_score:.1f}",
            'brand_warning': brand_result.get('is_suspicious', False) if 'brand_result' in locals() else False,
            'explanation': explanation_text,
            'top_factors': explanation_factors,
            'features_analyzed': 'Hybrid LLM + XGBoost'
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
        'llm_loaded': llm_analyzer is not None,
        'xgboost_loaded': model is not None,
        'maintenance_mode': is_maintenance_mode()
    })

@app.route('/admin/maintenance/<action>')
def admin_maintenance(action):
    """Admin endpoint to toggle maintenance mode"""
    from src.maintenance import enable_maintenance_mode, disable_maintenance_mode
    
    if action == 'enable':
        enable_maintenance_mode(reason='Scheduled maintenance', estimated_minutes=30)
        return jsonify({'status': 'success', 'message': 'Maintenance mode enabled'})
    elif action == 'disable':
        disable_maintenance_mode()
        return jsonify({'status': 'success', 'message': 'Maintenance mode disabled'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid action'})

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
