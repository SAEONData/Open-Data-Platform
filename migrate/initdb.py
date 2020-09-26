#!/usr/bin/env python

if __name__ == "__main__":
    from odp.db import engine, Base
    import odp.db.models

    Base.metadata.create_all(bind=engine)
