"""
Module #9: SHAP Explainer
Provides human-readable explanations for TRIDENT risk decisions.
Uses SHAP when available; falls back to contribution-based explanations.
"""
import logging
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

FEATURE_LABELS = {
    "credential_score": "Credential Exposure",
    "ai_text_score": "AI-Generated Text",
    "malware_score": "Malware / Attachment",
    "email_phishing_score": "Email Phishing",
    "url_score": "Malicious URL",
    "injection_score": "Prompt Injection",
}

WEIGHTS = {
    "credential_score": 0.30,
    "ai_text_score": 0.20,
    "malware_score": 0.25,
    "email_phishing_score": 0.15,
    "url_score": 0.07,
    "injection_score": 0.03,
}

SCORE_KEYS = list(WEIGHTS.keys())


class SHAPExplainer:
    """
    Explains TRIDENT risk scores using SHAP values or weighted contributions.
    """

    def __init__(self, model=None):
        self.model = model
        self._explainer = None
        if model is not None:
            self._init_shap(model)

    def set_model(self, model) -> None:
        self.model = model
        self._init_shap(model)

    def _init_shap(self, model) -> None:
        try:
            import shap  # type: ignore

            self._explainer = shap.TreeExplainer(model)
            logger.info("SHAP TreeExplainer initialised.")
        except Exception as exc:
            logger.warning(f"SHAP initialisation failed ({exc}). Using contribution fallback.")
            self._explainer = None

    def _shap_values(self, feature_vec: np.ndarray) -> Optional[np.ndarray]:
        if self._explainer is None:
            return None
        try:
            vals = self._explainer.shap_values(feature_vec.reshape(1, -1))
            if isinstance(vals, list):
                vals = vals[0]
            return np.abs(vals[0])
        except Exception as exc:
            logger.warning(f"SHAP inference error: {exc}")
            return None

    def explain(self, module_scores: Dict[str, float], unified_score: Optional[float] = None) -> Dict:
        """
        Generate explanation for a set of module scores.

        Args:
            module_scores: dict mapping score keys to 0-100 values
            unified_score: optional final risk score (for display)

        Returns:
            {
                'feature_importance': {label: percentage},
                'explanation_text': str,
                'top_3_factors': [str, ...],
                'shap_used': bool
            }
        """
        # Normalise keys
        alias_map = {
            "credential": "credential_score",
            "credentials": "credential_score",
            "ai_text": "ai_text_score",
            "malware": "malware_score",
            "email_phishing": "email_phishing_score",
            "phishing": "email_phishing_score",
            "url": "url_score",
            "injection": "injection_score",
        }
        normalised: Dict[str, float] = {}
        for k, v in module_scores.items():
            canonical = alias_map.get(k, k)
            normalised[canonical] = float(v)

        feature_vec = np.array(
            [normalised.get(k, 0.0) for k in SCORE_KEYS], dtype=float
        )

        # Try SHAP values
        shap_vals = self._shap_values(feature_vec)
        shap_used = shap_vals is not None

        if shap_used:
            raw_importance = {k: float(shap_vals[i]) for i, k in enumerate(SCORE_KEYS)}
        else:
            # Contribution = score × weight (weighted impact)
            raw_importance = {
                k: float(feature_vec[i] * WEIGHTS.get(k, 0.0))
                for i, k in enumerate(SCORE_KEYS)
            }

        total = sum(raw_importance.values()) or 1.0
        feature_importance = {
            FEATURE_LABELS.get(k, k): round(v / total * 100, 1)
            for k, v in raw_importance.items()
        }

        # Sort by importance
        sorted_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        top_3 = [f"{label} ({pct:.0f}%)" for label, pct in sorted_factors[:3] if pct > 0]

        # Risk score display
        score_display = f"{unified_score:.0f}/100" if unified_score is not None else "N/A"
        score_val = unified_score or 0.0
        if score_val >= 76:
            band = "CRITICAL"
        elif score_val >= 51:
            band = "HIGH"
        elif score_val >= 21:
            band = "MEDIUM"
        else:
            band = "LOW"

        # Build explanation text
        factor_lines = "\n".join(
            f"  - {label}: {pct:.0f}% contribution"
            for label, pct in sorted_factors
            if pct > 1.0
        )

        explanation_text = (
            f"Risk Score: {score_display} ({band})\n\n"
            f"Main contributing factors:\n{factor_lines}\n\n"
            f"Explanation: {'SHAP TreeExplainer' if shap_used else 'Weighted contribution analysis'} "
            f"identified {len([x for x in sorted_factors if x[1] > 1.0])} active risk factors. "
        )

        if sorted_factors and sorted_factors[0][1] > 0:
            top_label, top_pct = sorted_factors[0]
            explanation_text += f"The dominant risk factor is '{top_label}' at {top_pct:.0f}% of total risk weight."

        return {
            "feature_importance": feature_importance,
            "explanation_text": explanation_text,
            "top_3_factors": top_3,
            "shap_used": shap_used,
            "sorted_factors": sorted_factors,
        }
