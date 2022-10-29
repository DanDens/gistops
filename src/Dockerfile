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

# https://github.com/AGWA/git-crypt
# https://github.com/AGWA/git-crypt/blob/master/INSTALL.md
RUN DEBIAN_FRONTEND=noninteractive apt-get update 
RUN DEBIAN_FRONTEND=noninteractive && apt install -y git build-essential make libssl-dev
RUN git clone https://github.com/AGWA/git-crypt.git
RUN cd git-crypt && make && make install PREFIX=/usr/local

# ----------
FROM python:3.10.8-slim-bullseye
LABEL maintainer="DanDens <dandens@github.com>"

RUN apt-get update
# https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

RUN apt-get -y install git
# https://wiki.debianforum.de/GnuPG#Installation
RUN apt-get -y install gnupg
# Required for downstream scripts
RUN apt-get -y install jq curl wget
# pandoc requirements as stated in https://pandoc.org/installing.html
RUN apt-get -y install texlive-xetex librsvg2-bin

# Copy git-crypt from build
COPY --from=builder /usr/local/bin/git-crypt /usr/local/bin/git-crypt

# https://pandoc.org/installing.html
RUN wget --quiet https://github.com/jgm/pandoc/releases/download/2.19.2/pandoc-2.19.2-linux-amd64.tar.gz && \
    tar xvzf pandoc-2.19.2-linux-amd64.tar.gz --strip-components 1 -C /usr/local && \
    rm pandoc-2.19.2-linux-amd64.tar.gz
 
# Cleanup
RUN apt-get purge -y ruby
RUN apt-get remove sqlite3 -y
RUN apt-get clean

# Create USER
ARG USER=dandens
RUN adduser --disabled-password --gecos '' ${USER}

COPY --from=builder /build/dist /home/$USER/tmp
RUN chmod -R ugo+rwx /home/$USER/tmp

# Run as USER from here
USER ${USER}
WORKDIR /home/${USER}
ENV PATH="/home/${USER}/.local/bin:$PATH"

# Install gistops package
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 && python -m pip install --user /home/$USER/tmp/gistops-0.1.0.tar.gz 
RUN rm -rf /home/$USER/tmp

CMD [ "gistops" ]