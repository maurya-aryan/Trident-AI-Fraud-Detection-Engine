"""
Module #7: Fusion Model
Combines all 6 module scores into a unified risk score using XGBoost regression.
Falls back to weighted average if XGBoost is unavailable.
"""
import logging
from typing import Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Default weights for weighted-average fallback
WEIGHTS = {
    # Quick fallback: put stronger emphasis on email_phishing for immediate improvements
    "credential_score": 0.05,
    "ai_text_score": 0.03,
    "malware_score": 0.10,
    "email_phishing_score": 0.60,
    "url_score": 0.20,
    "injection_score": 0.02,
}

SCORE_KEYS = list(WEIGHTS.keys())

# Risk band thresholds
RISK_BANDS = [
    (76, 100, "CRITICAL", "BLOCK"),
    (51, 75, "HIGH", "ESCALATE"),
    (21, 50, "MEDIUM", "WARN"),
    (0, 20, "LOW", "VERIFY"),
]


def _classify(score: float):
    if score >= 75.0:
        return "CRITICAL", "BLOCK"
    elif score >= 50.0:
        return "HIGH", "ESCALATE"
    elif score >= 20.0:
        return "MEDIUM", "WARN"
    else:
        return "LOW", "VERIFY"


class FusionModel:
    """Combines module risk scores into a single unified risk score."""

    def __init__(self):
        self.model = None
        self._trained = False
        # Try to load a saved fusion model first
        try:
            import xgboost as xgb
            from pathlib import Path

            mp = Path("data/models/fusion_v2.json")
            if mp.exists():
                # Try to load as regressor or classifier
                m = xgb.XGBModel()
                try:
                    m.load_model(str(mp))
                    self.model = m
                    self._trained = True
                    logger.info(f"Loaded fusion model from {mp}")
                except Exception:
                    # fallback to synthetic training if loading fails
                    logger.warning(f"Failed to load fusion model from {mp}, will train on synthetic data if needed.")
        except Exception:
            pass

        # If no saved model available, fall back to synthetic training
        if not self._trained:
            self._train_synthetic()

    def _train_synthetic(self) -> None:
        try:
            import xgboost as xgb

            np.random.seed(42)
            n = 500
            # Generate synthetic feature matrix
            X = np.random.rand(n, len(SCORE_KEYS)) * 100  # scores 0-100

            # True labels: weighted average + noise
            weights_arr = np.array(list(WEIGHTS.values()))
            y = (X @ weights_arr) + np.random.randn(n) * 5
            y = np.clip(y, 0, 100)

            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
            )
            self.model.fit(X, y)
            self._trained = True
            logger.info("Fusion model trained on synthetic data.")
        except Exception as exc:
            logger.warning(f"Fusion model training failed ({exc}). Using weighted average.")

    def train(self, feature_matrix: np.ndarray, labels: np.ndarray) -> None:
        """Re-train on custom data."""
        try:
            import xgboost as xgb

            self.model = xgb.XGBRegressor(
                n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
            )
            self.model.fit(feature_matrix, labels)
            self._trained = True
        except Exception as exc:
            logger.error(f"Fusion model re-train error: {exc}")

    def _weighted_average(self, scores: Dict[str, float]) -> float:
        total = 0.0
        weight_sum = 0.0
        for key, weight in WEIGHTS.items():
            val = scores.get(key, 0.0)
            total += val * weight
            weight_sum += weight
        return total / max(weight_sum, 1e-9)

    def fuse_scores(self, module_scores: Dict[str, float]) -> Dict:
        """
        Fuse individual module scores into unified result.

        Args:
            module_scores: dict with any subset of SCORE_KEYS, values 0-100

        Returns:
            {
                'unified_risk_score': 0-100,
                'risk_band': 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW',
                'action': 'BLOCK' | 'ESCALATE' | 'WARN' | 'VERIFY',
                'confidence': 0-1,
                'module_contributions': {key: contribution},
                'weighted_average': float
            }
        """
        # Empty input → zero risk
        if not module_scores:
            return {
                "unified_risk_score": 0.0,
                "risk_band": "LOW",
                "action": "VERIFY",
                "confidence": 1.0,
                "module_contributions": {},
                "weighted_average": 0.0,
            }

        # Normalise keys – accept flexible naming
        normalised: Dict[str, float] = {}
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
        for k, v in module_scores.items():
            canonical = alias_map.get(k, k)
            normalised[canonical] = float(v)

        # Fill missing keys with 0
        feature_vec = np.array(
            [normalised.get(k, 0.0) for k in SCORE_KEYS], dtype=float
        )

        weighted_avg = self._weighted_average(normalised)

        if self._trained and self.model is not None:
            try:
                # XGBoost saved model could be a regressor or classifier. Handle both.
                if hasattr(self.model, 'predict_proba'):
                    proba = float(self.model.predict_proba(feature_vec.reshape(1, -1))[0][1])
                    predicted = proba * 100.0
                else:
                    predicted = float(self.model.predict(feature_vec.reshape(1, -1))[0])
                # Blend model prediction with weighted average (70/30)
                unified_score = 0.7 * predicted + 0.3 * weighted_avg
            except Exception as exc:
                logger.warning(f"Fusion model inference error ({exc}). Using weighted average.")
                unified_score = weighted_avg
        else:
            unified_score = weighted_avg

        unified_score = round(float(np.clip(unified_score, 0, 100)), 1)
        risk_band, action = _classify(unified_score)

        # Confidence: how far from band boundaries
        distance_from_50 = abs(unified_score - 50)
        confidence = round(min(distance_from_50 / 50.0, 1.0), 2)

        # Per-module contributions
        contributions = {
            k: round(normalised.get(k, 0.0) * WEIGHTS.get(k, 0.0), 1)
            for k in SCORE_KEYS
        }

        return {
            "unified_risk_score": unified_score,
            "risk_band": risk_band,
            "action": action,
            "confidence": confidence,
            "module_contributions": contributions,
            "weighted_average": round(weighted_avg, 1),
        }
