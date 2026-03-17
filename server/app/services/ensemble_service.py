"""
app/services/ensemble_service.py
─────────────────────────────────────────────────────────────
The unified Ensemble Service — combines predictions from:

  Model A: XGBoost + 111 structural/infrastructure features
           (from Project 2 — phishing_deep_clean_v1.pkl)

  Model B: Logistic Regression + Bag-of-Words text features
           (from Project 1 — phishing.pkl + vectorizer.pkl)

Fusion strategy: Weighted Soft-Voting
  p_final = w_xgb * p_xgb + w_nlp * p_nlp

  Default weights (configurable via .env):
    w_xgb = 0.65  (richer structural features, higher precision)
    w_nlp = 0.35  (fast lexical signal, complements XGBoost)

  Final label: 1 (phishing) if p_final >= PHISHING_THRESHOLD else 0

The response includes an ensemble_breakdown field showing each model's
individual contribution, enabling explainability and weight tuning.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from app.config import settings
from app.services.xgb_service import XGBService, get_xgb_service
from app.utils.nlp_feature_extractor import NLPModelBundle, load_nlp_bundle, get_nlp_proba

logger = logging.getLogger(__name__)


# ── Risk helpers ──────────────────────────────────────────────────────────────

def _risk_level(confidence: float, label: int) -> str:
    if label == 1:
        if confidence >= 0.85:
            return "HIGH"
        if confidence >= 0.60:
            return "MEDIUM"
        return "LOW"
    return "LOW"


# ── Ensemble Service ──────────────────────────────────────────────────────────

class EnsembleService:
    """
    Loads both models and fuses their predictions using weighted soft voting.

    Usage:
        svc = EnsembleService()
        svc.load()
        result = await run_prediction(feature_dict, url)
    """

    def __init__(self) -> None:
        self._xgb:     XGBService | None = None
        self._nlp:     NLPModelBundle | None = None
        self._loaded:  bool = False
        self._xgb_w:  float = settings.ENSEMBLE_XGB_WEIGHT
        self._nlp_w:  float = settings.ENSEMBLE_NLP_WEIGHT

    # ── Load ──────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load both models. Called once at API startup via lifespan."""
        # Load XGBoost model
        self._xgb = get_xgb_service()
        if not self._xgb.is_loaded:
            self._xgb.load()

        # Load NLP model (Logistic Regression + BoW vectorizer)
        self._nlp = load_nlp_bundle(
            vectorizer_path=settings.NLP_VECTORIZER_PATH,
            model_path=settings.NLP_MODEL_PATH,
        )

        self._loaded = True
        logger.info(
            "EnsembleService loaded — XGB weight=%.2f, NLP weight=%.2f",
            self._xgb_w, self._nlp_w,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def xgb_version(self) -> Optional[str]:
        return self._xgb.version if self._xgb else None

    # ── Predict ───────────────────────────────────────────────────────────────

    def predict(self, feature_dict: dict[str, Any], url: str) -> dict:
        """
        Run ensemble inference.

        Args:
            feature_dict: Output of DeepFeatureExtractor.extract() — 111 features.
            url:          Original URL string for the NLP model.

        Returns:
            dict with keys:
              prediction      — "phishing" | "safe"
              label           — 1 | 0
              confidence      — final weighted probability
              risk_level      — "HIGH" | "MEDIUM" | "LOW"
              latency_ms      — inference latency in ms
              ensemble_breakdown — per-model scores and weights
        """
        if not self._loaded:
            raise RuntimeError("EnsembleService not loaded. Call load() first.")

        t0 = time.perf_counter()

        # ── Model A: XGBoost (111 structural features) ────────────────────────
        try:
            p_xgb = self._xgb.predict_proba(feature_dict)
        except Exception as exc:
            logger.error("XGBoost inference failed: %s", exc)
            p_xgb = 0.5  # neutral fallback — don't crash

        # ── Model B: NLP Logistic Regression (Bag-of-Words text) ──────────────
        p_nlp = get_nlp_proba(url, self._nlp)

        # ── Weighted Soft-Voting ──────────────────────────────────────────────
        p_final = self._xgb_w * p_xgb + self._nlp_w * p_nlp

        label      = 1 if p_final >= settings.PHISHING_THRESHOLD else 0
        confidence = round(p_final, 4)
        prediction = "phishing" if label == 1 else "safe"
        risk       = _risk_level(confidence, label)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        logger.info(
            "ENSEMBLE  pred=%s  p_xgb=%.4f  p_nlp=%.4f  p_final=%.4f  "
            "conf=%.4f  latency=%.2fms",
            prediction, p_xgb, p_nlp, p_final, confidence, latency_ms,
        )

        return {
            "prediction": prediction,
            "label":      label,
            "confidence": confidence,
            "risk_level": risk,
            "latency_ms": latency_ms,
            "ensemble_breakdown": {
                "xgb_probability": round(p_xgb, 4),
                "nlp_probability": round(p_nlp, 4),
                "xgb_weight":      self._xgb_w,
                "nlp_weight":      self._nlp_w,
                "final_probability": round(p_final, 4),
            },
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

_ensemble_service = EnsembleService()


def get_ensemble_service() -> EnsembleService:
    """FastAPI dependency — returns the global EnsembleService singleton."""
    return _ensemble_service
