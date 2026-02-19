"""
TRIDENT Configuration
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
TEST_SAMPLES_DIR = DATA_DIR / "test_samples"

# Model configuration
AI_TEXT_MODEL = os.getenv("AI_TEXT_MODEL", "roberta-base-openai-detector")
AI_TEXT_FALLBACK = True  # Use heuristic if model unavailable

# ClamAV configuration
CLAMD_HOST = os.getenv("CLAMD_HOST", "127.0.0.1")
CLAMD_PORT = int(os.getenv("CLAMD_PORT", "3310"))
CLAMD_ENABLED = os.getenv("CLAMD_ENABLED", "false").lower() == "true"

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# Fusion model weights
FUSION_WEIGHTS = {
    "credential_score": 0.30,
    "ai_text_score": 0.20,
    "malware_score": 0.25,
    "email_phishing_score": 0.15,
    "url_score": 0.07,
    "injection_score": 0.03,
}

# Risk band thresholds
RISK_BANDS = {
    "CRITICAL": (76, 100),
    "HIGH": (51, 75),
    "MEDIUM": (21, 50),
    "LOW": (0, 20),
}

# Recommended actions per risk band
RISK_ACTIONS = {
    "CRITICAL": "BLOCK",
    "HIGH": "ESCALATE",
    "MEDIUM": "WARN",
    "LOW": "VERIFY",
}

# Dangerous file extensions
DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".scr", ".ps1", ".vbs",
    ".js", ".jar", ".msi", ".dll", ".com", ".pif",
    ".reg", ".hta", ".lnk", ".wsf", ".wsh"
}

# Urgency keywords for phishing detection
URGENCY_WORDS = [
    "urgent", "immediately", "verify", "confirm", "suspend",
    "expire", "click here", "act now", "limited time", "warning",
    "alert", "security", "account", "blocked", "unauthorized",
    "suspicious", "validate", "update", "required", "action needed"
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"system\s+prompt",
    r"dan\s+mode",
    r"jailbreak",
    r"forget\s+(?:all\s+)?instructions",
    r"show\s+me\s+(?:the\s+)?(?:api|key|secret|password)",
    r"enable\s+developer\s+mode",
    r"you\s+are\s+now\s+(?:an?\s+)?(?:unrestricted|free|evil)",
    r"pretend\s+(?:you\s+are|to\s+be)\s+(?:an?\s+)?(?:ai|bot|system)",
    r"disregard\s+(?:all\s+)?(?:previous|prior)\s+",
    r"override\s+(?:all\s+)?(?:safety|restrictions|rules)",
    r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
    r"bypass\s+(?:all\s+)?(?:filters|restrictions|rules|safety)",
]

# Trusted domains (not exhaustive, for demo)
TRUSTED_DOMAINS = {
    "google.com", "microsoft.com", "apple.com", "amazon.com",
    "github.com", "stackoverflow.com", "wikipedia.org", "youtube.com",
    "linkedin.com", "twitter.com", "facebook.com", "instagram.com",
    "paypal.com", "stripe.com", "cloudflare.com", "fastly.com",
}

# Known bank / financial domains
FINANCIAL_DOMAINS = {
    "barclays.co.uk", "barclays.com", "hsbc.com", "lloydsbank.com",
    "natwest.com", "santander.co.uk", "rbs.co.uk", "chase.com",
    "wellsfargo.com", "bankofamerica.com", "citibank.com",
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
