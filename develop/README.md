# Development

## Prerequisites
* Python 3.9
* Docker
* Docker Compose

## Local dev environment setup
First, `cd` to the project root directory, and create a Python virtual environment:

    python3.9 -m venv .venv
    source .venv/bin/activate
    pip install -U pip setuptools pip-tools
    pip-sync

Next, `cd` to the `develop` directory and create a `.env` file by copying the
adjacent `.env.example` and filling in username and password fields as needed.

Start up the containerized dependencies:

    docker-compose up -d

Type `docker ps` to check that the containers have started up successfully
(Hydra will be 'restarting' until the SQL migrations have completed).

Finally, run the following commands to initialize platform data:

    ../migrate/systemdata.py
    ../migrate/saeondata.py

## Running ODP services locally
Activate your Python virtual environment and `cd` to the `develop` directory.
Add the project root to the Python path:

    export PYTHONPATH=..

### Identity Service
    FLASK_APP=odp.identity.app flask run --port=2019

### ODP API
    uvicorn odp.api:app --port 2020

### ODP Admin UI
    FLASK_APP=odp.ui.admin flask run --port=2021 --host=odp-admin.localhost

### Data Access Portal
    FLASK_APP=odp.ui.dap flask run --port=2023 --host=dap.localhost
