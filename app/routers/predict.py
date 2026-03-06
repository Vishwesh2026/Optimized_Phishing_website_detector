"""
app/routers/predict.py
─────────────────────────────────────────────────────────────
API endpoints for the Ensemble Phishing Detection service.

Routes:
  POST /api/v1/analyze  — Ensemble analysis (primary endpoint)
  GET  /                — Web UI
  POST /predict         — HTML form submission
  GET  /health          — Liveness + readiness check
  POST /reload-model    — Hot-reload both models
  GET  /api/v1/metrics  — Training metrics
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas.prediction_schema import (
    AnalyzeResponse,
    DomainInfo,
    EnsembleBreakdown,
    HealthResponse,
    InfrastructureFeatures,
    PredictRequest,
)
from app.services.ensemble_service import EnsembleService, get_ensemble_service
from app.services.whois_service import get_domain_info
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Circuit breaker ───────────────────────────────────────────────────────────
_semaphore: asyncio.Semaphore | None = None


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT)
    return _semaphore


# ── Templates ─────────────────────────────────────────────────────────────────
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

# ── Infrastructure fields to surface ─────────────────────────────────────────
_INFRA_FIELDS = [
    "tls_ssl_certificate", "qty_ip_resolved", "qty_nameservers",
    "qty_mx_servers", "ttl_hostname", "time_response", "domain_spf",
    "asn_ip", "time_domain_activation", "time_domain_expiration",
    "qty_redirects", "url_google_index", "domain_google_index",
]


# ── Core analysis helper ──────────────────────────────────────────────────────

async def _run_analysis(url: str, svc: EnsembleService, is_root_check: bool = False) -> dict:
    """
    Unified entry point for URL analysis with 'Root-Domain-First' logic.
    For deep URLs (with paths/params), it checks the base domain first
    and inherits its verdict, as per the user's assumption that subdirectories
    inherit the legitimacy of the main site.
    """
    from app.utils.url_normalizer import normalize_url
    from urllib.parse import urlparse

    norm_url = normalize_url(url)
    parsed = urlparse(norm_url)

    # 1. Determine the base URL (protocol + netloc)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    norm_base = normalize_url(base_url)

    # 2. Check if we are currently at the root or already in a root-check recursion
    # We ignore the distinction between domain.com and domain.com/
    is_at_root = norm_url.rstrip("/") == norm_base.rstrip("/")

    # 3. If we are deep and NOT already doing a root check, check the root first
    if not is_at_root and not is_root_check:
        logger.info("Deep URL detected: %s. Checking base domain first: %s", norm_url, norm_base)
        root_result = await _run_analysis(norm_base, svc, is_root_check=True)

        # If the root has a valid prediction, we'll use it but still run the core analysis
        # for the deep URL to extract its specific infrastructure/WHOIS metadata for the UI (if needed).
        # Note: we use core analysis ONLY for features, but override the verdict.
        current_result = await _run_analysis_core(norm_url, svc)

        # APPLY OVERRIDE: Inherit verdict from root domain
        # The user's idea: if root is legit, subfolders are legit. If root is phish, subfolders are phish.
        current_result["prediction"] = root_result["prediction"]
        current_result["label"]      = root_result["label"]
        current_result["confidence"] = root_result["confidence"]
        current_result["risk_level"] = root_result["risk_level"]
        current_result["ensemble_breakdown"] = root_result.get("ensemble_breakdown")
        current_result["reason"] = f"Inherited prediction from base domain: {norm_base}"

        return current_result

    # 4. Otherwise (at root or root-check), perform standard core analysis
    return await _run_analysis_core(norm_url, svc)


async def _run_analysis_core(norm_url: str, svc: EnsembleService) -> dict:
    """
    Internal helper that performs the actual feature extraction and ML inference.
    Extracted from _run_analysis to support the root-inherit logic.
    """
    if not svc.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded. Please try again shortly.",
        )

    sem = _get_semaphore()

    # Fast-path: circuit breaker at capacity
    if sem._value == 0:
        logger.warning("Circuit breaker TRIPPED for %s", norm_url)
        return {
            "url": norm_url,
            "prediction": "unknown",
            "label": -1,
            "confidence": 0.0,
            "risk_level": "UNKNOWN",
            "infrastructure": None,
            "domain_info": None,
            "ensemble_breakdown": None,
            "degraded": True,
            "latency_ms": 0.0,
            "model_version": "ensemble-v1",
        }

    async with sem:
        from app.utils.deep_feature_extractor import extract as extract_features
        from app.services.dns_guard import domain_exists
        from urllib.parse import urlparse

        t_start  = time.perf_counter()

        parsed = urlparse(norm_url)
        domain = parsed.netloc.split(":")[0] or parsed.path.split("/")[0]

        # ── NXDOMAIN pre-check ────────────────────────────────────────────────
        if not await domain_exists(domain):
            total_ms = round((time.perf_counter() - t_start) * 1000, 2)
            logger.info("Blocking %s — domain does not exist (NXDOMAIN)", norm_url)
            return {
                "url": norm_url,
                "prediction": "invalid",
                "label": 1,
                "confidence": 1.0,
                "risk_level": "HIGH",
                "reason": "Domain does not resolve (NXDOMAIN)",
                "infrastructure": None,
                "domain_info": None,
                "ensemble_breakdown": None,
                "degraded": False,
                "latency_ms": total_ms,
                "model_version": "ensemble-v1",
            }

        # ── Feature extraction + WHOIS concurrently ───────────────────────────
        feature_dict, whois_result = await asyncio.gather(
            extract_features(norm_url, infra_timeout=settings.TIMEOUT_SECS),
            get_domain_info(norm_url),
            return_exceptions=True,
        )

        if isinstance(feature_dict, Exception):
            logger.error("Feature extraction failed for %s: %s", norm_url, feature_dict)
            feature_dict = {}

        if isinstance(whois_result, Exception):
            logger.warning("WHOIS failed for %s: %s", norm_url, whois_result)
            whois_result = {"whois_available": False, "error": str(whois_result)}

        # ── Ensemble inference (CPU-bound, run in thread) ─────────────────────
        try:
            ml_result = await asyncio.to_thread(svc.predict, feature_dict, norm_url)
        except Exception as exc:
            logger.exception("Ensemble inference failed for %s: %s", norm_url, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model inference failed: {exc}",
            ) from exc

        total_ms = round((time.perf_counter() - t_start) * 1000, 2)

        infra_dict = {k: feature_dict.get(k) for k in _INFRA_FIELDS} if feature_dict else {}

        return {
            "url":                norm_url,
            "prediction":         ml_result["prediction"],
            "label":              ml_result["label"],
            "confidence":         ml_result["confidence"],
            "risk_level":         ml_result["risk_level"],
            "infrastructure":     infra_dict or None,
            "domain_info":        whois_result if isinstance(whois_result, dict) else None,
            "ensemble_breakdown": ml_result.get("ensemble_breakdown"),
            "degraded":           False,
            "latency_ms":         total_ms,
            "model_version":      "ensemble-v1",
        }



# ── POST /api/v1/analyze ──────────────────────────────────────────────────────

@router.post(
    "/api/v1/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a URL for phishing (Ensemble: XGBoost + Logistic Regression)",
    tags=["Prediction"],
)
async def analyze(
    data: PredictRequest,
    svc: EnsembleService = Depends(get_ensemble_service),
) -> AnalyzeResponse:
    """
    Full ensemble phishing analysis.

    1. Extracts 111 structural + infrastructure features (DNS/SSL/WHOIS/ASN).
    2. Runs calibrated XGBoost inference (weight=0.65).
    3. Runs NLP Bag-of-Words + Logistic Regression inference (weight=0.35).
    4. Returns weighted soft-voting verdict with per-model breakdown.
    """
    result = await _run_analysis(data.url, svc)

    infra = None
    if result["infrastructure"]:
        clean_infra = {k: v for k, v in result["infrastructure"].items() if v is not None}
        infra = InfrastructureFeatures(**clean_infra) if clean_infra else None

    domain_info = None
    if isinstance(result.get("domain_info"), dict):
        domain_info = DomainInfo(**result["domain_info"])

    breakdown = None
    if result.get("ensemble_breakdown"):
        breakdown = EnsembleBreakdown(**result["ensemble_breakdown"])

    return AnalyzeResponse(
        url=result["url"],
        prediction=result["prediction"],
        label=result["label"],
        confidence=result["confidence"],
        risk_level=result["risk_level"],
        reason=result.get("reason"),
        infrastructure=infra,
        domain_info=domain_info,
        ensemble_breakdown=breakdown,
        degraded=result["degraded"],
        latency_ms=result["latency_ms"],
        model_version=result["model_version"],
    )


# ── GET / (Web UI) ────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(
    request: Request,
    url: Optional[str] = None,
    svc: EnsembleService = Depends(get_ensemble_service),
):
    context = {"request": request, "url": url}
    if url:
        try:
            if not url.startswith(("http://", "https://")):
                raise ValueError("URL must start with http:// or https://")
            result = await _run_analysis(url, svc)
            context.update({"result": result, "is_phishing": result["label"] == 1})
        except Exception as exc:
            logger.warning("Web UI analysis failed: %s", exc)
            context["error"] = str(exc)
    return templates.TemplateResponse("index.html", context)


# ── POST /predict (HTML form) ─────────────────────────────────────────────────

@router.post("/predict", response_class=HTMLResponse, include_in_schema=False)
async def predict_web(
    request: Request,
    url: str = Form(...),
    svc: EnsembleService = Depends(get_ensemble_service),
):
    try:
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        result = await _run_analysis(url, svc)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "url": url,
             "result": result, "is_phishing": result["label"] == 1},
        )
    except Exception as exc:
        logger.warning("Web form prediction failed: %s", exc)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "url": url, "error": str(exc)},
        )


# ── GET /health ───────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health / readiness check",
    tags=["Operations"],
)
async def health_check(svc: EnsembleService = Depends(get_ensemble_service)) -> HealthResponse:
    return HealthResponse(
        status="healthy" if svc.is_loaded else "degraded",
        model_loaded=svc.is_loaded,
        ensemble_loaded=svc.is_loaded,
        model_version="ensemble-v1",
        app_env=settings.APP_ENV,
    )


# ── GET /api/v1/metrics ───────────────────────────────────────────────────────

@router.get(
    "/api/v1/metrics",
    status_code=status.HTTP_200_OK,
    summary="Get training metrics (supports multiple experiment runs)",
    tags=["Operations"],
)
async def get_metrics(run_id: Optional[str] = None) -> dict:
    """
    Returns training metrics.
    If run_id is omitted, returns a list of available runs and the latest clean metrics.
    If run_id is provided, returns the specific JSON content for that experiment.
    """
    if not settings.EXPERIMENTS_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiments directory not found.",
        )

    # 1. List all available JSON files
    runs = [f.stem for f in settings.EXPERIMENTS_DIR.glob("*.json")]

    if run_id is None:
        # Load latest metrics_clean.json as default if it exists
        latest_data = {}
        target = settings.EXPERIMENTS_DIR / "metrics_clean.json"
        if target.exists():
            with open(target) as f:
                latest_data = json.load(f)

        # Normalization: ensure 'f1' exists
        if "f1_score" in latest_data and "f1" not in latest_data:
            latest_data["f1"] = latest_data["f1_score"]

        # Merge for backwards compatibility with the UI
        return {
            **latest_data,
            "available_runs": sorted(runs, reverse=True),
            "message": "Specify ?run_id=<name> to get full details for a specific run."
        }

    # 2. Return specific run details
    target_path = settings.EXPERIMENTS_DIR / f"{run_id}.json"
    if not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment '{run_id}' not found. Available: {', '.join(runs)}",
        )

    try:
        with open(target_path) as f:
            data = json.load(f)
            # Normalization: ensure 'f1' exists even if the source uses 'f1_score'
            if "f1_score" in data and "f1" not in data:
                data["f1"] = data["f1_score"]
            elif "metrics" in data and "f1" in data["metrics"]:
                # Flatten or ensure top-level f1 for consistency
                data["f1"] = data["metrics"]["f1"]
            return data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read experiment file: {exc}",
        ) from exc


# ── POST /reload-model ────────────────────────────────────────────────────────

@router.post(
    "/reload-model",
    status_code=status.HTTP_200_OK,
    summary="Hot-reload both models from disk",
    tags=["Operations"],
)
async def reload_model(svc: EnsembleService = Depends(get_ensemble_service)) -> dict:
    """Reload both the XGBoost and NLP models without restarting the server."""
    try:
        await asyncio.to_thread(svc.load)
        logger.info("Both models reloaded via /reload-model")
        return {"status": "success", "model_version": "ensemble-v1"}
    except Exception as exc:
        logger.exception("Model reload failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model reload failed: {exc}",
        ) from exc
