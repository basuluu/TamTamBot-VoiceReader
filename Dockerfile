FROM ubuntu:18.04

USER root
WORKDIR /app

COPY requirements.txt .

RUN apt-get update -qq -y \
    && apt-get install -y python3 python3-dev python3-pip ffmpeg

RUN pip3 install -r requirements.txt 

COPY . .

CMD python3 app.py