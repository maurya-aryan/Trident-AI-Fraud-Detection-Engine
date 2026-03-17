# Changes Summary — Phishing Model & OAuth fixes

This document lists all files created and modified during the recent work to improve the Email Phishing model and fix XOAUTH2 IMAP authentication. Use this to review changes across branches.

## New files created

- `scripts/augment_and_train_phishing.py`
  - Purpose: Generate synthetic phishing samples, build a TF-IDF + numeric-features pipeline, run 5‑fold CV, train final model and save it as `data/models/email_phishing_v2.pkl`.
  - Notes: Reproducible augmentation using templates; saves joblib pipeline.

- `docs/mailbox-frontend-integration.md`
  - Purpose: Documentation explaining how frontend, backend and poller integrate, env requirements, and how to run the OAuth flow and poller.

## Files modified

- `modules/gmail_xoauth2.py` (modified)
  - Purpose: Build XOAUTH2 auth string used by `imaplib.IMAP4_SSL.authenticate`.
  - Change summary: Previously returned a base64-encoded auth string, which caused `Invalid SASL argument` because `imaplib` base64-encodes the callback result again. Now the function returns the raw XOAUTH2 string (not base64-encoded) and includes a clarifying docstring comment.

- `modules/email_phishing.py` (modified)
  - Purpose: Email phishing detection module used by TRIDENT.
  - Change summary:
    - Added imports: `joblib`, `Path`.
    - Updated `EmailPhishingDetector.__init__` to attempt loading a persisted model in this order:
      1. `data/models/email_phishing_v2.pkl` (joblib pipeline)
      2. `data/models/email_phishing_v2.json` (legacy XGBoost JSON)
      3. Fall back to training on the small synthetic dataset if no persisted model exists
    - This allows the backend to use an improved pipeline if available, and preserves fallback behavior.

- `scripts/augment_and_train_phishing.py` (created) — note: added as new script; see above.

- `scripts/train_email_phishing_on_test.py` (unchanged but used)
  - Purpose: Existing training script that trains an XGBoost model on `data/test_emails.csv` and saves `data/models/email_phishing_v2.json`.
  - Notes: This script was used earlier to produce an XGBoost JSON model; the loader in `modules/email_phishing.py` now supports loading this legacy JSON model.

## Generated model files (training outputs)

- `data/models/email_phishing_v2.json` — XGBoost model saved by `scripts/train_email_phishing_on_test.py` (legacy format).
- `data/models/email_phishing_v2.pkl` — joblib pipeline (TF-IDF + numeric features + classifier) saved by `scripts/augment_and_train_phishing.py`.

> Note: The model files are generated artifacts and may or may not be committed to the repo depending on your branch policy. If you want them checked into a branch, commit them explicitly.

## How to inspect these changes across branches

From the repository root you can run the following (PowerShell) commands to compare branches and show changed files:

- Show changed files between current branch and `main`:

```powershell
# list file names changed between current branch and origin/main
git fetch origin
git diff --name-only origin/main..HEAD
```

- Show the full diff for a particular file across branches:

```powershell
# show diff of modules/email_phishing.py between current branch and origin/main
git fetch origin
git diff origin/main..HEAD -- modules/email_phishing.py
```

- See a short local commit history for files touched:

```powershell
git log --follow --pretty=oneline -- modules/email_phishing.py
```

- If you want to check whether the model files are present on a branch (they are generated locally), compare tree or list files on remote:

```powershell
# show if file exists on remote branch (quick check)
git ls-tree -r origin/devmain2 --name-only | Select-String "data/models/email_phishing_v2.pkl"
```

## Quick verification steps

1. Confirm model files exist locally:

```powershell
ls data\models\
```

2. Restart the API to pick up the saved model (backend auto-loads `.pkl` or `.json`):

```powershell
python main.py api
```

3. Run the test/eval script to see module-level metrics:

```powershell
$env:PYTHONPATH = 'C:\Users\91801\Documents\GitHub\Trident-AI-Fraud-Detection-Engine'
C:/Users/91801/AppData/Local/Programs/Python/Python310/python.exe scripts/test_models.py
```

## Notes & recommendations

- The augmentation script produces many synthetic phishing samples — results on that augmented set look excellent, but validate on realistic holdout data before trusting production thresholds.
- If you want me to add a small Git hook or a convenience command (e.g., `make train-phish`) to make reproducing the training easier, I can add it.

---

If you want, I can also produce a compact `git` command that lists exactly which of the above files differ between two branches you specify (e.g., `devmain2` vs `main`) and output a short report. Say which branches to compare and I'll add that to this doc or run it for you.