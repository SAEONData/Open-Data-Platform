# SAEON Open Data Platform

## Services
This project provides the codebase for the following services:

### ODP Public API
A public API providing a stable interface to ODP back-end systems, with automatic,
interactive API documentation using the OpenAPI standard.
Built on [FastAPI](https://fastapi.tiangolo.com/).

- [entry point](odp/api/public.py)

### ODP Admin API
Back-office API providing administrative and security-related functions,
built on [FastAPI](https://fastapi.tiangolo.com/).

- [entry point](odp/api/admin.py)

### ODP Admin UI

### ODP Identity Service

## Dependencies

## Deployment
This project provides a unified environment for the deployment of core framework
services and metadata services of the SAEON Open Data Platform.

ODP core framework services include:
- [ODP Identity Service](odp/identity)
- [ODP Admin Interface](odp/admin)
- [ODP Admin API](odp/api/admin.py)
- [ODP Public API](odp/api/public.py)
- ORY Hydra OAuth2 & OpenID Connect server

ODP metadata services include:
- CKAN-based metadata management server
- PyCSW metadata harvest endpoint
- Elasticsearch metadata discovery catalogue

### Configuration
Create a `.env` file in the `deploy` subdirectory on the target machine,
containing the following environment variables as applicable:

#### General configuration
Set these options for all deployments:

- **`SERVER_ENV`**: deployment environment: `development`|`testing`|`staging`|`production`
- **`ODP_PUBLIC_URL`**: URL of the ODP web-facing server
- **`ODP_ADMIN_URL`**: URL of the ODP admin server
- **`CORS_ORIGINS`**: JSON-encoded list of allowed CORS origins

#### Core services configuration
Set these options if deploying core framework services:

- **`ACCOUNTS_DB_HOST`**: ODP accounts database hostname / IP address
- **`ACCOUNTS_DB_PASSWORD`**: ODP accounts database password
- **`MAIL_SERVER`**: IP / hostname of mail server used for sending email verifications / password resets
- **`IDENTITY_FLASK_KEY`**: Flask secret key for the identity service
- **`ADMIN_FLASK_KEY`**: Flask secret key for the admin service
- **`ADMIN_OAUTH2_SECRET`**: OAuth2 client secret for the admin service UI
- **`HYDRA_IMAGE`**: the Hydra Docker image, e.g. `oryd/hydra:v1.4.10`
- **`HYDRA_DB_HOST`**: Hydra database hostname / IP address
- **`HYDRA_DB_PASSWORD`**: Hydra database password
- **`HYDRA_SYSTEM_SECRET`**: secret for encrypting the Hydra database; note that key rotation is not supported

#### Metadata services configuration
Set these options if deploying metadata services:

- **`CKAN_URL`**: URL of the CKAN server
- **`CKAN_DB_HOST`**: CKAN database hostname / IP address
- **`CKAN_DB_PASSWORD`**: CKAN database password
- **`CKAN_OAUTH2_SECRET`**: OAuth2 client secret for the CKAN UI

### Core services installation / upgrade
_Note: The following instructions assume that the ODP and Hydra databases already exist
(though their schemas may be empty)._

#### ODP accounts DB initialization & migrations
Create a Python 3.8 virtual environment in the project root directory on the target machine,
activate the environment and `pip install -e` the project (no extras required). Switch to the
`migrate` subdirectory and create a `.env` file containing an appropriately set `DATABASE_URL`
environment variable. Then run:

    python -m initdb
    alembic upgrade head

#### Hydra DB initialization & migrations
_Note: Do this before starting the Hydra container._

    source .env
    docker run -it --rm "${HYDRA_IMAGE}" migrate sql --yes "postgres://hydra_user:${HYDRA_DB_PASSWORD}@${HYDRA_DB_HOST}:5432/hydra_db?sslmode=disable"

#### Docker containers

    docker-compose -f core-services build --no-cache
    docker-compose -f core-services up -d

### Metadata services installation / upgrade

#### System configuration
The following command must be run on the host in order for the elasticsearch container to work:

    sudo sysctl -w vm.max_map_count=262144

To make the change permanent, edit the file `/etc/sysctl.conf` and add the following line:

    vm.max_map_count=262144

#### Docker containers

    docker-compose -f metadata-services build --no-cache
    docker-compose -f metadata-services up -d
