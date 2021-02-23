# ODP Development

## Project installation
Clone the development branch of the ODP repo:

    git clone -b development https://github.com/SAEONData/Open-Data-Platform.git

Create and activate the Python virtual environment:

    cd Open-Data-Platform/
    python3.8 -m venv .venv
    source .venv/bin/activate
    pip install -U pip setuptools

Install the project and its dependencies:

    pip install -e .[api,ui,test]

## Environment configuration
Switch to the `develop` subdirectory and create a `.env` and a `docker-compose.yml`
by copying the adjacent `*.example` files, and customizing as needed to suit your
environment.

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
    python -m initdata

### Database upgrade
If you already have an instance of the ODP database, then switch to the `migrate` subdirectory
and run the SQL migrations:

    alembic upgrade head

Also, make sure the static data is up-to-date:

    python -m initdata

## Required services
ODP services depend on ORY Hydra and Redis, while the CKAN-based metadata management
system requires Redis and Solr. We will run these in Docker containers.

To prevent a memory issue with Redis, run the following command on your local system:

    sudo sysctl vm.overcommit_memory=1

To make the change permanent, edit the file `/etc/sysctl.conf` and add the line:

    vm.overcommit_memory=1

Check that the `HYDRA_IMAGE` environment variable in your local `develop/.env`
config file matches the required version of ORY Hydra, and update as necessary.

Then, switch to the `develop` subdirectory and run the following commands:

    ./setup-hydra-db.sh
    docker-compose up -d

To create or update the Hydra client configurations required for logging in
to your local web applications, run:

    ./setup-hydra-clients.sh

## Running the ODP services
Activate the ODP Python virtual environment and switch to the `develop` subdirectory
to use the `.env` file located there.

### ODP Public API
    uvicorn odp.api.public:app --port 8888

### ODP Admin API
    uvicorn odp.api.admin:app --port 9999 --workers 2

### ODP Admin UI
    export FLASK_APP=odp.admin.app
    flask run --host=odpadmin.localhost --port=9025

### ODP Identity Service
    export FLASK_APP=odp.identity.app
    flask run --host=localhost --port=9024

### ODP Publisher
    python -m odp.publish.main

### DataCite Publisher
    python -m odp.publish.datacite

## Upgrading Python dependencies
To upgrade required Python libraries and re-generate the `requirements.txt`
file for the ODP, carry out the following steps:

- Delete your local ODP virtual environment: `rm -rf .venv`
- Create a new virtual environment, and install the ODP project, as described under
  [project installation](#project-installation).
- Start up all ODP services as described above, and check that everything works as expected.
- Ensure that unit tests all pass. (still to be implemented)
- Run the following command in the project root directory:
`pip freeze | sed -E '/^(-e\s|pkg-resources==)/d' > requirements.txt`
