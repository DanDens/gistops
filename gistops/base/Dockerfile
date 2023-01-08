# ----------
FROM python:3.10.9-bullseye as builder
LABEL maintainer="DanDens <dandens@github.com>"

WORKDIR /build

# https://github.com/AGWA/git-crypt
# https://github.com/AGWA/git-crypt/blob/master/INSTALL.md
RUN DEBIAN_FRONTEND=noninteractive apt-get update 
RUN DEBIAN_FRONTEND=noninteractive && apt install -y git build-essential make libssl-dev
RUN git clone https://github.com/AGWA/git-crypt.git
RUN cd git-crypt && make && make install PREFIX=/usr/local

# ----------
FROM python:3.10.9-slim-bullseye
LABEL maintainer="DanDens <dandens@github.com>"

RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 && \
    python3 -m pip install --upgrade pip 

RUN apt-get update
# Required for trusted ca's
RUN apt-get -y install ca-certificates
# https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
RUN apt-get -y install git
# https://wiki.debianforum.de/GnuPG#Installation
RUN apt-get -y install gnupg
# Cleanup cache
RUN apt-get clean

# Copy git-crypt from build
COPY --from=builder /usr/local/bin/git-crypt /usr/local/bin/git-crypt

# Create USER
ARG USER=dandens
RUN adduser --disabled-password --gecos '' ${USER}

# Ensure system trusted ca is available to python
ENV SSL_CERT_FILE /etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

# Run as USER from here
USER ${USER}
WORKDIR /home/${USER}
ENV PATH="/home/${USER}/.local/bin:$PATH"
