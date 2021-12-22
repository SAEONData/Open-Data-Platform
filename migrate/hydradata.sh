#!/bin/bash

# This script (re)creates OAuth2 clients for the ODP admin and
# public UIs. It should be run from the ../deploy or ../develop
# directory, as applicable.

source .env

echo 'Deleting existing OAuth2 clients...'
docker run -it --rm --network host -e HYDRA_ADMIN_URL=${HYDRA_ADMIN_URL} ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify ${ODP_UI_ADMIN_CLIENT_ID}
docker run -it --rm --network host -e HYDRA_ADMIN_URL=${HYDRA_ADMIN_URL} ${HYDRA_IMAGE} \
  clients delete --skip-tls-verify ${ODP_UI_PUBLIC_CLIENT_ID}

echo 'Creating an OAuth2 client for the ODP admin UI...'
docker run -it --rm --network host -e HYDRA_ADMIN_URL=${HYDRA_ADMIN_URL} ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id ${ODP_UI_ADMIN_CLIENT_ID} \
    --secret ${ODP_UI_ADMIN_CLIENT_SECRET} \
    --grant-types authorization_code,refresh_token \
    --response-types code \
    --scope openid,offline,odp.catalogue:read,odp.client:admin,odp.client:read,odp.collection:admin,odp.collection:read,odp.collection_flag:publish,odp.flag:read,odp.project:admin,odp.project:read,odp.provider:admin,odp.provider:read,odp.record:create,odp.record:manage,odp.record:read,odp.record_tag:qc,odp.role:admin,odp.role:read,odp.schema:read,odp.scope:read,odp.tag:read,odp.user:admin,odp.user:read \
    --callbacks ${ODP_UI_ADMIN_URL}/oauth2/logged_in \
    --post-logout-callbacks ${ODP_UI_ADMIN_URL}/oauth2/logged_out

echo 'Creating an OAuth2 client for the ODP public UI...'
docker run -it --rm --network host -e HYDRA_ADMIN_URL=${HYDRA_ADMIN_URL} ${HYDRA_IMAGE} \
  clients create --skip-tls-verify \
    --id ${ODP_UI_PUBLIC_CLIENT_ID} \
    --secret ${ODP_UI_PUBLIC_CLIENT_SECRET} \
    --grant-types authorization_code,refresh_token \
    --response-types code \
    --scope openid,offline \
    --callbacks ${ODP_UI_PUBLIC_URL}/oauth2/logged_in \
    --post-logout-callbacks ${ODP_UI_PUBLIC_URL}/oauth2/logged_out

echo 'Done.'