FROM tensorflow/tensorflow:1.15.0-gpu-py3
RUN mkdir /app
WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive

COPY requirements.txt .

RUN apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt update

RUN apt install wget -y
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update
RUN apt-get install postgresql -y


RUN pip install --upgrade pip
RUN apt install libpq-dev -y
RUN pip install -r requirements.txt
RUN apt install libsndfile1 -y
COPY separator/ separator/
COPY app.py .

RUN apt install ffmpeg -y

USER postgres

RUN /etc/init.d/postgresql start && createuser root && createdb root\
    && psql --command "ALTER USER root createdb" && createdb -O root music_recombiner\
    && /etc/init.d/postgresql stop

USER root

