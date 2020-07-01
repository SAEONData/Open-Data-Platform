# SAEON Open Data Platform

## Deployment

This project provides a unified environment for the deployment of core framework
services and metadata services of the SAEON Open Data Platform.

ODP core framework services include:
- [ODP Identity Service](odp/identity)
- [ODP Admin Interface](odp/admin)
- [ODP Admin API](odp/api/admin)
- [ODP Public API](odp/api/public)
- ORY Hydra OAuth2 & OpenID Connect server

ODP metadata services include:
- CKAN-based metadata management server
- PyCSW metadata harvest endpoint
- Elasticsearch metadata discovery catalogue

### Configuration

Create a `.env` file in the `deploy` subdirectory on the target machine,
containing the following environment variables as applicable:

#### General configuration
- **`SERVER_ENV`**: deployment environment: `development`|`testing`|`staging`|`production`
- **`ODP_PUBLIC_URL`**: URL of the ODP web-facing server
- **`ODP_ADMIN_URL`**: URL of the ODP admin server
- **`CORS_ORIGINS`**: JSON-encoded list of allowed CORS origins

#### Core services configuration
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

#### Metadata services configuration
- **`CKAN_URL`**: URL of the CKAN server
- **`CKAN_DB_HOST`**: CKAN database hostname / IP address
- **`CKAN_DB_PASSWORD`**: CKAN database password
- **`CKAN_OAUTH2_SECRET`**: OAuth2 client secret for the CKAN UI

### Core services installation / upgrade

#### Hydra database migrations

_Note: Do this before starting the Hydra container._

    source .env
    docker run -it --rm "${HYDRA_IMAGE}" migrate sql --yes "postgres://hydra_user:${HYDRA_DB_PASSWORD}@${HYDRA_DB_HOST}:5432/hydra_db?sslmode=disable"

#### Docker containers

    docker-compose -f core-services build --no-cache
    docker-compose -f core-services up -d

#### Accounts database migrations

_Note: Do this after starting the ODP Admin container._

    docker exec odp-admin flask initdb

### Metadata services installation / upgrade

#### System configuration

The following command must be run on the host in order for the elasticsearch container to work:

    sudo sysctl -w vm.max_map_count=262144

To make the change permanent, edit the file `/etc/sysctl.conf` and add the following line:

    vm.max_map_count=262144

#### Docker containers

    docker-compose -f metadata-services build --no-cache
    docker-compose -f metadata-services up -d

## Development

### Project installation

Clone the relevant projects from GitHub:

    git clone -b development https://github.com/SAEONData/Open-Data-Platform.git
    git clone https://github.com/SAEONData/Hydra-Admin-Client.git
    git clone https://github.com/SAEONData/Hydra-OAuth2-Blueprint.git
    git clone -b development https://github.com/SAEONData/ODP-API-CKANAdapter.git
    git clone -b development https://github.com/SAEONData/ODP-API-ElasticAdapter.git

Create and activate the Python virtual environment:

    python3.8 -m venv Open-Data-Platform/.venv
    source Open-Data-Platform/.venv/bin/activate
    pip install -U pip setuptools

Install the projects:

    pip install -e Open-Data-Platform/[api,ui,test]
    pip install -e Hydra-Admin-Client/
    pip install -e Hydra-OAuth2-Blueprint/
    pip install -e ODP-API-CKANAdapter/
    pip install -e ODP-API-ElasticAdapter/

### Service configurations

Create `.env` files in the following locations by copying the adjacent `.env.example` and updating
any settings as needed. See the corresponding README files for further info.
- [odp/identity](odp/identity)
- [odp/admin](odp/admin)
- [odp/api/admin](odp/api/admin)
- [odp/api/public](odp/api/public)

### ODP accounts database setup

Run the following commands to create the accounts DB and a DB user, entering `pass` (or a
password of your choice, which must be set in the various local `.env` files) when prompted
for a password:

    sudo -u postgres createuser -P odp_user
    sudo -u postgres createdb -O odp_user odp_accounts

Activate the Python virtual environment, switch to the `odp/admin/` subdirectory, and run:

    flask initdb

### ORY Hydra setup

Switch to the `develop` subdirectory and run the following commands:

    cp .env.example .env
    ./setup-hydra-db.sh
    docker-compose -f hydra.yml up -d
    ./setup-hydra-clients.sh

### Metadata services setup

_Note: this is still a work in progress!_

Switch to the `develop` subdirectory and run the following commands:

    docker-compose -f metadata.yml up -d

### Upgrading Python dependencies

To upgrade dependencies and re-generate the `requirements.txt` file,
carry out the following steps:

- Activate the Python virtual environment.
- Upgrade Python libraries as necessary.
- Start up all ODP applications and services as described in the respective README's,
and check that everything works as expected.
- Ensure that unit tests all pass. (still to be implemented)
- Switch to the project root directory and run the following command:
`pip freeze | sed -E '/^(-e\s|pkg-resources==)/d' > requirements.txt`
