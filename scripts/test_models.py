"""Evaluate Email Phishing model and TRIDENT on test_emails.csv.

Produces accuracy, precision, recall for:
 - EmailPhishingDetector (module level)
 - TRIDENT unified risk (thresholded at 50)

Run: python scripts/test_models.py
"""
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_EMAILS = Path('data/test_emails.csv')

try:
    from modules.email_phishing import EmailPhishingDetector
    from core.trident import TRIDENT
    from core.data_models import FraudSignal
except Exception as exc:
    logger.error('Imports failed: %s', exc)
    raise


def main():
    if not TEST_EMAILS.exists():
        raise FileNotFoundError('Run scripts/generate_test_data.py first')

    df = pd.read_csv(TEST_EMAILS)
    texts = df['text'].astype(str).tolist()
    labels = df['label'].astype(int).tolist()

    # Email phishing module
    phish = EmailPhishingDetector()
    y_true = labels
    y_pred_phish = []
    y_prob_phish = []

    for t in texts:
        r = phish.detect_phishing(t)
        prob = r.get('phishing_probability', 0)/100.0
        y_prob_phish.append(prob)
        y_pred_phish.append(1 if prob >= 0.5 else 0)

    acc_p = accuracy_score(y_true, y_pred_phish)
    prec_p = precision_score(y_true, y_pred_phish, zero_division=0)
    rec_p = recall_score(y_true, y_pred_phish, zero_division=0)
    logger.info('EmailPhishingDetector — Accuracy: %.3f Precision: %.3f Recall: %.3f', acc_p, prec_p, rec_p)

    # TRIDENT unified
    trident = TRIDENT(use_ai_model=False)
    y_pred_trident = []
    y_prob_trident = []
    for t in texts:
        sig = FraudSignal(email_text=t)
        res = trident.detect_fraud(sig)
        score = res.risk_score
        y_prob_trident.append(score/100.0)
        y_pred_trident.append(1 if score >= 50 else 0)

    acc_t = accuracy_score(y_true, y_pred_trident)
    prec_t = precision_score(y_true, y_pred_trident, zero_division=0)
    rec_t = recall_score(y_true, y_pred_trident, zero_division=0)
    logger.info('TRIDENT unified — Accuracy: %.3f Precision: %.3f Recall: %.3f', acc_t, prec_t, rec_t)

    # Confusion matrices
    cm_phish = confusion_matrix(y_true, y_pred_phish)
    cm_trid = confusion_matrix(y_true, y_pred_trident)
    logger.info('EmailPhishingDetector Confusion Matrix:\n%s', cm_phish)
    logger.info('TRIDENT Confusion Matrix:\n%s', cm_trid)

    # Save results
    out = Path('data/models/test_results.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    df_out = pd.DataFrame({
        'text': texts,
        'label': labels,
        'phish_prob': y_prob_phish,
        'phish_pred': y_pred_phish,
        'trident_prob': y_prob_trident,
        'trident_pred': y_pred_trident,
    })
    df_out.to_csv(out, index=False)
    logger.info('Saved per-sample results to %s', out)

if __name__ == '__main__':
    main()
