# Phishing Website Detection API — Merged Ensemble

A production-grade phishing URL detection API that combines two complementary machine learning algorithms into a single, more accurate **weighted ensemble**.

## How It Works

```
URL Input
   │
   ├──▶  [Model A] Deep Feature Extractor
   │         111 lexical + infrastructure features
   │         (URL structure, DNS, SSL, WHOIS, ASN)
   │              │
   │              ▼
   │         XGBoost + Isotonic Calibration
   │         ──────────────────────────────
   │         p_xgb  ×  weight 0.65
   │
   └──▶  [Model B] NLP Text Classifier
             URL tokenized as Bag-of-Words text
             (CountVectorizer + Snowball Stemmer)
                  │
                  ▼
             Logistic Regression
             ──────────────────
             p_nlp  ×  weight 0.35
                  │
                  ▼
         p_final = 0.65×p_xgb + 0.35×p_nlp
                  │
                  ▼
         label = 1 (phishing) if p_final ≥ 0.5
```

The two models use **completely orthogonal feature spaces**, so their combination captures phishing signals that each individual model would miss.

## Project Structure

```
merged/
├── app/
│   ├── config.py                      # All settings (ensemble weights, model paths)
│   ├── main.py                        # FastAPI entry point
│   ├── routers/
│   │   └── predict.py                 # API endpoints
│   ├── services/
│   │   ├── ensemble_service.py        # ★ Core merged algorithm
│   │   ├── xgb_service.py             # XGBoost model loader
│   │   ├── whois_service.py           # WHOIS domain info
│   │   └── dns_guard.py               # NXDOMAIN pre-check
│   ├── schemas/
│   │   └── prediction_schema.py       # Request/Response schemas
│   └── utils/
│       ├── nlp_feature_extractor.py   # ★ Project 1 NLP wrapper
│       ├── deep_feature_extractor.py  # 111-feature extractor
│       ├── deep_model_bundle.py       # XGBoost bundle
│       └── url_normalizer.py          # URL normalization
├── models/
│   ├── phishing_deep_clean_v1.pkl     # XGBoost + Isotonic (Project 2)
│   ├── deep_feature_cols_clean.json
│   ├── deep_feature_stats.json
│   ├── phishing.pkl                   # Logistic Regression (Project 1)
│   └── vectorizer.pkl                 # CountVectorizer (Project 1)
├── training/
│   ├── train_deep_clean.py            # Retrain XGBoost model
│   ├── train_nlp.py                   # Retrain NLP/LR model
│   └── generate_training_dataset.py
├── chrome-extension/                  # Browser extension
├── templates/index.html               # Web UI
├── requirements.txt
├── .env                               # Configuration
└── verify_imports.py                  # Pre-flight check script
```

## Quick Start

### 1. Create virtual environment & install dependencies
```bash
cd "D:\FINAL YEAR PROJECT\merged"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verify the setup
```bash
python verify_imports.py
```

### 3. Start the server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open the UI
- Web UI: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

## API Usage

### Analyze a URL (primary endpoint)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://secure-login-paypal.fakebank.xyz"}'
```

**Response:**
```json
{
  "url": "https://secure-login-paypal.fakebank.xyz",
  "prediction": "phishing",
  "label": 1,
  "confidence": 0.93,
  "risk_level": "HIGH",
  "ensemble_breakdown": {
    "xgb_probability": 0.97,
    "nlp_probability": 0.85,
    "xgb_weight": 0.65,
    "nlp_weight": 0.35,
    "final_probability": 0.93
  },
  "latency_ms": 1840.7,
  "model_version": "ensemble-v1"
}
```

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `MODEL_VERSION` | `clean_v1` | XGBoost model version suffix |
| `ENSEMBLE_XGB_WEIGHT` | `0.65` | Weight for XGBoost probability |
| `ENSEMBLE_NLP_WEIGHT` | `0.35` | Weight for NLP/LR probability |
| `PHISHING_THRESHOLD` | `0.5` | Probability threshold for phishing label |
| `TIMEOUT_SECS` | `15.0` | Infrastructure check timeout |

## Retraining

### Retrain XGBoost (Project 2 pipeline)
```bash
python -m training.generate_training_dataset
python -m training.train_deep_clean
```

### Retrain NLP / Logistic Regression (Project 1 pipeline)
```bash
# Place phishing_site_urls.csv in Dataset/
python -m training.train_nlp
```

## Chrome Extension
Load `chrome-extension/` as an unpacked extension in Chrome. It calls `/api/v1/analyze` to check every URL you visit.

## Health Check
```bash
curl http://127.0.0.1:8000/health
```
