# =============================================================================
# MPX - Next.js (frontend) + FastAPI (backend) in ONE container
#   Public : 3000  (Next.js)
#   Internal: 8000 (FastAPI, reached by Next.js rewrites at 127.0.0.1:8000)
# =============================================================================

# ---------- Stage 1: build the Next.js frontend ------------------------------
FROM node:20 AS fe-builder

WORKDIR /usr/src/app
ENV PATH=/usr/src/app/node_modules/.bin:$PATH \
    NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json* ./
RUN npm config set registry https://nexus.hedej.lge.com/repository/npm-group/ --global && \
    npm install -f

ARG BUILD_ARGS
RUN if [ -n "$BUILD_ARGS" ]; then \
      echo "${BUILD_ARGS}" | base64 -d > .env; \
    else \
      touch .env; \
    fi

COPY . .
RUN npm run build && \
    npm prune --omit=dev -f


# ---------- Stage 2: runtime (Python + Node) ---------------------------------
FROM python:3.10.19

# OS security patches
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Node runtime + npm/npx copied from the official node:20 image
COPY --from=fe-builder /usr/local/bin/node /usr/local/bin/node
COPY --from=fe-builder /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx && \
node -v && npm -v

WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    FRONTEND_PORT=3000 \
    BACKEND_PORT=8000

# Backend dependencies (cached layer)
RUN pip config set global.index-url https://nexus.hedej.lge.com/repository/pypi-group/simple --global
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Built frontend + production node_modules + .env from stage 1
COPY --from=fe-builder /usr/src/app /usr/src/app

# Backend source (overwrites nothing important; keeps code current)
COPY backend ./backend

# Process launcher (keeps the platform's "nginx" shim convention)
COPY settings/start-all.sh /usr/local/bin/start-all.sh
RUN chmod +x /usr/local/bin/start-all.sh && \
    mkdir -p /usr/share/nginx/html && \
    printf '#!/bin/sh\nexec /usr/local/bin/start-all.sh\n' > /usr/local/bin/nginx && \
    chmod +x /usr/local/bin/nginx

COPY settings/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000
ENTRYPOINT ["/entrypoint.sh"]
