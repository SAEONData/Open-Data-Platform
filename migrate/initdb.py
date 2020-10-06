#!/usr/bin/env python

"""Initialize the ODP database schema."""

if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    import odp.db.models
    from odp.db import engine, Base

    Base.metadata.create_all(bind=engine)
