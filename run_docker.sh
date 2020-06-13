#!/bin/bash

read -p "Docker image name (default=spleeter1.1:latest):" image_name
image_name=${image_name:-'spleeter1.1:latest'}
sudo docker run -p 5000:5000 --rm -it --name spleeter_music spleeter1.1:latest bash
