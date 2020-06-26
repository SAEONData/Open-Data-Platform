# ODP Admin Interface

Administrative interface for the SAEON Open Data Platform, built on
[Flask](https://flask.palletsprojects.com/) and
[Flask-Admin](https://flask-admin.readthedocs.io/en/latest/).

## Environment variables

### Flask app

- `FLASK_ENV`: `development`|`testing`|`staging`|`production`
- `FLASK_DEBUG`: enabled by default if `FLASK_ENV=development`;
    you may want to disable this (`FLASK_DEBUG=False`) if debugging in an IDE
- `FLASK_SECRET_KEY`: sets the Flask [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)
- `FLASK_ADMIN_SWATCH`: the Flask-Admin theme, e.g. `flatly`|`cerulean`|`...`; [samples here](https://bootswatch.com/2)

### Database

- `DATABASE_URL`: URL of the ODP accounts database, e.g. `postgresql://odp_user:pw@host/odp_accounts`
- `DATABASE_ECHO`: set to `True` to emit SQLAlchemy database calls to stderr (default `False`)

### OAuth2

- `HYDRA_PUBLIC_URL`: URL of the Hydra public API
- `OAUTH2_CLIENT_ID`: client ID of this service as registered with Hydra
- `OAUTH2_CLIENT_SECRET`: client secret of this service as registered with Hydra
- `OAUTH2_SCOPES`: `openid ODP.Admin`
- `OAUTHLIB_INSECURE_TRANSPORT`: set to `True` in development, to allow OAuth to work when running the server on HTTP (default `False`)

### Access control

- `ADMIN_INSTITUTION`: institution key of the institution that owns the platform
- `ADMIN_ROLE`: role key of the administrative role
- `ADMIN_SCOPE`: scope key of the scope applicable to this application (should be one of the `OAUTH2_SCOPES` values)

## Development quick start

Create a `.env` file in `odp/admin`, activate the Python virtual environment, and run:

    flask run --host=odpadmin.localhost --port=9025
