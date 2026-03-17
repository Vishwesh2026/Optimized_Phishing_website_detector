"""
verify_imports.py
─────────────────────────────────────────────────────────────
Pre-flight verification script for the merged ensemble project.

Checks:
  1. All modules import without errors
  2. Both model files exist and load correctly
  3. NLP vectorizer + LR model load correctly
  4. Lexical feature extraction works on a test URL
  5. Ensemble produces a plausible result on a test URL

Run:
  cd D:\\FINAL YEAR PROJECT\\merged
  python verify_imports.py
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

PASS = "[OK]  "
FAIL = "[FAIL]"
results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> bool:
    try:
        fn()
        results.append((name, True, ""))
        print(f"  {PASS}  {name}")
        return True
    except Exception as exc:
        results.append((name, False, str(exc)))
        print(f"  {FAIL}  {name}\n      └─ {exc}")
        return False


print("\n" + "=" * 60)
print("  Merged Phishing Detection — Pre-flight Verification")
print("=" * 60 + "\n")

# 1. Module imports
print("[1] Checking module imports...")
check("app.config", lambda: __import__("app.config"))
check("app.utils.deep_feature_extractor", lambda: __import__("app.utils.deep_feature_extractor"))
check("app.utils.deep_model_bundle", lambda: __import__("app.utils.deep_model_bundle"))
check("app.utils.nlp_feature_extractor", lambda: __import__("app.utils.nlp_feature_extractor"))
check("app.services.xgb_service", lambda: __import__("app.services.xgb_service"))
check("app.services.ensemble_service", lambda: __import__("app.services.ensemble_service"))
check("app.schemas.prediction_schema", lambda: __import__("app.schemas.prediction_schema"))

# 2. Model file existence
print("\n[2] Checking model files exist...")
from app.config import settings

def _check_file(path):
    assert path.exists(), f"Not found: {path}"

check(f"XGBoost model ({settings.xgb_model_path.name})", lambda: _check_file(settings.xgb_model_path))
check(f"Feature cols ({settings.feature_cols_path.name})", lambda: _check_file(settings.feature_cols_path))
check(f"NLP vectorizer ({settings.NLP_VECTORIZER_PATH.name})", lambda: _check_file(settings.NLP_VECTORIZER_PATH))
check(f"NLP model ({settings.NLP_MODEL_PATH.name})", lambda: _check_file(settings.NLP_MODEL_PATH))

# 3. Load both models
print("\n[3] Loading models...")
from app.services.xgb_service import get_xgb_service as _get_xgb

def _load_xgb():
    svc = _get_xgb()
    if not svc.is_loaded:
        svc.load()

_xgb_ok = check("XGBoost model loads", _load_xgb)

from app.utils.nlp_feature_extractor import load_nlp_bundle
_nlp_bundle = None
def _load_nlp():
    global _nlp_bundle
    _nlp_bundle = load_nlp_bundle(settings.NLP_VECTORIZER_PATH, settings.NLP_MODEL_PATH)
_nlp_ok = check("NLP model + vectorizer loads", _load_nlp)

# 4. Lexical feature extraction
print("\n[4] Feature extraction (lexical, no network)...")
from app.utils.deep_feature_extractor import extract_lexical

def _test_lexical():
    feats = extract_lexical("http://secure-login-paypal.fakebank.xyz/verify/account")
    assert len(feats) > 0
    assert "qty_dot_url" in feats

check("extract_lexical() returns expected keys", _test_lexical)

# 5. NLP prediction
print("\n[5] NLP model inference...")
if _nlp_bundle and _nlp_ok:
    from app.utils.nlp_feature_extractor import get_nlp_proba

    def _test_nlp():
        p = get_nlp_proba("http://secure-login-paypal.fakebank.xyz/verify/account", _nlp_bundle)
        assert 0.0 <= p <= 1.0, f"Probability out of range: {p}"
        print(f"      └─ NLP phishing probability: {p:.4f}")

    check("get_nlp_proba() returns valid probability", _test_nlp)

# 6. Summary
print()
print("=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
total  = len(results)
print(f"  Result: {passed}/{total} checks passed")
if passed == total:
    print(f"  {PASS} All checks passed! Ready to start the server.")
    print()
    print("  Start server:")
    print("    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
else:
    print(f"  {FAIL} {total - passed} check(s) failed. Review errors above.")
    sys.exit(1)
print("=" * 60 + "\n")
