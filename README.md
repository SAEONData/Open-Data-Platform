# Open Data Platform

This project provides a unified environment for the deployment of core and metadata
services of the SAEON Open Data Platform.

ODP core services include:
- [ODP Identity](https://github.com/SAEONData/ODP-Identity)
- [ODP Admin](https://github.com/SAEONData/ODP-Admin)
- [ODP Admin API](https://github.com/SAEONData/ODP-AccountsAPI)
- [ORY Hydra](https://www.ory.sh/docs/hydra/)

ODP metadata services include:
- [ODP API](https://github.com/SAEONData/ODP-API)
- CKAN-based metadata management server
- PyCSW metadata harvest endpoint
- Elasticsearch metadata discovery catalogue

## Configuration

Create a `.env` file in the `deploy` subdirectory on the target machine,
containing the following environment variables as applicable:

### General configuration
- **`SERVER_ENV`**: deployment environment: `development`|`testing`|`staging`|`production`
- **`ODP_PUBLIC_URL`**: URL of the ODP web-facing server
- **`ODP_ADMIN_URL`**: URL of the ODP admin server

### Core services configuration
- **`ACCOUNTS_DB_HOST`**: ODP accounts database hostname / IP address
- **`ACCOUNTS_DB_PASSWORD`**: ODP accounts database password
- **`MAIL_SERVER`**: IP / hostname of mail server used for sending email verifications / password resets
- **`IDENTITY_FLASK_KEY`**: Flask secret key for the identity service
- **`IDENTITY_OAUTH2_SECRET`**: OAuth2 client secret for the identity service UI
- **`ADMIN_FLASK_KEY`**: Flask secret key for the admin service
- **`ADMIN_OAUTH2_SECRET`**: OAuth2 client secret for the admin service UI
- **`HYDRA_IMAGE`**: the Hydra Docker image, e.g. `oryd/hydra:v1.4.10`
- **`HYDRA_DB_HOST`**: Hydra database hostname / IP address
- **`HYDRA_DB_PASSWORD`**: Hydra database password
- **`HYDRA_SYSTEM_SECRET`**: secret for encrypting the Hydra database; note that key rotation is not supported

### Metadata services configuration
- **`CKAN_URL`**: URL of the CKAN server
- **`CKAN_DB_HOST`**: CKAN database hostname / IP address
- **`CKAN_DB_PASSWORD`**: CKAN database password
- **`CKAN_OAUTH2_SECRET`**: OAuth2 client secret for the CKAN UI

## Core services installation / upgrade

### Hydra database migrations

_Note: Do this before starting the Hydra container._

    source .env
    docker run -it --rm "${HYDRA_IMAGE}" migrate sql --yes "postgres://hydra_user:${HYDRA_DB_PASSWORD}@${HYDRA_DB_HOST}:5432/hydra_db?sslmode=disable"

### Docker containers

    docker-compose -f core-services down
    docker-compose -f core-services build --no-cache
    docker-compose -f core-services up -d

### Accounts database migrations

_Note: Do this after starting the ODP Admin container._

    docker exec odp-admin flask initdb

## Metadata services installation / upgrade

### System configuration

The following command must be run on the host in order for the elasticsearch container to work:

    sudo sysctl -w vm.max_map_count=262144

To make the change permanent, edit the file `/etc/sysctl.conf` and add the following line:

    vm.max_map_count=262144

### Docker containers

    docker-compose -f metadata-services down
    docker-compose -f metadata-services build --no-cache
    docker-compose -f metadata-services up -d

## Local development

A Docker Compose configuration for setting up a local development environment is provided in the `develop` subdirectory.

To use this, copy `.env.example` to `.env` and update values if necessary (the defaults should work fine for a standard setup).

Next, initialise the Hydra DB:

    ./setup-hydra-db.sh

Then start the Docker containers:

    docker-compose up -d

Finally, create the requisite OAuth2 clients in Hydra:

    ./setup-hydra-clients.sh

### Upgrading dependencies

To upgrade dependencies and re-generate the `requirements.txt` file for an ODP service or API,
carry out the following steps:

1. Activate the virtual environment of the service / API.
1. Upgrade Python libraries as necessary.
1. Ensure that unit tests for the service / API and its dependencies all pass.
1. Run the following command:
`pip freeze | sed -E '/^(-e\s|pkg-resources==)/d' > requirements.txt`
