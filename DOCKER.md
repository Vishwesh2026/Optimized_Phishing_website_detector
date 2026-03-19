# 🐳 Docker Guide — SafeSurf Phishing Detection

Run the **entire SafeSurf stack** (FastAPI backend + React frontend) with a single command.  
No Python, no Node.js installation required — Docker handles everything.

---

## 📋 Prerequisites

| Tool | Minimum Version | Install |
|------|----------------|---------|
| Docker Desktop | 24.x | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| Docker Compose | v2 (bundled with Docker Desktop) | Included with Docker Desktop |

> **Tip:** Verify your installation by running `docker --version` and `docker compose version` in your terminal.

---

## ⚖️ Choose Your Setup

SafeSurf provides two ways to run the project with Docker. Choose the one that best fits your needs:

### 1. Run WITHOUT Source Code (Prebuilt Images Mode)
* **Best for:** Trying the app quickly, sharing with others, quick demos, or production deployments.
* **How it works:** Pulls ready-to-use compiled images from Docker Hub.
* **Pros:** Instant startup, completely plug-and-play. No `git clone` needed, no source code required, and absolutely no need to manage local ML models or `.env` files.

### 2. Run WITH Source Code (Development Mode)
* **Best for:** Developers, contributors, and team members actively modifying the code or retraining ML models.
* **How it works:** Uses `docker-compose.yml` to build images directly from your local source code.
* **Pros:** Instantly test local code changes, hot-reloading context, manages environment variables via local files, and perfectly mirrors the production build process.

---

## 🚀 Setup 1: Run WITHOUT Source Code (Prebuilt Images Mode)

This setup is pure plug-and-play. You do not need to download the project repository — you only need a single lightweight file.

### Step 1 — Create `docker-compose.prod.yml`

Create a new file named `docker-compose.prod.yml` in an empty folder and paste this minimal configuration:

```yaml
version: "3.8"

services:
  safesurf-server:
    # Standard Docker Hub naming convention: omteja04/safesurf-server:latest
    image: omteja04/safesurf-server:latest
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - ALLOWED_ORIGINS=*
      # Override any other environment variables here if needed

  safesurf-frontend:
    image: omteja04/safesurf-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - safesurf-server
```

### Step 2 — Start the services

Run the following command in the same folder where you created the file:

```bash
docker compose -f docker-compose.prod.yml up -d
```

This will automatically pull the compiled React frontend and FastAPI backend images from Docker Hub and start them in the background.

### Step 3 — Open in your browser

| Service | URL |
|---------|-----|
| 🌐 Frontend (React app) | http://localhost |
| ⚙️ Backend API | http://localhost:8000 |
| 📄 API Docs (Swagger) | http://localhost:8000/docs |
| ❤️ Health Check | http://localhost:8000/health |

---

## 🛠️ Setup 2: Run WITH Source Code (Development Mode)

Use this setup if you want to modify the application, tune the ML models, or contribute to the project's development.

### Step 1 — Clone and prepare the environment

Make sure you have cloned the SafeSurf repository and navigated into it. Then, copy the environment template:

```bash
cp server/.env.example server/.env
```

> 💡 The `.env` file is where you configure the API settings.  
> The defaults work out-of-the-box for local development — no edits needed to get started.

### Step 2 — Build and start all services

```bash
docker compose up --build
```

This will:
1. Build the **FastAPI backend** image (Python 3.11, Gunicorn + Uvicorn)
2. Build the **React frontend** image (Node 20 build → Nginx static serve)
3. Start both containers on an isolated Docker network

> ⏳ First build takes **3–6 minutes** (downloads base images + installs dependencies).  
> Subsequent builds are much faster thanks to Docker layer caching.

### Step 3 — Open in your browser

| Service | URL |
|---------|-----|
| 🌐 Frontend (React app) | http://localhost |
| ⚙️ Backend API | http://localhost:8000 |
| 📄 API Docs (Swagger) | http://localhost:8000/docs |
| ❤️ Health Check | http://localhost:8000/health |

---

## 📁 Project Structure (Docker-relevant files)

```text
Optimized_Phishing_website_detector/
├── docker-compose.yml          ← Orchestrates local development build
├── docker-compose.prod.yml     ← Orchestrates prebuilt images deployment
│
├── server/
│   ├── Dockerfile              ← FastAPI backend image
│   ├── .dockerignore           ← Files excluded from backend build
│   ├── .env.example            ← Template for your .env file  ← copy this!
│   ├── .env                    ← Your local config (git-ignored)
│   ├── requirements.txt        ← Python dependencies
│   └── models/                 ← ML model files (mounted read-only)
│
└── front-end/
    ├── Dockerfile              ← React + Nginx image
    ├── .dockerignore           ← Files excluded from frontend build
    └── nginx.conf              ← Nginx config (SPA routing + API proxy)
```

---

## 🛑 Common Commands

```bash
# Start in background (detached mode)
docker compose up --build -d

# View live logs
docker compose logs -f

# View logs for one service only
docker compose logs -f safesurf-server
docker compose logs -f safesurf-frontend

# Stop all services
docker compose down

# Stop and remove all data (full reset)
docker compose down -v

# Rebuild only one service (e.g. after changing backend code)
docker compose up --build safesurf-server
```

> **Using Prebuilt Images?** Just append `-f docker-compose.prod.yml` to the `docker compose` commands (e.g., `docker compose -f docker-compose.prod.yml down`).

---

## ⚙️ Environment Variables

All configuration is safely done through `server/.env` (Dev Mode) or the `environment:` block (Prebuilt Images Mode). Here are the key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment (`development` / `production`) |
| `DEBUG` | `false` | Enable debug logging |
| `API_HOST` | `0.0.0.0` | Host the API binds to (don't change for Docker) |
| `API_PORT` | `8000` | Port the API listens on |
| `MODEL_VERSION` | `clean_v1` | Which XGBoost model file to load |
| `ENSEMBLE_XGB_WEIGHT` | `0.65` | Weight of the XGBoost model in ensemble |
| `ENSEMBLE_NLP_WEIGHT` | `0.35` | Weight of the NLP/BoW model in ensemble |
| `PHISHING_THRESHOLD` | `0.45` | Probability above which a URL is flagged |
| `MAX_CONCURRENT` | `10` | Max simultaneous inference requests |
| `TIMEOUT_SECS` | `15.0` | Per-request timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG` / `INFO` / `WARNING`) |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins (lock down in production) |

---

## 🏗️ How It Works (Architecture)

```text
Browser
  │
  ▼
┌──────────────────────────────────┐
│  safesurf-frontend (Port 80)     │
│  Nginx serves React static files │
│                                  │
│  /api/* requests  ──────────────►│◄── Docker internal DNS
└──────────────────────────────────┘
                                   │
                                   ▼
              ┌────────────────────────────────────┐
              │  safesurf-server (Port 8000)        │
              │  FastAPI + Gunicorn + UvicornWorker  │
              │                                      │
              │  Ensemble ML Model (VotingClassifier)│
              │  ├── XGBoost (deep URL features)     │
              │  └── NLP / BoW (text features)       │
              └────────────────────────────────────┘
```

- The **frontend container** (Nginx) serves the React app directly to the browser.
- API calls from the browser go to `localhost/api/...`, which Nginx **proxies internally** to the backend container using Docker's built-in DNS (routing to `safesurf-server:8000`).
- The **backend container** strictly handles inference. It never directly exposes ML model files to the internet — the `models/` folder is rigidly mounted **read-only** in Dev Mode.

---

## 🔍 Troubleshooting

### ❌ `No such file or directory: ./server/.env` (Dev Mode)
You forgot Step 1. Run:
```bash
cp server/.env.example server/.env
```

### ❌ Port 80 or 8000 already in use
Another app is using that port. Either stop it, or change the exposed ports in your compose YAML file:
```yaml
ports:
  - "8080:80"   # change left side only (Host port:Container port)
```
Then access the app at http://localhost:8080.

### ❌ Frontend loads but API calls fail
Make sure both containers are running properly:
```bash
docker compose ps
```
Both `safesurf-server` and `safesurf-frontend` should show `running` (and preferably `healthy`). If one is crashing, inspect the logs directly: `docker compose logs -f`.

### ❌ Model not found / inference errors (Dev Mode)
The backend looks for model files in `server/models/`. Make sure the following files exist locally (likely generated by your training scripts):
- `server/models/phishing_deep_clean_v1.pkl` 
- `server/models/phishing.pkl`
- `server/models/vectorizer.pkl`

*(Note: Prebuilt images natively bundle these inside the container — you won't encounter this error in Setup 1!)*

### 🐢 Build is very slow on first run
That's entirely normal in Development Mode — Docker is fetching complex Machine Learning base images layer by layer (like Python + Scikit-Learn) and compiling heavy frontend assets. After the initial build, Docker layer caching kicks in, cutting subsequent rebuilds down to mere seconds.

---

## 🚢 Production Notes

For an authentic production deployment, execute these measures in your `docker-compose.prod.yml` or global environment variables:

1. **Lock down CORS** — change `ALLOWED_ORIGINS=*` to point exactly to your actual domain.
2. **Set `APP_ENV=production`** 
3. **Ensure HTTPS Setup** — Place the Nginx container proxy securely behind an edge router like [Traefik](https://traefik.io/) or [Caddy](https://caddyserver.com/) to automatically handle external TLS certificates.
4. **Change `VITE_API_BASE_URL`** (Dev Mode Build) — if building locally for production, specify your real remote backend URL so React is compiled appropriately.

---

> Built with ❤️ for the SafeSurf Phishing Detection project.
