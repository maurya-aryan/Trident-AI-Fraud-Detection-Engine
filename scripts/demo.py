"""
TRIDENT CLI Demo - Coordinated Fraud Attack Scenario

Demonstrates TRIDENT's multi-modal detection capabilities with a
simulated phishing attack containing multiple threat vectors.

Usage:
    python scripts/demo.py
"""
import sys
import os
import tempfile
from pathlib import Path

# Ensure project root is importable
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.trident import TRIDENT
from core.data_models import FraudSignal


def run_demo():
    """Run the CLI demo attack scenario."""
    print("\n" + "=" * 60)
    print("  🎯 TRIDENT — Demo: Coordinated Fraud Attack")
    print("=" * 60)
    print("\nInitialising TRIDENT engine...")
    trident = TRIDENT()

    # Create fake .exe attachment
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".exe", prefix="invoice_"
    ) as tmp:
        tmp.write(b"MZ\x90\x00" + b"\x00" * 100)
        exe_path = tmp.name

    # Get test password from environment or use a safe demo value
    # (No longer hardcoded in source code)
    test_password = os.getenv("DEMO_TEST_PASSWORD", "TestPassword123!")

    signal = FraudSignal(
        email_text=(
            "I trust this finds you well. Your bank account has been flagged for "
            "suspicious activity and requires immediate verification. "
            "Please be advised that failure to comply will result in suspension. "
            f"password={test_password} Click the link below to secure your account."
        ),
        email_subject="URGENT: Account Verification Required",
        sender="noreply@fake-bank.xyz",
        url="http://fake-bank.xyz/verify",
        attachment_path=exe_path,
    )

    print("\n📨 Input signal:")
    print(f"   Email: {signal.email_text[:80]}...")
    print(f"   URL:   {signal.url}")
    print(f"   File:  invoice.exe")
    print(f"   From:  {signal.sender}")
    print("\n🔎 Running detection pipeline...\n")

    result = trident.detect_fraud(signal)

    # Clean up temp file
    try:
        os.unlink(exe_path)
    except Exception:
        pass

    print("=" * 60)
    print(f"  RISK SCORE  : {result.risk_score:.0f}/100")
    print(f"  RISK BAND   : {result.risk_band}")
    print(f"  ACTION      : {result.recommended_action}")
    print(f"  CONFIDENCE  : {result.confidence * 100:.0f}%")
    print(f"  COORDINATED : {'YES ⚠️' if result.is_coordinated_attack else 'No'}")
    print(f"  TIME        : {result.processing_time_ms:.0f}ms")
    print("=" * 60)

    print("\n📊 Module Scores:")
    for module, score in result.module_scores.items():
        bar = "█" * int(score // 5)
        print(f"   {module:<25} {score:>5.1f}  {bar}")

    print("\n🔝 Top Risk Factors:")
    for i, factor in enumerate(result.top_factors, 1):
        print(f"   {i}. {factor}")

    print(f"\n🧠 Explanation:\n{result.explanation}")

    if result.is_coordinated_attack:
        print(f"\n⚠️  Campaign: {result.campaign_summary}")

    print("\n✅ Demo complete!\n")


if __name__ == "__main__":
    run_demo()
