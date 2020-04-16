#!/bin/bash

sudo docker run --gpus all -it --rm -v /home/vitrioil:/home/vitrioil --name spleeter_dev tensorflow/tensorflow:1.15.2-gpu-py3
