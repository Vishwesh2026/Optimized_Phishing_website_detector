"""
app/config.py — Centralised settings for the Merged Ensemble Phishing Detection API.
All values can be overridden via .env or environment variables.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application-wide settings."""

    # ── App meta ──────────────────────────────────────────────────────────────
    APP_NAME: str = "Phishing Website Detection API (Ensemble)"
    APP_VERSION: str = "4.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # ── Server ────────────────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ── XGBoost Deep Model ────────────────────────────────────────────────────
    MODEL_VERSION: str = "clean_v1"
    MODEL_DIR: Path = _PROJECT_ROOT / "models"

    @property
    def xgb_model_path(self) -> Path:
        return self.MODEL_DIR / f"phishing_deep_{self.MODEL_VERSION}.pkl"

    @property
    def feature_cols_path(self) -> Path:
        return self.MODEL_DIR / "deep_feature_cols_clean.json"

    @property
    def feature_stats_path(self) -> Path:
        return self.MODEL_DIR / "deep_feature_stats.json"

    # ── NLP Model (Project 1 — Logistic Regression + BoW) ────────────────────
    NLP_MODEL_PATH: Path = _PROJECT_ROOT / "models" / "phishing.pkl"
    NLP_VECTORIZER_PATH: Path = _PROJECT_ROOT / "models" / "vectorizer.pkl"

    # ── Ensemble Weights ─────────────────────────────────────────────────────
    # Must sum to 1.0. XGBoost is weighted higher (richer features).
    ENSEMBLE_XGB_WEIGHT: float = 0.65
    ENSEMBLE_NLP_WEIGHT: float = 0.35

    # ── Classification threshold ──────────────────────────────────────────────
    PHISHING_THRESHOLD: float = 0.5

    # ── Circuit breaker / timeouts ────────────────────────────────────────────
    MAX_CONCURRENT: int = 10
    TIMEOUT_SECS: float = 15.0

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ── Security ──────────────────────────────────────────────────────────────
    MAX_REQUEST_BODY_BYTES: int = 8_192
    ALLOWED_ORIGINS: str = "*"

    @property
    def allowed_origins_list(self) -> list[str]:
        raw = self.ALLOWED_ORIGINS.strip()
        if not raw:
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    # ── Experiments ───────────────────────────────────────────────────────────
    EXPERIMENTS_DIR: Path = _PROJECT_ROOT / "experiments"

    # Backward-compat alias for deep_feature_extractor (expects model_path)
    @property
    def model_path(self) -> Path:
        return self.xgb_model_path

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
