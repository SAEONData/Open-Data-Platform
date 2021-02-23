#!/bin/bash

echo "Loading environment variables..."
source .env

echo "Deleting existing clients..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify odp-init
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify ${ODP_ADMIN_UI_CLIENT_ID}
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify ${CKAN_CLIENT_ID}

echo "Creating OAuth2 client for local ODP init script..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id odp-init \
    --secret secret \
    --grant-types client_credentials \
    --scope ODP.Metadata,ODP.Admin

echo "Creating OAuth2 client for local admin service..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id ${ODP_ADMIN_UI_CLIENT_ID} \
    --secret ${ODP_ADMIN_UI_CLIENT_SECRET} \
    --grant-types authorization_code \
    --response-types code \
    --scope openid,offline,ODP.Admin \
    --callbacks ${ODP_ADMIN_UI_URL}/oauth2/logged_in \
    --post-logout-callbacks ${ODP_ADMIN_UI_URL}/oauth2/logged_out

echo "Creating OAuth2 client for local metadata manager..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=https://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id ${CKAN_CLIENT_ID} \
    --secret ${CKAN_CLIENT_SECRET} \
    --grant-types authorization_code \
    --response-types code \
    --scope openid,offline,ODP.Metadata \
    --callbacks ${CKAN_URL}/oidc/callback \
    --post-logout-callbacks ${CKAN_URL}/oidc/logged_out

echo "Done."
