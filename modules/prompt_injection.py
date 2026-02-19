"""
Module #4: Prompt Injection Detection
Detects jailbreak / prompt-injection attempts targeting AI systems.
"""
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

INJECTION_PATTERNS: List[tuple] = [
    ("ignore_instructions", r"ignore\s+(?:all\s+)?previous\s+instructions", "Ignore previous instructions"),
    ("system_prompt", r"(?:reveal|show|print|display|output)\s+(?:your\s+)?(?:system\s+)?prompt", "System prompt extraction"),
    ("dan_mode", r"\bdan\s*mode\b", "DAN mode jailbreak"),
    ("jailbreak", r"\bjailbreak\b", "Direct jailbreak request"),
    ("forget_instructions", r"forget\s+(?:all\s+)?(?:previous\s+|your\s+)?instructions", "Forget instructions"),
    ("show_secrets", r"show\s+(?:me\s+)?(?:the\s+)?(?:api|key|secret|password|token|credential)", "Request for secrets"),
    ("developer_mode", r"enable\s+developer\s+mode", "Enable developer mode"),
    ("unrestricted_ai", r"you\s+are\s+now\s+(?:an?\s+)?(?:unrestricted|free|evil|unfiltered)\s+(?:ai|bot|assistant|model)", "Unrestricted AI persona"),
    ("pretend_no_rules", r"pretend\s+(?:you\s+(?:have\s+no|don.t\s+have\s+any)\s+(?:rules|restrictions|filters|guidelines))", "Pretend no rules"),
    ("disregard_rules", r"disregard\s+(?:all\s+)?(?:previous|prior|your)\s+(?:instructions|rules|guidelines|training)", "Disregard rules"),
    ("override_safety", r"override\s+(?:all\s+)?(?:safety|restrictions|rules|filters|guidelines)", "Override safety restrictions"),
    ("no_restrictions", r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions", "Act without restrictions"),
    ("bypass_filter", r"bypass\s+(?:all\s+)?(?:content\s+)?(?:filters|restrictions|rules|safety|moderation)", "Bypass content filters"),
    ("new_persona", r"(?:your\s+new\s+(?:name|persona|role)|you\s+are\s+now\s+called)\s+\w+", "New AI persona injection"),
    ("token_manipulation", r"<\s*(?:/?\s*(?:system|human|assistant|user|context|instruction|prompt))\s*>", "Token/tag manipulation"),
    ("role_play_harmful", r"(?:role.?play|rp)\s+as\s+(?:an?\s+)?(?:evil|hacker|criminal|unethical|malicious)", "Harmful role-play"),
    ("base64_injection", r"(?:decode|run|execute|eval)\s+(?:this\s+)?(?:base64|b64)", "Encoded command injection"),
    ("prompt_leak", r"(?:repeat|print|echo|output|show)\s+(?:back\s+)?(?:everything|all|the\s+text)\s+(?:above|before|that\s+came)", "Prompt leakage attempt"),
]

# Compile patterns
_COMPILED: List[tuple] = [
    (name, re.compile(pattern, re.IGNORECASE), description)
    for name, pattern, description in INJECTION_PATTERNS
]


class PromptInjectionDetector:
    """Detects prompt injection and jailbreak attempts."""

    def __init__(self):
        self.patterns = _COMPILED

    def detect_injection(self, text: str) -> Dict:
        """
        Analyse text for prompt injection indicators.

        Returns:
            {
                'is_injection': bool,
                'patterns_found': [str, ...],
                'pattern_count': int,
                'risk': 'HIGH' | 'MEDIUM' | 'LOW',
                'matched_details': [{name, description}, ...]
            }
        """
        if not text:
            return {
                "is_injection": False,
                "patterns_found": [],
                "pattern_count": 0,
                "risk": "LOW",
                "matched_details": [],
            }

        patterns_found: List[str] = []
        matched_details: List[Dict] = []

        for name, pattern, description in self.patterns:
            if pattern.search(text):
                patterns_found.append(name)
                matched_details.append({"name": name, "description": description})

        count = len(patterns_found)
        is_injection = count > 0

        if count >= 3:
            risk = "HIGH"
        elif count >= 1:
            risk = "MEDIUM" if count == 1 else "HIGH"
        else:
            risk = "LOW"

        # Specific high-severity patterns always elevate to HIGH
        high_severity = {"ignore_instructions", "dan_mode", "jailbreak", "override_safety", "bypass_filter"}
        if any(p in high_severity for p in patterns_found):
            risk = "HIGH"

        return {
            "is_injection": is_injection,
            "patterns_found": patterns_found,
            "pattern_count": count,
            "risk": risk,
            "matched_details": matched_details,
        }

    def get_risk_score(self, text: str) -> float:
        """Return normalised 0-100 risk score for fusion model."""
        result = self.detect_injection(text)
        if not result["is_injection"]:
            return 5.0
        base = 50.0
        extra = min(result["pattern_count"] * 10, 40)
        if result["risk"] == "HIGH":
            base = 75.0
        return min(base + extra, 100.0)
