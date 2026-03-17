"""Augment phishing dataset with synthetic examples and train a robust classifier.

This script:
- Loads `data/test_emails.csv` if available (falls back to TRAINING_DATA).
- Generates additional synthetic phishing emails using templates + randomization.
- Builds a pipeline combining TF-IDF (1-2 grams) with numeric handcrafted features.
- Evaluates with 5-fold cross-validation (accuracy, precision, recall, f1, roc_auc).
- Trains on full augmented data and saves the pipeline to `data/models/email_phishing_v2.pkl`.
"""
from pathlib import Path
import random
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import FunctionTransformer
import joblib

# Project feature extractor
from modules.email_phishing import _extract_features, TRAINING_DATA

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "models" / "email_phishing_v2.pkl"
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "test_emails.csv"

# Small helper to generate synthetic phishing samples
PHISH_TEMPLATES = [
    "Urgent: Your {service} account has been suspended. Verify at {url} to avoid closure.",
    "Security Alert: Unusual login detected. Please confirm your identity here: {url}",
    "Dear {name}, we detected a problem with your recent payment. Click {url} to review and secure your account.",
    "Final warning: Your account will be deleted unless you verify at {url}",
    "Action required: confirm your banking details at {url} to avoid interruption.",
    "You have an unpaid invoice. View and pay now: {url}",
]
SERVICES = ["PayPal", "Bank", "Amazon", "Google", "SecureBank", "PayService", "ClientServices"]
NAMES = ["Alex","Sam","Pat","Chris","Morgan","Taylor","Jordan","Lee"]
DOMAINS = ["secure-verify.net","accountsecure.xyz","payment-confirm.org","verify-payments.us","secure-login.biz","update-info.co","account-check.io"]

random.seed(42)

class NumericFeaturesExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        feats = np.array([_extract_features(str(x)) for x in X])
        return feats


def to_dense(x):
    """Convert sparse matrix to dense numpy array in a pickle-friendly top-level function."""
    if hasattr(x, 'toarray'):
        return x.toarray()
    return np.asarray(x)

def generate_phish(n):
    samples = []
    for _ in range(n):
        t = random.choice(PHISH_TEMPLATES)
        service = random.choice(SERVICES)
        name = random.choice(NAMES)
        domain = random.choice(DOMAINS)
        path = "/login?uid=" + str(random.randint(1000,9999))
        url = f"https://{domain}{path}"
        text = t.format(service=service, name=name, url=url)
        # randomly append urgency line or P.S.
        if random.random() < 0.4:
            text += "\n\nP.S. Please respond as soon as possible to avoid delay."
        if random.random() < 0.25:
            text = text.upper()
        samples.append(text)
    return samples


def load_data():
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        texts = df['text'].fillna('').astype(str).tolist()
        labels = df['label'].astype(int).tolist()
        return texts, labels
    # fallback to small TRAINING_DATA
    texts = [t for t,_ in TRAINING_DATA]
    labels = [l for _,l in TRAINING_DATA]
    return texts, labels

if __name__ == '__main__':
    texts, labels = load_data()
    print(f"Loaded {len(texts)} labeled examples")

    # Generate synthetic phishing augmentation
    aug_n = 2000
    print(f"Generating {aug_n} synthetic phishing samples...")
    phish_samples = generate_phish(aug_n)
    phish_labels = [1]*len(phish_samples)

    # Combine with existing legitimate examples (we'll downsample phishing from original to avoid imbalance)
    combined_texts = texts + phish_samples
    combined_labels = labels + phish_labels

    # Shuffle
    combined = list(zip(combined_texts, combined_labels))
    random.shuffle(combined)
    X = [c[0] for c in combined]
    y = np.array([c[1] for c in combined], dtype=int)

    print("Building TF-IDF + numeric features pipeline...")
    tfidf = TfidfVectorizer(ngram_range=(1,2), max_features=5000, stop_words='english')
    num_feat = NumericFeaturesExtractor()

    combined_features = FeatureUnion([
        ('tfidf', Pipeline([('tfidf', tfidf)])),
        ('nums', Pipeline([('nums', num_feat)])),
    ])

    pipeline = Pipeline([
        ('features', combined_features),
        ('to_dense', FunctionTransformer(to_dense)),
        ('clf', __import__('xgboost').XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            use_label_encoder=False, eval_metric='logloss', random_state=42
        )),
    ])

    print("Running 5-fold cross-validation...")
    scoring = ['accuracy','precision','recall','f1','roc_auc']
    try:
        scores = cross_validate(pipeline, X, y, cv=5, scoring=scoring, n_jobs=1)
        for metric in scoring:
            vals = scores[f'test_{metric}']
            print(f"{metric}: mean={vals.mean():.4f} std={vals.std():.4f}")
    except Exception as exc:
        print("Cross-validation failed:", exc)

    # Fit on full data and save
    print("Training final model on full augmented dataset...")
    pipeline.fit(X, y)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, OUT_PATH)
    print('Saved trained pipeline to', OUT_PATH)

    # Quick evaluation on a held-out split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    preds = pipeline.predict(X_test)
    probs = pipeline.predict_proba(X_test)[:,1]
    print('\nClassification report on held-out split:')
    print(classification_report(y_test, preds))
    try:
        print('ROC AUC:', roc_auc_score(y_test, probs))
    except Exception:
        pass
