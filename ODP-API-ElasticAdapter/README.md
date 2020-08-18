# ODP API - Elasticsearch adapter

Search metadata via the Elasticsearch search API, using the
[Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/6.2/query-dsl.html).

## Installation

Requires Python 3.8

The package should be installed into the same virtual environment as the
[ODP API](https://github.com/SAEONData/Open-Data-Platform).

## Configuration

The adapter is configured using the environment variables specified below. 
See the [ODP API](https://github.com/SAEONData/Open-Data-Platform) README for more info.

### Environment variables

- **`ELASTIC_ADAPTER.ES_URL`**: URL of the Elasticsearch instance; must include port
- **`ELASTIC_ADAPTER.INDICES`**: JSON-encoded list of Elasticsearch indexes to search
