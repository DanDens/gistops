# ----------
FROM python:3.10.8-bullseye as builder
LABEL maintainer="DanDens <dandens@github.com>"

# Install gistops application
WORKDIR /build

COPY . .
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 && \
    pip install --no-cache-dir -r requirements.txt
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 && \
    python3 -m pip install --upgrade build 

RUN python3 -m build

# ----------
ARG GISTOPS_BASE_IMAGE_TAG
FROM ghcr.io/dandens/gistops-base:$GISTOPS_BASE_IMAGE_TAG
LABEL maintainer="DanDens <dandens@github.com>"

USER root
WORKDIR /root

COPY --from=builder /build/dist /home/$USER/tmp
RUN chmod -R ugo+rwx /home/$USER/tmp

# Run as USER from here
ARG USER=dandens
USER ${USER}
WORKDIR /home/${USER}

# Install gistops package
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 && python -m pip install --user /home/$USER/tmp/gistops-0.1.0.tar.gz 
RUN rm -rf /home/$USER/tmp

CMD [ "gistops" ]