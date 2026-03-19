"""
app/services/phishtank_service.py
─────────────────────────────────────────────────────────────
PhishTank API integration — queries PhishTank's public database
to check if a URL has been reported and verified as phishing.

This acts as a deterministic third signal in the ensemble:
  - If PhishTank confirms phishing → override ensemble verdict
  - If not in database or unavailable → no effect on ensemble

API Endpoint: https://checkurl.phishtank.com/checkurl/
Rate limits:  No hard limit for small projects, but we cache
              results per URL (10-min TTL) to be a good citizen.

Response format: XML or JSON (we use JSON via format=json).
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# ── PhishTank API config ─────────────────────────────────────────────────────

PHISHTANK_API_URL = "https://checkurl.phishtank.com/checkurl/"
PHISHTANK_TIMEOUT = 8.0  # seconds

# Optional: set your PhishTank API key here or via env for higher rate limits
# Get one free at: https://www.phishtank.com/api_register.php
PHISHTANK_API_KEY: Optional[str] = None

# ── In-memory cache (URL hash → result, with 10-min TTL) ─────────────────────

_cache: dict[str, tuple[dict, float]] = {}
_CACHE_TTL = 600  # 10 minutes


def _cache_key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _get_cached(url: str) -> Optional[dict]:
    key = _cache_key(url)
    if key in _cache:
        result, ts = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return result
        del _cache[key]
    return None


def _set_cached(url: str, result: dict) -> None:
    key = _cache_key(url)
    _cache[key] = (result, time.time())
    # Evict old entries if cache grows too large
    if len(_cache) > 1000:
        cutoff = time.time() - _CACHE_TTL
        expired = [k for k, (_, ts) in _cache.items() if ts < cutoff]
        for k in expired:
            del _cache[k]


# ── Public API ────────────────────────────────────────────────────────────────

async def check_phishtank(url: str) -> dict:
    """
    Query PhishTank to check if a URL is in their phishing database.

    Returns:
        dict with keys:
          available   — bool: whether PhishTank responded
          in_database — bool: whether the URL was found in PhishTank
          is_phishing — bool: whether PhishTank verified it as phishing
          phish_id    — Optional[str]: PhishTank's internal ID for the phish
          error       — Optional[str]: error message if unavailable
    """
    # Check cache first
    cached = _get_cached(url)
    if cached is not None:
        logger.debug("PhishTank cache HIT for %s", url)
        return cached

    logger.info("PhishTank API check for: %s", url)

    try:
        form_data = {
            "url": url,
            "format": "json",
        }
        if PHISHTANK_API_KEY:
            form_data["app_key"] = PHISHTANK_API_KEY

        async with httpx.AsyncClient(timeout=PHISHTANK_TIMEOUT) as client:
            response = await client.post(
                PHISHTANK_API_URL,
                data=form_data,
                headers={
                    "User-Agent": "phishtank/SafeSurf-Phishing-Detector",
                },
            )

        if response.status_code != 200:
            result = {
                "available": False,
                "in_database": False,
                "is_phishing": False,
                "phish_id": None,
                "error": f"HTTP {response.status_code}",
            }
            _set_cached(url, result)
            return result

        data = response.json()
        results = data.get("results", {})

        in_database = results.get("in_database", False)
        # PhishTank returns "in_database" as a string "true"/"false" sometimes
        if isinstance(in_database, str):
            in_database = in_database.lower() == "true"

        is_phishing = False
        phish_id = None

        if in_database:
            is_phishing = results.get("verified", False)
            if isinstance(is_phishing, str):
                is_phishing = is_phishing.lower() == "true"
            phish_id = str(results.get("phish_id", ""))

            # Also check the valid flag
            valid = results.get("valid", True)
            if isinstance(valid, str):
                valid = valid.lower() == "true"
            is_phishing = is_phishing and valid

        result = {
            "available": True,
            "in_database": in_database,
            "is_phishing": is_phishing,
            "phish_id": phish_id if phish_id else None,
            "error": None,
        }

        logger.info(
            "PhishTank result: in_db=%s  is_phishing=%s  phish_id=%s",
            in_database, is_phishing, phish_id,
        )

        _set_cached(url, result)
        return result

    except asyncio.TimeoutError:
        logger.warning("PhishTank API timed out for %s", url)
        result = {
            "available": False,
            "in_database": False,
            "is_phishing": False,
            "phish_id": None,
            "error": "Timeout",
        }
        _set_cached(url, result)
        return result

    except Exception as exc:
        logger.warning("PhishTank API error for %s: %s", url, exc)
        result = {
            "available": False,
            "in_database": False,
            "is_phishing": False,
            "phish_id": None,
            "error": str(exc),
        }
        # Don't cache errors for long — next request may succeed
        return result
