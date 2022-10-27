FROM python:3.7.15-slim-bullseye

RUN apt-get update
# https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
RUN apt-get -y install git
# https://wiki.debianforum.de/GnuPG#Installation
RUN apt-get -y install gnupg
# https://git-secret.io/installation
RUN apt-get -y install wget
# pandoc requirements as stated in https://pandoc.org/installing.html
RUN apt-get -y install texlive-xetex

# https://git-secret.io/installation
RUN sh -c "echo 'deb https://gitsecret.jfrog.io/artifactory/git-secret-deb git-secret main' >> /etc/apt/sources.list"
RUN wget -qO - 'https://gitsecret.jfrog.io/artifactory/api/gpg/key/public' | apt-key add -
RUN apt-get update && apt-get install -y git-secret

# https://pandoc.org/installing.html
RUN wget --quiet https://github.com/jgm/pandoc/releases/download/2.19.2/pandoc-2.19.2-linux-amd64.tar.gz && \
    tar xvzf pandoc-2.19.2-linux-amd64.tar.gz --strip-components 1 -C /usr/local && \
    rm pandoc-2.19.2-linux-amd64.tar.gz

# Install gistops application
WORKDIR /usr/src/app

COPY ./requirements.txt .
COPY ./src .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/usr/src/app/main.py" ]