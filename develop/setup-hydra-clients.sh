#!/bin/bash

echo "Loading environment variables..."
source .env

echo "Deleting existing clients..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=http://hydra:4445 ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify ${ODP_APP_CLIENT_ID}
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=http://hydra:4445 ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify odp-init
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=http://hydra:4445 ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify odp-client

echo "Creating OAuth2 client for local ODP app..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=http://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id ${ODP_APP_CLIENT_ID} \
    --secret ${ODP_APP_CLIENT_SECRET} \
    --grant-types authorization_code \
    --response-types code \
    --scope openid,odp.catalogue:manage,odp.catalogue:view,odp.client:manage,odp.client:view,odp.collection:manage,odp.collection:view,odp.record:manage,odp.record:view,odp.project:manage,odp.project:view,odp.provider:manage,odp.provider:view,odp.role:manage,odp.role:view,odp.scope:manage,odp.scope:view,odp.user:manage,odp.user:view \
    --callbacks ${ODP_APP_URL}/oauth2/logged_in \
    --post-logout-callbacks ${ODP_APP_URL}/oauth2/logged_out

echo "Creating OAuth2 client for local ODP init script..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=http://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id odp-init \
    --secret secret \
    --grant-types client_credentials \
    --scope ODP.Metadata,ODP.Admin

echo "Creating OAuth2 client for local API testing..."
docker run -it --rm --network odp-net -e HYDRA_ADMIN_URL=http://hydra:4445 ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id odp-client \
    --secret secret \
    --grant-types client_credentials \
    --scope ODP.Metadata,ODP.Admin,ODP.Catalogue

echo "Done."
