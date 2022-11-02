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
 
# Some additional packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update 
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  apt-utils \
  software-properties-common \
  unzip \
  apt-transport-https \
  ca-certificates \
  nano \
  dirmngr 

# Required to install python3.7 to ensure backward compatibility
RUN DEBIAN_FRONTEND=noninteractive && apt install -y build-essential libncursesw5-dev libssl-dev \
  libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev  

# Install docker and make dandens part of docker group
# Remember to mount docker.sock
# e.g. docker run -v /var/run/docker.sock:/var/run/docker.sock -dit ghcr.io/dandens/gistops-devenv:latest
RUN curl -sSL https://get.docker.com/ | sh
RUN usermod -aG docker ${USER}

# Make "dandens" a sudoer
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y sudo 

RUN adduser ${USER} sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Cleanup
RUN apt-get clean

# Run as USER when logging in, happy sudoing!
USER ${USER}
WORKDIR /home/${USER}
ENV PATH=$PATH:/home/${USER}/.local/bin

# Add necessary tools to build python packages
RUN python3 -m pip install --user --upgrade pip 
RUN python3 -m pip install --user --upgrade build 

# Setup some absolutely required git alias and configs
COPY ./setmeup-git-alias-and-config.sh /home/${USER}/setmeup-git-alias-and-config.sh
RUN sudo chmod ugo+xrw /home/${USER}/setmeup-git-alias-and-config.sh
RUN /home/${USER}/setmeup-git-alias-and-config.sh

# Install python3.7 to ensure backward compatibility
COPY ./setmeup-python37.sh /home/${USER}/setmeup-python37.sh
RUN sudo chmod ugo+xrw /home/${USER}/setmeup-python37.sh
RUN /home/${USER}/setmeup-python37.sh

CMD ["/bin/bash"]
