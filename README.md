<div align="center">

<br/>

# ⚔ TRIDENT

**Multi-Modal AI Fraud & Threat Detection Engine**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square)](#)
[![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)](#)
[![XGBoost](https://img.shields.io/badge/XGBoost-EC6C00?style=flat-square)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#)

*An AI-powered inbox guardian. Real-time threat classification with transparent, explainable scoring.*

<br/>

</div>

---

## Overview

TRIDENT is a multi-stage email threat detection engine. It polls your Gmail inbox via OAuth2, subjects each email to **9 parallel risk modules**, and surfaces a weighted composite score with SHAP-driven explanations on a live React dashboard.

**Three moving parts:**
- **API** — FastAPI backend that orchestrates detection and serves results
- **Poller** — Background IMAP daemon polling every 12 seconds via Google OAuth2
- **UI** — 3D-accelerated React dashboard with live alerts and risk breakdowns

---

## Threat Modules

| Module | Weight | Description |
|---|---:|---|
| 🔑 Credential Exposure | 30% | Detects exposed secrets, API keys, and PII |
| 🦠 Malware Scanner | 25% | Analyzes PDFs, macros, and binaries for payloads |
| 🤖 AI Text Detection | 20% | Spots GPT/Claude-generated phishing content |
| 🎣 Email Phishing | 15% | XGBoost + TF-IDF spear-phishing classifier |
| 🔗 URL Detection | 7% | Flags malicious domains, homographs, shortened URLs |
| 💉 Prompt Injection | 3% | Catches jailbreak patterns targeting upstream LLMs |

Scores are fused via an ensemble algorithm into a single **0–100 Risk Score**.

---

## Risk Bands

| Level | Range | Action |
|---|---|---|
| 🔴 CRITICAL | 76–100 | Block and neutralize immediately |
| 🟠 HIGH | 51–75 | Escalate for manual review |
| 🟡 MEDIUM | 21–50 | Flag with informational warning |
| 🟢 LOW | 0–20 | Cleared for reading |

---

## Quick Start

### Requirements
- Python 3.10+, Node.js
- Google Cloud Project (for OAuth2)
- A Gmail test account

### Install

```bash
git clone https://github.com/maurya-aryan/Trident-AI-Fraud-Detection-Engine.git
cd Trident-AI-Fraud-Detection-Engine

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Train Models (First Run Only)

```bash
python scripts/train_email_phishing_on_test.py
python scripts/train_url_detector_on_test.py
python scripts/train_fusion_on_test.py
```

### Configure

Create `.env` in the project root:

```env
TOKEN_MASTER_KEY="your-secure-fernet-key"
IMAP_POLL_INTERVAL=12
IMAP_MARK_SEEN=false

GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/google/callback"
```

### Run

Open three terminals:

```bash
# Terminal 1 — Backend
python main.py api
# → http://localhost:8000  |  Docs: http://localhost:8000/docs

# Terminal 2 — Frontend
cd frontend && npm install && npm run dev
# → http://localhost:5173

# Terminal 3 — Poller
python scripts/run_imap_poller.py
```

---

## Project Structure

```
Trident-AI-Fraud-Detection-Engine/
├── api/          FastAPI endpoints (auth, detect, alerts, health)
├── core/         Orchestrator, data models, token store
├── ingest/       IMAP adapter and processing trackers
├── modules/      Threat detection modules
├── frontend/     React + Vite dashboard
├── scripts/      Pollers, trainers, demo utilities
└── data/         SQLite/JSON persistence and ML model artifacts
```

---

## Disclaimer

TRIDENT is a research prototype built to study adversarial email mechanics and multi-layered ML orchestration. Obtain explicit permission before connecting to production environments.

<br/>

<div align="center">
<sub>Built to detect what the human eye cannot.</sub>
</div>
