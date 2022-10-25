FROM ubuntu:20.04

LABEL maintainer="DanDens <dandens@github.com>"

RUN DEBIAN_FRONTEND=noninteractive apt-get update 
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  sudo \
  apt-utils \
  software-properties-common \
  unzip \
  curl \
  apt-transport-https \
  ca-certificates \
  dirmngr \
  wget \
  gpg \
  jq \
  git-all

# Add USER and make USER a sudoer
ARG USER=ubuntu
RUN adduser --disabled-password --gecos '' ${USER}
RUN adduser ${USER} sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Copy script as ROOT to be able to change modificators
COPY ./setmeup-git-alias-and-config.sh /home/${USER}/setmeup-git-alias-and-config.sh
RUN chmod ugo+xrw /home/${USER}/setmeup-git-alias-and-config.sh
RUN /home/${USER}/setmeup-git-alias-and-config.sh

# Copy script as ROOT to be able to change modificators
COPY ./setmeup-python3.sh /home/${USER}/setmeup-python3.sh
RUN chmod ugo+xrw /home/${USER}/setmeup-python3.sh
RUN /home/${USER}/setmeup-python3.sh

# Run as USER from hereon
USER ${USER}
WORKDIR /home/${USER}

ENV PATH=$PATH:/home/${USER}/.local/bin

CMD ["/bin/bash"]
