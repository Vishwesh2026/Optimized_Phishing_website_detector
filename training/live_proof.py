
import asyncio
import json
import logging
import sys
import time
import csv
import random
from pathlib import Path

# Add root to path
ROOT = Path("D:/FINAL YEAR PROJECT/merged")
sys.path.insert(0, str(ROOT))

from app.services.ensemble_service import EnsembleService
from app.utils.deep_feature_extractor import extract_lexical

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("proof")

DATASET_CSV = Path("D:/FINAL YEAR PROJECT/Fine_tuned/Phishing-Website-Detection-System/Dataset/phishing_site_urls.csv")

async def run_proof():
    print("\n" + "="*60)
    print("      LIVE PROOF: ENSEMBLE PERFORMANCE (100 URLs)")
    print("="*60 + "\n")
    
    # 1. Load Ensemble
    svc = EnsembleService()
    svc.load()
    print("[OK] Model: XGBoost (65%) + NLP (35%) Loaded.\n")
    
    # 2. Read Dataset manually (no pandas)
    rows = []
    with open(DATASET_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Pick 100 random URLs
    sample = random.sample(rows, 100)
    
    hits = 0
    t0 = time.perf_counter()
    
    print(f"{'URL':<50} | {'Actual':<8} | {'Prediction':<10} | {'Match'}")
    print("-" * 85)
    
    for i, row in enumerate(sample):
        url = row['URL']
        actual = 1 if row['Label'].lower() == 'bad' else 0
        
        # Simulating extraction + prediction
        feats = extract_lexical(url)
        res = svc.predict(feats, url)
        pred = res['label']
        
        is_match = pred == actual
        match_str = "MATCH" if is_match else "MISS"
        if is_match: hits += 1
        
        # Print first 20 for visual proof
        if i < 20:
            url_short = (url[:47] + '..') if len(url) > 47 else url
            act_str = "BAD" if actual == 1 else "GOOD"
            pred_str = "PHISH" if pred == 1 else "SAFE"
            print(f"{url_short:<50} | {act_str:<8} | {pred_str:<10} | {match_str}")
    
    print(f"\n... (processed remaining {80} URLs) ...\n")
    
    total_time = time.perf_counter() - t0
    accuracy = (hits / 100) * 100
    
    print("="*60)
    print(f"  FINAL LIVE RESULT:")
    print(f"  Samples: 100")
    print(f"  Accuracy: {accuracy:.2f}%")
    print(f"  Time: {total_time:.2f}s")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_proof())
    except Exception as e:
        print(f"Error during proof: {e}")
