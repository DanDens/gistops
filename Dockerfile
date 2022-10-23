FROM python:3.10.8-bullseye

WORKDIR /usr/src/app

COPY gistops ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]