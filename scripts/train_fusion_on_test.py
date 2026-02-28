"""Train a FusionModel (classifier) on module outputs produced for data/test_emails.csv

This script will:
 - Load data/test_emails.csv (id,text,label)
 - For each sample, run the module detectors to collect module_scores
 - Train an XGBoost classifier to predict label (0/1) from module_scores
 - Save the trained model to data/models/fusion_v2.json
"""
from pathlib import Path
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_CSV = Path('data/test_emails.csv')
MODEL_DIR = Path('data/models')
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / 'fusion_v2.json'

try:
    from core.trident import TRIDENT
    from core.data_models import FraudSignal
    from xgboost import XGBClassifier
except Exception as exc:
    logger.error('Imports failed: %s', exc)
    raise


def collect_module_scores(trident, text):
    raw = {}
    raw['ai_text'] = trident.ai_text.detect_ai_text(text)
    raw['credentials'] = trident.credentials.detect_credentials(text)
    raw['email_phishing'] = trident.email_phishing.detect_phishing(text)
    raw['injection'] = trident.injection.detect_injection(text)
    # no attachment/url in the test set
    scores = trident._extract_scores(raw)
    # Ensure all keys present
    keys = [
        'credential_score', 'ai_text_score', 'malware_score',
        'email_phishing_score', 'url_score', 'injection_score'
    ]
    return [float(scores.get(k, 0.0)) for k in keys]


def main():
    if not DATA_CSV.exists():
        raise FileNotFoundError('data/test_emails.csv not found. Run generate_test_data first.')

    df = pd.read_csv(DATA_CSV)
    texts = df['text'].astype(str).tolist()
    labels = df['label'].astype(int).tolist()

    # Initialise TRIDENT (module detectors will load their saved models if available)
    trident = TRIDENT(use_ai_model=False)

    X = []
    y = []
    logger.info('Collecting module scores for %d samples...', len(texts))
    for t, lab in zip(texts, labels):
        feats = collect_module_scores(trident, t)
        X.append(feats)
        y.append(lab)

    X = np.array(X, dtype=float)
    y = np.array(y, dtype=int)

    # Train/test split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    clf = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss', random_state=42)
    logger.info('Training fusion classifier on module outputs...')
    clf.fit(X_train, y_train)

    acc = clf.score(X_test, y_test)
    logger.info('Fusion classifier validation accuracy: %.4f', acc)

    # Save model
    clf.save_model(str(MODEL_PATH))
    logger.info('Saved fusion model to %s', MODEL_PATH)

if __name__ == '__main__':
    main()
