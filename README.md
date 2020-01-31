# The Open Data Platform API

Provides a stable interface to ODP back-end systems, with automatic API documentation using the
OpenAPI standard. API requests are fulfilled by _adapters_ configured to handle particular routes.

## Installation

### System dependencies

* Python 3.6

### Project dependencies

* [ODP-AccountsLib](https://github.com/SAEONData/ODP-AccountsLib)

## Configuration

The system is configured using environment variables. For a local / non-containerised deployment,
these may be loaded from a `.env` file located in the project root directory. See `.env.example`
for an example configuration.

### Environment variables

#### Global

- **`SERVER_ENV`**: deployment environment; `development` | `testing` | `staging` | `production`
- **`SERVER_HOST`**: IP address / hostname to listen on
- **`SERVER_PORT`**: port number to listen on

- **`ACCOUNTS_API_URL`**: URL of the ODP Accounts API, for access token validation and introspection
- **`OAUTH2_AUDIENCE`**: `ODP-API` (expected value for 'aud' in received access tokens)
- **`NO_AUTH`**: optional, default `False`; set to `True` to disable access token validation

#### Metadata router

- **`METADATA.ADAPTER`**: class name of the adapter that will handle `/metadata/` requests
- **`METADATA.OAUTH2_SCOPE`**: OAuth2 scope required for `/metadata/` requests

## Adapters

An adapter (e.g. [ODP-API-CKANAdapter](https://github.com/SAEONData/ODP-API-CKANAdapter)) consists
of a class that inherits from `odp.lib.adapters.ODPAPIAdapter`, along with a corresponding `-Config`
class that inherits from `odp.lib.adapters.ODPAPIAdapterConfig`. These classes should be defined in
a module (or modules) located under an `odpapi_adapters` namespace package in the adapter project
directory. The adapter is enabled by installing it into the same Python environment as the ODP API,
and setting the applicable `ROUTER.ADAPTER` environment variable(s) for router(s) that should use
the adapter.

The adapter class contains methods that fulfil adapter calls as defined in one or more `odp.routers.*`
modules. The adapter's config class should define an environment variable prefix (e.g. `'FOOBAR_ADAPTER.'`),
and may define additional settings as needed, which will also be automatically loaded from the
environment at startup.
