
import asyncio
import sys
import time
import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

# Setup paths
ROOT = Path("D:/FINAL YEAR PROJECT/merged")
sys.path.insert(0, str(ROOT))

from app.services.ensemble_service import EnsembleService
from app.utils.deep_feature_extractor import extract
from app.config import settings

# Configuration
DATASET_CSV = ROOT / "Dataset" / "phishing_site_urls.csv"
OUTPUT_JSON = ROOT / "experiments" / "metrics_clean.json"
SAMPLE_SIZE = 200  # High-fidelity live tests

async def main():
    print("\n" + "="*70)
    print("   GENERATING OVERALL MERGED METRICS (ENSEMBLE: XGB + NLP)")
    print("="*70 + "\n")

    # 1. Load Ensemble
    svc = EnsembleService()
    svc.load()
    print(f"[OK] Models Loaded: XGBoost ({svc._xgb_w*100}%) + NLP ({svc._nlp_w*100}%)\n")

    # 2. Load Dataset
    if not DATASET_CSV.exists():
        print(f"Error: Dataset not found at {DATASET_CSV}")
        return

    df = pd.read_csv(DATASET_CSV)
    # Balanced sample
    phish = df[df['Label'].str.lower() == 'bad'].sample(SAMPLE_SIZE // 2, random_state=42)
    safe = df[df['Label'].str.lower() == 'good'].sample(SAMPLE_SIZE // 2, random_state=42)
    test_df = pd.concat([phish, safe]).sample(frac=1, random_state=42)

    print(f"Analyzing {SAMPLE_SIZE} URLs with LIVE infrastructure checks...")
    print("This may take 1-2 minutes depending on your internet connection.\n")

    y_true = []
    y_pred = []
    y_proba = []
    
    t0 = time.perf_counter()

    for i, (_, row) in enumerate(test_df.iterrows()):
        url = row['URL']
        actual = 1 if row['Label'].lower() == 'bad' else 0
        
        try:
            # REAL Live Extraction (DNS, SSL, WHOIS, Lexical)
            # We set a shorter timeout for speed in this batch test
            features = await extract(url, infra_timeout=5.0)
            
            # Predict using Ensemble
            res = svc.predict(features, url)
            
            y_true.append(actual)
            y_pred.append(res['label'])
            # Probability for ROC-AUC
            prob = res['confidence'] if res['label'] == 1 else 1 - res['confidence']
            y_proba.append(prob)
            
            if (i + 1) % 20 == 0:
                print(f"  [{i+1}/{SAMPLE_SIZE}] URLs processed...")
        except Exception as e:
            continue

    total_time = time.perf_counter() - t0
    
    # 3. Calculate Final Metrics
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred), 4),
        "recall": round(recall_score(y_true, y_pred), 4),
        "f1": round(f1_score(y_true, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_true, y_proba), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "sample_size": len(y_true),
        "latency_avg_ms": round((total_time / len(y_true)) * 1000, 2),
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model_file": "Unified Ensemble (XGBoost + NLP)"
    }

    # 4. Save to experiments/metrics_clean.json
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "="*70)
    print("   OVERALL METRICS GENERATED SUCCESSFULLY")
    print(f"   Accuracy  : {metrics['accuracy']*100:.2f}%")
    print(f"   F1 Score  : {metrics['f1']*100:.2f}%")
    print(f"   Metrics Saved to: experiments/metrics_clean.json")
    print("="*70)
    print("The Dashboard (index.html) will now display these OVERALL metrics.\n")

if __name__ == "__main__":
    asyncio.run(main())
