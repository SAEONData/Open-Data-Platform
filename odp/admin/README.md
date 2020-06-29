# ODP Admin Interface

Administrative interface for the SAEON Open Data Platform, built on
[Flask](https://flask.palletsprojects.com/) and
[Flask-Admin](https://flask-admin.readthedocs.io/en/latest/).

## Environment variables

- `FLASK_ENV`: `development`|`testing`|`staging`|`production`
- `FLASK_SECRET_KEY`: sets the Flask [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)
- `FLASK_ADMIN_SWATCH`: the Flask-Admin theme, e.g. `flatly`|`cerulean`|`...`; [samples here](https://bootswatch.com/2)
- `DATABASE_URL`: URL of the ODP accounts database, e.g. `postgresql://odp_user:pw@host/odp_accounts`
- `HYDRA_PUBLIC_URL`: URL of the Hydra public API
- `OAUTH2_CLIENT_ID`: client ID of this service as registered with Hydra
- `OAUTH2_CLIENT_SECRET`: client secret of this service as registered with Hydra
- `OAUTH2_SCOPES`: `"openid ODP.Admin"`
- `ADMIN_INSTITUTION`: institution key of the institution that owns the platform
- `ADMIN_ROLE`: role key of the administrative role
- `ADMIN_SCOPE`: scope key of the scope applicable to this application (should be one of the `OAUTH2_SCOPES` values)

## Development quick start

Create a `.env` file in `odp/admin`, activate the Python virtual environment, and run:

    flask run --host=odpadmin.localhost --port=9025
