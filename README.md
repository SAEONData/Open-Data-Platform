# SAEON Open Data Platform

## Services
This project provides the codebase for the following services:

### ODP Public API
A public API providing a stable interface to ODP back-end systems, with automatic,
interactive API documentation using the OpenAPI standard.
Built on [FastAPI](https://fastapi.tiangolo.com/).

- [entry point](odp/api/public.py)

### ODP Admin API
Back-office API providing administrative and security-related functions,
built on [FastAPI](https://fastapi.tiangolo.com/).

- [entry point](odp/api/admin.py)

### ODP Admin UI
Administrative interface for the ODP, built on [Flask](https://flask.palletsprojects.com/)
and [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/).

- [entry point](odp/admin/app.py)

### ODP Identity Service
A [Flask](https://flask.palletsprojects.com/) web application providing a unified
signup and login experience across the entire platform.

- [entry point](odp/identity/app.py)

### ODP Publisher
A scheduled background process for publishing ODP metadata to one or more
catalogues.

- [entry point](odp/publish/main.py)

## Dependencies

### Python
The SAEON ODP is made with love and [Python](https://www.python.org/)!

Python version 3.8 is required.

### PostgreSQL
ODP data and metadata are stored in [PostgreSQL](https://www.postgresql.org/) databases.

PostgreSQL version 11 is currently in use.

### Docker
ODP services are deployed using [Docker](https://docs.docker.com/reference/)
containerization technology.

### ORY Hydra
[ORY Hydra](https://www.ory.sh/hydra/docs/) is an open source, self-hosted OAuth 2.0
and OpenID Connect provider, which performs authentication, session management and
issuance of ID, access and refresh tokens.

### Elasticsearch
SAEON's metadata discovery catalogue runs on [Elasticsearch](https://www.elastic.co/).

### Metadata Management System
The CKAN-based metadata management system provides storage and curation functions
for SAEON-hosted metadata.

Source repositories:
- https://github.com/SAEONData/ckanext-metadata
- https://github.com/SAEONData/ckanext-accesscontrol
- https://github.com/SAEONData/ckanext-jsonpatch

### PyCSW
OGC-compliant CSW server providing a harvesting endpoint for published metadata.

Source repository:
- https://github.com/SAEONData/pycsw

## Deployment

See the deployment [README](deploy).

## Development

See the development [README](develop).
