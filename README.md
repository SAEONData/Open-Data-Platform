# ODP Identity Service

The SAEON Open Data Platform (ODP) consists of a diverse array of loosely coupled web applications and services.
The ODP Identity service is intended to provide a unified user registration and sign-on experience across the
entire platform, along with centralised management of users, roles, institutions, and the associations between
these entities.

The ODP Identity Service is a [Flask](https://palletsprojects.com/p/flask/) web application, which integrates with
the open source, self-hosted [ORY Hydra](https://www.ory.sh/docs/hydra/) system. ORY Hydra is an OAuth 2.0 and
OpenID Connect provider that performs authentication, session management and issuance of ID, access and refresh
tokens.

## Installation

### System dependencies

* Python 3.6
* PostgreSQL 10

### Project dependencies

* [Hydra-Admin-Client](https://github.com/SAEONData/Hydra-Admin-Client)
* [Hydra-Client-Blueprint](https://github.com/SAEONData/Hydra-Client-Blueprint)

### Database setup

An `initdb` CLI command is provided to initialize the Identity Service database.
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

* FLASK_APP: odpidentity
* FLASK_ENV: development|test|staging|production; note: setting `FLASK_ENV=development` disables TLS
    certificate verification when making requests to the Hydra server
* FLASK_DEBUG: enabled by default if `FLASK_ENV=development`; you may want to disable this (`FLASK_DEBUG=False`)
    if debugging in an IDE
* FLASK_SECRET_KEY: sets the Flask [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)

#### Database config

* DATABASE_URL: PostgreSQL database URL, e.g. `postgresql://dbuser:pwd@host/dbname`
* DATABASE_ECHO: set to `True` to emit SQLAlchemy database calls to stderr

#### Hydra admin config

Settings pertaining to integration with Hydra's login, consent and logout flows, in which the Identity Service
plays the role of identity provider:

* HYDRA_ADMIN_URL: URL of the Hydra admin API

#### Hydra client config

Settings pertaining to the usage of Hydra as OAuth2 / OpenID Connect provider, for users logging into and working
with the Identity Service as a client application:

* HYDRA_PUBLIC_URL: URL of the Hydra public API
* HYDRA_CLIENT_ID: client ID of this service as registered with Hydra
* HYDRA_CLIENT_SECRET: client secret of this service as registered with Hydra
* HYDRA_SCOPES: openid
* OAUTHLIB_INSECURE_TRANSPORT: set to `True` in development, to allow OAuth to work when running the server on HTTP
