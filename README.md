# Open Data Platform

This project provides a unified environment for the deployment of core and metadata
services of the SAEON Open Data Platform.

ODP core services include:
- [ODP Identity](https://github.com/SAEONData/ODP-Identity)
- [ODP Admin](https://github.com/SAEONData/ODP-Admin)
- [ODP Accounts API](https://github.com/SAEONData/ODP-AccountsAPI)
- [ORY Hydra](https://www.ory.sh/docs/hydra/)

ODP metadata services include:
- [ODP API](https://github.com/SAEONData/ODP-API)
- CKAN metadata management server
- PyCSW metadata harvest endpoint
- Elasticsearch metadata discovery catalogue

## Configuration

Create a `.env` file in the `docker` subdirectory on the target machine,
containing the following environment variables as applicable:

### Common options
- **`SERVER_ENV`**: deployment environment: `development`|`testing`|`staging`|`production`
- **`PROXY_IP`**: (optional) IP address of front-end reverse proxy server
- **`HYDRA_PUBLIC_URL`**: URL of the Hydra public API
- **`HYDRA_ADMIN_URL`**: URL of the Hydra admin API

### Core services options
- **`ACCOUNTS_DB_HOST`**: ODP accounts database hostname / IP address
- **`ACCOUNTS_DB_PASSWORD`**: ODP accounts database password
- **`MAIL_SERVER`**: IP / hostname of mail server used for sending email verifications / password resets
- **`IDENTITY_FLASK_KEY`**: Flask secret key for the identity service
- **`IDENTITY_OAUTH2_SECRET`**: OAuth2 client secret for the identity service UI
- **`ADMIN_FLASK_KEY`**: Flask secret key for the admin service
- **`ADMIN_OAUTH2_SECRET`**: OAuth2 client secret for the admin service UI
- **`HYDRA_IMAGE`**: the Hydra Docker image, e.g. `oryd/hydra:v1.2.3`
- **`HYDRA_LOGIN_EXPIRY`**: number of seconds to remember a successful login
- **`HYDRA_SYSTEM_SECRET`**: secret for encrypting the Hydra database; note that key rotation is not supported
- **`HYDRA_DB_HOST`**: Hydra database hostname / IP address
- **`HYDRA_DB_PASSWORD`**: Hydra database password

### Metadata services options
- **`CKAN_URL`**: URL of the CKAN server
- **`CKAN_DB_HOST`**: CKAN database hostname / IP address
- **`CKAN_DB_PASSWORD`**: CKAN database password
- **`CKAN_OAUTH2_SECRET`**: OAuth2 client secret for the CKAN UI
- **`DOI_PREFIX`**: SAEON DOI prefix
- **`IDENTITY_SERVICE_URL`**: URL of the ODP Identity service
- **`ACCOUNTS_API_URL`**: URL of the ODP Accounts API
- **`METADATA_READONLY_ROLES`**: JSON-encoded list of roles that may read metadata within the same institution
- **`METADATA_READWRITE_ROLES`**: JSON-encoded list of roles that may read and write metadata within the same institution
- **`METADATA_ADMIN_ROLES`**: JSON-encoded list of roles that may read and write metadata belonging to _any_ institution,
and that may access metadata admin functions
- **`ELASTICSEARCH_INDICES`**: JSON-encoded list of Elasticsearch indexes to query for metadata searches

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

## Notes

### Upgrading dependencies

To upgrade dependencies and re-generate the `requirements.txt` file for the identity service /
admin service / accounts API, carry out the following steps:

1. Activate the virtual environment of the service / API.
1. Upgrade Python libraries as necessary.
1. Ensure that unit tests for the service / API and its dependencies all pass.
1. Run the following command:
`pip freeze | sed -E '/^(-e\s|pkg-resources==)/d' > requirements.txt`
