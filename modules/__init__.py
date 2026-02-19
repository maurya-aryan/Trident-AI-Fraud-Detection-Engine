# modules/__init__.py
from .ai_text_detection import AITextDetector
from .credential_exposure import CredentialDetector
from .malware_scanner import MalwareScanner
from .prompt_injection import PromptInjectionDetector
from .email_phishing import EmailPhishingDetector
from .url_detection import URLDetector
from .fusion_model import FusionModel
from .campaign_graph import CampaignGraph
from .shap_explainer import SHAPExplainer

__all__ = [
    "AITextDetector",
    "CredentialDetector",
    "MalwareScanner",
    "PromptInjectionDetector",
    "EmailPhishingDetector",
    "URLDetector",
    "FusionModel",
    "CampaignGraph",
    "SHAPExplainer",
]
