"""
TRIDENT Module Base Classes

Abstract base class for all detection modules to ensure consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ModuleResult(BaseModel):
    """
    Standardized result from a detection module.

    All modules should return this structure for consistency.
    """
    module_name: str = Field(..., description="Name of the detection module")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Risk score normalized to 0.0-1.0 range"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the assessment (0.0-1.0)"
    )
    explanation: str = Field(
        default="",
        description="Human-readable explanation of the detection"
    )
    flags: List[str] = Field(
        default_factory=list,
        description="List of detected threat indicators"
    )
    raw_result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original module-specific result for backward compatibility"
    )


class BaseModule(ABC):
    """
    Abstract base class for all TRIDENT detection modules.

    All modules must implement the analyze() method which accepts
    a dictionary of email data and returns a ModuleResult.

    Example:
        class MyDetector(BaseModule):
            def analyze(self, email_data: dict) -> ModuleResult:
                # Perform analysis
                return ModuleResult(
                    module_name="my_detector",
                    score=0.75,
                    confidence=0.9,
                    explanation="Detected suspicious pattern",
                    flags=["pattern_match"]
                )
    """

    @abstractmethod
    def analyze(self, email_data: dict) -> ModuleResult:
        """
        Analyze email data and return standardized result.

        Args:
            email_data: Dictionary containing email fields like:
                - email_text: Email body text
                - email_subject: Subject line
                - sender: Sender address
                - url: URL to analyze (optional)
                - attachment_path: Path to attachment (optional)

        Returns:
            ModuleResult: Standardized detection result

        Raises:
            NotImplementedError: If not overridden in subclass
        """
        raise NotImplementedError("Subclasses must implement analyze()")

    @property
    @abstractmethod
    def module_name(self) -> str:
        """
        Return the name of this module.

        Returns:
            str: Module identifier (e.g., "ai_text_detection")
        """
        raise NotImplementedError("Subclasses must implement module_name property")
