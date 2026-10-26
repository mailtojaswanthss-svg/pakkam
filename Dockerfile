# Pakkam API and web UI. Two stages: uv builds the virtual environment, and a slim runtime
# image runs it as a non-root user. The search index, chunks and source list are not baked in:
# mount data/ (built on the host with the ingest and index commands) at /app/data.
#
#   docker compose up --build        (see compose.yaml)

ARG PYTHON_IMAGE=python:3.12-slim-trixie

# ---------- build: install dependencies, then the project ----------
FROM ghcr.io/astral-sh/uv:0.11.12 AS uv
FROM ${PYTHON_IMAGE} AS builder
COPY --from=uv /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app

# Dependencies first: this layer (PyTorch with CUDA, several GB) is rebuilt only when the
# lockfile changes, not on every code change.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project \
    --extra index --extra generate --extra gemini --extra api

# The project itself, installed in editable mode so the app finds web/ and data/ under /app.
COPY README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --extra index --extra generate --extra gemini --extra api

# ---------- runtime ----------
FROM ${PYTHON_IMAGE} AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/models
WORKDIR /app

RUN useradd --create-home --uid 10001 app \
    && mkdir -p /app/data /app/logs /app/models \
    && chown app:app /app/data /app/logs /app/models

# Code is owned by root and read-only for the app user; only data, logs and models are writable.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY web /app/web

USER app
EXPOSE 8000

# Startup loads two models (and downloads them, about 4.5 GB, on the first run).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10m --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"]

# One worker: the models sit on one GPU and requests are serialised anyway. Client addresses
# (used by the rate limit) come from X-Forwarded-For only for proxies listed in the
# FORWARDED_ALLOW_IPS environment variable (default 127.0.0.1).
CMD ["uvicorn", "schemebot.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

# ---------- Cloud Run: data and models baked in ----------
# Cloud Run has no host folder to mount, so this target copies the search index, the source
# list and the contacts into the image, and downloads both models at build time instead of
# on every cold start (the image is about 13 GB). Build it with `--target cloudrun`; the
# default target for `docker compose` and CI stays `runtime`. See deploy/cloudrun/README.md.
FROM builder AS models
ARG EMBEDDING_MODEL=BAAI/bge-m3
ARG RERANKER_MODEL=BAAI/bge-reranker-v2-m3
ENV HF_HOME=/models
# The ONNX exports in the bge-m3 repository are not used and add about 2 GB.
RUN /app/.venv/bin/python -c "import sys; from huggingface_hub import snapshot_download; \
[snapshot_download(m, ignore_patterns=['onnx/*', '*.onnx', 'imgs/*']) for m in sys.argv[1:]]" \
    "${EMBEDDING_MODEL}" "${RERANKER_MODEL}"

FROM runtime AS cloudrun
COPY --from=models --chown=app:app /models /app/models
# Only what the server reads: the index (Qdrant writes a lock file in it), sources, contacts.
COPY --chown=app:app data/index /app/data/index
COPY --chown=app:app data/sources.json data/contacts.json /app/data/
# Models load from the image, never from the network. Only Google's front end can reach a
# Cloud Run container, so trusting X-Forwarded-For from any address is safe here, and the
# rate limit then sees each visitor's address instead of the proxy's.
ENV HF_HUB_OFFLINE=1 \
    FORWARDED_ALLOW_IPS="*"
