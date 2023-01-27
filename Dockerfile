FROM phusion/baseimage:jammy-1.0.1

WORKDIR /opt/app

COPY . /opt/app

WORKDIR /opt/app/fact_extractor

ARG USER=root
ENV DEBIAN_FRONTEND=noninteractive

RUN install_clean python3.11 python3.11-dev python3.11-venv gcc

RUN python3.11 -m venv venv

RUN . venv/bin/activate && install/pre_install.sh

RUN . venv/bin/activate && venv/bin/python3.11 install.py

ENTRYPOINT ["./docker_extraction.py"]
