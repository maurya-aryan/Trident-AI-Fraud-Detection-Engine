# TRIDENT — AI Fraud Detection Engine

> A multi-modal AI system that monitors your Gmail inbox in real time, analyses every incoming email for fraud, phishing, malware links, credential exposure, and prompt injection, and displays live alerts on a web dashboard.

---

## What Does It Do?

When you run TRIDENT, three things work together:

| Component | What it does |
|---|---|
| **FastAPI backend** | The brain. Accepts emails, runs 9 detection modules, returns a risk score 0–100 |
| **Streamlit dashboard** | A live web page that shows all alerts with scores, risk bands, and SHAP explanations |
| **IMAP Poller** | Runs in the background, checks your Gmail every 12 seconds, sends new emails to the backend automatically |

---

## Requirements

- Python **3.10 or 3.11** (recommended)
- A **Gmail account** with 2-Step Verification turned on
- A **Gmail App Password** (explained step by step below)
- Windows, macOS, or Linux

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/Trident-AI-Fraud-Detection-Engine.git
cd Trident-AI-Fraud-Detection-Engine
```

---

## Step 2 — Create a Virtual Environment

```bash
# Create the virtual environment
python -m venv .venv

# Activate it — Windows
.venv\Scripts\activate

# Activate it — macOS / Linux
source .venv/bin/activate
```

You will see `(.venv)` at the start of your terminal prompt. This means the virtual environment is active.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs everything: FastAPI, Streamlit, XGBoost, HuggingFace Transformers, SHAP, and more. It may take a few minutes the first time.

---

## Step 4 — Set Up Gmail App Password (Important)

TRIDENT connects to your Gmail inbox over IMAP to read incoming emails. Gmail does **not** allow your normal password for this — you must create a special **App Password**. This takes about 2 minutes.

### 4a — Turn on 2-Step Verification (if not already on)

1. Go to your Google Account: [https://myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left menu
3. Under "How you sign in to Google", click **2-Step Verification**
4. Follow the on-screen steps to turn it on (you can use your phone number or the Google Authenticator app)

> If 2-Step Verification is already turned on, skip to step 4b.

### 4b — Generate an App Password

1. Go to: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - If you don't see this page, make sure 2-Step Verification is turned on first
2. You may be asked to sign in again
3. In the **App name** box, type anything you want — for example: `Trident`
4. Click **Create**
5. Google will show you a **16-character password** like `abcd efgh ijkl mnop`
6. **Copy this password** — you will not be able to see it again
7. Remove the spaces before using it, so it becomes: `abcdefghijklmnop`

> Keep this App Password private. It gives access to your Gmail inbox.

---

## Step 5 — Set Environment Variables

TRIDENT reads your Gmail credentials from environment variables, not from any file. This keeps your password out of the code.

### Windows (PowerShell)

```powershell
$env:IMAP_USER     = "your.email@gmail.com"
$env:IMAP_PASSWORD = "abcdefghijklmnop"   # The App Password from Step 4 (no spaces)
```

### macOS / Linux (Terminal)

```bash
export IMAP_USER="your.email@gmail.com"
export IMAP_PASSWORD="abcdefghijklmnop"   # The App Password from Step 4 (no spaces)
```

> These variables are only set for the current terminal session. You will need to set them again if you open a new terminal, or add them to your shell profile (`.bashrc`, `.zshrc`, etc.).

### Optional Variables

| Variable | Default | Description |
|---|---|---|
| `IMAP_POLL_INTERVAL` | `12` | How often (in seconds) to check for new emails |
| `IMAP_MARK_SEEN` | `false` | Set to `true` to mark emails as read after processing |
| `TRIDENT_URL` | `http://127.0.0.1:8000/detect` | URL of the FastAPI detection endpoint |
| `ALERTS_URL` | `http://127.0.0.1:8000/alerts` | URL where alerts are posted |

---

## Step 6 — Train the Models (First Time Only)

The ML models need to be trained once before the engine can run. This generates the model files in `data/models/`.

```bash
python scripts/train_email_phishing_on_test.py
python scripts/train_url_detector_on_test.py
python scripts/train_fusion_on_test.py
```

Each script takes about 10–30 seconds to run.

---

## Step 7 — Run TRIDENT

You need **three separate terminals** running at the same time. Open three terminal windows (all with the virtual environment activated).

### Terminal 1 — Start the FastAPI Backend

```bash
python main.py api
```

You should see:
```
Starting TRIDENT API server on http://0.0.0.0:8000
API docs: http://localhost:8000/docs
```

Leave this running.

### Terminal 2 — Start the Dashboard

```bash
python main.py dashboard
```

Streamlit will open a browser tab automatically at `http://localhost:8501`. This is your live alert dashboard.

Leave this running.

### Terminal 3 — Start the IMAP Poller

Make sure you have set `IMAP_USER` and `IMAP_PASSWORD` in this terminal first (Step 5), then:

```bash
python scripts/run_imap_poller.py
```

You should see:
```
[poller] Connecting to IMAP imap.gmail.com as your.email@gmail.com
```

The poller will now check your inbox every 12 seconds. Any unread email it finds will be automatically analysed and the result will appear on the dashboard.

---

## Step 8 — Send a Test Email (Optional)

If you want to test the system with a realistic fraud email without waiting for a real one to arrive, you can use the demo sender script.

Set your sender credentials in the same terminal:

**Windows (PowerShell)**
```powershell
$env:SENDER_EMAIL    = "your.email@gmail.com"
$env:SENDER_PASSWORD = "abcdefghijklmnop"   # App Password
$env:RECIPIENT_EMAIL = "your.email@gmail.com"
```

**macOS / Linux**
```bash
export SENDER_EMAIL="your.email@gmail.com"
export SENDER_PASSWORD="abcdefghijklmnop"
export RECIPIENT_EMAIL="your.email@gmail.com"
```

Then run:

```bash
python scripts/send_demo_emails.py
```

This sends several test emails (phishing, safe, malware warning, etc.) to your own inbox. Within 12 seconds the poller will pick them up, analyse them, and you will see alerts appear on the dashboard.

---

## How the Dashboard Works

Open `http://localhost:8501` in your browser.

- **Alerts Table** — shows every email processed, with risk score, risk band, sender, and subject
- **Risk Bands**:
  - `CRITICAL` (76–100) — blocked immediately
  - `HIGH` (51–75) — escalated for review
  - `MEDIUM` (21–50) — warning issued
  - `LOW` (0–20) — verify and allow
- **SHAP Explanation** — shows which factors (credentials found, AI-written text, suspicious URLs, etc.) contributed most to the score

---

## Run the Demo Without Gmail

If you just want to see the detection engine work without setting up Gmail, run the built-in demo:

```bash
python main.py demo
```

This simulates a coordinated fraud attack (fake invoice email + malicious URL + executable attachment) entirely in the terminal and prints a full risk report.

---

## Run Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
Trident-AI-Fraud-Detection-Engine/
│
├── main.py                        # Entry point (api / dashboard / demo / test)
├── config.py                      # All configuration in one place
├── requirements.txt
│
├── modules/
│   ├── ai_text_detection.py       # Detects AI-generated text (GPT, Claude, etc.)
│   ├── credential_exposure.py     # Finds passwords, API keys, card numbers
│   ├── malware_scanner.py         # Scans file attachments
│   ├── prompt_injection.py        # Detects jailbreak / injection attempts
│   ├── email_phishing.py          # XGBoost phishing classifier
│   ├── url_detection.py           # Detects malicious URLs
│   ├── fusion_model.py            # Combines all scores into one risk score
│   ├── campaign_graph.py          # Links multiple related attacks
│   └── shap_explainer.py          # Explains why a score was given
│
├── core/
│   ├── data_models.py             # Data structures (Pydantic v2)
│   └── trident.py                 # Main orchestrator
│
├── api/
│   └── routes.py                  # FastAPI endpoints (/detect, /alerts, /health)
│
├── ingest/
│   ├── imap_adapter.py            # Parses raw email bytes
│   ├── imap_processor.py          # Tracks which emails have been processed
│   └── models.py                  # Signal data model
│
├── scripts/
│   ├── run_imap_poller.py         # Background Gmail poller
│   ├── send_demo_emails.py        # Sends test fraud emails to your inbox
│   ├── train_email_phishing_on_test.py
│   ├── train_url_detector_on_test.py
│   └── train_fusion_on_test.py
│
├── ui/
│   └── dashboard.py               # Streamlit live dashboard
│
├── data/
│   └── models/                    # Trained ML model files (generated by training scripts)
│
└── tests/
    ├── test_modules.py
    └── test_integration.py
```

---

## API Endpoints

Once the backend is running, visit `http://localhost:8000/docs` for the interactive API explorer.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/detect` | Analyse an email, returns risk score + breakdown |
| `POST` | `/alerts` | Push an alert to the dashboard |
| `GET` | `/alerts` | Get all stored alerts |
| `GET` | `/health` | Check if the server is running |

---

## Troubleshooting

**"Please set IMAP_USER and IMAP_PASSWORD environment variables"**
You forgot to set the environment variables in the terminal where the poller is running. Go back to Step 5.

**"Authentication failed" or "Invalid credentials" from Gmail**
- Make sure you are using the **App Password**, not your normal Gmail password
- Make sure the App Password has no spaces (remove all spaces when you copy it)
- Make sure 2-Step Verification is still turned on on your Google account

**The poller connects but never finds new emails**
- Make sure the emails you sent are going to **Inbox**, not spam
- The poller only picks up **UNSEEN (unread)** emails
- Check that `IMAP_MARK_SEEN` is not set to `true` (if it is, emails will be marked read and skipped on next run)

**Dashboard shows nothing**
- Make sure the FastAPI backend (Terminal 1) is running
- Make sure the backend was started before the poller

**Model file not found errors**
You skipped Step 6. Run the three training scripts first.

---

## Module Risk Weights

| Module | Weight | Description |
|---|---|---|
| Credential Exposure | 30% | Passwords, API keys, credit cards |
| Malware Scanner | 25% | Dangerous files, macros, PDF scripts |
| AI Text Detection | 20% | ChatGPT / Claude-written content |
| Email Phishing | 15% | ML phishing classifier |
| URL Detection | 7% | Malicious domain / URL analysis |
| Prompt Injection | 3% | Jailbreak pattern detection |

---

## License

This project is a research prototype. Use it for educational and evaluation purposes only.
