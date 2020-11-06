# SAEON Open Data Platform

## Services
This repository provides the codebase for the following services:

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
Back-office admin interface for the ODP, built on [Flask](https://flask.palletsprojects.com/)
and [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/).

- [entry point](odp/admin/app.py)

### ODP Identity Service
A [Flask](https://flask.palletsprojects.com/) web application providing a unified
signup and login experience across the entire platform.

- [entry point](odp/identity/app.py)

### ODP Publisher
A scheduled background process for publishing ODP metadata from the metadata
management system, making it available at the ODP catalogue harvest endpoint.

- [entry point](odp/publish/main.py)

### DataCite Publisher
A scheduled background process for publishing ODP metadata to DataCite.

- [entry point](odp/publish/datacite.py)

## Dependencies

### Python
The SAEON ODP is made with love and [Python](https://www.python.org/)!

Python version 3.8 is required.

### PostgreSQL
ODP data and metadata are stored in [PostgreSQL](https://www.postgresql.org/) databases.

PostgreSQL version 11 is currently in use.

### Docker
ODP services are deployed using [Docker](https://www.docker.com/)
containerization technology.

### ORY Hydra
[ORY Hydra](https://www.ory.sh/hydra/) is an open source, self-hosted OAuth 2.0
and OpenID Connect provider, which performs authentication, session management and
issuance of ID, access and refresh tokens.

### Metadata Management System
The CKAN-based metadata management system provides storage and curation functions
for SAEON-hosted metadata.

Source repositories:
- https://github.com/SAEONData/ckanext-metadata
- https://github.com/SAEONData/ckanext-accesscontrol
- https://github.com/SAEONData/ckanext-jsonpatch

## Deployment

See the deployment [README](deploy).

## Development

See the development [README](develop).
