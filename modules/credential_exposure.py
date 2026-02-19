"""
Module #2: Credential Exposure Detection
Finds passwords, API keys, credit cards, SSNs, JWTs etc. in text.
"""
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns – (name, compiled_pattern, description)
# ---------------------------------------------------------------------------
CREDENTIAL_PATTERNS: List[tuple] = [
    (
        "api_key_openai",
        re.compile(r"sk[-_](?:live|test|proj)?[-_]?[a-zA-Z0-9]{20,}", re.IGNORECASE),
        "OpenAI / Stripe-style API key",
    ),
    (
        "api_key_aws",
        re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE),
        "AWS Access Key ID",
    ),
    (
        "api_key_generic",
        re.compile(
            r"(?:api[_\-\s]?key|access[_\-\s]?token|auth[_\-\s]?token)"
            r"\s*[:=>\s]+['\"]?([a-zA-Z0-9_\-]{16,})['\"]?",
            re.IGNORECASE,
        ),
        "Generic API key / token",
    ),
    (
        "password",
        re.compile(
            r"(?:password|passwd|pwd|pass)\s*[:=\->\s]+['\"]?([^\s'\"]{6,})['\"]?",
            re.IGNORECASE,
        ),
        "Exposed password",
    ),
    (
        "credit_card",
        re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
        "Credit card number",
    ),
    (
        "ssn",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "Social Security Number",
    ),
    (
        "jwt",
        re.compile(
            r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+"
        ),
        "JSON Web Token (JWT)",
    ),
    (
        "private_key",
        re.compile(
            r"-----BEGIN\s+(?:RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----",
            re.IGNORECASE,
        ),
        "Private cryptographic key",
    ),
    (
        "github_token",
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}", re.IGNORECASE),
        "GitHub Personal Access Token",
    ),
    (
        "google_api_key",
        re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
        "Google API key",
    ),
    (
        "slack_token",
        re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}", re.IGNORECASE),
        "Slack token",
    ),
]


def _luhn_check(number: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    digits = [int(d) for d in re.sub(r"\D", "", number)]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10 == 0


class CredentialDetector:
    """
    Scans text for exposed credentials and sensitive data.
    """

    def __init__(self):
        self.patterns = CREDENTIAL_PATTERNS

    def detect_credentials(self, text: str) -> Dict:
        """
        Scan *text* for credentials.

        Returns:
            {
                'secrets_found': {type: count, ...},
                'details': [{type, description, match_preview}, ...],
                'risk': 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW',
                'total_count': int
            }
        """
        if not text:
            return {
                "secrets_found": {},
                "details": [],
                "risk": "LOW",
                "total_count": 0,
            }

        secrets_found: Dict[str, int] = {}
        details: List[Dict] = []

        for name, pattern, description in self.patterns:
            matches = pattern.findall(text)
            if not matches:
                continue

            # For credit cards, validate with Luhn
            if name == "credit_card":
                valid = [m for m in matches if _luhn_check(m)]
                if not valid:
                    continue
                matches = valid

            count = len(matches)
            secrets_found[name] = count

            # Safe preview – mask middle chars
            for m in matches:
                raw = m if isinstance(m, str) else str(m)
                preview = raw[:4] + "****" + raw[-2:] if len(raw) > 8 else "****"
                details.append(
                    {
                        "type": name,
                        "description": description,
                        "match_preview": preview,
                    }
                )

        total = sum(secrets_found.values())

        # Risk classification
        critical_types = {"api_key_openai", "api_key_aws", "private_key", "credit_card", "ssn", "jwt"}
        high_types = {"password", "api_key_generic", "github_token", "google_api_key", "slack_token"}

        if any(k in critical_types for k in secrets_found):
            risk = "CRITICAL"
        elif any(k in high_types for k in secrets_found):
            risk = "HIGH"
        elif total > 0:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "secrets_found": secrets_found,
            "details": details,
            "risk": risk,
            "total_count": total,
        }

    def get_risk_score(self, text: str) -> float:
        """Return normalised 0-100 risk score for fusion model."""
        result = self.detect_credentials(text)
        risk_map = {"CRITICAL": 95, "HIGH": 75, "MEDIUM": 40, "LOW": 5}
        base = risk_map.get(result["risk"], 5)
        # Boost slightly for multiple secrets
        extra = min(result["total_count"] * 3, 15)
        return min(base + extra, 100)
