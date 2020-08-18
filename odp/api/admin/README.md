# ODP Admin API

Back-office API providing administrative and security-related functions,
built on [FastAPI](https://fastapi.tiangolo.com/).

## Environment variables

- `SERVER_ENV`: `development` | `testing` | `staging` | `production`
- `PATH_PREFIX`: (optional) URL path prefix at which the API is mounted, e.g. `/api`
- `ADMIN_API_URL`: URL of the ODP Admin API (this API)
- `ADMIN_INSTITUTION`: institution key of the institution that owns the platform
- `DATABASE_URL`: URL of the ODP accounts database, e.g. `postgresql://odp_user:pw@host/odp_accounts`
- `HYDRA_ADMIN_URL`: URL of the Hydra admin API
- `CKAN_URL`: URL of the CKAN metadata management server

## Development quick start

Create a `.env` file in `odp/api/admin`, activate the Python virtual environment, and run:

    uvicorn odp.api.admin.app:app --port 9999 --workers 2 --env-file .env
