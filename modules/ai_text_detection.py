"""
Module #1: AI Text Detection
Detects if email/text was written by an AI (ChatGPT/Claude/etc.)
Falls back to heuristic scoring if the HuggingFace model is unavailable.
"""
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Heuristic patterns that are common in AI-generated text
# ---------------------------------------------------------------------------
AI_PHRASES = [
    r"i\s+(?:hope|trust)\s+this\s+(?:email\s+)?(?:finds|message)\s+you\s+well",
    r"please\s+(?:do\s+not\s+hesitate\s+to\s+)?(?:contact|reach\s+out)",
    r"as\s+(?:an\s+)?(?:ai|language\s+model)",
    r"i\s+(?:understand|acknowledge)\s+(?:your|the)",
    r"it\s+(?:is|has\s+been)\s+brought\s+to\s+(?:our|my)\s+attention",
    r"we\s+(?:kindly\s+)?(?:request|ask)\s+(?:you\s+to|that\s+you)",
    r"(?:immediate|urgent)\s+(?:action|attention)\s+(?:is\s+)?required",
    r"thank\s+you\s+for\s+your\s+(?:prompt\s+)?(?:attention|cooperation|understanding)",
    r"please\s+be\s+advised\s+that",
    r"pursuant\s+to\s+(?:our|the)\s+(?:policies|terms|agreement)",
    r"(?:failure|failure\s+to)\s+(?:comply|respond|verify|confirm)\s+(?:will|may|could)",
    r"your\s+account\s+(?:has\s+been|will\s+be|may\s+be)\s+(?:suspended|terminated|restricted|blocked)",
    r"click\s+(?:the\s+)?(?:link|button|here)\s+(?:below\s+)?to\s+(?:verify|confirm|update|secure)",
    r"this\s+is\s+(?:an?\s+)?(?:automated|official|important|urgent)\s+(?:message|notice|notification)",
    r"(?:verify|confirm|update)\s+your\s+(?:account|identity|information|details)\s+(?:immediately|now|today)",
]

# Structural / stylistic patterns common in AI text
STRUCTURAL_PATTERNS = [
    r"\b(?:furthermore|moreover|additionally|consequently|nevertheless|notwithstanding)\b",
    r"\bin\s+(?:conclusion|summary|closing)\b",
    r"\b(?:it\s+is\s+(?:imperative|essential|crucial)\s+that)\b",
    r"\b(?:please\s+note\s+that)\b",
    r"\b(?:rest\s+assured)\b",
    r"\b(?:we\s+(?:sincerely\s+)?apologize)\b",
    r"\b(?:at\s+your\s+earliest\s+convenience)\b",
    r"\b(?:should\s+you\s+(?:have\s+any\s+)?(?:questions|concerns|queries))\b",
]


class AITextDetector:
    """
    Detects AI-generated text using a two-stage approach:
    1. Try to load the OpenAI RoBERTa detector from HuggingFace (optional).
    2. Fall back to a heuristic phrase/structure analyser.
    """

    def __init__(self, use_model: bool = True):
        self.model = None
        self.tokenizer = None
        self._model_loaded = False

        if use_model:
            self._try_load_model()

    # ------------------------------------------------------------------
    # Model loading (optional – graceful fallback)
    # ------------------------------------------------------------------
    def _try_load_model(self) -> None:
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch  # noqa: F401 – ensure torch is available

            model_name = "roberta-base-openai-detector"
            logger.info(f"Loading AI text detection model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()
            self._model_loaded = True
            logger.info("AI text detection model loaded successfully.")
        except Exception as exc:
            logger.warning(
                f"Could not load HuggingFace model ({exc}). "
                "Falling back to heuristic AI text detection."
            )
            self._model_loaded = False

    # ------------------------------------------------------------------
    # Model-based detection
    # ------------------------------------------------------------------
    def _model_score(self, text: str) -> float:
        """Return 0-1 probability that text is AI-generated via HuggingFace."""
        try:
            import torch

            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
            )
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze()
            # Index 0 = "Real", Index 1 = "Fake/AI"
            ai_prob = float(probs[1]) if probs.shape[0] > 1 else float(probs[0])
            return ai_prob
        except Exception as exc:
            logger.error(f"Model inference error: {exc}")
            return self._heuristic_score(text)

    # ------------------------------------------------------------------
    # Heuristic-based detection
    # ------------------------------------------------------------------
    def _heuristic_score(self, text: str) -> float:
        """
        Return 0-1 probability using phrase matching and structural analysis.
        Tuned so that generic human text scores ~0.05-0.15 and typical
        phishing / formal AI text scores ~0.60-0.85.
        """
        lower = text.lower()
        score = 0.0

        # Phrase matches
        ai_phrase_hits = sum(
            1 for p in AI_PHRASES if re.search(p, lower, re.IGNORECASE)
        )
        structural_hits = sum(
            1 for p in STRUCTURAL_PATTERNS if re.search(p, lower, re.IGNORECASE)
        )

        # Normalise phrase score (max 1.0 at 5+ hits)
        score += min(ai_phrase_hits / 5.0, 1.0) * 0.55
        score += min(structural_hits / 4.0, 1.0) * 0.20

        # Sentence length uniformity (AI tends toward uniform sentences)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if len(sentences) >= 3:
            lengths = [len(s.split()) for s in sentences]
            avg = sum(lengths) / len(lengths)
            variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
            # Low variance → more AI-like
            uniformity = max(0.0, 1.0 - (variance / (avg ** 2 + 1)))
            score += uniformity * 0.10

        # Formal vocabulary density
        formal_words = [
            "verification", "immediately", "confirm", "account", "security",
            "compliance", "credential", "authenticate", "identity", "procedure",
            "notification", "official", "mandatory", "policy", "regulation",
        ]
        word_set = set(re.findall(r"\b\w+\b", lower))
        formal_density = len(word_set & set(formal_words)) / max(len(word_set), 1)
        score += min(formal_density * 3, 0.15)

        return min(score, 1.0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def detect_ai_text(self, email_text: str) -> Dict:
        """
        Analyse text and return AI-generation probability.

        Returns:
            {
                'ai_probability': 0-100,
                'is_ai_generated': bool,
                'confidence': 0-1,
                'risk_level': 'HIGH' | 'MEDIUM' | 'LOW',
                'model_used': 'transformer' | 'heuristic'
            }
        """
        if not email_text or not email_text.strip():
            return {
                "ai_probability": 0,
                "is_ai_generated": False,
                "confidence": 1.0,
                "risk_level": "LOW",
                "model_used": "none",
            }

        if self._model_loaded:
            raw_prob = self._model_score(email_text)
            model_used = "transformer"
        else:
            raw_prob = self._heuristic_score(email_text)
            model_used = "heuristic"

        ai_probability = round(raw_prob * 100, 1)
        is_ai = ai_probability >= 50
        confidence = round(abs(raw_prob - 0.5) * 2, 2)  # 0 at boundary, 1 at extremes

        if ai_probability >= 70:
            risk_level = "HIGH"
        elif ai_probability >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "ai_probability": ai_probability,
            "is_ai_generated": is_ai,
            "confidence": confidence,
            "risk_level": risk_level,
            "model_used": model_used,
        }
