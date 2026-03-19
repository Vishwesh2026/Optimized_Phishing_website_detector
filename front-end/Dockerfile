# ─────────────────────────────────────────────────────────────
# Dockerfile — SafeSurf Front-end (Vite + React + TypeScript)
# Node 20-alpine | Multi-stage: build → Nginx static serve
# ─────────────────────────────────────────────────────────────

# ── Stage 1: Build ────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests first for cache efficiency
COPY package.json package-lock.json ./

# Install all dependencies (including devDependencies needed for build)
# Uses frozen lockfile to ensure the exact same versions as local dev
RUN npm ci --frozen-lockfile

# Copy source and config files
COPY index.html            ./
COPY vite.config.ts        ./
COPY tsconfig.json         ./
COPY tsconfig.app.json     ./
COPY tsconfig.node.json    ./
COPY postcss.config.js     ./
COPY components.json       ./
COPY src/                  ./src/
COPY public/               ./public/

# Build production bundle
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build


# ── Stage 2: Serve with Nginx ─────────────────────────────────
FROM nginx:1.27-alpine AS production

# Remove default Nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy the built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom Nginx config for a single-page application:
#   • All unknown routes rewrite to index.html (React Router support)
#   • Proxies /api and /health to the backend container (safesurf-server)
#     — resolved via Docker internal DNS using service name
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
