#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
# cd /coba/www/Portofolio-E-Commerce-Backend
# git pull

source ~/.profile
echo "$DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin
sudo docker stop trello-fe
sudo docker rm trello-fe
sudo docker rmi alulfazlur/trello-fe:latest
sudo docker run -d --name trello-fe -p 9000:9000 alulfazlur/trello-fe:latest
