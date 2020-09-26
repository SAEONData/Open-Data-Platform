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

## ODP database

### Database creation
Run the following commands to create the ODP database and a database user. The password you
enter must match that specified by the `ODP_DB_PASS` variable in your local `.env` files.

    sudo -u postgres createuser -P odp_user
    sudo -u postgres createdb -O odp_user odp_db

Switch to the `migrate` subdirectory and create a `.env` file by copying the adjacent
`.env.example` and updating any values as needed.

Activate the ODP Python virtual environment and run:

    python -m initdb

### Database upgrade
If you already have an instance of the ODP database, then switch to the `migrate` subdirectory
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
    uvicorn odp.api.public:app --port 8888

### ODP Admin API
    uvicorn odp.api.admin:app --port 9999 --workers 2

### ODP Admin UI
    export FLASK_APP=odp.admin.app
    flask run --host=odpadmin.localhost --port=9025

### ODP Identity Service
    export FLASK_APP=odp.identity.app
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
