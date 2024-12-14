FROM phusion/baseimage:noble-1.0.0

RUN --mount=type=cache,target=/var/cache/apt \
apt update && apt install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    gcc

RUN python3.12 -m venv /venv

ENV PATH=/venv/bin:$PATH \
    VIRTUAL_ENV=/venv \
    PYTHONPATH=/app/fact_extractor

ADD ./fact_extractor/install/pre_install.sh /app/fact_extractor/install/pre_install.sh
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/root/.cache/pip \
/app/fact_extractor/install/pre_install.sh

ADD . /app
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/root/.cache/pip \
/app/fact_extractor/install.py


ENTRYPOINT ["/app/fact_extractor/docker_extraction.py"]
