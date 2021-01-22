FROM ubuntu:20.04
ENTRYPOINT []
RUN apt-get update && apt-get install -y python3 python3-pip && python3 -m pip install --no-cache --upgrade pip
ADD ./requirements.txt /app/

RUN cd /app && pip install -r requirements.txt

#ENV DEBIAN_FRONTEND noninteractive
#RUN apt install wget -y && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
#RUN apt-get update -y && apt-get install -y google-chrome-stable





