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

See the [ODP API](https://github.com/SAEONData/ODP-API) README for more info.

### Environment variables

- CKAN_URL: If set, will override the `config.ckan_url` option set above
