#!/bin/bash

source .env

echo "Deleting OAuth2 clients..."
docker run -it --rm --network host -e HYDRA_ADMIN_URL=http://localhost:9001 ${HYDRA_IMAGE} \
  clients delete ${ODP_UI_CLIENT_ID}
docker run -it --rm --network host -e HYDRA_ADMIN_URL=http://localhost:9001 ${HYDRA_IMAGE} \
  clients delete odp.cli

echo "Creating OAuth2 client for the ODP UI..."
docker run -it --rm --network host -e HYDRA_ADMIN_URL=http://localhost:9001 ${HYDRA_IMAGE} \
  clients create \
    --id ${ODP_UI_CLIENT_ID} \
    --secret ${ODP_UI_CLIENT_SECRET} \
    --grant-types authorization_code,refresh_token \
    --response-types code \
    --scope openid,offline,odp.catalogue:read,odp.client:admin,odp.client:read,odp.collection:admin,odp.collection:read,odp.project:admin,odp.project:read,odp.provider:admin,odp.provider:read,odp.record:admin,odp.record:create,odp.record:read,odp.role:admin,odp.role:read,odp.schema:read,odp.scope:read,odp.tag:read,odp.user:admin,odp.user:read \
    --callbacks ${ODP_UI_URL}/oauth2/logged_in \
    --post-logout-callbacks ${ODP_UI_URL}/oauth2/logged_out

echo "Creating OAuth2 client for CLI use..."
docker run -it --rm --network host -e HYDRA_ADMIN_URL=http://localhost:9001 ${HYDRA_IMAGE} \
  clients create \
    --id odp.cli \
    --secret secret \
    --grant-types client_credentials \
    --scope odp.catalogue:read,odp.client:admin,odp.client:read,odp.collection:admin,odp.collection:read,odp.project:admin,odp.project:read,odp.provider:admin,odp.provider:read,odp.record:admin,odp.record:create,odp.record:read,odp.role:admin,odp.role:read,odp.schema:read,odp.scope:read,odp.tag:read,odp.user:admin,odp.user:read \

echo "Done."
