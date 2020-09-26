#!/bin/bash

echo "Loading environment variables..."
source .env

echo "Creating network..."
docker network create odp-net

echo "Creating data volume..."
docker volume create hydra-data

echo "Starting the Hydra DB container..."
docker run -d --name hydra-db --network odp-net --volume hydra-data:/var/lib/postgresql/data \
    -e PGDATA=/var/lib/postgresql/data \
    -e POSTGRES_DB=hydra_db \
    -e POSTGRES_USER=hydra_user \
    -e POSTGRES_PASSWORD="${HYDRA_DB_PASS}" \
    postgres:11

echo "Running SQL migrations..."
docker run -it --rm --network odp-net "${HYDRA_IMAGE}" migrate sql --yes \
    "postgres://hydra_user:${HYDRA_DB_PASS}@hydra-db:5432/hydra_db?sslmode=disable"

echo "Deleting the Hydra DB container..."
docker rm -f hydra-db

echo "Done."
