FROM phusion/baseimage:noble-1.0.0

ARG DEBIAN_FRONTEND=noninteractive
ARG TARGETARCH

RUN rm -f /etc/apt/apt.conf.d/docker-clean

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache-$TARGETARCH \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib-$TARGETARCH \
    apt update && apt install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    gcc

RUN python3 -m venv venv
ENV PATH=/venv/bin:$PATH \
    VIRTUAL_ENV=/venv \
    PYTHONPATH=/app/fact_extractor

ADD ./fact_extractor/install/pre_install.sh /app/fact_extractor/install/pre_install.sh
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache-$TARGETARCH \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib-$TARGETARCH \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked,id=pip-$TARGETARCH \
    /app/fact_extractor/install/pre_install.sh

ADD . /app
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache-$TARGETARCH \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib-$TARGETARCH \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked,id=pip-$TARGETARCH \
    /app/fact_extractor/install.py

ENTRYPOINT ["/app/fact_extractor/docker_extraction.py"]
