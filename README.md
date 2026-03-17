<div align="center">

# 🔱 TRIDENT
**Multi-Modal AI Fraud & Threat Detection Engine**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](#)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](#)
[![XGBoost](https://img.shields.io/badge/XGBoost-123456?style=for-the-badge&logo=xgboost)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](#)

*A state-of-the-art AI-driven email monitor that evaluates inbox threats in real time. Deploys seamlessly alongside an immersive React-based 3D dashboard.*

---

</div>

<br/>

## 🌟 What is TRIDENT?

TRIDENT acts as an ultra-paranoid AI guardian for your inbox. It ingests incoming emails through a background IMAP poller and subjects them to an advanced multi-stage classification pipeline. Each email component is evaluated using **9 distinct risk modules**, producing a transparent Risk Score and corresponding **SHAP explanation** on the frontend.

### 🎭 Core Components
- **The Brain (FastAPI)**: Accepts emails, orchestrates the 9 sub-agents, aggregates scores, and serves the data.
- **The Watcher (IMAP Poller / OAuth)**: A seamless background daemon. Connects securely to Google via explicit **OAuth2**, polling your Gmail inbox every 12 seconds and dispatching unseen mail instantly.
- **The Command Center (React UI)**: An aesthetic, 3D-accelerated interactive web interface that displays live alerts, risk bands, and granular threat explanations.

---

## ⚡ Key Features

| 🛡️ Security Module | ⚖️ Risk Weight | 🔍 What it Does |
| --- | ---: | --- |
| **🔑 Credential Exposure** | 30% | Scans for accidentally exposed secrets, API keys, passwords, and PII. |
| **🦠 Malware Scanner** | 25% | Analyzes attachments (PDFs, macros, binaries) for embedded malicious payloads. |
| **🤖 AI Text Detection** | 20% | Classifies linguistic artifacts to spot GPT/Claude generated phishing traps. |
| **🎣 Email Phishing** | 15% | High-accuracy `XGBoost` & TF-IDF pipeline specialized in modern spear-phishing. |
| **🔗 URL Detection** | 7% | Unmasks malicious domains, homograph attacks, and shortened URL exploits. |
| **💉 Prompt Injection** | 3% | Flags jailbreak patterns intended to manipulate upstream LLMs or endpoints. |
| **🧠 Fusion Engine** | Overall | Uses an ensemble algorithm to calculate realistic composite threat scores. |

---

## 🚀 Quick Start Guide

### 1. Requirements
*   **Python 3.10+** and **Node.js**
*   A **Google Cloud Project** (for OAuth2 Credentials)
*   A test **Gmail account**

### 2. Setup the Environment

```bash
# Clone the repository
git clone https://github.com/maurya-aryan/Trident-AI-Fraud-Detection-Engine.git
cd Trident-AI-Fraud-Detection-Engine

# Setup backend Python environment
python -m venv .venv
# Activate: `source .venv/bin/activate` (Mac/Linux) or `.venv\Scripts\activate` (Windows)
pip install -r requirements.txt
```

### 3. Model Training (First Time Only)
The ML models require a one-time pipeline initialization to generate `.pkl` and `.json` artifacts in `data/models/`.
```bash
python scripts/train_email_phishing_on_test.py
python scripts/train_url_detector_on_test.py
python scripts/train_fusion_on_test.py
```

### 4. Configuration
Create a `.env` file in the root directory. This configures critical encryption keys and OAuth settings.

```env
# Backend/IMAP Settings
TOKEN_MASTER_KEY="your-secure-fernet-key-here"
IMAP_POLL_INTERVAL=12
IMAP_MARK_SEEN=false

# Google OAuth2 Credentials
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/google/callback"
```

---

## 💻 Running the Ecosystem

You need your **Backend**, **Frontend**, and **Poller** running simultaneously in three separate terminal tabs.

#### Terminal 1: FastAPI Backend
```bash
python main.py api
# Runs on http://0.0.0.0:8000
# OpenAPI Docs: http://localhost:8000/docs
```

#### Terminal 2: React Frontend UI
```bash
cd frontend
npm install
npm run dev
# Vite runs the app, accessible via http://localhost:5173
```

#### Terminal 3: IMAP Action Poller
*(Make sure the Python virtual env is active)*
```bash
python scripts/run_imap_poller.py
# Poller intercepts unseen messages and forwards them to the API
```

---

## 📊 Dashboard & Risk Protocol

TRIDENT classifies inbound emails into four operational risk bands:

*   `CRITICAL [🔴 76-100]` — High confidence of severe threat. Immediate block/neutralize target.
*   `HIGH     [🟠 51-75]`  — Escalated for manual review. Contains definitive suspicious payloads.
*   `MEDIUM   [🟡 21-50]`  — Flagged. Informational warning issued to user.
*   `LOW      [🟢 0-20]`   — Verified and cleared for reading.

Beneath each email entry, a **SHAP Explanation Chart** renders local interpretable explanations, showing *exactly* which module attributed what percentage to the final risk score.

---

## 📦 Architecture Map
```text
Trident-AI-Fraud-Detection-Engine/
├── api/             # FastAPI endpoints (auth, detect, alerts, health)
├── core/            # Main orchestrator (trident.py), Data models, Token stores
├── ingest/          # IMAP adapter bytes parsing & processing trackers
├── modules/         # Threat Detection Modules (Phishing, Malware, AI Text, etc.)
├── frontend/        # React + Vite 3D interactive user interface
├── scripts/         # Pollers, standalone trainers, demo scripts
└── data/            # Local SQLite/JSON persistence & ML model pipelines
```

---

## 🛡️ License & Disclaimer

> **Note:** TRIDENT is primarily a research prototype. Built to evaluate adversarial mechanics in email threat vectors and showcase multi-layered ML orchestration. Ensure explicit permission before connecting TRIDENT to production enterprise environments.

<br/>

<div align="center">
  <i>Built to detect what the human eye cannot.</i>
</div>
