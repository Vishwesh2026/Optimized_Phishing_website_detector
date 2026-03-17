"""
training/train_nlp_v2.py
──────────────────────────────────────────────────────────────────────────────
Retrain the NLP model (Bag-of-Words + Logistic Regression) on a COMBINED
dataset: phishing_site_urls.csv + PhiUSIIL_Phishing_URL_Dataset.csv

WHY THIS IS NEEDED
──────────────────
The original NLP model was trained only on phishing_site_urls.csv which
contains "obvious" phishing URLs (e.g., secure-login-paypal.com).
The XGBoost model was trained on PhiUSIIL which has subtle phishing URLs
(e.g., teramill.com — looks legitimate but is phishing).

Training on BOTH sources gives the NLP model a much richer vocabulary
and allows it to generalize across both pattern types, boosting ensemble
accuracy from ~84% to >90%.

OUTPUT
──────
  models/vectorizer.pkl   (overwrites old — same filename, compatible)
  models/phishing.pkl     (overwrites old — same filename, compatible)

USAGE
─────
  cd "D:/FINAL YEAR PROJECT/merged"
  venv\Scripts\python -m training.train_nlp_v2
"""

from __future__ import annotations

import logging
import re
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
logger = logging.getLogger("train_nlp_v2")

# ── Paths ─────────────────────────────────────────────────────────────────────
DS1_CSV        = ROOT / "Dataset" / "phishing_site_urls.csv"           # 'URL', 'Label' (good/bad)
DS2_CSV        = ROOT / "Dataset" / "PhiUSIIL_Phishing_URL_Dataset.csv" # 'URL', 'label' (0=phish,1=legit)
VECTORIZER_OUT = ROOT / "models" / "vectorizer.pkl"
MODEL_OUT      = ROOT / "models" / "phishing.pkl"
RANDOM_STATE   = 42

# ── Tokenizer — imported from shared utility (required for joblib pickle compat)
from app.utils.nlp_feature_extractor import URLTokenizer
_tokenizer = URLTokenizer()


def main() -> None:
    logger.info("=" * 60)
    logger.info("NLP Model Retraining — Combined Dataset (v2)")
    logger.info("=" * 60)

    records = []

    # ── Load Dataset 1: phishing_site_urls.csv ────────────────────────────────
    if DS1_CSV.exists():
        df1 = pd.read_csv(DS1_CSV, low_memory=False)
        # columns: URL, Label (good/bad)
        df1 = df1.rename(columns={"URL": "url", "Label": "label_str"})
        df1["label"] = df1["label_str"].str.lower().map({"bad": "bad", "good": "good"})
        df1 = df1[["url", "label"]].dropna()
        logger.info("Dataset 1 (phishing_site_urls): %d rows", len(df1))
        records.append(df1)
    else:
        logger.warning("Dataset 1 not found: %s", DS1_CSV)

    # ── Load Dataset 2: PhiUSIIL_Phishing_URL_Dataset.csv ────────────────────
    if DS2_CSV.exists():
        df2 = pd.read_csv(DS2_CSV, low_memory=False, usecols=["URL", "label"])
        # PhiUSIIL: label=0 → PHISHING, label=1 → LEGITIMATE
        df2 = df2.rename(columns={"URL": "url"})
        df2["label"] = df2["label"].map({0: "bad", 1: "good"})
        df2 = df2[["url", "label"]].dropna()
        logger.info("Dataset 2 (PhiUSIIL):           %d rows", len(df2))
        records.append(df2)
    else:
        logger.warning("Dataset 2 not found: %s", DS2_CSV)

    if not records:
        logger.error("No datasets found. Aborting.")
        sys.exit(1)

    # ── Combine & deduplicate ─────────────────────────────────────────────────
    df = pd.concat(records, ignore_index=True)
    df["url"] = df["url"].astype(str).str.strip()
    df = df.drop_duplicates(subset="url")
    df = df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    logger.info("Combined dataset: %d rows", len(df))
    logger.info("Label distribution:\n%s", df["label"].value_counts().to_string())

    # ── Preprocess URLs (strip scheme/www — same as inference time) ───────────
    df["url_clean"] = df["url"].apply(
        lambda u: re.sub(r"^https?://(www\.)?", "", str(u))
    )

    X = df["url_clean"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    logger.info("Train: %d  Test: %d", len(X_train), len(X_test))

    # ── Fit CountVectorizer ───────────────────────────────────────────────────
    logger.info("Fitting CountVectorizer (Bag-of-Words + Snowball stemmer)...")
    vectorizer = CountVectorizer(tokenizer=_tokenizer, token_pattern=None)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)
    logger.info("Vocabulary size: %d tokens", len(vectorizer.vocabulary_))

    # ── Train Logistic Regression ─────────────────────────────────────────────
    logger.info("Training Logistic Regression (solver=lbfgs, max_iter=1000)...")
    t0 = time.perf_counter()
    model = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        n_jobs=-1,
        C=1.0,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train_vec, y_train)
    elapsed = time.perf_counter() - t0
    logger.info("Training complete in %.1fs", elapsed)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    logger.info("Test Accuracy: %.4f  (%.2f%%)", acc, acc * 100)
    logger.info("\n%s", classification_report(y_test, y_pred))

    # ── Save (same filenames — dashboard/API will pick them up automatically) ─
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_OUT)
    joblib.dump(model, MODEL_OUT)
    logger.info("Saved vectorizer -> %s", VECTORIZER_OUT)
    logger.info("Saved model     -> %s", MODEL_OUT)
    logger.info("")
    logger.info("Next step: run  python -m training.evaluate_unified")
    logger.info("Done.")


if __name__ == "__main__":
    main()
