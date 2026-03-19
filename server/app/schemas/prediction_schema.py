"""
app/schemas/prediction_schema.py
─────────────────────────────────────────────────────────────
Pydantic v2 request / response schemas for the Ensemble API.
Extended from Project 2 to include ensemble_breakdown field.
"""

from pydantic import BaseModel, field_validator
from typing import Optional


# ── Request ───────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """Validated input URL for phishing detection."""

    url: str

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(v.strip())
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must start with http:// or https://")
        if not parsed.netloc:
            raise ValueError("URL must have a valid domain.")
        if len(v) > 2048:
            raise ValueError("URL exceeds maximum allowed length of 2048 characters.")
        return v.strip()

    model_config = {"json_schema_extra": {"example": {"url": "https://www.google.com"}}}


# ── Shared sub-schemas ────────────────────────────────────────────────────────

class DomainInfo(BaseModel):
    """WHOIS-derived domain metadata. All fields are optional."""
    domain:           Optional[str]  = None
    registrar:        Optional[str]  = None
    creation_date:    Optional[str]  = None
    expiration_date:  Optional[str]  = None
    updated_date:     Optional[str]  = None
    domain_age:       Optional[str]  = None
    is_new_domain:    bool           = False
    is_expiring_soon: bool           = False
    name_servers:     list[str]      = []
    status:           list[str]      = []
    country:          Optional[str]  = None
    org:              Optional[str]  = None
    whois_available:  bool           = False
    error:            Optional[str]  = None


class InfrastructureFeatures(BaseModel):
    """Selected infrastructure signals from the deep feature extractor."""
    tls_ssl_certificate:    Optional[int]   = None  # 1=valid, 0=invalid, -1=error
    qty_ip_resolved:        Optional[int]   = None
    qty_nameservers:        Optional[int]   = None
    qty_mx_servers:         Optional[int]   = None
    ttl_hostname:           Optional[int]   = None
    time_response:          Optional[float] = None  # seconds
    domain_spf:             Optional[int]   = None  # 1=present, 0=absent
    asn_ip:                 Optional[int]   = None
    time_domain_activation: Optional[int]   = None  # days since activation
    time_domain_expiration: Optional[int]   = None  # days until expiration
    qty_redirects:          Optional[int]   = None
    url_google_index:       int = -1                # sentinel at runtime
    domain_google_index:    int = -1                # sentinel at runtime


class EnsembleBreakdown(BaseModel):
    """Per-model scores and weights from the ensemble fusion step."""
    xgb_probability:      float   # XGBoost calibrated phishing probability
    nlp_probability:      float   # NLP (Logistic Regression) phishing probability
    xgb_weight:           float   # Weight applied to XGBoost score
    nlp_weight:           float   # Weight applied to NLP score
    ensemble_probability: Optional[float] = None  # Weighted average before boost
    heuristic_boost:      Optional[float] = None  # Heuristic suspicion boost applied
    final_probability:    float   # Final probability after all adjustments
    phishtank_override:   bool    = False  # Whether PhishTank overrode the ML verdict


# ── Unified Ensemble Analysis Response ───────────────────────────────────────

class AnalyzeResponse(BaseModel):
    """Response for POST /api/v1/analyze (ensemble model)."""
    url:                str
    prediction:         str             # "phishing" | "safe" | "invalid" | "unknown"
    label:              int             # 1 = phishing, 0 = safe, -1 = unknown
    confidence:         float           # ensemble phishing probability (0–1)
    risk_level:         str             # "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN"
    reason:             Optional[str]   = None
    infrastructure:     Optional[InfrastructureFeatures] = None
    domain_info:        Optional[DomainInfo]             = None
    ensemble_breakdown: Optional[EnsembleBreakdown]      = None  # NEW
    heuristic_reasons:  list[str]                         = []    # URL suspicion reasons
    phishtank_flagged:  bool                              = False # PhishTank override
    degraded:           bool  = False
    latency_ms:         float = 0.0
    model_version:      str   = "ensemble-v1"

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://suspicious-login.xyz",
                "prediction": "phishing",
                "label": 1,
                "confidence": 0.93,
                "risk_level": "HIGH",
                "ensemble_breakdown": {
                    "xgb_probability": 0.97,
                    "nlp_probability": 0.85,
                    "xgb_weight": 0.65,
                    "nlp_weight": 0.35,
                    "final_probability": 0.93,
                },
                "degraded": False,
                "latency_ms": 1840.7,
                "model_version": "ensemble-v1",
            }
        }
    }


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:          str
    model_loaded:    bool
    ensemble_loaded: bool
    model_version:   Optional[str]
    app_env:         str
