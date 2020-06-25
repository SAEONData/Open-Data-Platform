# The ODP Admin API

Back-office API providing administrative and security-related functions.

## Environment variables

- `SERVER_ENV`: deployment environment; `development` | `testing` | `staging` | `production`
- `PATH_PREFIX`: (optional) URL path prefix at which the API is mounted, e.g. `/api`
- `DATABASE_URL`: URL of the ODP Accounts database, e.g. `postgresql://odp_user:pw@host/odp_accounts`
- `DATABASE_ECHO`: set to `True` to emit SQLAlchemy database calls to stderr (default `False`)
- `HYDRA_ADMIN_URL`: URL of the Hydra admin API

## Development

### Installation

    cd Open-Data-Platform/
    python3.8 -m venv .venv
    source .venv/bin/activate
    pip install -U pip setuptools
    pip install -e .[api]
    cd ../Hydra-Admin-Client/
    pip install -e .

### Quick start

    uvicorn odp.api.admin:app --reload --env-file .env
