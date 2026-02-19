"""
TRIDENT Entry Point
Starts the FastAPI server or the Streamlit dashboard based on CLI args.

Usage:
    python main.py api          → Start FastAPI server on :8000
    python main.py dashboard    → Start Streamlit dashboard
    python main.py demo         → Run CLI demo test case
    python main.py test         → Run pytest suite
"""
import sys
import os
import logging

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("trident.main")


def run_api():
    """Launch the FastAPI server with uvicorn."""
    try:
        import uvicorn
        logger.info("Starting TRIDENT API server on http://0.0.0.0:8000")
        logger.info("API docs: http://localhost:8000/docs")
        uvicorn.run("api.routes:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        logger.error("uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)


def run_dashboard():
    """Launch the Streamlit dashboard."""
    import subprocess
    dashboard_path = os.path.join(os.path.dirname(__file__), "ui", "dashboard.py")
    logger.info(f"Starting TRIDENT Dashboard: {dashboard_path}")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)


def run_demo():
    """Run the CLI demo attack scenario."""
    import tempfile
    from core.trident import TRIDENT
    from core.data_models import FraudSignal

    print("\n" + "="*60)
    print("  🎯 TRIDENT — Demo: Coordinated Fraud Attack")
    print("="*60)
    print("\nInitialising TRIDENT engine...")
    trident = TRIDENT()

    # Create fake .exe attachment
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".exe", prefix="invoice_"
    ) as tmp:
        tmp.write(b"MZ\x90\x00" + b"\x00" * 100)
        exe_path = tmp.name

    signal = FraudSignal(
        email_text=(
            "I trust this finds you well. Your bank account has been flagged for "
            "suspicious activity and requires immediate verification. "
            "Please be advised that failure to comply will result in suspension. "
            "password=Bank@123! Click the link below to secure your account."
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

    print("="*60)
    print(f"  RISK SCORE  : {result.risk_score:.0f}/100")
    print(f"  RISK BAND   : {result.risk_band}")
    print(f"  ACTION      : {result.recommended_action}")
    print(f"  CONFIDENCE  : {result.confidence*100:.0f}%")
    print(f"  COORDINATED : {'YES ⚠️' if result.is_coordinated_attack else 'No'}")
    print(f"  TIME        : {result.processing_time_ms:.0f}ms")
    print("="*60)

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


def run_tests():
    """Run pytest suite."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "demo"

    commands = {
        "api": run_api,
        "dashboard": run_dashboard,
        "demo": run_demo,
        "test": run_tests,
        "tests": run_tests,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[command]()
