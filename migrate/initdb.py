#!/usr/bin/env python

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    from odp.db import engine, Base

    Base.metadata.create_all(bind=engine)
