FROM python:3.7.15-slim-bullseye

RUN apt-get update
# https://pandoc.org/installing.html
RUN apt-get -y install pandoc texlive-latex-recommended librsvg2-bin
# https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
RUN apt-get -y install git
# https://wiki.debianforum.de/GnuPG#Installation
RUN apt-get -y install gnupg
# https://git-secret.io/installation
RUN apt-get -y install wget
RUN sh -c "echo 'deb https://gitsecret.jfrog.io/artifactory/git-secret-deb git-secret main' >> /etc/apt/sources.list"
RUN wget -qO - 'https://gitsecret.jfrog.io/artifactory/api/gpg/key/public' | apt-key add -
RUN apt-get update && apt-get install -y git-secret

# Install gistops application
WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]