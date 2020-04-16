FROM tensorflow/tensorflow:1.15.2-gpu-py3

RUN apt upgrade
RUN apt update

RUN apt install spleeter
