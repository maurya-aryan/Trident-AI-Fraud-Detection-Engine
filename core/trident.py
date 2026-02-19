"""
TRIDENT Core Orchestrator
Runs all 9 detection modules and assembles the final result.
"""
import logging
import time
from typing import Dict, Optional

from core.data_models import FraudSignal, TridentResult
from modules.ai_text_detection import AITextDetector
from modules.campaign_graph import CampaignGraph
from modules.credential_exposure import CredentialDetector
from modules.email_phishing import EmailPhishingDetector
from modules.fusion_model import FusionModel
from modules.malware_scanner import MalwareScanner
from modules.prompt_injection import PromptInjectionDetector
from modules.shap_explainer import SHAPExplainer
from modules.url_detection import URLDetector

logger = logging.getLogger(__name__)


class TRIDENT:
    """
    TRIDENT AI-Fraud Detection Engine.
    Orchestrates all 9 detection modules into a unified pipeline.
    """

    def __init__(self, use_ai_model: bool = False):
        logger.info("Initialising TRIDENT engine...")
        t0 = time.time()

        # Module #1 – AI Text Detection
        self.ai_text = AITextDetector(use_model=use_ai_model)

        # Module #2 – Credential Exposure
        self.credentials = CredentialDetector()

        # Module #3 – Malware Scanner
        self.malware = MalwareScanner()

        # Module #4 – Prompt Injection
        self.injection = PromptInjectionDetector()

        # Module #5 – Email Phishing
        self.email_phishing = EmailPhishingDetector()

        # Module #6 – URL Detection
        self.url_detect = URLDetector()

        # Module #7 – Fusion Model
        self.fusion = FusionModel()

        # Module #8 – Campaign Graph (stateful across calls)
        self.graph = CampaignGraph()

        # Module #9 – SHAP Explainer
        self.shap = SHAPExplainer(model=self.fusion.model)

        elapsed = (time.time() - t0) * 1000
        logger.info(f"TRIDENT initialised in {elapsed:.0f}ms.")

    def _extract_scores(self, raw_results: Dict) -> Dict[str, float]:
        """Map raw module results to normalised 0-100 scores."""
        scores: Dict[str, float] = {}

        if "ai_text" in raw_results:
            scores["ai_text_score"] = raw_results["ai_text"].get("ai_probability", 0)

        if "credentials" in raw_results:
            risk_map = {"CRITICAL": 95, "HIGH": 75, "MEDIUM": 40, "LOW": 5}
            cr = raw_results["credentials"]
            base = risk_map.get(cr.get("risk", "LOW"), 5)
            extra = min(cr.get("total_count", 0) * 3, 15)
            scores["credential_score"] = min(base + extra, 100)

        if "malware" in raw_results:
            risk_map = {"CRITICAL": 95, "HIGH": 80, "MEDIUM": 45, "LOW": 5}
            scores["malware_score"] = risk_map.get(raw_results["malware"].get("risk", "LOW"), 5)

        if "injection" in raw_results:
            inj = raw_results["injection"]
            if inj.get("is_injection"):
                count = inj.get("pattern_count", 0)
                base = 50 if inj.get("risk") == "MEDIUM" else 75
                scores["injection_score"] = min(base + count * 5, 100)
            else:
                scores["injection_score"] = 5

        if "email_phishing" in raw_results:
            scores["email_phishing_score"] = raw_results["email_phishing"].get("phishing_probability", 0)

        if "url" in raw_results:
            scores["url_score"] = raw_results["url"].get("malicious_probability", 0)

        return scores

    def detect_fraud(self, signal: FraudSignal) -> TridentResult:
        """
        Run the full TRIDENT detection pipeline.

        Steps:
          1. Run applicable detection modules
          2. Extract normalised scores
          3. Fuse scores via Module #7
          4. Update campaign graph and correlate (Module #8)
          5. Generate SHAP explanation (Module #9)
          6. Build and return TridentResult
        """
        t0 = time.time()
        raw_results: Dict = {}
        module_details: Dict = {}

        # ------------------------------------------------------------------ #
        # Step 1 – Run modules
        # ------------------------------------------------------------------ #
        if signal.email_text:
            raw_results["ai_text"] = self.ai_text.detect_ai_text(signal.email_text)
            raw_results["credentials"] = self.credentials.detect_credentials(signal.email_text)
            raw_results["email_phishing"] = self.email_phishing.detect_phishing(signal.email_text)
            raw_results["injection"] = self.injection.detect_injection(signal.email_text)

            module_details["ai_text"] = raw_results["ai_text"]
            module_details["credentials"] = raw_results["credentials"]
            module_details["email_phishing"] = raw_results["email_phishing"]
            module_details["injection"] = raw_results["injection"]

        if signal.attachment_path:
            raw_results["malware"] = self.malware.scan_attachment(signal.attachment_path)
            module_details["malware"] = raw_results["malware"]

        if signal.url:
            raw_results["url"] = self.url_detect.detect_malicious(signal.url)
            module_details["url"] = raw_results["url"]

        # ------------------------------------------------------------------ #
        # Step 2 – Extract normalised scores
        # ------------------------------------------------------------------ #
        module_scores = self._extract_scores(raw_results)

        # ------------------------------------------------------------------ #
        # Step 3 – Fusion model
        # ------------------------------------------------------------------ #
        if not module_scores:
            # Nothing to analyse
            fusion_result = {
                "unified_risk_score": 0.0,
                "risk_band": "LOW",
                "action": "VERIFY",
                "confidence": 1.0,
                "module_contributions": {},
            }
        else:
            fusion_result = self.fusion.fuse_scores(module_scores)

        # ------------------------------------------------------------------ #
        # Step 4 – Campaign graph
        # ------------------------------------------------------------------ #
        # Build signal data dict for graph
        graph_data: Dict = {}
        if signal.sender:
            graph_data["sender"] = signal.sender
        if signal.email_text:
            graph_data["text"] = signal.email_text
        if signal.url:
            graph_data["url"] = signal.url
        if signal.attachment_path:
            graph_data["filename"] = signal.attachment_path

        self.graph.add_signal("combined", graph_data, signal.timestamp)
        campaign_info = self.graph.correlate()

        # ------------------------------------------------------------------ #
        # Step 5 – SHAP explanation
        # ------------------------------------------------------------------ #
        explanation = self.shap.explain(
            module_scores,
            unified_score=fusion_result["unified_risk_score"],
        )

        # ------------------------------------------------------------------ #
        # Step 6 – Assemble result
        # ------------------------------------------------------------------ #
        elapsed_ms = (time.time() - t0) * 1000

        return TridentResult(
            risk_score=fusion_result["unified_risk_score"],
            risk_band=fusion_result["risk_band"],
            recommended_action=fusion_result["action"],
            confidence=fusion_result["confidence"],
            module_scores=module_scores,
            module_details=module_details,
            is_coordinated_attack=campaign_info["is_coordinated"],
            campaign_timeline=campaign_info["timeline"],
            campaign_summary=campaign_info["campaign_summary"],
            explanation=explanation["explanation_text"],
            top_factors=explanation["top_3_factors"],
            feature_importance=explanation["feature_importance"],
            processing_time_ms=round(elapsed_ms, 1),
        )

    def reset_graph(self) -> None:
        """Reset the campaign graph (call between independent detection sessions)."""
        self.graph.reset()

    def analyze_email_only(self, email_text: str) -> Dict:
        """Quick email-only analysis (no attachment/URL)."""
        signal = FraudSignal(email_text=email_text)
        result = self.detect_fraud(signal)
        return result.model_dump()

    def analyze_url_only(self, url: str) -> Dict:
        """Quick URL-only analysis."""
        return self.url_detect.detect_malicious(url)

    def scan_file_only(self, file_path: str) -> Dict:
        """Quick file scan."""
        return self.malware.scan_attachment(file_path)
