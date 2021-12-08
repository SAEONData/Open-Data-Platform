#!/usr/bin/env python
"""
This script sets up an OAuth2 client for Swagger / scripting use.
"""

import os
import pathlib
import sys

from dotenv import load_dotenv
from ory_hydra_client import ApiClient, Configuration
from ory_hydra_client.api.admin_api import AdminApi, OAuth2Client
from ory_hydra_client.exceptions import ApiException
from ory_hydra_client.model.string_slice_pipe_delimiter import StringSlicePipeDelimiter as StringArray

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

dotenv_path = pathlib.Path.cwd() / '.env'
load_dotenv(dotenv_path)

from odp import ODPScope
from odp.db import Session
from odp.db.models import Scope, Client

ODP_CLI_CLIENT_ID = os.getenv('ODP_CLI_CLIENT_ID')
ODP_CLI_CLIENT_SECRET = os.getenv('ODP_CLI_CLIENT_SECRET')
ODP_CLI_CLIENT_NAME = 'Swagger / Scripting Client'
HYDRA_ADMIN_URL = os.getenv('HYDRA_ADMIN_URL')

if __name__ == '__main__':
    print('Setting up Swagger/scripting client...')
    with Session.begin():
        client = Session.get(Client, ODP_CLI_CLIENT_ID) or Client(id=ODP_CLI_CLIENT_ID)
        client.name = ODP_CLI_CLIENT_NAME,
        client.scopes = [Session.get(Scope, s.value) for s in ODPScope]
        client.save()

        hydra_admin_api = AdminApi(ApiClient(Configuration(HYDRA_ADMIN_URL)))
        oauth2_client = OAuth2Client(
            client_id=ODP_CLI_CLIENT_ID,
            client_name=ODP_CLI_CLIENT_NAME,
            client_secret=ODP_CLI_CLIENT_SECRET,
            scope=' '.join(s.value for s in ODPScope),
            grant_types=StringArray(['client_credentials']),
            response_types=StringArray([]),
            redirect_uris=StringArray([]),
            contacts=StringArray([]),
        )
        try:
            hydra_admin_api.create_o_auth2_client(body=oauth2_client)
        except ApiException as e:
            if e.status == 409:
                hydra_admin_api.update_o_auth2_client(id=ODP_CLI_CLIENT_ID, body=oauth2_client)
            else:
                raise

    print('Done.')
