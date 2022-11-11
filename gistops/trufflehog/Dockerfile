# ----------
FROM ghcr.io/dandens/gistops-base:latest as builder
LABEL maintainer="DanDens <dandens@github.com>"

USER root
WORKDIR /root

# Clone git-secrets repository
WORKDIR /build
RUN curl -L -s https://github.com/trufflesecurity/trufflehog/releases/download/v3.16.4/trufflehog_3.16.4_linux_amd64.tar.gz --output trufflehog_3.16.4_linux_amd64.tar.gz
RUN tar -xzf ./trufflehog_3.16.4_linux_amd64.tar.gz 

# ----------
FROM ghcr.io/dandens/gistops-base:latest
LABEL maintainer="DanDens <dandens@github.com>"
ARG USER=dandens

USER root
WORKDIR /root

# Copy executable
COPY --from=builder /build/trufflehog /usr/local/bin/trufflehog
RUN chmod -R ugo+x /usr/local/bin/trufflehog


# Run as USER from here
USER ${USER}
WORKDIR /home/${USER}

# Make function available
ENV ENV /home/${USER}/.profile
RUN echo 'gistops () { trufflehog git "file://$1" --no-update --only-verified --json --fail; }' >> /home/${USER}/.profile 

CMD [ "bash","-c", "gistops", "." ]
