#!/usr/bin/env python
"""
This script sets up an OAuth2 client for Swagger / scripting use.
"""

import os
import pathlib
import sys

from dotenv import load_dotenv

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

dotenv_path = pathlib.Path.cwd() / '.env'
load_dotenv(dotenv_path)

from odp import ODPScope
from odp.db import Session
from odp.db.models import Scope, Client
from odp.lib.hydra import HydraAdminAPI

ODP_CLI_CLIENT_ID = os.getenv('ODP_CLI_CLIENT_ID')
ODP_CLI_CLIENT_SECRET = os.getenv('ODP_CLI_CLIENT_SECRET')
ODP_CLI_CLIENT_NAME = 'Swagger UI / Scripting Client'
HYDRA_ADMIN_URL = os.getenv('HYDRA_ADMIN_URL')

if __name__ == '__main__':
    print('Setting up Swagger/scripting client...')
    with Session.begin():
        client = Session.get(Client, ODP_CLI_CLIENT_ID) or Client(id=ODP_CLI_CLIENT_ID)
        client.name = ODP_CLI_CLIENT_NAME,
        client.scopes = [Session.get(Scope, s.value) for s in ODPScope]
        client.save()

        hydra_admin_api = HydraAdminAPI(HYDRA_ADMIN_URL)
        hydra_admin_api.create_or_update_client_credentials_client(
            client_id=ODP_CLI_CLIENT_ID,
            client_name=ODP_CLI_CLIENT_NAME,
            client_secret=ODP_CLI_CLIENT_SECRET,
            allowed_scope_ids=[s.value for s in ODPScope],
        )

    print('Done.')
