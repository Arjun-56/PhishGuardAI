# PhishGuard AI - UML Diagram Specifications

This document contains comprehensive technical specifications extracted from the actual source code to enable any AI to generate UML diagrams for the PhishGuard AI project.

---

## 1. DATA FLOW DIAGRAM (DFD) SPECIFICATIONS

### **External Entities**
- **User**: Person who submits URLs for analysis via web interface
- **Admin**: Administrator who manages maintenance mode and system operations
- **External Data Sources**: OpenPhish feed, Tranco list (for training data)

### **Processes**

#### **Process 1: URL Input Reception**
- **Input**: URL string from User via HTTP POST request
- **Operation**: Receive and validate URL format
- **Output**: Validated URL string or error message

#### **Process 2: Feature Extraction**
- **Input**: Validated URL string
- **Operation**: Extract 19 URL features using URLFeatureExtractor class
  - URL length, domain length, path length
  - Subdomain count, path depth
  - Special character counts (dots, hyphens, slashes, etc.)
  - Security indicators (HTTPS, IP address, suspicious keywords)
  - Entropy calculation
  - Brand indicators
- **Output**: Feature dictionary with 19 key-value pairs

#### **Process 3: Whitelist Check**
- **Input**: URL string
- **Operation**: Compare domain against 20 whitelisted legitimate domains
  - flipkart.com, amazon.com, amazon.in, google.com, youtube.com
  - facebook.com, instagram.com, twitter.com, linkedin.com
  - microsoft.com, apple.com, netflix.com, spotify.com
  - github.com, stackoverflow.com, wikipedia.org, reddit.com
  - ebay.com, walmart.com, target.com, bestbuy.com
  - myntra.com, snapdeal.com, paytm.com, phonepe.com
- **Output**: Safe status (if match) or continue to analysis (if no match)

#### **Process 4: Brand Detection**
- **Input**: URL string
- **Operation**: Check for brand impersonation using BrandDetector class
  - Compare against 25+ known brands (PayPal, Apple, Amazon, Google, etc.)
  - Calculate Levenshtein distance for typosquatting detection
  - Check suspicious TLDs (tk, ml, ga, cf, gq, etc.)
- **Output**: Brand detection result (suspicious flag, matched brand, similarity score)

#### **Process 5: ML Prediction**
- **Input**: Feature dictionary
- **Operation**: Predict phishing probability using XGBoost model
  - Convert features to DataFrame with proper column order
  - Call model.predict_proba() to get probability
- **Output**: Risk probability (0.0 to 1.0)

#### **Process 6: Explanation Generation**
- **Input**: URL, features, risk probability
- **Operation**: Generate SHAP-based explanation using URLExplainer class
  - Calculate feature impact scores
  - Generate human-readable summary
  - Identify top 5 risk factors
- **Output**: Explanation dictionary with summary and top factors

#### **Process 7: Response Formatting**
- **Input**: Risk probability, brand detection, explanation
- **Operation**: Format JSON response
  - Determine status (safe/suspicious/phishing) based on risk thresholds
  - Add brand warning if detected
  - Include explanation and top factors
- **Output**: JSON response with status, icon, text, details, risk_score, explanation

#### **Process 8: Maintenance Mode Check**
- **Input**: HTTP request
- **Operation**: Check if maintenance flag file exists
- **Output**: Maintenance page or normal page

### **Data Stores**

#### **Store 1: Model Files (models/)**
- **xgboost_model.pkl**: Trained XGBoost classifier model
- **feature_names.pkl**: List of 19 feature names
- **metrics.pkl**: Model performance metrics (ROC-AUC, PR-AUC, accuracy)

#### **Store 2: Training Data (data/raw/)**
- **urls.csv**: CSV file with 600 URLs (300 phishing, 300 benign)
  - Columns: url, label (0=benign, 1=phishing)

#### **Store 3: Maintenance Flags (data/)**
- **.maintenance**: Flag file indicating maintenance mode active
- **.maintenance_status.json**: JSON with maintenance details
  - enabled: boolean
  - started_at: timestamp
  - reason: string
  - estimated_minutes: integer

### **Data Flows**

1. **User → Process 1**: URL string via HTTP POST to /analyze endpoint
2. **Process 1 → Process 2**: Validated URL string
3. **Process 2 → Process 3**: Feature dictionary
4. **Process 3 → Process 4**: URL (if not whitelisted)
5. **Process 4 → Process 5**: Brand detection result
6. **Process 5 → Process 6**: Risk probability
7. **Process 6 → Process 7**: Explanation dictionary
8. **Process 7 → User**: JSON response
9. **Process 8 → User**: Maintenance page (if active)
10. **Admin → Process 8**: Maintenance enable/disable requests via /admin/maintenance/<action>

---

## 2. USE CASE DIAGRAM SPECIFICATIONS

### **Actors**

#### **Actor 1: User**
- **Description**: End user who wants to check if a URL is phishing
- **Characteristics**: No authentication required, can access from any browser

#### **Actor 2: Administrator**
- **Description**: System administrator who manages maintenance mode
- **Characteristics**: Has access to admin endpoints, can enable/disable maintenance

### **Use Cases**

#### **UC1: Analyze URL**
- **Actor**: User
- **Description**: User submits a URL for phishing analysis
- **Preconditions**: System is online (not in maintenance mode), model is loaded
- **Main Flow**:
  1. User navigates to main page
  2. User enters URL in input field
  3. User clicks "Analyze" button
  4. System validates URL format
  5. System checks whitelist
  6. System extracts features
  7. System performs ML prediction
  8. System generates explanation
  9. System displays results with risk score
- **Alternative Flows**:
  - Invalid URL: Show error message
  - Maintenance mode: Show maintenance page
  - Whitelisted domain: Show immediate safe status
- **Postconditions**: User sees risk assessment with explanation

#### **UC2: View Health Status**
- **Actor**: User, Administrator
- **Description**: Check if system is healthy and operational
- **Preconditions**: None
- **Main Flow**:
  1. User accesses /health endpoint
  2. System returns JSON with status, model_loaded, maintenance_mode
- **Postconditions**: User knows system status

#### **UC3: Enable Maintenance Mode**
- **Actor**: Administrator
- **Description**: Enable maintenance mode to perform updates
- **Preconditions**: Administrator has access to admin endpoint
- **Main Flow**:
  1. Administrator accesses /admin/maintenance/enable
  2. System creates .maintenance flag file
  3. System saves maintenance status to JSON
  4. System returns success message
- **Postconditions**: System shows maintenance page to all users

#### **UC4: Disable Maintenance Mode**
- **Actor**: Administrator
- **Description**: Disable maintenance mode to resume normal operation
- **Preconditions**: Maintenance mode is active
- **Main Flow**:
  1. Administrator accesses /admin/maintenance/disable
  2. System removes .maintenance flag file
  3. System updates maintenance status JSON
  4. System returns success message
- **Postconditions**: System resumes normal operation

#### **UC5: View Maintenance Status**
- **Actor**: User, Administrator
- **Description**: View current maintenance mode status
- **Preconditions**: None
- **Main Flow**:
  1. User accesses main page
  2. System checks maintenance flag
  3. If active, display maintenance page with status details
  4. If inactive, display normal page
- **Postconditions**: User sees appropriate page

### **Relationships**
- **UC1** extends **UC5** (if maintenance mode active)
- **UC3** and **UC4** are generalizations of **UC5** (admin controls maintenance)
- **UC2** is independent and can be called by any actor

---

## 3. CLASS DIAGRAM SPECIFICATIONS

### **Classes and Their Specifications**

#### **Class 1: PhishingModel**
- **Package**: src.model
- **Purpose**: XGBoost-based phishing detection model
- **Attributes**:
  - `model: XGBClassifier` - The trained XGBoost model
  - `feature_names: List[str]` - List of 19 feature names
  - `metrics: Dict` - Performance metrics dictionary
- **Methods**:
  - `__init__()` - Initialize empty model
  - `train(X: DataFrame, y: Series) -> Dict` - Train model with data
    - Splits data 80/20 train/test
    - Initializes XGBoost with specific parameters
    - Calculates ROC-AUC, PR-AUC, accuracy
    - Returns metrics dictionary
  - `predict(X: DataFrame) -> Array` - Predict class labels
  - `predict_proba(X: DataFrame) -> Array` - Predict probabilities
  - `get_feature_importance() -> DataFrame` - Get feature importance scores
  - `save(model_dir: str)` - Save model to disk (3 .pkl files)
  - `load(model_dir: str) -> PhishingModel` - Load model from disk
- **Relationships**: None (standalone model class)

#### **Class 2: URLFeatureExtractor**
- **Package**: src.features
- **Purpose**: Extract 19 features from URLs for ML
- **Attributes**:
  - `suspicious_keywords: List[str]` - 16 suspicious keyword patterns
  - `brand_names: List[str]` - 25 brand names for detection
  - `shortening_services: List[str]` - 10 URL shortener domains
- **Methods**:
  - `__init__()` - Initialize keyword and brand lists
  - `extract_single(url: str) -> Dict` - Extract features from single URL
    - Returns dictionary with 19 features
  - `extract_batch(urls: List[str]) -> List[Dict]` - Extract features from multiple URLs
  - `_has_ip_address(url: str) -> bool` - Check for IP address in URL
  - `_calculate_entropy(text: str) -> float` - Calculate Shannon entropy
- **Relationships**: None (utility class)

#### **Class 3: BrandDetector**
- **Package**: src.brand_detector
- **Purpose**: Detect brand impersonation in URLs
- **Attributes**:
  - `known_brands: Dict[str, List[str]]` - 22 brands with official domains
  - `suspicious_tlds: List[str]` - 9 suspicious top-level domains
- **Methods**:
  - `__init__()` - Initialize brand dictionary and TLD list
  - `check_url(url: str) -> Dict` - Check URL for brand impersonation
    - Returns: is_suspicious, matched_brand, similarity, reason, indicators
  - `_domain_similarity(domain1: str, domain2: str) -> float` - Calculate Levenshtein similarity
  - `get_brand_list() -> List[str]` - Return all known brands
- **Relationships**: None (utility class)

#### **Class 4: URLExplainer**
- **Package**: src.explainer
- **Purpose**: Generate SHAP-based explanations for predictions
- **Attributes**:
  - `model: XGBClassifier` - The trained model
  - `feature_names: List[str]` - List of 19 feature names
  - `explainer: shap.TreeExplainer` - SHAP explainer instance
- **Methods**:
  - `__init__(model, feature_names)` - Initialize with model and features
  - `_setup_explainer()` - Initialize SHAP TreeExplainer
  - `explain(url: str, features: Dict, prediction_prob: float) -> Dict` - Generate explanation
    - Returns: top_factors, summary, risk_score, url
  - `_get_top_factors(features: Dict, prediction_prob: float) -> List[Dict]` - Get top contributing features
  - `_generate_summary(url: str, risk_score: float, factors: List) -> str` - Generate human-readable summary
- **Relationships**: 
  - **Composition**: Uses XGBClassifier model
  - **Association**: Uses shap.TreeExplainer

#### **Class 5: FlaskApp (web_app.py)**
- **Package**: Root (web_app.py)
- **Purpose**: Main Flask web application
- **Attributes**:
  - `app: Flask` - Flask application instance
  - `model: XGBClassifier` - Global loaded model
  - `feature_names: List[str]` - Global feature names
  - `brand_detector: BrandDetector` - Global brand detector instance
  - `explainer: URLExplainer` - Global explainer instance
- **Methods**:
  - `load_components() -> Tuple` - Load all ML components from disk
  - `index() -> Response` - Serve main page (checks maintenance mode)
  - `analyze_url() -> JSON` - Analyze URL endpoint (POST)
    - Validates input, checks whitelist, extracts features
    - Predicts, checks brand, generates explanation
    - Returns JSON response with all details
  - `health_check() -> JSON` - Health check endpoint
  - `admin_maintenance(action: str) -> JSON` - Toggle maintenance mode
- **Relationships**:
  - **Aggregation**: Contains PhishingModel (via model attribute)
  - **Aggregation**: Contains URLFeatureExtractor (instantiated in analyze_url)
  - **Aggregation**: Contains BrandDetector (global instance)
  - **Aggregation**: Contains URLExplainer (global instance)
  - **Association**: Uses maintenance module functions

#### **Class 6: Maintenance Functions (maintenance.py)**
- **Package**: src.maintenance
- **Purpose**: Manage maintenance mode state
- **Attributes** (Module-level constants):
  - `MAINTENANCE_FLAG: Path` - Path to .maintenance flag file
  - `MAINTENANCE_STATUS: Path` - Path to .maintenance_status.json file
- **Functions**:
  - `is_maintenance_mode() -> bool` - Check if maintenance flag exists
  - `enable_maintenance(reason: str, estimated_minutes: int) -> Dict` - Enable maintenance
  - `disable_maintenance()` - Disable maintenance
  - `get_maintenance_status() -> Dict` - Get current maintenance status
  - `update_maintenance_progress(message: str, percent_complete: int)` - Update progress
- **Relationships**: None (module-level functions)

### **Class Relationships Summary**

- **FlaskApp** aggregates **PhishingModel** (loaded from disk)
- **FlaskApp** aggregates **URLFeatureExtractor** (instantiated per request)
- **FlaskApp** aggregates **BrandDetector** (global instance)
- **FlaskApp** aggregates **URLExplainer** (global instance)
- **URLExplainer** uses **XGBClassifier** (composition)
- **URLExplainer** uses **shap.TreeExplainer** (association)
- **FlaskApp** uses **Maintenance Functions** (association)
- **PhishingModel** is independent
- **URLFeatureExtractor** is independent
- **BrandDetector** is independent

---

## 4. SEQUENCE DIAGRAM SPECIFICATIONS

### **Sequence 1: URL Analysis Flow**

**Participants**:
- **User**: Browser/user submitting URL
- **FlaskApp**: Flask web application
- **MaintenanceModule**: Maintenance mode functions
- **URLFeatureExtractor**: Feature extraction class
- **BrandDetector**: Brand detection class
- **PhishingModel**: ML model
- **URLExplainer**: Explanation generation class

**Message Sequence**:

1. **User → FlaskApp**: POST /analyze with URL in JSON body
2. **FlaskApp → MaintenanceModule**: is_maintenance_mode()
3. **MaintenanceModule → FlaskApp**: boolean (true/false)
4. **FlaskApp → FlaskApp**: Check if model is loaded
5. **FlaskApp → FlaskApp**: Validate URL format
6. **FlaskApp → FlaskApp**: Check whitelist (20 domains)
7. **FlaskApp → URLFeatureExtractor**: extract_single(url)
8. **URLFeatureExtractor → FlaskApp**: Feature dictionary (19 features)
9. **FlaskApp → PhishingModel**: predict_proba(X)
10. **PhishingModel → FlaskApp**: Risk probability (0.0-1.0)
11. **FlaskApp → BrandDetector**: check_url(url)
12. **BrandDetector → FlaskApp**: Brand detection result
13. **FlaskApp → URLExplainer**: explain(url, features, risk_prob)
14. **URLExplainer → FlaskApp**: Explanation dictionary
15. **FlaskApp → FlaskApp**: Format JSON response
16. **FlaskApp → User**: JSON response with status, risk_score, explanation

**Alternative Flows**:
- If maintenance mode active: FlaskApp returns maintenance JSON immediately
- If URL invalid: FlaskApp returns error JSON
- If whitelisted: FlaskApp returns safe status immediately (skip ML)

### **Sequence 2: Maintenance Mode Enable**

**Participants**:
- **Admin**: Administrator
- **FlaskApp**: Flask web application
- **MaintenanceModule**: Maintenance mode functions

**Message Sequence**:

1. **Admin → FlaskApp**: GET /admin/maintenance/enable
2. **FlaskApp → MaintenanceModule**: enable_maintenance(reason, minutes)
3. **MaintenanceModule → MaintenanceModule**: Create .maintenance flag file
4. **MaintenanceModule → MaintenanceModule**: Write status to .maintenance_status.json
5. **MaintenanceModule → FlaskApp**: Status dictionary
6. **FlaskApp → Admin**: JSON response {"status": "success", "message": "Maintenance mode enabled"}

### **Sequence 3: Maintenance Mode Disable**

**Participants**:
- **Admin**: Administrator
- **FlaskApp**: Flask web application
- **MaintenanceModule**: Maintenance mode functions

**Message Sequence**:

1. **Admin → FlaskApp**: GET /admin/maintenance/disable
2. **FlaskApp → MaintenanceModule**: disable_maintenance()
3. **MaintenanceModule → MaintenanceModule**: Remove .maintenance flag file
4. **MaintenanceModule → MaintenanceModule**: Update .maintenance_status.json
5. **MaintenanceModule → FlaskApp**: Success confirmation
6. **FlaskApp → Admin**: JSON response {"status": "success", "message": "Maintenance mode disabled"}

### **Sequence 4: Health Check**

**Participants**:
- **User**: Any user or monitoring system
- **FlaskApp**: Flask web application
- **MaintenanceModule**: Maintenance mode functions

**Message Sequence**:

1. **User → FlaskApp**: GET /health
2. **FlaskApp → FlaskApp**: Check if model is loaded
3. **FlaskApp → MaintenanceModule**: is_maintenance_mode()
4. **MaintenanceModule → FlaskApp**: boolean
5. **FlaskApp → User**: JSON {"status": "healthy", "model_loaded": true, "maintenance_mode": false}

---

## 5. COLLABORATION DIAGRAM SPECIFICATIONS

### **Collaboration 1: URL Analysis**

**Objects**:
- **FlaskApp**: Controller object
- **URLFeatureExtractor**: Feature extraction object
- **PhishingModel**: ML model object
- **BrandDetector**: Brand detection object
- **URLExplainer**: Explanation object

**Responsibilities**:
- **FlaskApp**: Coordinates analysis flow, validates input, formats response
- **URLFeatureExtractor**: Extracts 19 URL features
- **PhishingModel**: Predicts phishing probability
- **BrandDetector**: Detects brand impersonation
- **URLExplainer**: Generates explanations

**Collaboration Links**:
- FlaskApp → URLFeatureExtractor (requests feature extraction)
- FlaskApp → PhishingModel (requests prediction)
- FlaskApp → BrandDetector (requests brand check)
- FlaskApp → URLExplainer (requests explanation)
- URLFeatureExtractor → PhishingModel (provides features)
- BrandDetector → FlaskApp (provides brand result)
- URLExplainer → PhishingModel (uses model for SHAP values)

**Messages**:
- extract_single(url)
- predict_proba(X)
- check_url(url)
- explain(url, features, risk_prob)

### **Collaboration 2: Maintenance Management**

**Objects**:
- **FlaskApp**: Controller object
- **MaintenanceModule**: Maintenance state manager

**Responsibilities**:
- **FlaskApp**: Receives admin requests, returns responses
- **MaintenanceModule**: Manages flag files and status JSON

**Collaboration Links**:
- FlaskApp → MaintenanceModule (requests enable/disable)
- MaintenanceModule → FlaskApp (returns status)

**Messages**:
- enable_maintenance(reason, minutes)
- disable_maintenance()
- is_maintenance_mode()
- get_maintenance_status()

---

## 6. ACTIVITY DIAGRAM SPECIFICATIONS

### **Activity 1: URL Analysis Workflow**

**Start**: User submits URL

**Decision Nodes**:
1. **Maintenance Mode Check**
   - If YES: Show maintenance page (END)
   - If NO: Continue

2. **Model Loaded Check**
   - If NO: Return error (END)
   - If YES: Continue

3. **URL Validation**
   - If Invalid: Return error (END)
   - If Valid: Continue

4. **Whitelist Check**
   - If Matched: Return safe status (END)
   - If Not Matched: Continue

**Action Nodes**:
1. Extract 19 URL features
2. Convert features to DataFrame
3. Predict phishing probability
4. Check for brand impersonation
5. Generate SHAP explanation
6. Format JSON response

**Decision Nodes (Result Determination)**:
5. **Risk Probability > 0.7**
   - If YES: Status = "phishing"
   - If NO: Continue

6. **Risk Probability > 0.4**
   - If YES: Status = "suspicious"
   - If NO: Status = "safe"

7. **Brand Suspicious**
   - If YES: Upgrade status to "suspicious" (if safe)
   - If NO: Keep current status

**End**: Return JSON response to user

### **Activity 2: Maintenance Mode Toggle**

**Start**: Admin accesses admin endpoint

**Decision Node**:
1. **Action Type**
   - If "enable": Go to Enable Flow
   - If "disable": Go to Disable Flow
   - If invalid: Return error (END)

**Enable Flow**:
1. Create .maintenance flag file
2. Write maintenance status to JSON
3. Return success message
4. END

**Disable Flow**:
1. Remove .maintenance flag file
2. Update maintenance status JSON
3. Return success message
4. END

### **Activity 3: Model Training Workflow**

**Start**: Run train_model.py

**Action Nodes**:
1. Load dataset from data/raw/urls.csv
2. Initialize URLFeatureExtractor
3. Extract features for all URLs
4. Initialize PhishingModel
5. Train XGBoost model (80/20 split)
6. Evaluate model (ROC-AUC, PR-AUC, accuracy)
7. Save model to models/xgboost_model.pkl
8. Save feature names to models/feature_names.pkl
9. Save metrics to models/metrics.pkl

**End**: Training complete, files saved

### **Activity 4: Feature Extraction Workflow**

**Start**: URL received

**Action Nodes**:
1. Add https:// protocol if missing
2. Parse URL with urlparse
3. Extract domain with tldextract
4. Calculate URL length
5. Calculate domain length
6. Count subdomains
7. Calculate path length and depth
8. Count special characters (., -, _, /, ?, =, &, @, %, +)
9. Count digits and letters
10. Check for HTTPS/HTTP
11. Check for IP address pattern
12. Check for URL shortener domains
13. Count suspicious keywords
14. Check for brand names
15. Check for suspicious TLDs
16. Calculate entropy (Shannon)
17. Return feature dictionary

**End**: 19 features extracted

---

## 7. COMPONENT DIAGRAM SPECIFICATIONS

### **Components**

#### **Component 1: Web Interface**
- **Type**: User Interface
- **Technology**: HTML5, CSS3, JavaScript
- **Responsibility**: Display UI, capture user input, show results
- **Interfaces**: 
  - Provides: User input (URL)
  - Requires: Analysis results (JSON)

#### **Component 2: Flask API**
- **Type**: Web Service
- **Technology**: Flask, Gunicorn
- **Responsibility**: Handle HTTP requests, coordinate analysis
- **Interfaces**:
  - Provides: REST API endpoints (/analyze, /health, /admin/maintenance)
  - Requires: Model components, maintenance module

#### **Component 3: Feature Extraction Engine**
- **Type**: Business Logic
- **Technology**: Python (URLFeatureExtractor class)
- **Responsibility**: Extract 19 URL features
- **Interfaces**:
  - Provides: Feature extraction service
  - Requires: URL string

#### **Component 4: ML Model**
- **Type**: AI/ML Component
- **Technology**: XGBoost, joblib
- **Responsibility**: Predict phishing probability
- **Interfaces**:
  - Provides: Prediction service
  - Requires: Feature DataFrame

#### **Component 5: Brand Detector**
- **Type**: Business Logic
- **Technology**: Python (BrandDetector class), Levenshtein
- **Responsibility**: Detect brand impersonation
- **Interfaces**:
  - Provides: Brand detection service
  - Requires: URL string

#### **Component 6: Explanation Engine**
- **Type**: AI/ML Component
- **Technology**: SHAP, Python (URLExplainer class)
- **Responsibility**: Generate explainable AI insights
- **Interfaces**:
  - Provides: Explanation generation service
  - Requires: URL, features, prediction probability

#### **Component 7: Maintenance Manager**
- **Type**: System Management
- **Technology**: Python (maintenance module)
- **Responsibility**: Manage maintenance mode state
- **Interfaces**:
  - Provides: Maintenance state management
  - Requires: Enable/disable commands

#### **Component 8: Data Storage**
- **Type**: Persistence
- **Technology**: File system (.pkl files, CSV, JSON)
- **Responsibility**: Store models, features, training data
- **Interfaces**:
  - Provides: Data persistence
  - Requires: Read/write operations

### **Component Relationships**

- **Web Interface** → **Flask API** (HTTP requests)
- **Flask API** → **Feature Extraction Engine** (method calls)
- **Flask API** → **ML Model** (method calls)
- **Flask API** → **Brand Detector** (method calls)
- **Flask API** → **Explanation Engine** (method calls)
- **Flask API** → **Maintenance Manager** (function calls)
- **ML Model** → **Data Storage** (read/write)
- **Explanation Engine** → **ML Model** (access for SHAP)
- **Maintenance Manager** → **Data Storage** (read/write)

---

## 8. DEPLOYMENT DIAGRAM SPECIFICATIONS

### **Nodes**

#### **Node 1: User Browser**
- **Type**: Client Device
- **Technology**: Any modern web browser (Chrome, Firefox, Safari, Edge)
- **Responsibility**: Display web interface, send HTTP requests
- **Artifacts**: HTML, CSS, JavaScript

#### **Node 2: Render Cloud Platform**
- **Type**: Cloud Infrastructure
- **Technology**: Render (PaaS)
- **Responsibility**: Host Flask application, provide SSL, auto-scaling
- **Configuration**:
  - Runtime: Python 3.11
  - Server: Gunicorn
  - Region: Oregon (US West)
  - Auto-deploy: Enabled on git push
- **Artifacts**: 
  - Flask application code
  - Model files (.pkl)
  - Training data (.csv)

#### **Node 3: GitHub Repository**
- **Type**: Version Control
- **Technology**: GitHub
- **Responsibility**: Source code storage, CI/CD trigger
- **Artifacts**: Complete source code repository

### **Communication Paths**

- **User Browser** → **Render Cloud** (HTTPS, port 443)
- **Render Cloud** → **GitHub** (Git pull on deployment)
- **Developer** → **GitHub** (Git push)

### **Deployment Artifacts**

- **web_app.py**: Main Flask application
- **src/**: Python modules (model, features, brand_detector, explainer, maintenance)
- **models/**: Trained ML model files
- **data/**: Training data and maintenance flags
- **templates/**: HTML templates
- **requirements.txt**: Python dependencies
- **.gitignore**: Git ignore rules

---

## 9. PACKAGE DIAGRAM SPECIFICATIONS

### **Packages**

#### **Package 1: PhishGuardAI (Root)**
- **Sub-packages**: src, templates, static, data, models
- **Files**: web_app.py, train_model.py, data.py, requirements.txt

#### **Package 2: src**
- **Classes**: 
  - model.py (PhishingModel)
  - features.py (URLFeatureExtractor)
  - brand_detector.py (BrandDetector)
  - explainer.py (URLExplainer)
  - maintenance.py (functions)
- **File**: __init__.py

#### **Package 3: templates**
- **Files**: index.html, maintenance.html

#### **Package 4: static**
- **Files**: CSS, JavaScript, images (if any)

#### **Package 5: data**
- **Sub-packages**: raw, processed
- **Files**: .maintenance, .maintenance_status.json

#### **Package 6: models**
- **Files**: xgboost_model.pkl, feature_names.pkl, metrics.pkl

### **Package Dependencies**

- **Root** imports **src** (all modules)
- **Root** imports **templates** (Jinja2)
- **src.model** imports sklearn, xgboost, joblib
- **src.features** imports re, math, urllib, tldextract, numpy
- **src.brand_detector** imports re, urllib, Levenshtein
- **src.explainer** imports shap, pandas, numpy
- **src.maintenance** imports json, pathlib, datetime
- **web_app.py** imports flask, pandas, joblib, src modules

---

## 10. STATE MACHINE DIAGRAM SPECIFICATIONS

### **State Machine: Flask Application**

**States**:
1. **Initializing**: Loading model and components
2. **Online**: Normal operation, accepting requests
3. **Maintenance**: Maintenance mode active
4. **Error**: Model not loaded or error state

**Transitions**:
- **Initializing** → **Online**: Model loaded successfully
- **Initializing** → **Error**: Model load failed
- **Online** → **Maintenance**: Admin enables maintenance
- **Maintenance** → **Online**: Admin disables maintenance
- **Online** → **Error**: Critical error occurs
- **Error** → **Online**: Error resolved, model reloaded

**Events**:
- `load_components()`: Trigger initialization
- `enable_maintenance()`: Transition to maintenance
- `disable_maintenance()`: Transition to online
- `error_occurred()`: Transition to error
- `model_reloaded()`: Transition to online

### **State Machine: URL Analysis**

**States**:
1. **Received**: URL received from user
2. **Validating**: Checking URL format
3. **Whitelisting**: Checking whitelist
4. **Extracting**: Extracting features
5. **Predicting**: ML prediction
6. **Explaining**: Generating explanation
7. **Completed**: Response ready

**Transitions**:
- **Received** → **Validating**: URL received
- **Validating** → **Whitelisting**: URL valid
- **Validating** → **Completed**: URL invalid (error)
- **Whitelisting** → **Completed**: Domain whitelisted
- **Whitelisting** → **Extracting**: Domain not whitelisted
- **Extracting** → **Predicting**: Features extracted
- **Predicting** → **Explaining**: Prediction complete
- **Explaining** → **Completed**: Explanation generated

---

## END OF DOCUMENT

This document contains all technical specifications extracted from the actual PhishGuard AI source code. Any AI can use this information to generate accurate UML diagrams for the project.

**File Generated**: April 18, 2026
**Project**: PhishGuard AI
**Version**: 1.0
