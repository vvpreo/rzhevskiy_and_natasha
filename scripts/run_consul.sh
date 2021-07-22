#!/bin/bash

docker-compose -f compose-consul.yml up -d
docker ps | grep consul
echo "Consul UI http://172.20.0.2:8500"