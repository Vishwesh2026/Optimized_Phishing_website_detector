"""
training/train_nlp.py
─────────────────────────────────────────────────────────────
Trains / re-trains the NLP (Bag-of-Words + Logistic Regression)
phishing classifier from Project 1.

This script reproduces the training pipeline from the original
Project 1 notebook: "Phishing website detection system.ipynb"

OUTPUT:
  models/vectorizer.pkl — CountVectorizer (BoW, Snowball stemmer tokenizer)
  models/phishing.pkl   — LogisticRegression classifier

USAGE:
  cd D:\\FINAL YEAR PROJECT\\merged
  python -m training.train_nlp

REQUIREMENTS:
  pip install scikit-learn pandas nltk joblib
  python -c "import nltk; nltk.download('punkt')"

DATASET:
  Place phishing_site_urls.csv in: Dataset/phishing_site_urls.csv
  Format: columns [url, label] where label = 'good' or 'bad'.
  (Same dataset as Project 1's Dataset/phishing_site_urls.csv)
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train_nlp")

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_CSV   = ROOT / "Dataset" / "phishing_site_urls.csv"
VECTORIZER_OUT = ROOT / "models" / "vectorizer.pkl"
MODEL_OUT      = ROOT / "models" / "phishing.pkl"
RANDOM_STATE   = 42

# ── Tokenizer matching Project 1 notebook ────────────────────────────────────
import re
try:
    from nltk.stem.snowball import SnowballStemmer
    _stemmer = SnowballStemmer("english")

    def _tokenizer(url: str) -> list[str]:
        tokens = re.split(r"\W+", url)
        return [_stemmer.stem(t) for t in tokens if t]
except ImportError:
    logger.warning("NLTK not available — using simple regex tokenizer (no stemming)")

    def _tokenizer(url: str) -> list[str]:
        return re.findall(r"[A-Za-z]+", url)


def main() -> None:
    if not DATASET_CSV.exists():
        logger.error("Dataset not found: %s", DATASET_CSV)
        logger.error("Copy phishing_site_urls.csv from Project 1 Dataset/ folder.")
        sys.exit(1)

    logger.info("Loading dataset from %s", DATASET_CSV)
    df = pd.read_csv(DATASET_CSV)
    logger.info("Dataset shape: %s", df.shape)
    logger.info("Label distribution:\n%s", df["label"].value_counts().to_string())

    X = df["url"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    logger.info("Train: %d  Test: %d", len(X_train), len(X_test))

    # Vectorize
    logger.info("Fitting CountVectorizer (Bag-of-Words)...")
    vectorizer = CountVectorizer(tokenizer=_tokenizer)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)
    logger.info("Vocabulary size: %d", len(vectorizer.vocabulary_))

    # Train Logistic Regression
    logger.info("Training Logistic Regression...")
    t0 = time.perf_counter()
    model = LogisticRegression(solver="lbfgs", max_iter=1000, n_jobs=-1)
    model.fit(X_train_vec, y_train)
    logger.info("Training complete in %.1fs", time.perf_counter() - t0)

    # Evaluate
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    logger.info("Test accuracy: %.4f", acc)
    logger.info("\n%s", classification_report(y_test, y_pred))

    # Save
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_OUT)
    joblib.dump(model, MODEL_OUT)
    logger.info("Saved vectorizer → %s", VECTORIZER_OUT)
    logger.info("Saved model     → %s", MODEL_OUT)
    logger.info("Done.")


if __name__ == "__main__":
    main()
