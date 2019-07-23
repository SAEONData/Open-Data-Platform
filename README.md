# CKAN Adapter for the ODP API

## Installation

Requires Python 3.6

The package should be installed into the same virtual environment as the
[ODP API](https://github.com/SAEONData/ODP-API).

## Configuration

Add an entry for the `CKANAdapter` class to `config.yml`.
See the [ODP API](https://github.com/SAEONData/ODP-API) README for more info.

### config.yml

Supported routes:
- /metadata/
- /institutions/

### Environment variables

- CKAN_URL: URL of the CKAN server
- CKAN_APIKEY: API key of a CKAN sysadmin account used for access to CKAN (temporary solution until single sign-on
integration has been implemented)
