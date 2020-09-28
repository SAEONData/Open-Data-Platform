# ODP Deployment

## Configuration
Create a `.env` file in the `deploy` subdirectory on the target machine,
containing the following environment variables:

- **`ODP_ENV`**: deployment environment: `development`|`testing`|`staging`|`production`
- **`ODP_LOG_LEVEL`**: logging detail level: `debug`|`info`|`warning`|`error`|`critical`
- **`ODP_PUBLIC_URL`**: URL of the ODP web-facing server
- **`ODP_ADMIN_URL`**: URL of the ODP admin server
- **`ODP_API_ALLOW_ORIGINS`**: JSON-encoded list of allowed CORS origins
- **`ODP_DB_HOST`**: IP address of the ODP database
- **`ODP_DB_NAME`**: ODP DB name
- **`ODP_DB_USER`**: ODP DB user
- **`ODP_DB_PASS`**: ODP DB password
- **`ODP_MAIL_HOST`**: IP address of the SAEON mail server
- **`ODP_IDENTITY_FLASK_KEY`**: Flask secret key for the ODP identity service
- **`ODP_ADMIN_UI_FLASK_KEY`**: Flask secret key for the ODP admin service
- **`ODP_ADMIN_UI_CLIENT_ID`**: OAuth2 client ID for the ODP admin service
- **`ODP_ADMIN_UI_CLIENT_SECRET`**: OAuth2 client secret for the ODP admin service
- **`HYDRA_IMAGE`**: Hydra Docker image
- **`HYDRA_DB_HOST`**: IP address of the Hydra DB
- **`HYDRA_DB_NAME`**: Hydra DB name
- **`HYDRA_DB_USER`**: Hydra DB user
- **`HYDRA_DB_PASS`**: Hydra DB password
- **`HYDRA_SYSTEM_SECRET`**: secret for encrypting the Hydra DB; note that key rotation is not supported
- **`CKAN_URL`**: URL of the CKAN metadata management server
- **`CKAN_DB_HOST`**: IP address of the CKAN DB
- **`CKAN_DB_NAME`**: CKAN DB name
- **`CKAN_DB_USER`**: CKAN DB user
- **`CKAN_DB_PASS`**: CKAN DB password
- **`CKAN_CLIENT_ID`**: OAuth2 client ID for the CKAN UI
- **`CKAN_CLIENT_SECRET`**: OAuth2 client secret for the CKAN UI
- **`ELASTIC_INDICES`**: JSON-encoded list of indices to use for search queries
- **`CATALOGUE_METADATA_LANDING_PAGE_BASE_URL`**: base URL for published metadata landing pages
- **`DATACITE_API_URL`**: URL of the DataCite REST API
- **`DATACITE_USERNAME`**: DataCite account username
- **`DATACITE_PASSWORD`**: DataCite account password
- **`DATACITE_DOI_PREFIX`**: DOI prefix

## ODP database initialization & migrations
Create a Python 3.8 virtual environment in the project root directory on the target machine,
activate the environment and `pip install -e` the project (no extras required). Switch to the
`migrate` subdirectory and create a `.env` file containing appropriately set `ODP_DB_*`
environment variables. Then run:

    python -m initdb
    alembic upgrade head

## Hydra database initialization & migrations
_Note: Do this before starting the Hydra container._

Run the following commands in the `deploy` subdirectory:

    source .env
    docker run -it --rm "${HYDRA_IMAGE}" migrate sql --yes "postgres://${HYDRA_DB_USER}:${HYDRA_DB_PASS}@${HYDRA_DB_HOST}:5432/${HYDRA_DB_NAME}?sslmode=disable"

## Installing / upgrading ODP services:

### System configuration
The following command must be run on the host in order for the elasticsearch container to work:

    sudo sysctl -w vm.max_map_count=262144

To make the change permanent, edit the file `/etc/sysctl.conf` and add the following line:

    vm.max_map_count=262144

### Docker containers
Run the following commands in the `deploy` subdirectory:

    docker-compose build --no-cache
    docker-compose up -d
