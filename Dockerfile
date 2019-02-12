FROM phusion/baseimage:0.11

WORKDIR /opt/app

COPY . /opt/app

WORKDIR /opt/app/fact_extractor

ARG USER=root

RUN install/pre_install.sh

RUN ./install.py

RUN SUDO_FORCE_REMOVE=yes apt-get remove -y sudo

ENTRYPOINT ["./docker_extraction.py"]
