# TRIDENT — AI-Fraud Detection Engine 🎯

> Multi-modal fraud detection: detects coordinated fraud campaigns across Email, Files, URLs, and Voice.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Demo Attack Scenario
```bash
python main.py demo
```

### 3. Launch the Streamlit Dashboard
```bash
streamlit run ui/dashboard.py
# OR
python main.py dashboard
```

### 4. Start the FastAPI Backend
```bash
uvicorn api.routes:app --reload --port 8000
# OR
python main.py api
```

API docs available at: http://localhost:8000/docs

### 5. Run Tests
```bash
pytest tests/ -v
# OR
python main.py test
```

---

## 🏗️ Architecture

```
INPUT (Email + File + URL)
    ↓
┌─────────────────────────────────────┐
│  Module #1 — AI Text Detection      │  Detects ChatGPT/Claude-written text
│  Module #2 — Credential Exposure    │  Finds passwords, API keys, credit cards
│  Module #3 — Malware Scanner        │  Scans attachments (ClamAV + heuristics)
│  Module #4 — Prompt Injection       │  Detects jailbreak attempts
│  Module #5 — Email Phishing         │  XGBoost phishing classifier
│  Module #6 — URL Detection          │  Detects malicious/spoofed URLs
└─────────────────────────────────────┘
    ↓
┌──────────────────────────┐
│ Module #7 — Fusion Model │  XGBoost regression → unified 0-100 score
└──────────────────────────┘
    ↓
┌──────────────────────────────┐
│ Module #8 — Campaign Graph   │  NetworkX correlation graph
└──────────────────────────────┘
    ↓
┌──────────────────────────┐
│ Module #9 — SHAP Explainer│  Human-readable explanations
└──────────────────────────┘
    ↓
OUTPUT: Risk Score 0-100 + Band + Action + Timeline + Explanation
```

---

## 📁 Project Structure

```
trident/
├── main.py                    # Entry point (demo / api / dashboard / test)
├── config.py                  # Central configuration
├── requirements.txt
│
├── modules/
│   ├── ai_text_detection.py  # Module #1 — HuggingFace + heuristic fallback
│   ├── credential_exposure.py # Module #2 — Regex-based credential scanner
│   ├── malware_scanner.py    # Module #3 — ClamAV + static analysis
│   ├── prompt_injection.py   # Module #4 — Pattern-based injection detector
│   ├── email_phishing.py     # Module #5 — XGBoost email classifier
│   ├── url_detection.py      # Module #6 — XGBoost URL classifier
│   ├── fusion_model.py       # Module #7 — Score fusion
│   ├── campaign_graph.py     # Module #8 — NetworkX graph
│   └── shap_explainer.py     # Module #9 — SHAP explanations
│
├── core/
│   ├── data_models.py        # Pydantic v2 models
│   └── trident.py            # Main orchestrator
│
├── api/
│   └── routes.py             # FastAPI endpoints
│
├── ui/
│   └── dashboard.py          # Streamlit dashboard
│
└── tests/
    ├── test_modules.py       # Unit tests (9 module test classes)
    └── test_integration.py   # Integration + API tests
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/detect` | Full multi-modal detection |
| POST | `/analyze-email?text=...` | Email-only analysis |
| POST | `/analyze-url?url=...` | URL safety check |
| POST | `/scan-file` | File upload + malware scan |
| POST | `/check-credentials?text=...` | Credential exposure check |
| POST | `/check-injection?text=...` | Prompt injection check |
| POST | `/reset-graph` | Reset campaign graph |
| GET | `/campaign-status` | Current campaign correlation |

---

## 🧪 Demo Test Case

```
Input:
  Email: AI-written, contains "password=Bank@123"
  URL:   http://fake-bank.xyz (no SSL, suspicious TLD)
  File:  invoice.exe (dangerous executable)

Expected Output:
  Risk Score: ~85/100
  Risk Band:  CRITICAL
  Action:     BLOCK
  Coordinated: True (all from fake-bank.xyz domain)
```

Run it: `python main.py demo`

---

## ⚙️ Configuration

All configuration lives in `config.py`:
- `FUSION_WEIGHTS` — per-module weight in fusion score
- `RISK_BANDS` — threshold boundaries
- `DANGEROUS_EXTENSIONS` — file types blocked by malware scanner
- `TRUSTED_DOMAINS` — domains whitelisted in URL detector
- `INJECTION_PATTERNS` — regex patterns for prompt injection

---

## 🛡️ Module Risk Weights

| Module | Weight | Description |
|--------|--------|-------------|
| Credential Exposure | 30% | Passwords, API keys, credit cards |
| Malware Scanner | 25% | Dangerous files, macros, PDF JS |
| AI Text Detection | 20% | ChatGPT/Claude-written content |
| Email Phishing | 15% | ML phishing classifier |
| URL Detection | 7% | Malicious domain/URL analysis |
| Prompt Injection | 3% | Jailbreak pattern detection |

---

## 📦 Dependencies

- `transformers` + `torch` — AI text detection model
- `xgboost` — phishing, URL, and fusion models
- `scikit-learn` — feature extraction
- `networkx` — campaign correlation graph
- `shap` — explainability
- `fastapi` + `uvicorn` — REST API
- `streamlit` + `plotly` — dashboard
- `pydantic` v2 — data validation

---

Built for the 48-hour hackathon · February 2026
