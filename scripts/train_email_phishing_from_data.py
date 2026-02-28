"""Train Email Phishing detector from combined datasets (test + labeled IMAP).

Usage:
  python scripts/train_email_phishing_from_data.py

This script will look for `data/test_emails.csv` and `data/labeled_emails.csv` (created
by `label_emails.py`) and train an `EmailPhishingDetector` on the combined data,
then save the model to `data/models/email_phishing_v3.json`.
"""
from __future__ import annotations

import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    try:
        from modules.email_phishing import EmailPhishingDetector
    except Exception as exc:
        logger.error('Failed to import EmailPhishingDetector: %s', exc)
        return

    base = Path('data')
    test_csv = base / 'test_emails.csv'
    labelled_csv = base / 'labeled_emails.csv'

    frames = []
    if test_csv.exists():
        df = pd.read_csv(test_csv)
        # test_emails.csv uses columns id?, text, label, source. Ensure text & label exist
        if 'text' in df.columns and 'label' in df.columns:
            frames.append(df[['text', 'label']])

    if labelled_csv.exists():
        df2 = pd.read_csv(labelled_csv)
        if 'text' in df2.columns and 'label' in df2.columns:
            frames.append(df2[['text', 'label']].rename(columns={'label': 'label'}))

    if not frames:
        logger.error('No training data found. Run generate_test_data.py or label some IMAP emails first.')
        return

    data = pd.concat(frames, ignore_index=True)
    # drop rows with missing text
    data = data.dropna(subset=['text'])

    emails = data['text'].astype(str).tolist()
    labels = data['label'].astype(int).tolist()

    phish = EmailPhishingDetector()
    logger.info('Training EmailPhishingDetector on %d samples', len(emails))
    phish.train(emails, labels)

    # Try to save the XGBoost model if present
    try:
        import xgboost as xgb
        model = phish.model
        mp = Path('data/models/email_phishing_v3.json')
        mp.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(model, 'save_model'):
            model.save_model(str(mp))
            logger.info('Saved model to %s', mp)
        else:
            # fallback: try sklearn joblib
            import joblib
            joblib.dump(model, str(mp.with_suffix('.pkl')))
            logger.info('Saved sklearn model to %s', mp.with_suffix('.pkl'))
    except Exception as exc:
        logger.warning('Failed to save XGBoost model (%s).', exc)


if __name__ == '__main__':
    main()
