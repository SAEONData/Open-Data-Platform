FROM alpine as build
RUN apk --no-cache add curl

ARG CA_CERT_URL
RUN if [ -n "${CA_CERT_URL}" ]; then curl ${CA_CERT_URL} -k >> /etc/ssl/certs/ca-certificates.crt; fi

COPY config.yml rules.yml ./
ARG ODP_UI_DAP_URL
ARG ODP_UI_DAP_THREDDS_URL
RUN sed -i "s~ODP_UI_DAP_URL~${ODP_UI_DAP_URL}~g" config.yml
RUN sed -i "s~ODP_UI_DAP_THREDDS_URL~${ODP_UI_DAP_THREDDS_URL}~g" rules.yml
RUN cat config.yml
RUN cat rules.yml

FROM oryd/oathkeeper:v0.38.25-beta.1
COPY --from=build config.yml rules.yml ./
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
