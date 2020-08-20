# ODP Deployment

## Configuration
Create a `.env` file in the `deploy` subdirectory on the target machine,
containing the following environment variables:

- **`SERVER_ENV`**: deployment environment: `development`|`testing`|`staging`|`production`
- **`ODP_PUBLIC_URL`**: URL of the ODP web-facing server
- **`ODP_ADMIN_URL`**: URL of the ODP admin server
- **`CORS_ORIGINS`**: JSON-encoded list of allowed CORS origins
- **`ACCOUNTS_DB_HOST`**: IP address of the ODP accounts DB
- **`ACCOUNTS_DB_PASSWORD`**: ODP accounts DB password
- **`MAIL_SERVER`**: IP address of the SAEON mail server
- **`IDENTITY_FLASK_KEY`**: Flask secret key for the ODP identity service
- **`ADMIN_FLASK_KEY`**: Flask secret key for the ODP admin service
- **`ADMIN_OAUTH2_SECRET`**: OAuth2 client secret for the ODP admin service
- **`HYDRA_IMAGE`**: Hydra Docker image
- **`HYDRA_DB_HOST`**: IP address of the Hydra DB
- **`HYDRA_DB_PASSWORD`**: Hydra DB password
- **`HYDRA_SYSTEM_SECRET`**: secret for encrypting the Hydra DB; note that key rotation is not supported
- **`CKAN_URL`**: URL of the CKAN metadata management server
- **`CKAN_DB_HOST`**: IP address of the CKAN DB
- **`CKAN_DB_PASSWORD`**: CKAN DB password
- **`CKAN_OAUTH2_SECRET`**: OAuth2 client secret for the CKAN UI

## ODP accounts DB initialization & migrations
Create a Python 3.8 virtual environment in the project root directory on the target machine,
activate the environment and `pip install -e` the project (no extras required). Switch to the
`migrate` subdirectory and create a `.env` file containing an appropriately set `DATABASE_URL`
environment variable. Then run:

    python -m initdb
    alembic upgrade head

## Hydra DB initialization & migrations
_Note: Do this before starting the Hydra container._

Run the following commands in the `deploy` subdirectory:

    source .env
    docker run -it --rm "${HYDRA_IMAGE}" migrate sql --yes "postgres://hydra_user:${HYDRA_DB_PASSWORD}@${HYDRA_DB_HOST}:5432/hydra_db?sslmode=disable"

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
