#/bin/bash

docker-compose down --rmi all
docker-compose up --build --force-recreate --no-deps
