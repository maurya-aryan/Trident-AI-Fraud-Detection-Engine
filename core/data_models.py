"""
Core Data Models (Pydantic v2)
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FraudSignal(BaseModel):
    """Input signal for fraud detection."""

    email_text: Optional[str] = Field(None, description="Raw email body text")
    email_subject: Optional[str] = Field(None, description="Email subject line")
    attachment_path: Optional[str] = Field(None, description="Path to attachment file")
    url: Optional[str] = Field(None, description="URL to analyse")
    voice_path: Optional[str] = Field(None, description="Path to voice file (future)")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of signal",
    )
    sender: Optional[str] = Field(None, description="Email sender address")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ModuleResult(BaseModel):
    """Result from a single detection module."""

    module_name: str
    risk_score: float = Field(ge=0, le=100)
    risk_level: str  # CRITICAL / HIGH / MEDIUM / LOW
    details: Dict[str, Any] = Field(default_factory=dict)


class TridentResult(BaseModel):
    """Full TRIDENT detection output."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Core result
    risk_score: float = Field(ge=0, le=100, description="Unified risk score 0-100")
    risk_band: str = Field(description="CRITICAL | HIGH | MEDIUM | LOW")
    recommended_action: str = Field(description="BLOCK | ESCALATE | WARN | VERIFY")
    confidence: float = Field(ge=0, le=1)

    # Module scores
    module_scores: Dict[str, float] = Field(default_factory=dict)
    module_details: Dict[str, Any] = Field(default_factory=dict)

    # Campaign info
    is_coordinated_attack: bool = False
    campaign_timeline: List[Dict] = Field(default_factory=list)
    campaign_summary: str = ""

    # Explanation
    explanation: str = ""
    top_factors: List[str] = Field(default_factory=list)
    feature_importance: Dict[str, float] = Field(default_factory=dict)

    # Metadata
    processing_time_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @model_validator(mode="before")
    @classmethod
    def coerce_numpy_types(cls, values):
        """Convert numpy scalars to native Python types for JSON serialisation."""
        import numpy as np

        def _convert(obj):
            if isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_convert(i) for i in obj]
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        if isinstance(values, dict):
            return _convert(values)
        return values
