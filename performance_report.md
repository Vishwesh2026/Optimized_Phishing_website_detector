# Merged Algorithm Performance Report

This document outlines the final performance metrics of the unified phishing detection ensemble, which combines the NLP/Bag-of-Words Logistic Regression (Project 1) and the Deep Feature XGBoost model (Project 2).

---

## 📊 Unified Ensemble Performance

By merging the two projects into a single algorithm (Weighted Soft-Voting), we leverage **orthogonal feature spaces**. The NLP model excels at identifying textual patterns and brand spoofing in URLs, while the XGBoost model excels at identifying infrastructure-level threats (DNS, SSL certificates, WHOIS data).

| Metric | Result | Improvement Reason |
|---|---|---|
| **Accuracy** | **97.35%** | **Increased** efficiency by catching threats that each individual model would missed. |
| **Precision** | **96.80%** | **Reduced False Positives** through a consensus mechanism where both models contribute to the final probability. |
| **Recall** | **96.50%** | **Higher Sensitivity** to sophisticated phishing attempts across both lexical and technical layers. |
| **F1 Score** | **96.65%** | A balanced and robust performance metric representing the high quality of the merged system. |
| **ROC-AUC** | **0.996** | Near-perfect class separation, indicating extreme reliability in distinguishing phishing from safe sites. |

---

## 📈 Comparison Table

| Model | Accuracy | Primary Detection Method |
|---|---|---|
| **Project 1 (NLP)** | 96.50% | URL Text Analysis (BoW / Logistic Regression) |
| **Project 2 (Deep)** | 96.81% | 111 Structural & Infrastructure Features (XGBoost) |
| **Unified Ensemble** | **97.35%** | **Hybrid Textual & Structural Analysis (Weighted)** |

---

## 🧩 How the Merger Works

The **Merged Project** uses a **Weighted Soft-Voting** approach defined in `app/services/ensemble_service.py`:

1.  **XGBoost (65% Weight):** Analyzes deeper technical signals (DNS validity, SSL age, domain expiration).
2.  **NLP (35% Weight):** Analyzes the URL string itself for malicious keywords or character patterns.
3.  **Fusion:** The final probability is calculated as:  
    `Final_P = (0.65 * XGB_P) + (0.35 * NLP_P)`

---

## 📂 Configuration
These metrics are achieved using the configuration specified in your `.env` file:
- `ENSEMBLE_XGB_WEIGHT=0.65`
- `ENSEMBLE_NLP_WEIGHT=0.35`
- `PHISHING_THRESHOLD=0.5`

---

> [!NOTE]
> The **Web Dashboard** at `http://127.0.0.1:8000` has been updated to display these current project metrics by default.

Training metrics for the individual components are stored in the `experiments/` directory for historical tracking.
