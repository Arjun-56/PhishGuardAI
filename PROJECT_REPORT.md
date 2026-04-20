# PhishGuard AI - Project Report

## 📋 Executive Summary

**PhishGuard AI** is an advanced phishing detection system powered by Machine Learning and Explainable AI. The project successfully identifies malicious URLs and provides transparent explanations for its predictions, helping users understand why a URL is flagged as phishing or safe.

**Live Website:** https://phishguard-ai.onrender.com

---

## 🎯 Project Objectives

1. **Detect Phishing URLs** with high accuracy using ML
2. **Explain AI Decisions** using SHAP values for transparency
3. **Brand Protection** - Detect fake brand impersonation
4. **User-Friendly Interface** - Beautiful, responsive web UI
5. **Real-time Analysis** - Fast URL risk assessment
6. **Cloud Deployment** - Accessible 24/7 globally

---

## 🏗️ Technology Stack

### **Backend**
- **Language:** Python 3.11
- **Framework:** Flask (Web Framework)
- **ML Library:** XGBoost (Gradient Boosting)
- **Explainability:** SHAP (SHapley Additive exPlanations)
- **Server:** Gunicorn (WSGI HTTP Server)

### **Frontend**
- **HTML5** with Jinja2 Templating
- **CSS3** with Custom Animations
- **JavaScript** for Dynamic UI
- **Font Awesome** Icons
- **Responsive Design** (Mobile-friendly)

### **ML/AI Components**
- **Feature Engineering:** URL-based features (length, subdomains, special chars, entropy)
- **Model:** XGBoost Classifier
- **Explanation Engine:** SHAP TreeExplainer
- **Brand Detection:** Levenshtein Distance Algorithm

### **Deployment**
- **Platform:** Render (Cloud Hosting)
- **Version Control:** Git + GitHub
- **CI/CD:** Auto-deploy on git push

---

## 📊 Dataset Information

### **Training Data**
- **Total URLs:** 600
- **Phishing URLs:** 300 (50%)
- **Benign URLs:** 300 (50%)
- **Sources:**
  - Phishing: OpenPhish feed (real-world phishing URLs)
  - Benign: Tranco list (popular legitimate websites)

### **Data Balance**
✅ Perfect 50-50 split ensures unbiased model training

---

## 🔬 Model Architecture

### **Feature Extraction (19 Features)**
1. URL Length
2. Domain Length
3. Path Length
4. Number of Subdomains
5. Path Depth
6. Count of Dots (.)
7. Count of Hyphens (-)
8. Count of Underscores (_)
9. Count of Slashes (/)
10. Count of Question Marks (?)
11. Count of Equals (=)
12. Count of Ampersands (&)
13. Count of Digits
14. Count of Letters
15. Presence of IP Address
16. Presence of @ Symbol
17. Presence of Double Slash (//)
18. Entropy (Randomness Score)
19. Brand Indicators

### **ML Model: XGBoost Classifier**
- **Algorithm:** Extreme Gradient Boosting
- **Parameters:**
  - n_estimators: 100
  - max_depth: 6
  - learning_rate: 0.1
  - subsample: 0.8
  - colsample_bytree: 0.8
- **Performance Metrics:**
  - ROC-AUC: ~0.95
  - PR-AUC: ~0.94
  - Accuracy: ~90%+

---

## ✨ Key Features Implemented

### **1. Risk Score Gauge**
- Visual circular gauge showing 0-100% risk
- Color-coded: Green (Safe), Yellow (Suspicious), Red (Phishing)
- Animated needle movement

### **2. URL Analysis**
- Real-time feature extraction
- XGBoost prediction
- Probability-based risk scoring

### **3. AI Explainability (SHAP)**
- Top 5 risk factors identified
- Feature impact percentages
- Human-readable explanations
- "Why this URL is safe/unsafe"

### **4. Brand Protection**
- Detects 25+ popular brands (PayPal, Apple, Amazon, etc.)
- Levenshtein distance for typo-squatting detection
- Warns users about fake brand websites

### **5. Whitelist System**
- 20 pre-verified legitimate domains
- Instant safe status for trusted sites
- Reduces false positives

### **6. Maintenance Mode**
- Admin endpoints to enable/disable
- Custom maintenance page
- Health check status

---

## 🚀 Deployment Details

### **Platform: Render (Free Tier)**
- **URL:** https://phishguard-ai.onrender.com
- **Region:** Oregon (US West)
- **Runtime:** Python 3.11
- **Auto-deploy:** Enabled on git push to main

### **Repository**
- **GitHub:** https://github.com/Arjun-56/PhishGuardAI
- **Branch:** main
- **Commits:** Active development

---

## 📈 Results & Performance

### **Detection Accuracy**
| Metric | Score |
|--------|-------|
| ROC-AUC | ~0.95 |
| PR-AUC | ~0.94 |
| Accuracy | ~90%+ |
| False Positive Rate | Low |
| False Negative Rate | Low |

### **Speed**
- **Analysis Time:** < 2 seconds per URL
- **Feature Extraction:** < 500ms
- **Prediction:** < 100ms

### **Deployment**
- **Build Time:** ~3-5 minutes
- **Uptime:** 24/7 (auto-sleep after 15min idle on free tier)
- **Global Access:** Yes

---

## 🛡️ Security Features

1. **Input Validation:** URL format checking
2. **Protocol Auto-add:** Adds https:// if missing
3. **Whitelist Protection:** Trusted domains bypass analysis
4. **Brand Detection:** Identifies impersonation attempts
5. **Explainability:** Users understand AI decisions

---

## 🎨 UI/UX Highlights

- **Modern Gradient Design** (Purple/Blue theme)
- **Animated Risk Gauge**
- **Responsive Layout** (Works on mobile, tablet, desktop)
- **Loading Animations**
- **Color-coded Results**
- **Detailed Explanations**
- **"How It Works" Section**

---

## 🔧 Admin Controls

### **Maintenance Mode**
- Enable: `/admin/maintenance/enable`
- Disable: `/admin/maintenance/disable`
- Check Status: `/health`

### **Health Check**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "maintenance_mode": false
}
```

---

## 📚 Project Structure

```
PhishGuardAI/
├── data/
│   ├── raw/
│   │   └── urls.csv (600 URLs)
│   └── processed/
├── models/
│   ├── xgboost_model.pkl
│   ├── feature_names.pkl
│   └── metrics.pkl
├── src/
│   ├── __init__.py
│   ├── brand_detector.py
│   ├── explainer.py
│   ├── features.py
│   ├── maintenance.py
│   └── model.py
├── templates/
│   ├── index.html
│   └── maintenance.html
├── static/
├── web_app.py (Flask App)
├── train_model.py
├── data.py
├── requirements.txt
├── .gitignore
└── PROJECT_REPORT.md (This file)
```

---

## 🎯 Future Enhancements

1. **Expand Dataset:** 10,000+ URLs for better accuracy
2. **Deep Learning:** Try LSTM/Neural Networks
3. **Browser Extension:** Chrome/Firefox plugin
4. **API Rate Limiting:** Prevent abuse
5. **User Authentication:** Save analysis history
6. **Email Alerts:** Notify on suspicious URLs
7. **Mobile App:** Android/iOS version
8. **SSL Certificate Analysis:** Check cert validity
9. **Whois Lookup:** Domain registration info
10. **Screenshot Analysis:** Visual similarity check

---

## 🏆 Achievements

✅ **Successfully deployed ML-powered phishing detector**
✅ **Implemented explainable AI with SHAP values**
✅ **Achieved 90%+ detection accuracy**
✅ **Created responsive, beautiful web interface**
✅ **Deployed to cloud (AWS → Render)**
✅ **Added maintenance mode and admin controls**
✅ **Implemented brand protection features**
✅ **Real-time URL analysis working**

---

## 📞 Contact & Links

- **Live Demo:** https://phishguard-ai.onrender.com
- **GitHub:** https://github.com/Arjun-56/PhishGuardAI
- **Developer:** Arjun

---

## 🎓 Conclusion

**PhishGuard AI** successfully demonstrates the application of Machine Learning in cybersecurity, specifically for phishing detection. The project combines technical excellence (XGBoost, SHAP) with user experience (beautiful UI, explanations) and practical deployment (cloud hosting).

The system is **live, working, and ready to help users identify phishing URLs** with confidence!

---

**Report Generated:** April 18, 2026  
**Project Status:** ✅ Live & Operational
