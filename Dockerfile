FROM ubuntu:18.04

USER root
WORKDIR /app

COPY requirements.txt .

RUN apt-get update -qq -y \
    && apt-get install -qq -y python3 python3-dev python3-pip ffmpeg \
    && apt install -qq -y curl unzip
    
RUN curl https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip --output ngrok.zip \
    && unzip ngrok.zip ngrok && rm ngrok.zip
    
RUN pip3 install -r requirements.txt 
 
COPY . .

CMD /app/ngrok http 5000 > /dev/null & sleep 1 && python3 app.py 