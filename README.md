# ODP Admin Service

Accounts administration and system configuration for the SAEON Open Data Platform.
The ODP Admin Service is a [Flask](https://palletsprojects.com/p/flask/) +
[Flask-Admin](https://flask-admin.readthedocs.io/en/latest/) web application.

## Installation

### System dependencies

* Python 3.6
* PostgreSQL 10

### Project dependencies

* [ODP-AccountsLib](https://github.com/SAEONData/ODP-AccountsLib)
* [Hydra-Admin-Client](https://github.com/SAEONData/Hydra-Admin-Client)
* [Hydra-Client-Blueprint](https://github.com/SAEONData/Hydra-Client-Blueprint)
* [Fork of Flask-Admin](https://github.com/SAEONData/flask-admin)

### Database setup

An `initdb` CLI command is provided to initialize the accounts database.
`cd` to the project root directory, activate the virtual environment, and run:

    flask initdb

### Quick start

Create a `.env` file, as described under **Configuration**. Then, to start the development server,
`cd` to the project root directory, activate the virtual environment, and run:

    flask run --host=localhost --port=nnnn

N.B. Flask's built-in server is not suitable for production. See [this page](https://flask.palletsprojects.com/en/1.1.x/deploying/)
for deployment options.

## Configuration

All configuration is done via environment variables, which can be automatically loaded from a `.env`
file located in the project root directory. See `.env.example` for an example configuration.

### Environment variables

Applicable environment variables are listed below with example / allowed values:

#### Standard Flask config

* FLASK_APP: odpadmin
* FLASK_ENV: development|testing|staging|production; note: setting `FLASK_ENV=development` disables TLS
    certificate verification when making requests to the Hydra server
* FLASK_DEBUG: enabled by default if `FLASK_ENV=development`; you may want to disable this (`FLASK_DEBUG=False`)
    if debugging in an IDE
* FLASK_SECRET_KEY: sets the Flask [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)

#### Database config

* DATABASE_URL: URL of the ODP Accounts database, e.g. `postgresql://dbuser:pwd@host/dbname`
* DATABASE_ECHO: set to `True` to emit SQLAlchemy database calls to stderr

#### Hydra admin config

Settings pertaining to Hydra administrative functions:

* HYDRA_ADMIN_URL: URL of the Hydra admin API

#### Hydra client config

Settings pertaining to the usage of Hydra as OAuth2 / OpenID Connect provider, for users logging into and working
with the Admin Service as a client application:

* HYDRA_PUBLIC_URL: URL of the Hydra public API
* HYDRA_CLIENT_ID: client ID of this service as registered with Hydra
* HYDRA_CLIENT_SECRET: client secret of this service as registered with Hydra
* HYDRA_SCOPES: openid ODP.Admin
* OAUTHLIB_INSECURE_TRANSPORT: set to `True` in development, to allow OAuth to work when running the server on HTTP

#### Admin interface config

Settings for controlling access to the admin interface.

* ADMIN_INSTITUTION: institution code of the institution that owns this service
* ADMIN_ROLE: role code of the administrative role
* ADMIN_SCOPE: scope code applicable to this service (should be one of the `HYDRA_SCOPES` values)
