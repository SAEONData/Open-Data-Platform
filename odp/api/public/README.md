# The Open Data Platform API

A public API providing a stable interface to ODP back-end systems, with automatic,
interactive API documentation using the OpenAPI standard. API requests are fulfilled
by _adapters_ configured to handle particular routes.
Built on [FastAPI](https://fastapi.tiangolo.com/).

## Environment variables

- `SERVER_ENV`: `development` | `testing` | `staging` | `production`
- `PATH_PREFIX`: (optional) URL path prefix at which the API is mounted, e.g. `/api`
- `ALLOW_ORIGINS`: (optional) list of allowed CORS origins; `["*"]` to allow any origin
- `ADMIN_API_URL`: URL of the ODP Admin API

Router-specific environment variables are prefixed with the uppercased name of the router module,
e.g. `METADATA.ADAPTER`, etc. Following are the options that are applicable per router:

- `<ROUTER>.ADAPTER`: class name of the adapter that will fulfil requests to the router
- `<ROUTER>.OAUTH2_SCOPE`: OAuth2 scope applicable to the router
- `<ROUTER>.READONLY_ROLES`: list of roles that may read resources via this router;
if the router is institution-aware, the resources must belong to the same institution as the user
- `<ROUTER>.READWRITE_ROLES`: list of roles that may read and write resources via this router;
if the router is institution-aware, the resources must belong to the same institution as the user
- `<ROUTER>.ADMIN_ROLES`: list of roles that may read and write resources belonging
to _any_ institution, and that may access administrative functions, via this router

Note: list-type options should be entered as JSON-encoded lists without spaces between items, e.g.

    METADATA.READWRITE_ROLES=["contributor","curator"]

The `*_ROLES` options are optional, defaulting to the empty list `[]`, i.e. no roles allowed
access of the specified type.

## Adapters

An adapter (e.g. [ODP-API-CKANAdapter](https://github.com/SAEONData/ODP-API-CKANAdapter))
consists of a class that inherits from `odp.api.public.adapter.ODPAPIAdapter`, along with
a corresponding `-Config` class that inherits from `odp.api.public.adapter.ODPAPIAdapterConfig`.
These classes should be defined in a module (or modules) located under the `odp_api_adapters`
namespace package in the adapter's project directory. The adapter is enabled by installing
it into the ODP Python environment, and setting the applicable `<ROUTER>.ADAPTER` environment
variable for any router that should use the adapter.

The adapter class contains methods that fulfil adapter calls as defined in one or more
`odp.api.routers.*` modules. The adapter's config class should define an environment
variable prefix (e.g. `'CKAN_ADAPTER.'`), and may define additional settings as needed,
which will also be automatically loaded from the environment at startup.

## Development quick start

Create a `.env` file in `odp/api/public`, activate the Python virtual environment, and run:

    uvicorn odp.api.public.app:app --port 8888 --reload --env-file .env
