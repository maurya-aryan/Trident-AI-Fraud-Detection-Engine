"""Train email phishing detector and save improved model.

Usage:
  - Place `data/phishing_emails.csv` with columns: text,label (0 or 1)
  - Or the script will fall back to the in-module synthetic TRAINING_DATA.

Outputs:
  - data/models/email_phishing_v2.json (XGBoost model file)
"""
from pathlib import Path
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_DIR = Path("data/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "email_phishing_v2.json"

try:
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from xgboost import XGBClassifier
except Exception as exc:
    logger.error("Required packages missing: pandas, scikit-learn, xgboost. Install them in your venv.")
    raise

# Import the feature extractor and synthetic dataset
try:
    from modules.email_phishing import _extract_features, TRAINING_DATA
except Exception as exc:
    logger.error(f"Could not import feature extractor from modules.email_phishing: {exc}")
    raise


def load_csv_data(csv_path: Path):
    df = pd.read_csv(csv_path)
    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError('CSV must contain text and label columns')
    texts = df['text'].astype(str).tolist()
    labels = df['label'].astype(int).tolist()
    return texts, labels


def prepare_features(texts):
    X = np.array([_extract_features(t) for t in texts])
    return X


def main():
    data_csv = Path('data/phishing_emails.csv')

    if data_csv.exists():
        logger.info(f"Loading training data from {data_csv}")
        texts, labels = load_csv_data(data_csv)
    else:
        logger.warning("data/phishing_emails.csv not found; falling back to synthetic TRAINING_DATA")
        texts = [t for t, _ in TRAINING_DATA]
        labels = [l for _, l in TRAINING_DATA]

    X = prepare_features(texts)
    y = np.array(labels, dtype=int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(set(y))>1 else None
    )

    model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss', random_state=42)
    logger.info("Training XGBoost classifier...")
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    logger.info(f"Validation accuracy: {acc:.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))
    logger.info(f"Saved model to {MODEL_PATH}")

    # Quick smoke test
    sample_idx = 0
    if X_test.shape[0] > 0:
        p = model.predict_proba(X_test[:5])[:, 1]
        logger.info(f"Sample predictions (proba): {p}")


if __name__ == '__main__':
    main()
