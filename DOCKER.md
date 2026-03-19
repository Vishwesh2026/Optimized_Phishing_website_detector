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

## 🚀 Quick Start (3 steps)

### Step 1 — Copy the environment file

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

```
Optimized_Phishing_website_detector/
├── docker-compose.yml          ← Orchestrates both services
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

---

## ⚙️ Environment Variables

All configuration is done through `server/.env`. Here are the key variables:

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

```
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

- The **frontend container** (Nginx) serves the React app to the browser.
- API calls from the browser go to `localhost/api/...`, which Nginx **proxies internally** to the backend container using Docker's built-in DNS (`safesurf-server:8000`).
- The **backend container** never directly exposes ML model files to the internet — the `models/` folder is mounted **read-only**.

---

## 🔍 Troubleshooting

### ❌ `No such file or directory: ./server/.env`
You forgot Step 1. Run:
```bash
cp server/.env.example server/.env
```

### ❌ Port 80 or 8000 already in use
Another app is using that port. Either stop it, or change the ports in `docker-compose.yml`:
```yaml
ports:
  - "8080:80"   # change left side only
```
Then access the app at http://localhost:8080.

### ❌ Frontend loads but API calls fail
Make sure both containers are running:
```bash
docker compose ps
```
Both `safesurf-server` and `safesurf-frontend` should show `running (healthy)`.

### ❌ Model not found / inference errors
The backend looks for model files in `server/models/`. Make sure the following files exist:
- `server/models/phishing_deep_clean_v1.pkl`
- `server/models/phishing.pkl`
- `server/models/vectorizer.pkl`

### 🐢 Build is very slow on first run
That's normal — Docker is downloading base images and installing all dependencies. After the first build, subsequent builds use the **cache** and complete in ~30 seconds.

---

## 🚢 Production Notes

For a real production deployment, make these changes in `docker-compose.yml`:

1. **Lock down CORS** — change `ALLOWED_ORIGINS=*` to your actual domain
2. **Set `APP_ENV=production`** in your `.env`
3. **Use HTTPS** — put Nginx behind a reverse proxy like [Traefik](https://traefik.io/) or [Caddy](https://caddyserver.com/) for TLS
4. **Change `VITE_API_BASE_URL`** — update the build arg to your real public backend URL

---

> Built with ❤️ for the SafeSurf Phishing Detection project.
