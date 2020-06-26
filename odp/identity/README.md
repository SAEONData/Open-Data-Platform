# ODP Identity Service

A [Flask](https://flask.palletsprojects.com/) web application providing a unified signup
and login experience across the entire SAEON Open Data Platform. The ODP Identity Service
is integrated with the open source, self-hosted [ORY Hydra](https://www.ory.sh/hydra/docs/)
OAuth 2.0 and OpenID Connect server, which performs authentication, session management and
issuance of ID, access and refresh tokens.

## Environment variables

### Flask app

- `FLASK_ENV`: `development`|`testing`|`staging`|`production`;
    setting `FLASK_ENV=development` disables TLS certificate verification when making requests to the Hydra server
- `FLASK_DEBUG`: enabled by default if `FLASK_ENV=development`;
    you may want to disable this (`FLASK_DEBUG=False`) if debugging in an IDE
- `FLASK_SECRET_KEY`: sets the Flask [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)

### Database

- `DATABASE_URL`: URL of the ODP accounts database, e.g. `postgresql://odp_user:pw@host/odp_accounts`
- `DATABASE_ECHO`: set to `True` to emit SQLAlchemy database calls to stderr (default `False`)

### Mail server

- `MAIL_SERVER`: mail server hostname / IP address
- `MAIL_PORT`: mail server port (default `25`)

### Hydra admin

- `HYDRA_ADMIN_URL`: URL of the Hydra admin API
- `HYDRA_LOGIN_EXPIRY`: number of seconds to remember a successful login (default `86400` = 24 hours)

### OAuth2

- `HYDRA_PUBLIC_URL`: URL of the Hydra public API
- `OAUTH2_CLIENT_ID`: client ID of this service as registered with Hydra
- `OAUTH2_CLIENT_SECRET`: client secret of this service as registered with Hydra
- `OAUTH2_SCOPES`: `openid`
- `OAUTHLIB_INSECURE_TRANSPORT`: set to `True` in development, to allow OAuth to work when running the server on HTTP (default `False`)

## Development quick start

Create a `.env` file in `odp/identity`, activate the Python virtual environment, and run:

    flask run --host=odpidentity.localhost --port=9024
