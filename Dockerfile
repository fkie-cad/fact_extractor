FROM phusion/baseimage:noble-1.0.0

ARG DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt \
    apt update && apt install -y \
    python3.12 \
    python3.12-dev \
    git \
    gcc \
    curl \
    sudo \
    wget

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

ADD . /app
WORKDIR /app

RUN uv venv --python python3.12
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV=/app/.venv \
    PYTHONPATH=/app/fact_extractor

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

RUN --mount=type=cache,target=/var/cache/apt \
    uv run fact-extractor install -d

ENTRYPOINT ["/app/fact_extractor/docker_extraction.py"]
