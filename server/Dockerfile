# ─────────────────────────────────────────────────────────────
# Dockerfile — SafeSurf Phishing Detection API (FastAPI)
# Python 3.11-slim | Gunicorn + Uvicorn workers
# ─────────────────────────────────────────────────────────────

# ── Stage 1: Build / dependency resolution ────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps required by some Python packages (e.g. scipy, lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer cache
COPY requirements.txt .

# Install into a prefix so we can copy cleanly into the final stage
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: Production image ─────────────────────────────────
FROM python:3.11-slim AS production

# Security: run as non-root
RUN addgroup --system safesurf && adduser --system --ingroup safesurf safesurf

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source (exclude heavy dirs via .dockerignore)
COPY app/          ./app/
COPY models/       ./models/
COPY templates/    ./templates/
COPY experiments/  ./experiments/

# Copy example env — real secrets should be mounted or passed as env vars
COPY .env.example .env.example

# Expose the API port (default 8000, overridable via API_PORT env var)
EXPOSE 8000

# Switch to non-root user
USER safesurf

# ── Entrypoint ────────────────────────────────────────────────
# Gunicorn with UvicornWorker — suitable for production.
# Workers = 2*(CPU cores) + 1 is a common guideline; using 2 here
# as a safe default for containerised deployments.
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
