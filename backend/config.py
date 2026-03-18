"""
TRIDENT Configuration using Pydantic Settings
"""
from pathlib import Path
from typing import Dict, Set, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with type validation and .env loading"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ========== Security & Auth ==========
    TOKEN_MASTER_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # ========== API Configuration ==========
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    TRIDENT_API_URL: str = "http://localhost:8000"

    # ========== Database ==========
    DATABASE_URL: str = "sqlite:///./trident_alerts.db"

    # ========== IMAP Configuration ==========
    IMAP_HOST: str = "imap.gmail.com"
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""
    IMAP_POLL_INTERVAL: int = 12
    IMAP_MARK_SEEN: bool = False
    IMAP_PROCESSOR_FILE: str = "processed_uids.txt"

    # ========== URLs ==========
    TRIDENT_URL: str = "http://127.0.0.1:8000/detect"
    ALERTS_URL: str = "http://127.0.0.1:8000/alerts"

    # ========== AI Model Configuration ==========
    AI_TEXT_MODEL: str = "roberta-base-openai-detector"
    AI_TEXT_FALLBACK: bool = True

    # ========== ClamAV Configuration ==========
    CLAMD_HOST: str = "127.0.0.1"
    CLAMD_PORT: int = 3310
    CLAMD_ENABLED: bool = False

    # ========== Logging ==========
    LOG_LEVEL: str = "INFO"

    # ========== Base Paths ==========
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def DATA_DIR(self) -> Path:
        return self.BASE_DIR / "data"

    @property
    def MODELS_DIR(self) -> Path:
        return self.DATA_DIR / "models"

    @property
    def TEST_SAMPLES_DIR(self) -> Path:
        return self.DATA_DIR / "test_samples"

    # ========== Fusion Model Weights ==========
    @property
    def FUSION_WEIGHTS(self) -> Dict[str, float]:
        return {
            "credential_score": 0.30,
            "ai_text_score": 0.20,
            "malware_score": 0.25,
            "email_phishing_score": 0.15,
            "url_score": 0.07,
            "injection_score": 0.03,
        }

    # ========== Risk Band Thresholds ==========
    @property
    def RISK_BANDS(self) -> Dict[str, tuple]:
        return {
            "CRITICAL": (76, 100),
            "HIGH": (51, 75),
            "MEDIUM": (21, 50),
            "LOW": (0, 20),
        }

    # ========== Risk Actions ==========
    @property
    def RISK_ACTIONS(self) -> Dict[str, str]:
        return {
            "CRITICAL": "BLOCK",
            "HIGH": "ESCALATE",
            "MEDIUM": "WARN",
            "LOW": "VERIFY",
        }

    # ========== Dangerous File Extensions ==========
    @property
    def DANGEROUS_EXTENSIONS(self) -> Set[str]:
        return {
            ".exe", ".bat", ".cmd", ".scr", ".ps1", ".vbs",
            ".js", ".jar", ".msi", ".dll", ".com", ".pif",
            ".reg", ".hta", ".lnk", ".wsf", ".wsh"
        }

    # ========== Urgency Keywords ==========
    @property
    def URGENCY_WORDS(self) -> List[str]:
        return [
            "urgent", "immediately", "verify", "confirm", "suspend",
            "expire", "click here", "act now", "limited time", "warning",
            "alert", "security", "account", "blocked", "unauthorized",
            "suspicious", "validate", "update", "required", "action needed"
        ]

    # ========== Prompt Injection Patterns ==========
    @property
    def INJECTION_PATTERNS(self) -> List[str]:
        return [
            r"ignore\s+(?:all\s+)?previous\s+instructions",
            r"system\s+prompt",
            r"dan\s+mode",
            r"jailbreak",
            r"forget\s+(?:all\s+)?(?:instructions|memory)",
            r"show\s+me\s+(?:the\s+)?(?:api|key|secret|password)",
            r"enable\s+developer\s+mode",
            r"you\s+are\s+now\s+(?:an?\s+)?(?:unrestricted|free|evil)",
            r"pretend\s+(?:you\s+are|to\s+be)\s+(?:an?\s+)?(?:ai|bot|system)",
            r"disregard\s+(?:all\s+)?(?:previous|prior)\s+",
            r"override\s+(?:all\s+)?(?:safety|restrictions|rules)",
            r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
            r"bypass\s+(?:all\s+)?(?:filters|restrictions|rules|safety)",
        ]

    # ========== Trusted Domains ==========
    @property
    def TRUSTED_DOMAINS(self) -> Set[str]:
        return {
            "google.com", "microsoft.com", "apple.com", "amazon.com",
            "github.com", "stackoverflow.com", "wikipedia.org", "youtube.com",
            "linkedin.com", "twitter.com", "facebook.com", "instagram.com",
            "paypal.com", "stripe.com", "cloudflare.com", "fastly.com",
        }

    # ========== Financial Domains ==========
    @property
    def FINANCIAL_DOMAINS(self) -> Set[str]:
        return {
            "barclays.co.uk", "barclays.com", "hsbc.com", "lloydsbank.com",
            "natwest.com", "santander.co.uk", "rbs.co.uk", "chase.com",
            "wellsfargo.com", "bankofamerica.com", "citibank.com",
        }


# Global settings instance
settings = Settings()
