# Phishing Detection System — Project Walkthrough

This guide explains how to use, maintain, and retrain the phishing detection system.

---

## 🌓 1. The Ensemble Model Architecture 🚀

The system utilizes a unified **Ensemble Service** combining two distinct models recursively via weighted soft-voting.

### 🌳 Model A: Structural & Infrastructure (XGBoost)
*   **Active as:** models/phishing_deep_clean_v1.pkl files.
*   **Best for:** Deep-path phishing URLs and complex structural analysis.
*   **Features:** 111 Structural and infrastructure metrics.
*   **Weight:** Default 65% contribution.

### 📝 Model B: Lexical Text (Logistic Regression NLP)
*   **Active as:** models/phishing.pkl & models/vectorizer.pkl files.
*   **Best for:** Rapid assessment of raw text utilizing a Bag-of-Words paradigm.
*   **Weight:** Default 35% contribution.

> **💡 How the Fusion Works:**
> The EnsembleService receives a URL, extracts infrastructure tokens for Model A, extracts raw text n-grams for Model B, multiplies both outputs by their configured weights (.env), and outputs a consolidated risk probability.
---

## 🏃 2. Everyday Usage

### Start the API
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Access the dashboard at **`http://127.0.0.1:8000`**.

### Use the Chrome Extension
1. Go to `chrome://extensions`.
2. Enable "Developer mode".
3. "Load unpacked" and select the `chrome-extension/` folder.
4. Pin the SafeSurf icon. It will turn red when you visit a phishing site.

---

## 🔄 3. Maintenance & Retraining

If you want to update the model with new data, follow the **3-Phase Retraining Pipeline**:

### Phase 1: Refresh the training data
Run the feature extractor on your raw URL dataset.
```bash
python -m training.generate_training_dataset
```
*   **Action:** Extracts 111 features from `Dataset/PhiUSIIL_Phishing_URL_Dataset.csv`.
*   **Speed:** Uses 40 threads and domain caching.

### Phase 2: Train the Ensemble Models
1. Train the XGBoost model utilizing `python -m training.train_deep_clean`.
2. Train the NLP Logistic Regression model utilizing `python -m training.train_nlp`.
*   **Action:** Compiles `phishing_deep_clean_v1.pkl` and `phishing.pkl` / `vectorizer.pkl`.
*   **Result:** Updates respective metrics.

### Phase 3: Sanity Check
```bash
python -m training.validate_clean_model
```
*   **Action:** Runs the new model against high-traffic safe sites (google.com, wikipedia.org) to ensure no false positives.

---

## 🛠️ 4. Project Organization

| Directory | Purpose |
|---|---|
| `app/routers/` | API endpoints (`analyze`, `metrics`, `health`). |
| `app/services/` | Core logic: `dns_guard` (NXDOMAIN blocker), `ensemble_service` (Inference fusion). |
| `app/utils/` | `deep_feature_extractor` & `nlp_feature_extractor`. |
| `chrome-extension/` | Browser security plugin files. |
| `models/` | Trained model bundles (`.pkl`) and feature lists. |
| `templates/` | **Dashboard UI:** The frontend you see on the homepage. |

---

## 🛡️ 5. How Detection Works (The 3 Layers)

1.  **DNS Guard (Deterministic):** Before the ML runs, it checks if the domain actually exists. If it returns NXDOMAIN, the URL is blocked immediately as "Invalid".
2.  **Feature Extraction:** Extracts 111 numeric signals (structural logic) alongside raw URL character ingestion (NLP logic).
3.  **Ensemble ML Inference:** A weighted soft-voting fusion runs XGBoost and Logistic Regression simultaneously. If the final combined probability > 85%, it flags it as **High Risk**.
## 🏁 6. Quick Verification

After setting up, verify your system by running these checks:

1. **Health Check:** `curl http://127.0.0.1:8000/health` → Should show `healthy`.
2. **Metrics:** `curl http://127.0.0.1:8000/api/v1/metrics` → Should show accuracy > 85%.
3. **Live Scan:** Submit `https://google.com` on the dashboard. It should return **SAFE** in < 2 seconds.
4. **DNS Guard Scan:** Submit `https://this-domain-does-not-exist-xyz123.com`. It should return **INVALID** immediately.
