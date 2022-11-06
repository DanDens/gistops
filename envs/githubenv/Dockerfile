FROM ghcr.io/dandens/gistops-base:latest
LABEL maintainer="DanDens <dandens@github.com>"
ARG USER=dandens

USER root
WORKDIR /root 

RUN apt-get update

# pandoc requirements as stated in https://pandoc.org/installing.html
RUN apt-get -y install wget texlive-xetex librsvg2-bin

# https://pandoc.org/installing.html
RUN wget --quiet https://github.com/jgm/pandoc/releases/download/2.19.2/pandoc-2.19.2-linux-amd64.tar.gz && \
    tar xvzf pandoc-2.19.2-linux-amd64.tar.gz --strip-components 1 -C /usr/local && \
    rm pandoc-2.19.2-linux-amd64.tar.gz
 
# Cleanup
RUN apt-get clean

CMD ["/bin/bash"]
