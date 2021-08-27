#!/usr/bin/env python

import pathlib
import sys

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

"""Initialize the ODP database schema."""

if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    import odp.db.models
    from odp.db import engine, Base

    Base.metadata.create_all(bind=engine)
