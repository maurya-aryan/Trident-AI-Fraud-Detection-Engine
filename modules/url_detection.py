"""
Module #6: URL Detection
Detects malicious / spoofed URLs using XGBoost + heuristics.
"""
import logging
import re
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Trusted / known-good domains (short-list for demo)
# ---------------------------------------------------------------------------
TRUSTED_DOMAINS = {
    "google.com", "microsoft.com", "apple.com", "amazon.com",
    "github.com", "stackoverflow.com", "wikipedia.org", "youtube.com",
    "linkedin.com", "twitter.com", "facebook.com", "instagram.com",
    "paypal.com", "stripe.com", "cloudflare.com", "fastly.com",
    "barclays.co.uk", "barclays.com", "hsbc.com", "lloydsbank.com",
    "natwest.com", "santander.co.uk", "chase.com", "wellsfargo.com",
    "bankofamerica.com", "citibank.com",
}

# TLDs commonly abused in phishing
SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".pw", ".top", ".click", ".link", ".info"}

# Brand spoofing keywords
BRAND_KEYWORDS = [
    "paypal", "amazon", "microsoft", "apple", "google", "facebook",
    "instagram", "twitter", "netflix", "bank", "secure", "alert",
    "update", "verify", "signin", "login", "account", "confirm",
    "barclays", "hsbc", "natwest", "chase", "citibank",
]

# ---------------------------------------------------------------------------
# Synthetic training data  (url, is_malicious)
# ---------------------------------------------------------------------------
TRAINING_URLS: List[Tuple[str, int]] = [
    # Malicious
    ("http://secure-alert.xyz/login.php", 1),
    ("http://fake-bank.xyz/verify", 1),
    ("http://paypa1.com/account", 1),
    ("http://amazon-security-alert.com/update", 1),
    ("http://192.168.1.1/phish", 1),
    ("http://bit.ly/2xXkq9z", 1),
    ("http://microsoft-support-alert.tk/fix", 1),
    ("http://secure.login-now.pw/account", 1),
    ("http://verify-your-identity.xyz/step1", 1),
    ("http://banking-alert.ml/login", 1),
    ("http://account-suspended.click/verify", 1),
    ("http://apple-id-alert.top/signin", 1),
    # Legitimate
    ("https://www.google.com/search", 0),
    ("https://github.com/user/repo", 0),
    ("https://www.microsoft.com/en-us", 0),
    ("https://stackoverflow.com/questions", 0),
    ("https://www.amazon.com/product", 0),
    ("https://www.paypal.com/signin", 0),
    ("https://mail.google.com/mail/u/0/", 0),
    ("https://docs.python.org/3/library", 0),
    ("https://en.wikipedia.org/wiki/Python", 0),
    ("https://www.linkedin.com/in/user", 0),
    ("https://www.youtube.com/watch?v=abc", 0),
    ("https://twitter.com/user/status", 0),
]


def _get_base_domain(hostname: str) -> str:
    """Extract base domain (e.g. 'sub.example.co.uk' → 'example.co.uk')."""
    parts = hostname.lower().split(".")
    if len(parts) >= 3 and parts[-2] in {"co", "com", "net", "org", "gov"}:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else hostname


def _extract_url_features(url: str) -> np.ndarray:
    """Extract 12 numerical features from a URL string."""
    try:
        parsed = urlparse(url if "://" in url else "http://" + url)
        hostname = parsed.hostname or ""
        path = parsed.path or ""
        full = url.lower()
    except Exception:
        return np.zeros(12)

    base_domain = _get_base_domain(hostname)

    # 1. Is HTTPS
    is_https = 1.0 if parsed.scheme == "https" else 0.0

    # 2. Domain length (longer = more suspicious)
    domain_len = min(len(hostname) / 50.0, 1.0)

    # 3. Special characters in domain
    special_in_domain = len(re.findall(r"[-_]", hostname)) / max(len(hostname), 1)

    # 4. Number of subdomains
    subdomain_count = max(len(hostname.split(".")) - 2, 0) / 5.0

    # 5. IP address as domain
    is_ip = 1.0 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname) else 0.0

    # 6. Suspicious TLD
    tld = "." + hostname.split(".")[-1] if "." in hostname else ""
    suspicious_tld = 1.0 if tld in SUSPICIOUS_TLDS else 0.0

    # 7. Brand keyword in domain (typosquatting)
    brand_hit = 1.0 if any(k in hostname and base_domain not in TRUSTED_DOMAINS for k in BRAND_KEYWORDS) else 0.0

    # 8. Trusted domain
    is_trusted = 1.0 if base_domain in TRUSTED_DOMAINS else 0.0

    # 9. URL length
    url_len = min(len(url) / 200.0, 1.0)

    # 10. Query parameter count
    param_count = len(parsed.query.split("&")) / 10.0 if parsed.query else 0.0

    # 11. Path depth
    path_depth = len([p for p in path.split("/") if p]) / 5.0

    # 12. Numeric characters in domain ratio
    num_ratio = sum(c.isdigit() for c in hostname) / max(len(hostname), 1)

    return np.array([
        is_https, domain_len, special_in_domain, subdomain_count,
        is_ip, suspicious_tld, brand_hit, is_trusted,
        url_len, param_count, path_depth, num_ratio,
    ], dtype=float)


class URLDetector:
    """Detects malicious URLs using ML + heuristics."""

    def __init__(self):
        self.model = None
        self._trained = False
        # Try to load a saved URL model first
        try:
            import xgboost as xgb
            from pathlib import Path

            mp = Path("data/models/url_detector_v2.json")
            if mp.exists():
                m = xgb.XGBClassifier()
                try:
                    m.load_model(str(mp))
                    self.model = m
                    self._trained = True
                    logger.info(f"Loaded URL detection model from {mp}")
                    return
                except Exception:
                    logger.warning(f"Failed to load URL model from {mp}; will train on synthetic data.")
        except Exception:
            pass

        # Fallback: train on small synthetic dataset if xgboost available
        self._train_on_synthetic()

    def _train_on_synthetic(self) -> None:
        try:
            import xgboost as xgb

            X = np.array([_extract_url_features(url) for url, _ in TRAINING_URLS])
            y = np.array([label for _, label in TRAINING_URLS], dtype=int)

            self.model = xgb.XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1,
                use_label_encoder=False, eval_metric="logloss", random_state=42,
            )
            self.model.fit(X, y)
            self._trained = True
            logger.info("URL detection model trained on synthetic data.")
        except Exception as exc:
            logger.warning(f"URL model training failed ({exc}). Using heuristic fallback.")

    def _heuristic_score(self, url: str) -> float:
        features = _extract_url_features(url)
        # is_https (inverse), domain_len, special, subdomain, ip, susp_tld, brand, trusted (inverse)
        weight_vec = np.array([
            -0.20,  # is_https (negative = good)
            0.10,   # domain_len
            0.10,   # special_in_domain
            0.05,   # subdomain_count
            0.20,   # is_ip
            0.15,   # suspicious_tld
            0.15,   # brand_hit
            -0.25,  # is_trusted (negative = good)
            0.05,   # url_len
            0.05,   # param_count
            0.05,   # path_depth
            0.05,   # num_ratio
        ])
        raw = float(np.dot(features, weight_vec))
        # Shift & clamp to 0-1
        return max(0.0, min(raw + 0.5, 1.0))

    def train(self, urls: List[str], labels: List[int]) -> None:
        """Re-train on custom data."""
        try:
            import xgboost as xgb

            X = np.array([_extract_url_features(u) for u in urls])
            y = np.array(labels, dtype=int)
            self.model = xgb.XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1,
                use_label_encoder=False, eval_metric="logloss", random_state=42,
            )
            self.model.fit(X, y)
            self._trained = True
        except Exception as exc:
            logger.error(f"Training error: {exc}")

    def detect_malicious(self, url: str) -> Dict:
        """
        Analyse a URL for malicious indicators.

        Returns:
            {
                'malicious_probability': 0-100,
                'is_malicious': bool,
                'confidence': 0-1,
                'risk': 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW',
                'indicators': [str, ...]
            }
        """
        if not url:
            return {
                "malicious_probability": 0,
                "is_malicious": False,
                "confidence": 1.0,
                "risk": "LOW",
                "indicators": [],
            }

        features = _extract_url_features(url)

        if self._trained and self.model is not None:
            try:
                proba = self.model.predict_proba(features.reshape(1, -1))[0][1]
            except Exception:
                proba = self._heuristic_score(url)
        else:
            proba = self._heuristic_score(url)

        # Clamp trusted domains to LOW
        try:
            parsed = urlparse(url if "://" in url else "http://" + url)
            base = _get_base_domain(parsed.hostname or "")
            if base in TRUSTED_DOMAINS:
                proba = min(proba, 0.15)
        except Exception:
            pass

        prob_pct = float(round(float(proba) * 100, 1))
        is_malicious = prob_pct >= 50
        confidence = float(round(abs(float(proba) - 0.5) * 2, 2))

        if prob_pct >= 80:
            risk = "CRITICAL"
        elif prob_pct >= 60:
            risk = "HIGH"
        elif prob_pct >= 35:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # Human-readable indicators
        indicators: List[str] = []
        feature_names = [
            ("is_https", lambda v: v == 0.0, "No HTTPS (unencrypted)"),
            ("is_ip", lambda v: v == 1.0, "IP address used as domain"),
            ("suspicious_tld", lambda v: v == 1.0, "Suspicious top-level domain"),
            ("brand_hit", lambda v: v == 1.0, "Possible brand impersonation"),
            ("domain_len", lambda v: v > 0.5, "Unusually long domain name"),
            ("subdomain_count", lambda v: v > 0.4, "Multiple subdomains"),
        ]
        for idx, (fname, check, msg) in enumerate(feature_names):
            if check(features[idx if idx < 8 else idx]):
                indicators.append(msg)

        return {
            "malicious_probability": prob_pct,
            "is_malicious": bool(is_malicious),
            "confidence": float(confidence),
            "risk": risk,
            "indicators": indicators,
        }

    def get_risk_score(self, url: str) -> float:
        """Return normalised 0-100 risk score for fusion model."""
        result = self.detect_malicious(url)
        return result["malicious_probability"]
