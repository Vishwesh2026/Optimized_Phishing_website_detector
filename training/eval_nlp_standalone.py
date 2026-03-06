"""
Evaluates the NLP model (Project 1) standalone on phishing_site_urls.csv
and saves results to experiments/metrics_clean.json for the dashboard.
"""
import sys, warnings, json, time
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from app.config import settings
from app.utils.nlp_feature_extractor import load_nlp_bundle, get_nlp_proba

ROOT      = Path("D:/FINAL YEAR PROJECT/merged")
NLP_CSV   = ROOT / "Dataset" / "phishing_site_urls.csv"
OUT_JSON  = ROOT / "experiments" / "metrics_clean.json"

# Load NLP model
print("[1/4] Loading NLP model...")
nlp = load_nlp_bundle(settings.NLP_VECTORIZER_PATH, settings.NLP_MODEL_PATH)

# Load dataset
print("[2/4] Loading dataset...")
df = pd.read_csv(NLP_CSV)
df["_label"] = (df["Label"].str.lower() == "bad").astype(int)

# Use same test split
_, df_test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["_label"])
print(f"      Test samples: {len(df_test):,}  (phishing={df_test['_label'].sum():,}, safe={(df_test['_label']==0).sum():,})")

# Run predictions
print("[3/4] Running NLP predictions...")
t0 = time.perf_counter()
p_nlp  = np.array([get_nlp_proba(url, nlp) for url in df_test["URL"]])
y_test = df_test["_label"].values
elapsed = time.perf_counter() - t0
y_pred = (p_nlp >= 0.5).astype(int)
print(f"      Done in {elapsed:.1f}s")

# Metrics
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec  = recall_score(y_test, y_pred, zero_division=0)
f1   = f1_score(y_test, y_pred, zero_division=0)
roc  = roc_auc_score(y_test, p_nlp)
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

print("\n[4/4] Results:")
print(f"  Accuracy  : {acc*100:.2f}%")
print(f"  Precision : {prec*100:.2f}%")
print(f"  Recall    : {rec*100:.2f}%")
print(f"  F1 Score  : {f1*100:.2f}%")
print(f"  ROC-AUC   : {roc:.4f}")
print(f"\n  Confusion Matrix:")
print(f"  True Safe predicted Safe   (TN): {tn:,}")
print(f"  True Safe predicted Phish  (FP): {fp:,}")
print(f"  True Phish predicted Safe  (FN): {fn:,}")
print(f"  True Phish predicted Phish (TP): {tp:,}")

out = {
    "model_file":       "NLP Model (Bag-of-Words + Logistic Regression)",
    "dataset_size":     len(df_test),
    "feature_count":    112,
    "trained_at":       time.strftime("%Y-%m-%dT%H:%M:%S"),
    "accuracy":         round(float(acc),  4),
    "precision":        round(float(prec), 4),
    "recall":           round(float(rec),  4),
    "f1":               round(float(f1),   4),
    "f1_score":         round(float(f1),   4),
    "roc_auc":          round(float(roc),  4),
    "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
}

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_JSON, "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[OK] Dashboard metrics updated -> {OUT_JSON}")
