# ODP API - Elasticsearch adapter

Provides access to the search function of the [Elastic search agent](https://github.com/SAEONData/elastic-search-agent).

## Installation

Requires Python 3.6

The package should be installed into the same virtual environment as the
[ODP API](https://github.com/SAEONData/ODP-API).

## Configuration

The adapter is configured using the environment variables specified below. 
See the [ODP API](https://github.com/SAEONData/ODP-API) README for more info.

### Environment variables

- **`ELASTIC_ADAPTER.ES_URL`**: URL of the Elasticsearch instance; must include port
- **`ELASTIC_ADAPTER.INDICES`**: JSON-encoded list of Elasticsearch indexes
