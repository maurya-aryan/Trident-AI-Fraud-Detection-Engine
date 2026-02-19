"""
Module #5: Email Phishing Detection
Detects phishing emails using TF-IDF + XGBoost classifier.
Auto-trains on a synthetic dataset on first use.
"""
import logging
import re
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Synthetic training data (email text, is_phishing)
# ---------------------------------------------------------------------------
TRAINING_DATA: List[Tuple[str, int]] = [
    # Phishing
    ("Your account needs verification NOW! Click here to confirm your identity!", 1),
    ("URGENT: Your bank account has been suspended. Verify immediately.", 1),
    ("Dear customer, your password will expire. Update now or lose access.", 1),
    ("Congratulations! You have won $1,000,000. Click here to claim your prize.", 1),
    ("Security Alert: Suspicious login detected. Verify your account immediately.", 1),
    ("Your PayPal account has been limited. Please confirm your information now.", 1),
    ("ACTION REQUIRED: Confirm your email address within 24 hours.", 1),
    ("Your credit card has been compromised. Click here to secure your account.", 1),
    ("Final warning: Your account will be deleted. Log in now to prevent this.", 1),
    ("ALERT: Unauthorized access to your account. Verify your identity immediately.", 1),
    ("Click here to verify your account details and avoid suspension.", 1),
    ("Your invoice is attached. Please confirm payment details.", 1),
    ("We detected unusual activity. Please update your password immediately.", 1),
    ("Your package could not be delivered. Confirm your address to reschedule.", 1),
    ("Login attempt from unknown device. Click here to secure your account.", 1),
    ("I trust this finds you well. Your account requires immediate verification.", 1),
    ("Please verify your banking credentials to continue using our services.", 1),
    ("Your account has been flagged for suspicious activity. Act now.", 1),
    # Legitimate
    ("Hi, just checking in with you. Hope you're doing well!", 0),
    ("Meeting at 2pm tomorrow in conference room B.", 0),
    ("Can you review the quarterly report before Friday?", 0),
    ("Happy birthday! Hope you have a wonderful day.", 0),
    ("The team lunch is scheduled for next Wednesday at noon.", 0),
    ("Please find attached the notes from today's meeting.", 0),
    ("Looking forward to catching up at the conference next week.", 0),
    ("Thank you for submitting your application. We will be in touch.", 0),
    ("Your order has been shipped. Expected delivery: Monday.", 0),
    ("The project deadline has been moved to March 15th.", 0),
    ("Reminder: performance reviews are due by end of month.", 0),
    ("Here's the summary of our Q4 results as discussed.", 0),
    ("Let me know if you need any help with the report.", 0),
    ("Can we reschedule our 1:1 to Thursday afternoon?", 0),
    ("Great work on the presentation today, the client was impressed.", 0),
    ("Just sent over the budget spreadsheet for your review.", 0),
]

# Urgency / phishing keywords
URGENCY_WORDS = [
    "urgent", "immediately", "verify", "confirm", "suspend", "expire",
    "click here", "act now", "limited time", "warning", "alert", "security",
    "account", "blocked", "unauthorized", "suspicious", "validate", "update",
    "required", "action needed", "final warning", "compromised", "flagged",
]


def _extract_features(text: str) -> np.ndarray:
    """Hand-crafted feature vector for a single email string."""
    lower = text.lower()
    words = re.findall(r"\b\w+\b", lower)
    word_set = set(words)

    # 1. URL count
    url_count = len(re.findall(r"https?://\S+|www\.\S+", lower))

    # 2. Urgency words count
    urgency_count = sum(1 for w in URGENCY_WORDS if w in lower)

    # 3. Exclamation marks
    excl_count = text.count("!")

    # 4. ALL CAPS words ratio
    all_caps = sum(1 for w in text.split() if w.isupper() and len(w) > 2)
    caps_ratio = all_caps / max(len(words), 1)

    # 5. Email length (normalised)
    length_norm = min(len(text) / 500.0, 1.0)

    # 6. Special character ratio
    special = sum(1 for c in text if not c.isalnum() and not c.isspace())
    special_ratio = special / max(len(text), 1)

    # 7. Contains suspicious domain-like strings
    suspicious_domains = len(re.findall(r"\b\w+\.\w{2,4}\b", lower))

    # 8. Action verbs (click, verify, confirm, update, login)
    action_verbs = len(re.findall(r"\b(click|verify|confirm|update|login|log.?in|secure|access)\b", lower))

    # 9. Financial terms
    financial = len(re.findall(r"\b(account|bank|credit|payment|invoice|billing|password|credential)\b", lower))

    # 10. Grammar quality proxy (avg sentence length – very long = suspicious)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    avg_sentence_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    grammar_score = min(avg_sentence_len / 20.0, 1.0)

    return np.array([
        url_count,
        urgency_count,
        excl_count,
        caps_ratio,
        length_norm,
        special_ratio,
        suspicious_domains,
        action_verbs,
        financial,
        grammar_score,
    ], dtype=float)


class EmailPhishingDetector:
    """XGBoost-based phishing email classifier."""

    def __init__(self):
        self.model = None
        self._trained = False
        self._train_on_synthetic()

    def _train_on_synthetic(self) -> None:
        try:
            import xgboost as xgb

            X = np.array([_extract_features(text) for text, _ in TRAINING_DATA])
            y = np.array([label for _, label in TRAINING_DATA], dtype=int)

            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                use_label_encoder=False,
                eval_metric="logloss",
                random_state=42,
            )
            self.model.fit(X, y)
            self._trained = True
            logger.info("Email phishing model trained on synthetic data.")
        except Exception as exc:
            logger.warning(f"XGBoost training failed ({exc}). Using heuristic fallback.")

    def _heuristic_score(self, text: str) -> float:
        features = _extract_features(text)
        # Weighted sum of features
        weights = [0.15, 0.25, 0.10, 0.10, 0.05, 0.05, 0.05, 0.15, 0.10, 0.00]
        score = float(np.dot(features[:len(weights)], weights))
        return min(score, 1.0)

    def train(self, emails: List[str], labels: List[int]) -> None:
        """Re-train on custom data."""
        try:
            import xgboost as xgb

            X = np.array([_extract_features(e) for e in emails])
            y = np.array(labels, dtype=int)
            self.model = xgb.XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1,
                use_label_encoder=False, eval_metric="logloss", random_state=42,
            )
            self.model.fit(X, y)
            self._trained = True
        except Exception as exc:
            logger.error(f"Training error: {exc}")

    def detect_phishing(self, email_text: str) -> Dict:
        """
        Classify an email as phishing or legitimate.

        Returns:
            {
                'phishing_probability': 0-100,
                'is_phishing': bool,
                'confidence': 0-1,
                'risk': 'HIGH' | 'MEDIUM' | 'LOW',
                'features': {feature_name: value}
            }
        """
        if not email_text:
            return {
                "phishing_probability": 0,
                "is_phishing": False,
                "confidence": 1.0,
                "risk": "LOW",
                "features": {},
            }

        features = _extract_features(email_text)

        if self._trained and self.model is not None:
            try:
                proba = self.model.predict_proba(features.reshape(1, -1))[0][1]
            except Exception:
                proba = self._heuristic_score(email_text)
        else:
            proba = self._heuristic_score(email_text)

        prob_pct = round(proba * 100, 1)
        is_phishing = prob_pct >= 50
        confidence = round(abs(proba - 0.5) * 2, 2)

        if prob_pct >= 70:
            risk = "HIGH"
        elif prob_pct >= 40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        feature_names = [
            "url_count", "urgency_count", "exclamation_marks",
            "caps_ratio", "length_norm", "special_char_ratio",
            "suspicious_domains", "action_verbs", "financial_terms",
            "grammar_score",
        ]

        return {
            "phishing_probability": prob_pct,
            "is_phishing": is_phishing,
            "confidence": confidence,
            "risk": risk,
            "features": dict(zip(feature_names, features.tolist())),
        }

    def get_risk_score(self, email_text: str) -> float:
        """Return normalised 0-100 risk score for fusion model."""
        result = self.detect_phishing(email_text)
        return result["phishing_probability"]
