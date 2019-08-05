# The Open Data Platform API

Provides a stable interface to ODP back-end systems, with automatic API documentation using the
OpenAPI standard. API requests are fulfilled by _adapters_ configured to handle particular routes.

## Installation

Requires Python 3.6 (NB: does not currently work with Python &ge; 3.7).

Adapters must be installed into the same Python environment as the ODP API. On startup, the
system looks for adapters in the `odpapi_adapters` namespace package; an adapter is enabled by
configuring an appropriate entry under the `adapters` configuration key (see below for details).

## Configuration

Server and adapters are configured in `config.yml`.

This file is structured as follows:

    server:                                       # Uvicorn server configuration
      host: '0.0.0.0'                               # IP address to listen on
      port: 8999                                    # port number to listen on
    
    security:                                     # security-related config
      hydra_admin_url: 'https://localhost:9001'     # URL of the Hydra admin API
      oauth2_audience: 'ODP-API'                    # required value for 'aud' in received access tokens
      
      # the following options are for development/internal use only (optional, default 'false'):
      hydra_dev_server: 'false'                     # set to 'true' to disable TLS certificate verification
      no_access_token_validation: 'false'           # set to 'true' to disable access token validation

    adapters:                                     # list of adapter configurations
      - name: 'FooBarAdapter'                       # adapter class name
        routes:                                     # list of routes to be handled by the adapter
          - '/foo/'
          - '/bar/'
        config:                                     # custom adapter config (if applicable)
          key1: 'foo'
          key2: 'bar'

See `config.yml.example` for an example configuration.
