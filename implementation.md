# Implementation Guide — Merged Phishing Detection Ensemble API

Step-by-step commands to set up and run the project on Windows.

---

## Step 1 — Navigate to the Project Folder

```powershell
cd "D:\FINAL YEAR PROJECT\merged"
```

---

## Step 2 — Set Up a Virtual Environment

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

> Your terminal prompt should now show `(venv)` at the beginning.

---

## Step 3 — Install Dependencies

```powershell
pip install -r requirements.txt
```

> **Note on Dependencies:** The system utilizes the latest stable iterations of FastAPI, XGBoost 2.x, and scikit-learn 1.6+. Any legacy Tailwind CSS package conflicts have been resolved in the optimized build process, ensuring fully compatible frontend assets and Python backends.
> This may take 2–5 minutes on first run.

---

## Step 4 — Verify the Setup (Pre-flight Check)

```powershell
python verify_imports.py
```

Expected output:
```
[1] Checking module imports...
  [OK]  app.config
  [OK]  app.utils.deep_feature_extractor
  [OK]  app.utils.nlp_feature_extractor
  [OK]  app.services.ensemble_service
  ...

[3] Loading models...
  [OK]  XGBoost model loads
  [OK]  NLP model + vectorizer loads

Result: 15/15 checks passed
[OK]  All checks passed! Ready to start the server.
```

If all checks pass, proceed to Step 5.

---

## Step 5 — Start the API Server

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

You should see:
```
INFO  | Phishing Detection Ensemble API — Starting Up
INFO  | EnsembleService loaded (Multi-Model VotingClassifier containing LR, SVC, RF, HGB, XGB)
INFO  | Local:   http://127.0.0.1:8000
INFO  | Docs:    http://127.0.0.1:8000/docs
```

---

## Step 6 — Test the API

### Option A — Swagger UI (Recommended)
Open in browser: **http://127.0.0.1:8000/docs**

1. Click **POST /api/v1/analyze**
2. Click **Try it out**
3. Enter a URL and click **Execute**

### Option B — PowerShell (command line)

Test a **safe** URL:
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/v1/analyze" `
  -ContentType "application/json" `
  -Body '{"url": "https://www.google.com"}'
```

Test a **phishing** URL:
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/v1/analyze" `
  -ContentType "application/json" `
  -Body '{"url": "http://secure-login-paypal.fakebank.xyz/verify/account"}'
```

### Option C — Web UI
Open in browser: **http://127.0.0.1:8000**

Enter any URL in the input box and click Analyze.

> **UI Abstraction Feature:** The Web UI and the Chrome Extension specifically abstract away the raw probability confidence metric. This intentional design choice prevents users from agonizing over integer percentages (e.g. 70% vs 40%) and instead delivers a highly definitive **Safe** or **Phishing Risk** diagnosis powered by the backend ensemble.

---

## Step 7 — Health Check

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "ensemble_loaded": true,
  "model_version": "ensemble-v1",
  "app_env": "development"
}
```

---

## Step 8 — Install Chrome Extension (Optional)

1. Open Chrome and go to: `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the folder: `D:\FINAL YEAR PROJECT\merged\chrome-extension`
5. The extension will now check every URL you visit against the local API

> The server (Step 5) must be running for the extension to work.

---

## Restarting the Server Later

Every time you open a new terminal session:

```powershell
cd "D:\FINAL YEAR PROJECT\merged"
venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Tuning Ensemble Weights (Optional)

Edit the `.env` file to adjust model weights without restarting:

```ini
ENSEMBLE_STRUCTURAL_WEIGHT=0.65   # Weight for Multi-Model VotingClassifier (LR, SVC, RF, HGB, XGB)
ENSEMBLE_NLP_WEIGHT=0.35          # Weight for NLP text model fallback
PHISHING_THRESHOLD=0.5            # Lower = more sensitive (more phishing alerts)
```

After editing `.env`, restart the server for changes to take effect.

---

## Retraining Models (Optional)

### Retrain XGBoost (Deep Structural Model)
```powershell
python -m training.generate_training_dataset
python -m training.train_deep_clean
```

### Retrain NLP / Logistic Regression
```powershell
# Place phishing_site_urls.csv in Dataset/ folder first
python -m training.train_nlp
```

After retraining, hot-reload without restarting:
```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/reload-model"
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: pydantic_settings` | Run `pip install -r requirements.txt` again |
| `FileNotFoundError: phishing_deep_clean_v1.pkl` | Ensure `models/` folder has all `.pkl` files |
| `Port 8000 already in use` | Use `--port 8001` in the uvicorn command |
| sklearn version warning on startup | Safe to ignore, or retrain with `python -m training.train_nlp` |
| Chrome extension shows no badge | Ensure server is running on port 8000 |
