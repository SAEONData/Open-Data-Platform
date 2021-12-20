FROM alpine as build
RUN apk --no-cache add curl

ARG CA_CERT_URL
RUN if [ -n "${CA_CERT_URL}" ]; then curl ${CA_CERT_URL} -k >> /etc/ssl/certs/ca-certificates.crt; fi

COPY config.yml rules.yml ./
ARG ODP_UI_PUBLIC_URL
ARG ODP_UI_PUBLIC_THREDDS_URL
ARG ODP_PUBLIC_DOMAIN
RUN sed -i "s~ODP_UI_PUBLIC_URL~${ODP_UI_PUBLIC_URL}~g" config.yml
RUN sed -i "s~ODP_PUBLIC_DOMAIN~${ODP_PUBLIC_DOMAIN}~g" rules.yml
#todo: match on https not http - next oathkeeper release will support x-forwarded-proto header
#RUN sed -i "s~ODP_UI_PUBLIC_THREDDS_URL~${ODP_UI_PUBLIC_THREDDS_URL}~g" rules.yml
RUN cat config.yml
RUN cat rules.yml

FROM oryd/oathkeeper:v0.38.15-beta.1
COPY --from=build config.yml rules.yml ./
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
