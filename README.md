# CKAN Adapter for the ODP API

## Installation

Requires Python 3.6

The package should be installed into the same virtual environment as the
[ODP API](https://github.com/SAEONData/ODP-API).

## Configuration

Add an entry for the `CKANAdapter` class to the ODP API's `config.yml`. For example:

    adapters:
      - name: 'CKANAdapter'
        routes:
          - '/metadata/'
          - '/institutions/'
        config:
          ckan_url: 'http://localhost:5000'
          use_apikey: 'false'  # optional, default 'false'

_For development/internal use only:_
The `config.use_apikey` option, if set to 'true', specifies that the ODP API was called with a CKAN API key
in the Authorization header (rather than an access token), and will forward the API key appropriately.
In order for this to work, normal access token validation will have to be disabled by also setting the
application's `security.no_access_token_validation` option to 'true'.

See the [ODP API](https://github.com/SAEONData/ODP-API) README for more info.

### Environment variables

- CKAN_URL: If set, will override the `config.ckan_url` option above.
