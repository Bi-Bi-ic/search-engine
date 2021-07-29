#!/bin/sh
cd "$(dirname "$0")"
#disable database local for using same port
sudo systemctl stop postgresql

#Get Environment Variables
export $(cat .env_example)

#Deploy service
docker-compose up --force-recreate --build -d
# for removing old image
docker image prune -f

# This run for mac
# env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install psycopg2
