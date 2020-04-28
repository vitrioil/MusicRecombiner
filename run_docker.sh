#!/bin/bash

username=$(whoami)
read -p "Docker image name:" image_name
echo $username
sudo docker run --gpus all -it --rm -v /home/$username:/home/$username --name spleeter_dev $image_name
