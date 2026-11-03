# Pakkam on a free Hugging Face Space (CPU, 16 GB). push.py copies this file to the Space's
# root together with the code, the web UI, the search index and the official PDFs; the Space
# builds it. Differences from the main Dockerfile: Spaces run the container as uid 1000 on
# port 7860, there is no GPU (so PyTorch is the CPU build, not the CUDA build in the lockfile),
# and both models are downloaded while building, so a restart does not fetch 4.5 GB again.
FROM ghcr.io/astral-sh/uv:0.11.12@sha256:3a59a3cdd5f7c217faa36e32dbc7fddbb0412889c2a0a5229f6d790e5a019dd7 AS uv
FROM python:3.12-slim-trixie

COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/models \
    FORWARDED_ALLOW_IPS="*"

# ffmpeg converts voice uploads to 16 kHz mono WAV (schemebot/voice/audio.py).
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 1000 user
WORKDIR /app

# Locked dependencies, minus PyTorch and the CUDA libraries; then the CPU build of the same
# PyTorch version. This layer changes only when the lockfile does.
COPY pyproject.toml uv.lock ./
RUN uv venv /app/.venv \
    && uv export --frozen --no-dev --no-emit-project --no-hashes \
       --extra ingest --extra index --extra generate --extra gemini --extra api \
       --no-emit-package torch -o /tmp/requirements.txt \
    && grep -vE '^(nvidia-|cuda-|triton)' /tmp/requirements.txt > /tmp/requirements-cpu.txt \
    && TORCH=$(grep -A1 '^name = "torch"$' uv.lock | sed -n 's/^version = "\([0-9.]*\)+cu.*/\1/p' | head -1) \
    && test -n "$TORCH" \
    && uv pip install "torch==${TORCH}" --index-url https://download.pytorch.org/whl/cpu \
    && uv pip install -r /tmp/requirements-cpu.txt \
    && rm /tmp/requirements*.txt

# Both models, baked in. Revisions come from SCHEMEBOT_*_REVISION in the laptop's .env
# (push.py writes them here); empty means the latest version, as on the laptop.
ARG EMBEDDING_MODEL=BAAI/bge-m3
ARG RERANKER_MODEL=BAAI/bge-reranker-v2-m3
ARG EMBEDDING_REVISION=
ARG RERANKER_REVISION=
RUN python -c "import sys; from huggingface_hub import snapshot_download; \
[snapshot_download(m, revision=r or None, ignore_patterns=['onnx/*', '*.onnx', 'imgs/*']) \
 for m, r in zip(sys.argv[1::2], sys.argv[2::2])]" \
    "${EMBEDDING_MODEL}" "${EMBEDDING_REVISION}" "${RERANKER_MODEL}" "${RERANKER_REVISION}"

# The project, editable, so the app finds web/ and data/ under /app.
COPY README.md ./
COPY src ./src
RUN uv pip install --no-deps -e .

COPY web ./web
# data/ must be writable: Qdrant's lock file, the answer cache and the daily call counter.
COPY --chown=user:user data ./data
RUN mkdir -p /app/logs && chown -R user:user /app/logs /app/models

USER user
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=10m --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/health', timeout=4)"]
# Behind the Space's proxy; FORWARDED_ALLOW_IPS lets the rate limit see visitors' addresses.
CMD ["uvicorn", "schemebot.api.main:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers"]
