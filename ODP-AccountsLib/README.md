# ODP Accounts Lib

Data access layer for the SAEON Open Data Platform Accounts Database.

This library provides data models and database initialization code.

## Installation

Requires Python 3.6

The package should be installed into the virtual environment of each
consuming service (i.e. ODP Admin, ODP Identity).

## Database setup

The ODP Admin service should be used to initialize the database.

## Configuration

The library reads the following environment variables: 

* DATABASE_URL: PostgreSQL database URL, e.g. `postgresql://dbuser:pwd@host/dbname`
* DATABASE_ECHO: (optional, default `False`) set to `True` to emit SQLAlchemy database calls to stderr
