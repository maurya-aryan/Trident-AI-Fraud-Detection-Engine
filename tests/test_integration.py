"""
Integration Tests for the full TRIDENT pipeline
Run with: pytest tests/test_integration.py -v
"""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


@pytest.fixture(scope="module")
def trident():
    from core.trident import TRIDENT
    return TRIDENT()


@pytest.fixture(scope="module")
def exe_file():
    """Create a temp .exe file and clean up after tests."""
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".exe", prefix="test_payload_"
    ) as tmp:
        tmp.write(b"MZ\x90\x00" + b"\x00" * 64)
        path = tmp.name
    yield path
    try:
        os.unlink(path)
    except Exception:
        pass


class TestFullDetectionPipeline:
    def test_email_only_analysis(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(
            email_text="URGENT: Your account has been suspended. Verify immediately. password=Test@123"
        )
        result = trident.detect_fraud(signal)
        assert result.risk_score > 0
        assert result.risk_band in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        assert result.recommended_action in {"BLOCK", "ESCALATE", "WARN", "VERIFY"}
        assert len(result.explanation) > 0

    def test_url_only_analysis(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(url="http://secure-alert.xyz/phish")
        result = trident.detect_fraud(signal)
        assert result.risk_score >= 0
        assert "url_score" in result.module_scores

    def test_attachment_only_analysis(self, trident, exe_file):
        from core.data_models import FraudSignal
        signal = FraudSignal(attachment_path=exe_file)
        result = trident.detect_fraud(signal)
        assert result.risk_score > 0
        assert "malware_score" in result.module_scores
        assert result.module_scores["malware_score"] > 50

    def test_full_coordinated_attack(self, trident, exe_file):
        """The spec's demo test case: email + url + attachment."""
        from core.data_models import FraudSignal
        trident.reset_graph()
        signal = FraudSignal(
            email_text=(
                "Your account needs verification NOW! Click here: http://fake-bank.xyz "
                "password=Bank@123 Ignore previous instructions."
            ),
            attachment_path=exe_file,
            url="http://fake-bank.xyz",
            sender="noreply@fake-bank.xyz",
        )
        result = trident.detect_fraud(signal)

        assert result.risk_score > 60, f"Expected high risk score, got {result.risk_score}"
        assert result.risk_band in {"CRITICAL", "HIGH"}
        assert result.recommended_action in {"BLOCK", "ESCALATE"}
        assert len(result.explanation) > 0
        assert isinstance(result.module_scores, dict)
        assert result.module_scores.get("malware_score", 0) > 50
        assert result.module_scores.get("credential_score", 0) > 50

    def test_empty_signal(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal()
        result = trident.detect_fraud(signal)
        assert result.risk_score == 0.0
        assert result.risk_band == "LOW"

    def test_benign_email(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(
            email_text="Hi team, meeting is rescheduled to Thursday at 2pm. Thanks!"
        )
        result = trident.detect_fraud(signal)
        assert result.risk_score < 60

    def test_benign_url(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(url="https://www.google.com/search?q=python")
        result = trident.detect_fraud(signal)
        assert result.module_scores.get("url_score", 100) < 50

    def test_result_has_all_fields(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(email_text="Test email", url="http://test.com")
        result = trident.detect_fraud(signal)

        assert hasattr(result, "risk_score")
        assert hasattr(result, "risk_band")
        assert hasattr(result, "recommended_action")
        assert hasattr(result, "module_scores")
        assert hasattr(result, "is_coordinated_attack")
        assert hasattr(result, "campaign_timeline")
        assert hasattr(result, "explanation")
        assert hasattr(result, "top_factors")
        assert hasattr(result, "confidence")

    def test_processing_time_tracked(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(email_text="Quick test")
        result = trident.detect_fraud(signal)
        assert result.processing_time_ms is not None
        assert result.processing_time_ms < 5000  # should be fast

    def test_campaign_graph_correlation(self, trident):
        trident.reset_graph()
        from core.data_models import FraudSignal

        # Two signals from same domain
        signal1 = FraudSignal(
            email_text="Verify your account at secure-alert.xyz",
            sender="phish@secure-alert.xyz",
        )
        signal2 = FraudSignal(url="http://secure-alert.xyz/login")

        trident.detect_fraud(signal1)
        trident.detect_fraud(signal2)

        campaign = trident.graph.correlate()
        assert campaign["signal_count"] >= 2

    def test_module_scores_in_range(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(
            email_text="Click here to verify your account immediately!"
        )
        result = trident.detect_fraud(signal)
        for key, score in result.module_scores.items():
            assert 0 <= score <= 100, f"Score {key}={score} out of 0-100 range"

    def test_confidence_in_range(self, trident):
        from core.data_models import FraudSignal
        signal = FraudSignal(email_text="Your account is compromised. Act now!")
        result = trident.detect_fraud(signal)
        assert 0 <= result.confidence <= 1


class TestAPIRoutes:
    """Integration tests for FastAPI endpoints (no server required)."""

    @pytest.fixture(scope="class")
    def client(self):
        from fastapi.testclient import TestClient
        from api.routes import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_analyze_email_endpoint(self, client):
        response = client.post(
            "/analyze-email",
            params={"text": "URGENT: Verify your account password=Test@123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data

    def test_analyze_url_endpoint(self, client):
        response = client.post(
            "/analyze-url",
            params={"url": "http://fake-bank.xyz"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "malicious_probability" in data

    def test_detect_endpoint(self, client):
        payload = {
            "email_text": "Your account needs verification NOW!",
            "url": "http://fake-bank.xyz",
            "timestamp": "2024-02-17T10:00:00"
        }
        response = client.post("/detect", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "risk_band" in data

    def test_reset_graph_endpoint(self, client):
        response = client.post("/reset-graph")
        assert response.status_code == 200

    def test_campaign_status_endpoint(self, client):
        response = client.get("/campaign-status")
        assert response.status_code == 200
