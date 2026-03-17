"""
training/evaluate_unified.py
──────────────────────────────────────────────────────────────────────────────
Unified Phishing Detection Model — Evaluation Script (v2 — Aligned)

WHAT THIS DOES
──────────────
Evaluates the FULL Ensemble (XGBoost 65% + NLP 35%) on the same ALIGNED test
split where BOTH models process the EXACT SAME URL.

HOW ALIGNMENT WORKS
────────────────────
- `PhiUSIIL_Phishing_URL_Dataset.csv` is the original source (URL + label).
- `generated_training_dataset_clean.csv` was generated from PhiUSIIL using
  the same shuffle (random_state=42). Row i in generated CSV = row i in PhiUSIIL
  (after the same shuffle). We merge them by index to get (URL + 111 features).
- With aligned data: XGBoost sees deep_features[i] AND NLP sees url[i].
  Both produce a probability for the SAME URL/label.
- The weighted soft-vote is now mathematically correct.

OUTPUT
──────
  experiments/unified_metrics.json   — full breakdown
  experiments/metrics_clean.json     — dashboard update

USAGE
─────
  cd "D:/FINAL YEAR PROJECT/merged"
  venv\Scripts\python -m training.evaluate_unified
"""

from __future__ import annotations

import json
import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.services.xgb_service import XGBService
from app.utils.nlp_feature_extractor import load_nlp_bundle, get_nlp_proba

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.WARNING, format="%(levelname)-8s  %(message)s")
logger = logging.getLogger("evaluate_unified")
logger.setLevel(logging.INFO)

# ── Paths ─────────────────────────────────────────────────────────────────────
PHIUSIIL_CSV  = ROOT / "Dataset" / "PhiUSIIL_Phishing_URL_Dataset.csv"   # source with URLs
DEEP_CSV      = ROOT / "Dataset" / "generated_training_dataset_clean.csv" # pre-computed features
OUT_JSON      = ROOT / "experiments" / "unified_metrics.json"
DASH_JSON     = ROOT / "experiments" / "metrics_clean.json"

XGB_WEIGHT   = settings.ENSEMBLE_XGB_WEIGHT   # 0.65
NLP_WEIGHT   = settings.ENSEMBLE_NLP_WEIGHT   # 0.35
THRESHOLD    = settings.PHISHING_THRESHOLD    # 0.5
TEST_SIZE    = 0.20
RANDOM_STATE = 42


# ── Helpers ───────────────────────────────────────────────────────────────────

def _metrics_dict(y_true, y_pred, y_proba) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return {
        "accuracy":         round(float(accuracy_score(y_true, y_pred)), 4),
        "precision":        round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall":           round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1":               round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc":          round(float(roc_auc_score(y_true, y_proba)), 4),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
    }


def _banner(title: str) -> None:
    print(f"\n{'='*62}")
    print(f"  {title}")
    print(f"{'='*62}")


def _print_metrics(name: str, m: dict, n: int) -> None:
    print(f"\n  [{name}]  (n={n:,})")
    print(f"  {'Accuracy':<14} {m['accuracy']*100:.2f}%")
    print(f"  {'Precision':<14} {m['precision']*100:.2f}%")
    print(f"  {'Recall':<14} {m['recall']*100:.2f}%")
    print(f"  {'F1 Score':<14} {m['f1']*100:.2f}%")
    print(f"  {'ROC-AUC':<14} {m['roc_auc']:.4f}")
    tn = m["confusion_matrix"][0][0]; fp_v = m["confusion_matrix"][0][1]
    fn = m["confusion_matrix"][1][0]; tp = m["confusion_matrix"][1][1]
    print(f"\n  Confusion Matrix:          Pred Safe   Pred Phish")
    print(f"  {'True Safe':<24}  {tn:>9,}   {fp_v:>9,}")
    print(f"  {'True Phish':<24}  {fn:>9,}   {tp:>9,}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _banner("UNIFIED ENSEMBLE EVALUATION  |  XGBoost 65% + NLP 35%")
    print(f"  Weights: XGB={XGB_WEIGHT}, NLP={NLP_WEIGHT}  |  Threshold={THRESHOLD}")

    # ── Validate paths ────────────────────────────────────────────────────────
    for p, name in [(PHIUSIIL_CSV, "PhiUSIIL source CSV"),
                    (DEEP_CSV,     "Generated deep feature CSV")]:
        if not p.exists():
            print(f"\n  [ERROR] {name} not found:\n    {p}")
            sys.exit(1)

    # ── Step 1: Load models ───────────────────────────────────────────────────
    print("\n[1/5] Loading XGBoost model...")
    xgb_svc = XGBService()
    xgb_svc.load()
    feature_cols = xgb_svc._feature_cols
    print(f"      OK  ({len(feature_cols)} features)")

    print("[2/5] Loading NLP model (CountVectorizer + Logistic Regression)...")
    nlp_bundle = load_nlp_bundle(
        vectorizer_path=settings.NLP_VECTORIZER_PATH,
        model_path=settings.NLP_MODEL_PATH,
    )
    print(f"      OK")

    # ── Step 2: Load and ALIGN both datasets ──────────────────────────────────
    # The PhiUSIIL CSV was used as input to generate_training_dataset.py.
    # That script: (a) keeps only URL + label, (b) shuffles with random_state=42,
    # (c) maps labels, (d) adds http:// prefix.
    # We replicate the EXACT same preprocessing here so row indices match.
    print("[3/5] Loading and aligning datasets...")

    df_src = pd.read_csv(PHIUSIIL_CSV, low_memory=False, usecols=["URL", "label"])
    # PhiUSIIL: label=0 is PHISHING, label=1 is LEGITIMATE (inverted convention)
    # map to our convention: phishing=1, safe=0
    label_map = {0: 1, 1: 0}
    df_src["label"] = df_src["label"].map(label_map)
    df_src = df_src.dropna(subset=["URL"]).reset_index(drop=True)
    df_src["URL"] = df_src["URL"].apply(lambda u: u if str(u).startswith("http") else f"http://{u}")
    # Apply the SAME shuffle as generate_training_dataset.py
    df_src = df_src.sample(frac=1, random_state=42).reset_index(drop=True)

    df_deep = pd.read_csv(DEEP_CSV, low_memory=False)

    # Align: both should have the same length (PhiUSIIL → generated)
    n_match = min(len(df_src), len(df_deep))
    df_src  = df_src.iloc[:n_match].reset_index(drop=True)
    df_deep = df_deep.iloc[:n_match].reset_index(drop=True)

    print(f"      Aligned {n_match:,} rows (PhiUSIIL URL + deep features)")

    # Build aligned arrays
    X_all   = df_deep.reindex(columns=feature_cols, fill_value=-1)
    urls    = df_src["URL"].values
    y_all   = df_deep["label"].astype(int).values   # authoritative label from deep CSV

    # ── Step 3: Stratified train/test split ───────────────────────────────────
    indices = np.arange(n_match)
    idx_train, idx_test = train_test_split(
        indices, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_all
    )

    X_test     = X_all.iloc[idx_test]
    y_test     = y_all[idx_test]
    urls_test  = urls[idx_test]
    n_test     = len(y_test)

    print(f"      Test split:  {n_test:,} rows  "
          f"(safe={int((y_test==0).sum()):,}, phishing={int((y_test==1).sum()):,})")

    # ── Step 4: XGBoost predictions ───────────────────────────────────────────
    print("[4/5] Running XGBoost inference...")
    t0 = time.perf_counter()
    xgb_raw = xgb_svc._pipeline.predict_proba(X_test.values)
    p_xgb   = (xgb_raw[:, 1] if xgb_raw.ndim == 2 else xgb_raw).astype(float)
    y_pred_xgb = (p_xgb >= THRESHOLD).astype(int)
    print(f"      Done in {(time.perf_counter()-t0)*1000:.0f}ms")

    # ── Step 5: NLP predictions on the SAME aligned URLs ─────────────────────
    print("[5/5] Running NLP inference on SAME URLs (aligned)...")
    t0 = time.perf_counter()
    p_nlp = np.array([get_nlp_proba(url, nlp_bundle) for url in urls_test])
    y_pred_nlp = (p_nlp >= THRESHOLD).astype(int)
    print(f"      Done in {(time.perf_counter()-t0)*1000:.0f}ms  ({(time.perf_counter()-t0)*1000/n_test:.2f}ms/URL)")

    # ── Step 6: Ensemble — weighted soft-vote (same URL, same label) ──────────
    p_ensemble = XGB_WEIGHT * p_xgb + NLP_WEIGHT * p_nlp
    y_pred_ens = (p_ensemble >= THRESHOLD).astype(int)

    # ── Step 7: Compute metrics ───────────────────────────────────────────────
    m_xgb = _metrics_dict(y_test, y_pred_xgb, p_xgb)
    m_nlp = _metrics_dict(y_test, y_pred_nlp, p_nlp)
    m_ens = _metrics_dict(y_test, y_pred_ens, p_ensemble)

    # ── Step 8: Print all results ─────────────────────────────────────────────
    _banner("EVALUATION RESULTS")
    _print_metrics("XGBoost (Deep Features - Project 2)", m_xgb, n_test)
    _print_metrics("NLP (Bag-of-Words + LR - Project 1)", m_nlp, n_test)
    _print_metrics("UNIFIED ENSEMBLE (XGB 65% + NLP 35%)", m_ens, n_test)

    # ── Step 9: Save results ──────────────────────────────────────────────────
    out = {
        "model_file":        "Unified Ensemble (XGBoost + NLP)",
        "ensemble_weights":  {"xgb": XGB_WEIGHT, "nlp": NLP_WEIGHT},
        "threshold":         THRESHOLD,
        "dataset_size":      n_test,
        "feature_count":     len(feature_cols),
        "trained_at":        time.strftime("%Y-%m-%dT%H:%M:%S"),

        # Ensemble (primary — what dashboard shows)
        "accuracy":          m_ens["accuracy"],
        "precision":         m_ens["precision"],
        "recall":            m_ens["recall"],
        "f1":                m_ens["f1"],
        "f1_score":          m_ens["f1"],
        "roc_auc":           m_ens["roc_auc"],
        "confusion_matrix":  m_ens["confusion_matrix"],

        # Per-component breakdown
        "component_metrics": {
            "xgboost": m_xgb,
            "nlp":     m_nlp,
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n[OK] Saved -> {OUT_JSON}")

    with open(DASH_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[OK] Dashboard updated -> {DASH_JSON}")

    # ── Step 10: Final summary ────────────────────────────────────────────────
    _banner("FINAL SUMMARY  (same URLs, aligned evaluation)")
    print(f"\n  {'Component':<38} {'Accuracy':>10}  {'F1':>8}  {'ROC-AUC':>10}")
    print(f"  {'-'*68}")
    print(f"  {'XGBoost (Project 2 - Deep Features)':<38} {m_xgb['accuracy']*100:>9.2f}%  {m_xgb['f1']*100:>7.2f}%  {m_xgb['roc_auc']:>10.4f}")
    print(f"  {'NLP (Project 1 - URL Text)':<38} {m_nlp['accuracy']*100:>9.2f}%  {m_nlp['f1']*100:>7.2f}%  {m_nlp['roc_auc']:>10.4f}")
    print(f"  {'-'*68}")
    print(f"  {'UNIFIED ENSEMBLE <- Dashboard':<38} {m_ens['accuracy']*100:>9.2f}%  {m_ens['f1']*100:>7.2f}%  {m_ens['roc_auc']:>10.4f}")
    print(f"\n  Files: experiments/unified_metrics.json")
    print(f"         experiments/metrics_clean.json  (dashboard)")
    print()


if __name__ == "__main__":
    main()
