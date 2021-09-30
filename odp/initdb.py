#!/usr/bin/env python
"""
This script creates any new tables and inserts any new static data.
Existing tables and data are not affected.
"""

import pathlib
import sys

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

if __name__ == "__main__":
    import odp

    odp.create_odp_schema()
    odp.create_odp_scopes()
    odp.create_odp_admin_role()
    odp.create_odp_admin_user()
    odp.create_odp_app_client()
