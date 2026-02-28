"""Train URL detector on data/test_urls.csv and save model.
"""
from pathlib import Path
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_DIR = Path('data/models')
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / 'url_detector_v2.json'

try:
    from modules.url_detection import _extract_url_features
    from xgboost import XGBClassifier
except Exception as exc:
    logger.error('Dependencies missing or import error: %s', exc)
    raise


def main():
    csv = Path('data/test_urls.csv')
    if not csv.exists():
        raise FileNotFoundError('data/test_urls.csv not found. Run scripts/generate_test_data.py first')
    df = pd.read_csv(csv)
    urls = df['url'].astype(str).tolist()
    labels = df['label'].astype(int).tolist()

    X = np.array([_extract_url_features(u) for u in urls])
    y = np.array(labels, dtype=int)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss', random_state=42)
    logger.info('Training URL detector model on test_urls.csv...')
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    logger.info('Validation accuracy: %.4f', acc)

    model.save_model(str(MODEL_PATH))
    logger.info('Saved model to %s', MODEL_PATH)

    # quick sample predictions
    p = model.predict_proba(X_test[:8])[:,1]
    logger.info('Sample probabilities: %s', p)

if __name__ == '__main__':
    main()
