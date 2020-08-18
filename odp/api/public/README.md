# The Open Data Platform API

A public API providing a stable interface to ODP back-end systems, with automatic,
interactive API documentation using the OpenAPI standard.
Built on [FastAPI](https://fastapi.tiangolo.com/).

## Environment variables

- `SERVER_ENV`: `development` | `testing` | `staging` | `production`
- `PATH_PREFIX`: (optional) URL path prefix at which the API is mounted, e.g. `/api`
- `ALLOW_ORIGINS`: (optional) JSON-encoded list of allowed CORS origins; `["*"]` to allow any origin
- `ADMIN_API_URL`: URL of the ODP Admin API
- `ADMIN_INSTITUTION`: institution key of the institution that owns the platform
- `DATABASE_URL`: URL of the ODP accounts database, e.g. `postgresql://odp_user:pw@host/odp_accounts`
- `HYDRA_ADMIN_URL`: URL of the Hydra admin API
- `CKAN_URL`: URL of the CKAN metadata management server
- `ES_URL`: URL of the Elasticsearch instance; must include port
- `INDICES`: JSON-encoded list of Elasticsearch indexes to search

## Development quick start

Create a `.env` file in `odp/api/public`, activate the Python virtual environment, and run:

    uvicorn odp.api.public.app:app --port 8888 --env-file .env
