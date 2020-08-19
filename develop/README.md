# ODP Development

## Project installation
Clone the relevant projects from GitHub:

    git clone -b development https://github.com/SAEONData/Open-Data-Platform.git
    git clone https://github.com/SAEONData/Hydra-OAuth2-Blueprint.git

Create and activate the Python virtual environment:

    python3.8 -m venv Open-Data-Platform/.venv
    source Open-Data-Platform/.venv/bin/activate
    pip install -U pip setuptools

Install the projects:

    pip install -e Open-Data-Platform/[api,ui,test]
    pip install -e Hydra-OAuth2-Blueprint/

## Environment configuration
Switch to the `develop` subdirectory and create a `.env` file by copying the adjacent
`.env.example` and updating any values as needed.

## ODP accounts database

### Database creation
Run the following commands to create the accounts DB and a DB user. The password you
enter must match that specified by the `DATABASE_URL` settings in your local `.env` files.

    sudo -u postgres createuser -P odp_user
    sudo -u postgres createdb -O odp_user odp_accounts

Switch to the `migrate` subdirectory and create a `.env` file by copying the adjacent
`.env.example` and updating the `DATABASE_URL` if necessary.

Activate the ODP Python virtual environment and run:

    python -m initdb

### Database upgrade
If you already have an instance of the accounts DB, then switch to the `migrate` subdirectory
and run the SQL migrations:

    alembic upgrade head

## ORY Hydra setup
Switch to the `develop` subdirectory and run the following commands:

    ./setup-hydra-db.sh
    docker-compose -f hydra.yml up -d
    ./setup-hydra-clients.sh

## Metadata services setup
_work in progress_

Switch to the `develop` subdirectory and run the following commands:

    docker-compose -f metadata.yml up -d

## Running the services
Activate the ODP Python virtual environment and switch to the `develop` subdirectory
so as to use the `.env` file located there.

### ODP Public API
    uvicorn odp.api.public:app --port 8888 --env-file .env

### ODP Admin API
    uvicorn odp.api.admin:app --port 9999 --workers 2 --env-file .env

### ODP Admin UI
    flask run --host=odpadmin.localhost --port=9025

### ODP Identity Service
    flask run --host=odpidentity.localhost --port=9024

## Upgrading Python dependencies
To upgrade dependencies and re-generate the `requirements.txt` file for the ODP,
carry out the following steps:

- Activate the ODP Python virtual environment.
- Upgrade Python libraries as necessary.
- Start up all ODP services as described above, and check that everything works as expected.
- Ensure that unit tests all pass. (still to be implemented)
- Switch to the project root directory and run the following command:
`pip freeze | sed -E '/^(-e\s|pkg-resources==)/d' > requirements.txt`
