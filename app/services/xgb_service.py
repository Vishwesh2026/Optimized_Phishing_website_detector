"""
app/services/xgb_service.py
─────────────────────────────────────────────────────────────
XGBoost model loader and inference service.
Loads phishing_deep_clean_v1.pkl (XGBoost + IsotonicRegression,
wrapped in DeepModelBundle or a plain dict bundle).

Returns a raw phishing probability (0–1) via predict_proba_url().
The EnsembleService owns the final weighted decision.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.config import settings
from app.utils.deep_model_bundle import DeepModelBundle

logger = logging.getLogger(__name__)


class XGBService:
    """Loads and serves the deep XGBoost phishing model."""

    def __init__(self) -> None:
        self._pipeline: DeepModelBundle | None = None
        self._feature_cols: list[str] = []
        self._feature_stats: dict[str, dict] = {}
        self._loaded: bool = False
        self._version: str | None = None

    # ── Loading ───────────────────────────────────────────────────────────────

    def load(self) -> None:
        model_path = settings.xgb_model_path
        cols_path  = settings.feature_cols_path
        stats_path = settings.feature_stats_path

        if not model_path.exists():
            raise FileNotFoundError(
                f"XGBoost model not found at {model_path}. "
                "Run: python -m training.train_deep_clean"
            )

        logger.info("Loading XGBoost model from %s", model_path)
        t0 = time.perf_counter()
        raw = joblib.load(model_path)
        elapsed = (time.perf_counter() - t0) * 1000

        # Support both dict-bundle format (train_deep_clean) and DeepModelBundle
        if isinstance(raw, dict) and "xgb" in raw:
            logger.info("Detected dict-bundle — wrapping in DeepModelBundle")
            self._pipeline = DeepModelBundle(
                imputer=raw["imputer"],
                xgb=raw["xgb"],
                iso_regressor=raw["iso_regressor"],
            )
            if "feature_cols" in raw and raw["feature_cols"]:
                self._feature_cols = raw["feature_cols"]
        else:
            self._pipeline = raw

        # Load canonical feature column order
        if cols_path.exists():
            with open(cols_path) as f:
                self._feature_cols = json.load(f)
            logger.info("Feature cols loaded: %d features", len(self._feature_cols))
        else:
            logger.warning("feature_cols_path not found — using built-in FEATURE_COLS")
            from app.utils.deep_feature_extractor import FEATURE_COLS
            self._feature_cols = FEATURE_COLS

        # Load drift guard stats
        if stats_path.exists():
            with open(stats_path) as f:
                self._feature_stats = json.load(f)
            logger.info("Drift guard stats loaded")
        else:
            logger.warning("feature_stats.json not found — drift guard disabled")

        self._version = settings.MODEL_VERSION
        self._loaded = True
        logger.info("XGBoost model loaded in %.1f ms (version=%s)", elapsed, self._version)

    # ── Drift guard ───────────────────────────────────────────────────────────

    def _check_drift(self, feature_dict: dict[str, Any]) -> None:
        if not self._feature_stats:
            return
        for col, val in feature_dict.items():
            if val == -1:
                continue
            stats = self._feature_stats.get(col)
            if not stats:
                continue
            mean, std = stats["mean"], stats["std"]
            if std > 0 and abs(val - mean) > 3 * std:
                logger.warning(
                    "DRIFT  feature=%s  val=%.4f  mean=%.4f  std=%.4f",
                    col, val, mean, std,
                )

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict_proba(self, feature_dict: dict[str, Any]) -> float:
        """
        Run XGBoost inference on the 111-feature dict.

        Returns:
            float — calibrated phishing probability in [0, 1].
        """
        if not self._loaded or self._pipeline is None:
            raise RuntimeError("XGBoost model not loaded. Call load() first.")

        from app.utils.deep_feature_extractor import to_vector
        vec = to_vector(feature_dict, self._feature_cols)
        self._check_drift(feature_dict)

        X = np.array(vec, dtype=np.float64).reshape(1, -1)
        proba = self._pipeline.predict_proba(X)[0]
        return float(proba[1])

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def version(self) -> str | None:
        return self._version


# ── Singleton ─────────────────────────────────────────────────────────────────
_xgb_service = XGBService()


def get_xgb_service() -> XGBService:
    return _xgb_service
