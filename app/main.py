"""
app/main.py
─────────────────────────────────────────────────────────────
FastAPI application factory for the Ensemble Phishing Detection API.

Features:
  • Lifespan event: BOTH models (XGBoost + NLP) loaded on startup
  • CORS middleware
  • Request-size limit middleware
  • Global exception handler
  • Swagger/ReDoc docs at /docs and /redoc
"""

from __future__ import annotations

import logging
import socket
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers.predict import router
from app.services.ensemble_service import get_ensemble_service


# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load BOTH models (XGBoost + NLP LR). Shutdown: clean up."""
    logger.info("=" * 65)
    logger.info("=== Phishing Detection Ensemble API — Starting Up ===")
    logger.info("=" * 65)
    svc = get_ensemble_service()
    try:
        svc.load()
        logger.info("✓ EnsembleService loaded (XGBoost + NLP Logistic Regression)")
    except Exception as exc:
        logger.critical("FATAL — EnsembleService failed to load: %s", exc)
        # Don't raise — /health will report degraded state

    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info("Local:   http://127.0.0.1:%d", settings.API_PORT)
        logger.info("Network: http://%s:%d", local_ip, settings.API_PORT)
        logger.info("Docs:    http://127.0.0.1:%d/docs", settings.API_PORT)
    except Exception:
        pass

    yield  # ── App is running ─────────────────────────────────────────────────

    logger.info("=== Phishing Detection Ensemble API — Shutting Down ===")


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Ensemble ML API for real-time phishing URL detection. "
            "Combines XGBoost (111 structural features) with "
            "Logistic Regression (Bag-of-Words NLP) via weighted soft-voting. "
            "Returns prediction, confidence, risk level, and per-model breakdown."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request-size limit ────────────────────────────────────────────────────
    @application.middleware("http")
    async def limit_request_size(request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Request body too large.",
                    "max_bytes": settings.MAX_REQUEST_BODY_BYTES,
                },
            )
        return await call_next(request)

    # ── Latency logging ───────────────────────────────────────────────────────
    @application.middleware("http")
    async def log_requests(request: Request, call_next) -> Response:
        t0 = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            "method=%s path=%s status=%d latency=%.2fms",
            request.method, request.url.path, response.status_code, duration_ms,
        )
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        return response

    # ── Global exception handler ──────────────────────────────────────────────
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception for %s %s: %s", request.method, request.url, exc)
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected internal error occurred.", "detail": str(exc)},
        )

    # ── Routes ────────────────────────────────────────────────────────────────
    application.include_router(router)

    return application


# ── Module-level app instance ─────────────────────────────────────────────────
app = create_app()
