# The Open Data Platform API

Provides a stable interface to ODP back-end systems, with automatic API documentation using the
OpenAPI standard. API requests are fulfilled by _adapters_ configured to handle particular routes.

## Installation

### System dependencies

* Python 3.6 (NB: does not currently work with Python &ge; 3.7)

### Project dependencies

* [Hydra-Admin-Client](https://github.com/SAEONData/Hydra-Admin-Client)

## Configuration

The system is configured using environment variables. For a local / non-containerised deployment,
these may be loaded from a `.env` file located in the project root directory. See `.env.example`
for an example configuration.

### Environment variables

* SERVER_ENV: deployment environment; `development` | `test` | `staging` | `production`
* SERVER_HOST: IP address / hostname to listen on
* SERVER_PORT: port number to listen on

* HYDRA_ADMIN_URL: URL of the Hydra admin API, for access token validation and introspection
* OAUTH2_AUDIENCE: the required value for `'aud'` in received access tokens; `ODP-API`
* NO_AUTH: optional, default `False`; set to `True` to disable access token validation

## Adapters

An adapter (e.g. [ODP-API-CKANAdapter](https://github.com/SAEONData/ODP-API-CKANAdapter)) consists
of a class that inherits from `odp.lib.adapters.ODPAPIAdapter`, along with a corresponding `-Config`
class that inherits from `odp.lib.adapters.ODPAPIAdapterConfig`. These classes should be defined in
a module (or modules) located under an `odpapi_adapters` namespace package in the adapter project
directory. The adapter is then enabled by simply installing it into the same Python environment
as the ODP API.

The adapter class contains methods that fulfil adapter calls as defined in one or more `odp.routers.*`
modules. The adapter's config class should define an environment variable prefix (e.g. `'FOOBAR_ADAPTER.'`),
and may define additional settings as needed, which will also be automatically loaded from the
environment at startup.The environment supplied to the system at startup must at a minimum include
a `ROUTES` variable (e.g. `FOOBAR_ADAPTER.ROUTES`) whose value is a JSON-encoded list of routes that
the adapter will handle.
