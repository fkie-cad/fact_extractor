FROM phusion/baseimage:jammy-1.0.3

RUN --mount=type=cache,target=/var/cache/apt \
apt update && apt install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    gcc

RUN python3.11 -m venv /venv
ENV PATH=/venv/bin:$PATH \
    VIRTUAL_ENV=/venv \
    PYTHONPATH=/app/

ADD ./fact_extractor/install/pre_install.sh /app/fact_extractor/install/pre_install.sh
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/root/.cache/pip \
/app/fact_extractor/install/pre_install.sh

ADD . /app
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/root/.cache/pip \
/app/install.py


ENTRYPOINT ["/app/fact_extractor/docker_extraction.py"]
