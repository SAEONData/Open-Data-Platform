# ODP Identity Service

A [Flask](https://flask.palletsprojects.com/) web application providing a unified signup
and login experience across the entire SAEON Open Data Platform. The ODP Identity Service
is integrated with the open source, self-hosted [ORY Hydra](https://www.ory.sh/hydra/docs/)
OAuth 2.0 and OpenID Connect server, which performs authentication, session management and
issuance of ID, access and refresh tokens.

## Environment variables

- `FLASK_ENV`: `development`|`testing`|`staging`|`production`
- `FLASK_SECRET_KEY`: sets the Flask [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)
- `DATABASE_URL`: URL of the ODP accounts database, e.g. `postgresql://odp_user:pw@host/odp_accounts`
- `MAIL_SERVER`: mail server hostname / IP address
- `MAIL_PORT`: mail server port (default `25`)
- `ADMIN_INSTITUTION`: institution key of the institution that owns the platform
- `HYDRA_ADMIN_URL`: URL of the Hydra admin API
- `HYDRA_LOGIN_EXPIRY`: number of seconds to remember a successful login (default `86400` = 24 hours)
- `HYDRA_PUBLIC_URL`: URL of the Hydra public API
- `OAUTH2_CLIENT_ID`: client ID of this service as registered with Hydra
- `OAUTH2_CLIENT_SECRET`: client secret of this service as registered with Hydra
- `OAUTH2_SCOPES`: `openid`

## Development quick start

Create a `.env` file in `odp/identity`, activate the Python virtual environment, and run:

    flask run --host=odpidentity.localhost --port=9024
