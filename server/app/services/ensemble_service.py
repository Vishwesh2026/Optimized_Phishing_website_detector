"""
app/services/ensemble_service.py
─────────────────────────────────────────────────────────────
The unified Ensemble Service — combines predictions from:

  Model A: XGBoost + 111 structural/infrastructure features
           (from Project 2 — phishing_deep_clean_v1.pkl)

  Model B: Logistic Regression + Bag-of-Words text features
           (from Project 1 — phishing.pkl + vectorizer.pkl)

  Layer C: PhishTank API — deterministic database lookup
           (override when verified phishing)

  Layer D: Heuristic URL suspicion booster
           (boosts borderline URLs with suspicious patterns)

Fusion strategy: Weighted Soft-Voting + Heuristic Boost + PhishTank Override
  p_ensemble = w_xgb * p_xgb + w_nlp * p_nlp
  p_boosted  = min(1.0, p_ensemble + heuristic_boost)
  p_final    = 0.95 if PhishTank says phishing, else p_boosted

  Default weights (configurable via .env):
    w_xgb = 0.65  (richer structural features, higher precision)
    w_nlp = 0.35  (fast lexical signal, complements XGBoost)

  Final label: 1 (phishing) if p_final >= PHISHING_THRESHOLD else 0

The response includes an ensemble_breakdown field showing each model's
individual contribution, enabling explainability and weight tuning.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Optional
from urllib.parse import urlparse

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


# ── Heuristic URL suspicion booster ──────────────────────────────────────────

# Brand names commonly impersonated in phishing
_BRAND_KEYWORDS = {
    "paypal", "apple", "microsoft", "amazon", "google", "facebook",
    "instagram", "netflix", "chase", "wells", "fargo", "citibank",
    "bank", "hsbc", "barclays", "dropbox", "icloud", "outlook",
    "office365", "onedrive", "linkedin", "twitter", "whatsapp",
    "telegram", "coinbase", "binance", "metamask", "blockchain",
}

# Suspicious action keywords in URL path/query
_ACTION_KEYWORDS = {
    "login", "signin", "sign-in", "log-in", "verify", "verification",
    "confirm", "confirmation", "update", "secure", "security",
    "account", "suspend", "locked", "unusual", "authenticate",
    "validate", "recover", "restore", "webscr", "cmd=_login",
}


def _heuristic_boost(url: str) -> tuple[float, list[str]]:
    """
    Compute a heuristic suspicion boost for a URL based on common
    phishing URL patterns. Returns (boost_amount, list_of_reasons).

    The boost is additive to the ensemble probability, pushing borderline
    URLs over the classification threshold.
    """
    boost = 0.0
    reasons: list[str] = []
    url_lower = url.lower()

    try:
        parsed = urlparse(url_lower)
        domain = parsed.netloc.split(":")[0] if parsed.netloc else ""
        path = parsed.path or ""
        full_text = domain + path + (parsed.query or "")
    except Exception:
        return 0.0, []

    # 1. IP address as domain (e.g., http://192.168.1.1/paypal/login)
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
        boost += 0.12
        reasons.append("IP address as domain")

    # 2. Excessive subdomain depth (≥4 dots = suspicious nesting)
    dot_count = domain.count(".")
    if dot_count >= 4:
        boost += 0.08
        reasons.append(f"Excessive subdomains ({dot_count} dots)")
    elif dot_count >= 3:
        boost += 0.04
        reasons.append(f"Deep subdomains ({dot_count} dots)")

    # 3. Brand impersonation — brand name appears in domain or path
    #    but the domain itself is NOT the actual brand
    for brand in _BRAND_KEYWORDS:
        if brand in full_text:
            # Check if this IS the real brand domain (e.g., paypal.com)
            is_real = domain == f"{brand}.com" or domain == f"www.{brand}.com"
            if not is_real:
                boost += 0.10
                reasons.append(f"Brand impersonation: '{brand}'")
                break  # Only count once

    # 4. Suspicious action keywords in path/query
    action_count = sum(1 for kw in _ACTION_KEYWORDS if kw in full_text)
    if action_count >= 2:
        boost += 0.08
        reasons.append(f"Multiple suspicious keywords ({action_count})")
    elif action_count == 1:
        boost += 0.04
        reasons.append("Suspicious action keyword in URL")

    # 5. Very long URL (>100 chars, common in phishing to obfuscate)
    if len(url) > 150:
        boost += 0.06
        reasons.append(f"Very long URL ({len(url)} chars)")
    elif len(url) > 100:
        boost += 0.03
        reasons.append(f"Long URL ({len(url)} chars)")

    # 6. URL contains @ symbol (credential confusion attack)
    if "@" in url:
        boost += 0.10
        reasons.append("@ symbol in URL (credential confusion)")

    # 7. Hex-encoded characters in URL (obfuscation)
    hex_count = len(re.findall(r"%[0-9a-fA-F]{2}", url))
    if hex_count >= 3:
        boost += 0.05
        reasons.append(f"URL obfuscation ({hex_count} hex-encoded chars)")

    # Cap the total boost — heuristics shouldn't cause extreme swings
    boost = min(boost, 0.25)

    if reasons:
        logger.info("Heuristic boost=%.2f  reasons=%s", boost, reasons)

    return boost, reasons


# ── Ensemble Service ──────────────────────────────────────────────────────────

class EnsembleService:
    """
    Loads both models and fuses their predictions using weighted soft voting,
    enhanced with heuristic URL suspicion boosting and PhishTank API override.

    Usage:
        svc = EnsembleService()
        svc.load()
        result = svc.predict(feature_dict, url)
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

    def predict(self, feature_dict: dict[str, Any], url: str,
                phishtank_result: dict | None = None) -> dict:
        """
        Run ensemble inference with optional PhishTank override.

        Args:
            feature_dict:     Output of DeepFeatureExtractor.extract() — 111 features.
            url:              Original URL string for the NLP model.
            phishtank_result: Optional result from PhishTank API check.

        Returns:
            dict with keys:
              prediction         — "phishing" | "safe"
              label              — 1 | 0
              confidence         — final weighted probability
              risk_level         — "HIGH" | "MEDIUM" | "LOW"
              latency_ms         — inference latency in ms
              ensemble_breakdown — per-model scores and weights
              heuristic_reasons  — list of heuristic suspicion reasons
              phishtank_flagged  — bool, whether PhishTank flagged this URL
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
        p_ensemble = self._xgb_w * p_xgb + self._nlp_w * p_nlp

        # ── Layer D: Heuristic URL suspicion boost ────────────────────────────
        h_boost, h_reasons = _heuristic_boost(url)
        p_boosted = min(1.0, p_ensemble + h_boost)

        # ── Layer C: PhishTank override ───────────────────────────────────────
        phishtank_flagged = False
        if phishtank_result and phishtank_result.get("is_phishing"):
            phishtank_flagged = True
            p_final = 0.95  # High confidence override
            logger.info(
                "PhishTank OVERRIDE: URL confirmed as phishing (phish_id=%s)",
                phishtank_result.get("phish_id"),
            )
        else:
            p_final = p_boosted

        label      = 1 if p_final >= settings.PHISHING_THRESHOLD else 0
        confidence = round(p_final, 4)
        prediction = "phishing" if label == 1 else "safe"
        risk       = _risk_level(confidence, label)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        logger.info(
            "ENSEMBLE  pred=%s  p_xgb=%.4f  p_nlp=%.4f  p_ensemble=%.4f  "
            "h_boost=%.2f  p_boosted=%.4f  p_final=%.4f  phishtank=%s  "
            "conf=%.4f  latency=%.2fms",
            prediction, p_xgb, p_nlp, p_ensemble, h_boost, p_boosted,
            p_final, phishtank_flagged, confidence, latency_ms,
        )

        return {
            "prediction": prediction,
            "label":      label,
            "confidence": confidence,
            "risk_level": risk,
            "latency_ms": latency_ms,
            "heuristic_reasons": h_reasons,
            "phishtank_flagged":  phishtank_flagged,
            "ensemble_breakdown": {
                "xgb_probability":   round(p_xgb, 4),
                "nlp_probability":   round(p_nlp, 4),
                "xgb_weight":        self._xgb_w,
                "nlp_weight":        self._nlp_w,
                "ensemble_probability": round(p_ensemble, 4),
                "heuristic_boost":   round(h_boost, 4),
                "final_probability": round(p_final, 4),
                "phishtank_override": phishtank_flagged,
            },
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

_ensemble_service = EnsembleService()


def get_ensemble_service() -> EnsembleService:
    """FastAPI dependency — returns the global EnsembleService singleton."""
    return _ensemble_service
