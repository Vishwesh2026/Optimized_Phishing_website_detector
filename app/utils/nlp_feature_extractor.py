"""
app/utils/nlp_feature_extractor.py
─────────────────────────────────────────────────────────────
Wraps Project 1's NLP pipeline:
  - CountVectorizer (vectorizer.pkl)  — Bag-of-Words tokenizer
  - LogisticRegression (phishing.pkl) — trained text classifier

Exposes a single function: get_nlp_proba(url) → float [0, 1]
that returns the phishing probability from the NLP model alone.

The URL is pre-processed exactly as during training:
  strip scheme/www → feed as raw text to the same CountVectorizer.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import joblib
import numpy as np

logger = logging.getLogger(__name__)


# ── Shared Tokenizer ──────────────────────────────────────────────────────────
# Defined here (not in training scripts) so joblib can find it on deserialization
# when loading vectorizer.pkl from any context (train, evaluate, or API).

class URLTokenizer:
    """
    Bag-of-Words tokenizer for URL strings.
    Splits on non-word characters and optionally applies Snowball stemming.
    Must be defined at module level for joblib pickle compatibility.
    """
    def __init__(self):
        try:
            from nltk.stem.snowball import SnowballStemmer
            self._stemmer = SnowballStemmer("english")
        except Exception:
            self._stemmer = None

    def __call__(self, url: str) -> list[str]:
        import re
        tokens = re.split(r"\W+", str(url))
        tokens = [t for t in tokens if t]
        if self._stemmer:
            tokens = [self._stemmer.stem(t) for t in tokens]
        return tokens



class NLPModelBundle:
    """
    Holds the Bag-of-Words vectorizer + Logistic Regression classifier
    from Project 1. Provides predict_proba() compatible interface.
    """

    def __init__(self, vectorizer, model) -> None:
        self.vectorizer = vectorizer
        self.model = model

    def predict_proba(self, url: str) -> float:
        """
        Returns phishing probability (0–1) for a URL string.
        Mirrors Project 1 app.py: strip scheme/www before vectorizing.
        """
        cleaned = re.sub(r"^https?://(www\.)?", "", url)
        vec = self.vectorizer.transform([cleaned])
        # predict_proba returns [[p_safe, p_phish]]
        proba = self.model.predict_proba(vec)[0]
        # class 1 = "bad" (phishing), but order depends on model classes_
        classes = list(self.model.classes_)
        phish_class = "bad" if "bad" in classes else 1
        if phish_class in classes:
            idx = classes.index(phish_class)
        else:
            idx = 1  # fallback: assume index 1 is phishing
        return float(proba[idx])


_nlp_bundle: Optional[NLPModelBundle] = None


def load_nlp_bundle(vectorizer_path: Path, model_path: Path) -> NLPModelBundle:
    """Load vectorizer + LR model from disk. Called once at startup."""
    logger.info("Loading NLP vectorizer from %s", vectorizer_path)
    vectorizer = joblib.load(vectorizer_path)
    logger.info("Loading NLP model (Logistic Regression) from %s", model_path)
    model = joblib.load(model_path)
    return NLPModelBundle(vectorizer=vectorizer, model=model)


def get_nlp_proba(url: str, bundle: NLPModelBundle) -> float:
    """
    Get phishing probability from the NLP (BoW + LR) model.

    Args:
        url:    Full URL string (with or without scheme).
        bundle: Loaded NLPModelBundle instance.

    Returns:
        Float in [0, 1] — probability of being phishing.
    """
    try:
        return bundle.predict_proba(url)
    except Exception as exc:
        logger.warning("NLP model prediction failed for %s: %s", url, exc)
        return 0.5  # neutral fallback — don't bias the ensemble
