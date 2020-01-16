# CKAN Adapter for the ODP API

## Installation

Requires Python 3.6

The package should be installed into the same virtual environment as the
[ODP API](https://github.com/SAEONData/ODP-API).

## Configuration

The adapter is configured using the environment variables specified below. 
See the [ODP API](https://github.com/SAEONData/ODP-API) README for more info.

### Environment variables

- **`CKAN_ADAPTER.ROUTES`**: JSON-encoded list of routes that the adapter will handle
- **`CKAN_ADAPTER.CKAN_URL`**: URL of the CKAN server
