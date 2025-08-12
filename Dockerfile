###############################
# Multi-stage Build (Python 3.10 due to TF 2.13 compatibility)
###############################

FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for building scientific libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first (layer caching)
COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

# Create virtual env & install only runtime deps (dev optional)
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip setuptools wheel \
    && /venv/bin/pip install -r requirements.txt

# Copy source (minimal set required for runtime)
COPY pyproject.toml setup.py ./
COPY src ./src
COPY config ./config

###############################
# Runtime Image
###############################
FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

WORKDIR /app

# Runtime packages (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /venv /venv

# Copy application source
COPY --from=builder /app/src ./src
COPY --from=builder /app/config ./config
COPY pyproject.toml setup.py ./

# Create non-root user
RUN useradd -ms /bin/bash appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Start API server (FastAPI public server module)
CMD ["uvicorn", "seismic_classifier.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
