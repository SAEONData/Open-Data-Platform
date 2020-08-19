#!/bin/bash

echo "Loading environment variables..."
source .env

echo "Creating OAuth2 client for the admin service..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id odp-admin \
    --secret ${ADMIN_SECRET} \
    --grant-types authorization_code \
    --response-types code \
    --scope openid,ODP.Admin \
    --callbacks ${ADMIN_URL}/oauth2/authorized \
    --post-logout-callbacks ${ADMIN_URL}/oauth2/logged_out

echo "Creating OAuth2 client for the metadata manager..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id ckan-ui \
    --secret ${CKAN_SECRET} \
    --grant-types authorization_code \
    --response-types code \
    --scope openid,ODP.Metadata \
    --callbacks ${CKAN_URL}/oidc/callback \
    --post-logout-callbacks ${CKAN_URL}/oidc/logged_out

echo "Done."
