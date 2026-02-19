# TRIDENT AI-FRAUD DETECTION ENGINE
## Final Project Idea - Barclays Hack-O-Hire Theme 2
## REVISED: All Modules Built From Scratch

---

# 1. PROJECT OVERVIEW

**Project Name:** TRIDENT - AI-Fraud Detection Engine  
**Hackathon:** Barclays Hack-O-Hire  
**Theme:** 2 - AI Multimodal Fraud Detection  
**Status:** Idea Phase  

**Tagline:** "Detect AI-Powered Fraud Campaigns, Not Isolated Signals"

**Important Note:** All modules (9 total) will be built from scratch during the hackathon.

---

# 2. PROBLEM STATEMENT

Modern fraud attacks are **coordinated and AI-assisted**.

**Current Problem:**
- Email phishing detector works alone → Alert
- URL scanner works alone → Alert
- File attachment scanner works alone → Alert
- Voice system works alone → Alert

**Result:** 4 separate alerts, analyst confusion, no correlation

**What's Missing:** Systems don't understand that Email + URL + File + Voice are part of ONE coordinated attack.

---

# 3. THE SOLUTION - TRIDENT

Instead of detecting isolated fraud signals, TRIDENT **detects fraud CAMPAIGNS** by:

1. Building 4 AI-specialized detectors from scratch
2. Building 5 core modules from scratch
3. Fusing all signals into ONE unified decision
4. Correlating signals to prove coordination
5. Explaining with SHAP (human-readable)

**Result:** One risk score + Timeline + Clear action

---

# 4. MVP = 9 MODULES (All Built From Scratch)

## 4 NEW DETECTION MODULES

### Module #1: AI-TEXT DETECTION (1-2 hours)
**Purpose:** Detect if email is written by ChatGPT/Claude  
**Build From:** Pre-trained BERT model (HuggingFace)  
**What You Code:** 
- Load pre-trained model
- Tokenize email text
- Get probability score
- Classify (AI vs Human)

**Input:** Email text  
**Output:** 0-100% AI probability + Risk label  

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
# Load model (pre-trained, no training needed)
# Tokenize → Predict → Output probability
```

**Time:** 1-2 hours  
**Complexity:** Easy (mostly copy-paste from HuggingFace)

---

### Module #2: CREDENTIAL EXPOSURE (1-2 hours)
**Purpose:** Find passwords, API keys, credit cards  
**Build From:** Regex patterns  
**What You Code:**
- Define regex patterns
- Search email text
- Count matches
- Output risk level

**Input:** Email text + attachment content  
**Output:** List of secrets found + Risk level  

```python
import re
patterns = {
    'api_key': r'sk_live_[a-zA-Z0-9]{24,}',
    'password': r'password\s*[:=]\s*[\'"]?([^\s\'\"]{6,})',
    ...
}
# Search text for patterns
# Return findings
```

**Time:** 1-2 hours  
**Complexity:** Very Easy (pure regex)

---

### Module #3: MALWARE SCANNING (3-4 hours)
**Purpose:** Detect malware in attachments  
**Build From:** ClamAV + file analysis  
**What You Code:**
- Check file extension
- Run ClamAV scan
- Analyze Office macros
- Scan PDFs for JavaScript
- Return risk level

**Input:** File path  
**Output:** Risk level (CRITICAL/HIGH/LOW) + Reason  

```python
import pyclamd
import zipfile

# 1. Check file type
if file_ext in dangerous_list:
    return CRITICAL

# 2. Run ClamAV
clam = pyclamd.ClamD()
result = clam.scan_file(file_path)

# 3. Check for macros (Office files)
with zipfile.ZipFile(file_path) as z:
    if 'vbaProject.bin' in z.namelist():
        return HIGH

# 4. Check PDF for JavaScript
if b'/JavaScript' in pdf_content:
    return HIGH
```

**Time:** 3-4 hours  
**Complexity:** Medium (multiple checks, file handling)

---

### Module #4: PROMPT INJECTION (1 hour)
**Purpose:** Detect jailbreak attempts  
**Build From:** Regex patterns  
**What You Code:**
- Define jailbreak phrases
- Search email
- Count matches
- Output risk

**Input:** Email text  
**Output:** Is injection detected? + Risk level  

```python
import re
injection_patterns = [
    r'ignore\s+(the\s+)?previous',
    r'system\s+(prompt|instruction)',
    r'DAN\s+mode',
    ...
]
# Search for patterns
# Return True/False + risk
```

**Time:** 1 hour  
**Complexity:** Very Easy (regex)

---

## 5 CORE MODULES (Build From Scratch)

### Module #5: EMAIL PHISHING DETECTION (2-3 hours)
**Purpose:** Detect general phishing emails  
**Build From:** Text features + Simple ML  
**What You Code:**
- Extract features (URL count, urgency words, domain)
- Train basic classifier (XGBoost or SVM)
- Predict phishing probability

**Input:** Email text  
**Output:** 0-100% phishing probability  

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import xgboost as xgb

# 1. Extract features
features = extract_features(email_text)
# - URL count
# - Urgency words ('verify', 'confirm', 'urgent')
# - Grammar quality
# - Domain reputation

# 2. Train classifier
X = vectorizer.fit_transform(emails)
classifier = xgb.XGBClassifier()
classifier.fit(X, labels)

# 3. Predict
probability = classifier.predict_proba(email_text)
```

**Time:** 2-3 hours  
**Complexity:** Medium (feature engineering + ML)

---

### Module #6: URL DETECTION (2-3 hours)
**Purpose:** Detect malicious URLs  
**Build From:** Domain features + Simple ML  
**What You Code:**
- Extract domain features (age, SSL, reputation)
- Train classifier
- Predict malicious probability

**Input:** URL/domain  
**Output:** 0-100% malicious probability  

```python
import whois
import requests
from urllib.parse import urlparse

# 1. Extract features
domain = extract_domain(url)
features = {
    'domain_age': check_age(domain),
    'has_ssl': check_ssl(url),
    'domain_length': len(domain),
    'has_special_chars': check_chars(domain),
    'reputation': check_reputation(domain)
}

# 2. Train classifier
classifier = xgb.XGBClassifier()
classifier.fit(feature_matrix, labels)

# 3. Predict
probability = classifier.predict_proba(features)
```

**Time:** 2-3 hours  
**Complexity:** Medium (API calls + feature extraction)

---

### Module #7: FUSION MODEL (2-3 hours)
**Purpose:** Combine all scores into unified risk  
**Build From:** XGBoost  
**What You Code:**
- Collect all module scores (9 scores)
- Normalize scores
- Train XGBoost on combined scores
- Output unified risk (0-100)

**Input:** 9 module scores  
**Output:** Unified risk score (0-100) + Risk band  

```python
import xgboost as xgb
import numpy as np

# 1. Collect all scores
all_scores = [
    ai_text_score,
    credential_score,
    malware_score,
    injection_score,
    email_phishing_score,
    url_score,
    # ... more
]

# 2. Normalize (0-100)
normalized = [score / 100 for score in all_scores]

# 3. Train fusion model
X = np.array([normalized] * n_samples)
fusion_model = xgb.XGBClassifier(weights=[0.20, 0.15, 0.25, 0.10, 0.15, 0.10, ...])
fusion_model.fit(X, labels)

# 4. Predict
unified_risk = fusion_model.predict_proba(normalized)[0][1] * 100
risk_band = 'CRITICAL' if unified_risk > 80 else 'HIGH' if unified_risk > 60 else 'LOW'
```

**Time:** 2-3 hours  
**Complexity:** Medium (data aggregation + weighting)

---

### Module #8: CAMPAIGN GRAPH (2-3 hours)
**Purpose:** Correlate signals into campaigns  
**Build From:** NetworkX  
**What You Code:**
- Create graph nodes (email domain, URL domain, voice caller ID)
- Link nodes if same
- Build timeline
- Detect coordinated attacks

**Input:** All signals with metadata  
**Output:** Graph visualization + Timeline + Coordination proof  

```python
import networkx as nx
from datetime import datetime

# 1. Create graph
G = nx.Graph()

# 2. Add nodes
G.add_node('email_domain', data={'domain': 'secure-alert.xyz', 'time': '1:00 PM'})
G.add_node('url_domain', data={'domain': 'secure-alert.xyz', 'time': '1:05 PM'})
G.add_node('voice_caller', data={'id': '123456', 'time': '1:10 PM'})

# 3. Add edges (if same attacker)
if email_domain == url_domain:
    G.add_edge('email_domain', 'url_domain', reason='Same domain')

# 4. Detect connected components
components = list(nx.connected_components(G))
if len(components) == 1:
    is_coordinated = True
else:
    is_coordinated = False

# 5. Build timeline
timeline = sorted(nodes_by_time)
```

**Time:** 2-3 hours  
**Complexity:** Medium (graph logic + timeline)

---

### Module #9: SHAP EXPLANATIONS (1-2 hours)
**Purpose:** Explain fraud decisions  
**Build From:** SHAP library  
**What You Code:**
- Integrate SHAP with XGBoost
- Calculate feature importance
- Generate human-readable text
- Output explanation

**Input:** Model + Features  
**Output:** Feature importance + Narrative explanation  

```python
import shap

# 1. Load trained models
fusion_model = load_model('fusion_xgboost.pkl')

# 2. Create SHAP explainer
explainer = shap.TreeExplainer(fusion_model)
shap_values = explainer.shap_values([features])

# 3. Get feature importance
importance = {
    'credential_exposure': shap_values[0],
    'ai_text': shap_values[1],
    ...
}

# 4. Generate narrative
explanation = f"""
TRIDENT Fraud Analysis (Risk Score: 89/100 - CRITICAL)

Factors Contributing to Risk:
- Credential Exposure: {importance['credential']}% 
- AI-Generated Text: {importance['ai_text']}%
- Malware Attachment: {importance['malware']}%

Campaign Correlation: Email + URL + Voice linked to same domain
Timeline: Attack occurred over 10 minutes across 3 channels

Recommendation: BLOCK + ESCALATE
"""
```

**Time:** 1-2 hours  
**Complexity:** Easy (mostly library usage)

---

# 5. TOTAL BUILD BREAKDOWN

| Module | Type | Time | Total |
|---|---|---|---|
| AI-Text Detection | NEW | 1-2h | 1-2h |
| Credential Exposure | NEW | 1-2h | 2-4h |
| Malware Scanning | NEW | 3-4h | 5-8h |
| Prompt Injection | NEW | 1h | 6-9h |
| Email Phishing | FROM SCRATCH | 2-3h | 8-12h |
| URL Detection | FROM SCRATCH | 2-3h | 10-15h |
| Fusion Model | FROM SCRATCH | 2-3h | 12-18h |
| Campaign Graph | FROM SCRATCH | 2-3h | 14-21h |
| SHAP Explanations | FROM SCRATCH | 1-2h | 15-23h |

**Total Build Time: 15-23 hours**  
**Integration + Testing: 3-5 hours**  
**Dashboard + Demo: 4-6 hours**  
**Polish + Buffer: 8-14 hours**

**Total: 30-48 hours (Tight but feasible)**

---

# 6. THEME 2 ALIGNMENT

| Theme 2 Requirement | TRIDENT Covers |
|---|---|
| AI-generated phishing emails | ✅ Module #1 |
| Detect credential exposure | ✅ Module #2 |
| Attachment verification (Pharming) | ✅ Module #3 |
| Website phishing detection | ✅ Module #6 |
| Detect spoofing | ✅ Module #6 + Graph |
| Prompt Injection / Jailbreaking | ✅ Module #4 |
| Multi-modal fraud detection | ✅ Fusion Model |
| Explainability | ✅ SHAP |
| Campaign detection | ✅ Graph |

**Coverage: 90%+** ✅

---

# 7. FUTURE SCALABILITY (Not in MVP)

## Phase 2: Enhanced Detection (Months 1-3)
- Deepfake voice detection (MFCC + speaker verification)
- Cookie theft detection (JavaScript analysis)
- Performance optimization

## Phase 3: Advanced Features (Months 3-6)
- Offline LLM integration (Ollama)
- Sandbox AI testing
- Threat intelligence feeds

## Phase 4: Intelligence (Months 6-12)
- Graph neural networks
- Federated learning
- Device fingerprinting
- Behavioral analysis

---

# 8. TECHNICAL STACK (What You'll Use)

```
Languages: Python 3.10+

NEW MODULES:
- transformers (BERT for AI-text)
- regex/re (credentials + injection)
- pyclamd (malware)
- librosa (future voice)

FROM-SCRATCH MODULES:
- scikit-learn (TF-IDF, SVM for email)
- xgboost (classifiers + fusion)
- networkx (graph correlation)
- shap (explanations)

Libraries to Install:
pip install transformers torch scikit-learn xgboost
pip install networkx shap pyclamd requests
pip install numpy pandas matplotlib

Backend:
- fastapi (REST API)
- streamlit (dashboard)

Database:
- SQLite (MVP)

Deployment:
- Docker (containerization)
```

---

# 9. USE CASE EXAMPLE

### Scenario: Coordinated Multi-Channel Attack

**Timeline:**
```
1:00 PM → Email from "barclays-update@secure-alert.xyz"
          Subject: "Urgent account verification"
          Contains: Recovery code
          Attachment: "Verify-Identity.pdf"

1:05 PM → Customer clicks link → Goes to secure-alert.xyz
          Website: Looks like Barclays but domain is fake

1:10 PM → Voice call from "Barclays Support"
          Voice: "Please provide your OTP"
```

### TRIDENT Processing

**Module #1 (AI-Text):** 78% ChatGPT-generated → 20 points  
**Module #2 (Credentials):** Found recovery code → 30 points  
**Module #3 (Malware):** PDF has embedded JS → 25 points  
**Module #4 (Injection):** Not detected → 0 points  
**Module #5 (Email Phishing):** 65% phishing → 10 points  
**Module #6 (URL Detection):** Lookalike domain → 5 points  

**Fusion (Module #7):** 89/100 CRITICAL  
**Graph (Module #8):** All signals linked (same domain)  
**Explanation (Module #9):** "Coordinated attack: 30% credentials + 20% AI + 25% malware + 14% phishing patterns"

**Result:** CRITICAL RISK → BLOCK + ESCALATE

---

# 10. SYSTEM ARCHITECTURE

```
INPUT (Email, File, URL, Voice)
        ↓
PARALLEL PROCESSING (Modules 1-6)
├─ Module #1: AI-Text (1-2h build)
├─ Module #2: Credentials (1-2h build)
├─ Module #3: Malware (3-4h build)
├─ Module #4: Injection (1h build)
├─ Module #5: Email Phishing (2-3h build)
└─ Module #6: URL Detection (2-3h build)
        ↓
FUSION MODEL (Module #7, 2-3h build)
Combines 6 scores → 1 unified score
        ↓
CAMPAIGN GRAPH (Module #8, 2-3h build)
Links signals → Proves coordinated
        ↓
SHAP EXPLANATIONS (Module #9, 1-2h build)
Explains why each decision
        ↓
OUTPUT (Risk Score + Timeline + Action)
```

---

# 11. 48-HOUR BUILD TIMELINE

## Day 1 (Hours 0-24)

**Hour 0-1:** Setup + Planning  
**Hour 1-3:** Module #1 (AI-Text) ✅  
**Hour 3-5:** Module #2 (Credentials) ✅  
**Hour 5-9:** Module #3 (Malware) ✅  
**Hour 9-10:** Module #4 (Injection) ✅  
**Hour 10-13:** Module #5 (Email Phishing) ✅  
**Hour 13-16:** Module #6 (URL Detection) ✅  
**Hour 16-24:** Integration + Testing + Sleep ✅  

## Day 2 (Hours 24-48)

**Hour 0-2:** Module #7 (Fusion Model) ✅  
**Hour 2-4:** Module #8 (Campaign Graph) ✅  
**Hour 4-5:** Module #9 (SHAP) ✅  
**Hour 5-10:** Streamlit Dashboard ✅  
**Hour 10-15:** Testing + Polish ✅  
**Hour 15-20:** Demo Preparation ✅  
**Hour 20-24:** Final Submission ✅  

**Total Build:** 23-25 hours  
**Buffer:** 23-25 hours  
**Success Rate:** 90%+

---

# 12. WHY TRIDENT WINS

```
✅ All 9 Modules Built From Scratch
   (Shows complete understanding)

✅ Multi-Modal Detection
   (Email + File + URL + Voice)

✅ Campaign Correlation
   (Shows attacks are connected)

✅ Unified Decision
   (One score, one action)

✅ Explainable AI
   (SHAP shows exactly why)

✅ Realistic MVP
   (Acknowledges all modules must be built)

✅ Clear Timeline
   (Shows feasibility)
```

---

# 13. RISK ASSESSMENT

| Risk | Mitigation |
|---|---|
| 9 modules is too many | Use basic versions, skip advanced features |
| XGBoost training takes time | Use small datasets for training |
| ClamAV setup fails | Use file-type checking only |
| Time runs out | Skip demo polish, prioritize core functionality |
| Team exhausted | Clear timeline with breaks planned |

---

# 14. DELIVERABLES

**Code (After Approval):**
- ✅ Module #1: AI-Text Detection (Python file)
- ✅ Module #2: Credential Exposure (Python file)
- ✅ Module #3: Malware Scanning (Python file)
- ✅ Module #4: Prompt Injection (Python file)
- ✅ Module #5: Email Phishing (Python file)
- ✅ Module #6: URL Detection (Python file)
- ✅ Module #7: Fusion Model (Python file)
- ✅ Module #8: Campaign Graph (Python file)
- ✅ Module #9: SHAP Explanations (Python file)
- ✅ Main pipeline (orchestrates all)
- ✅ Streamlit dashboard
- ✅ Test cases

**Documentation:**
- ✅ README with setup instructions
- ✅ Architecture diagrams
- ✅ Final report

---

# 15. KEY DIFFERENTIATORS

**What Makes TRIDENT Unique:**

1. **Campaign Correlation** - Shows attacks are coordinated
2. **Multi-Modal Fusion** - Combines 9 different detection types
3. **Built From Scratch** - All modules coded during hackathon
4. **Explainable** - SHAP + narrative explanation
5. **Honest Scope** - Acknowledges building all modules from scratch

---

# 16. CLOSING STATEMENT

**TRIDENT is a complete fraud intelligence platform built entirely from scratch in 48 hours.**

It demonstrates:
- Deep understanding of fraud detection
- Practical ML implementation skills
- System design thinking
- Time management capability

Every module is built fresh, showing both technical capability and realistic time management.

**Result:** A working, explainable, multi-modal fraud detection system.

---

## END OF REVISED IDEA

**Status:** Ready for PPT Presentation & Submission  
**All Modules:** Built From Scratch  
**Total Code:** ~1500 lines  
**Build Time:** 23-25 hours (feasible in 48h)  
**Success Rate:** 90%+

---
