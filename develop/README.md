# Development

## Prerequisites
* Python 3.9+
* Docker
* docker-compose

## Local dev environment setup
First, `cd` to the project root directory, and create a Python virtual environment:

    python -m venv .venv
    . .venv/bin/activate
    pip install -U pip setuptools pip-tools
    pip-sync

Next, `cd` to the `develop` directory and start up the Docker containers:

    docker-compose up -d

Type `docker ps` to check that the containerized dev services have started up
successfully (Hydra will be "restarting" until the SQL migrations have completed).
Then run the following command to create your local OAuth2 clients:

    ./init-oauth2-clients.sh

Finally, `cd` to the `migrate` directory, and initialize the ODP database.
The `systemdata.py` script will prompt you to input admin user details the
first time it is run:

    python -m systemdata
    python -m saeondata
