FROM phusion/baseimage:noble-1.0.0

ARG USER=root
ARG DEBIAN_FRONTEND=noninteractive

RUN install_clean python3.12 python3.12-dev python3.12-venv gcc

WORKDIR /opt/app

RUN python3 -m venv venv

COPY fact_extractor/install/pre_install.sh ./pre_install.sh

RUN . venv/bin/activate && ./pre_install.sh

COPY . /opt/app

WORKDIR /opt/app/fact_extractor

RUN . ../venv/bin/activate && ../venv/bin/python install.py

ENV PATH=/opt/app/venv/bin:$PATH

ENTRYPOINT ["./docker_extraction.py"]
