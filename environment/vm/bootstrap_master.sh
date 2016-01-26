#!/bin/bash

docker kill rabbit-srv && docker rm rabbit-srv
docker kill rabbit-mng && docker rm rabbit-mng

docker run -d --hostname my-rabbit --name rabbit-srv rabbitmq:3
docker run -d --hostname my-rabbit --name rabbit-mng -p 8080:15672 rabbitmq:3-management
