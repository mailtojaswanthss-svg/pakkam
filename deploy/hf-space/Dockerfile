# Pakkam on a free Hugging Face Space (CPU, 16 GB). push.py copies this file to the Space's
# root together with the code, the web UI and the search index; the Space builds it.
# Differences from the main Dockerfile: Spaces run the container as uid 1000, there is no GPU
# (the CUDA wheels from the lockfile run on the CPU), and the models download from the Hub
# at first start into the container's writable cache.
FROM ghcr.io/astral-sh/uv:0.11.12 AS uv
FROM python:3.12-slim-trixie

COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/models \
    FORWARDED_ALLOW_IPS="*"

# ffmpeg converts voice uploads to 16 kHz mono WAV (schemebot/voice/audio.py).
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 1000 user
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project \
    --extra index --extra generate --extra gemini --extra api
COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --extra index --extra generate --extra gemini --extra api

COPY web ./web
COPY --chown=user:user data ./data
RUN mkdir -p /app/logs /app/models && chown user:user /app/logs /app/models

USER user
EXPOSE 7860
# Behind the Space's proxy; FORWARDED_ALLOW_IPS lets the rate limit see visitors' addresses.
CMD ["uvicorn", "schemebot.api.main:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers"]
