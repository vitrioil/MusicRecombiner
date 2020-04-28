FROM tensorflow/tensorflow:1.15.2-gpu-py3

RUN apt upgrade
RUN apt update

COPY requirements.txt .

RUN pip install -r requirements.txt
