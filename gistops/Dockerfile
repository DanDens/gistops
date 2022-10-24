FROM python:3.10.8-slim-bullseye

RUN apt-get update
RUN apt-get -y install pandoc texlive-latex-recommended librsvg2-bin
RUN apt-get -y install git
RUN apt-get -y install gnupg

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]