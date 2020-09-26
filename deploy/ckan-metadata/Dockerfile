FROM python:2.7
RUN apt-get update && apt-get install -y supervisor

WORKDIR /srv

RUN curl -OL https://github.com/ckan/ckan/archive/ckan-2.8.2.tar.gz
RUN tar xzf ckan-2.8.2.tar.gz
RUN mv ckan-ckan-2.8.2 ckan
RUN git clone https://github.com/SAEONData/ckanext-jsonpatch.git

ARG SERVER_ENV

ARG clone_ckanext_metadata='git clone https://github.com/SAEONData/ckanext-metadata.git'
RUN /bin/bash -c 'if [[ ${SERVER_ENV} == development ]]; then ${clone_ckanext_metadata} -b development; else ${clone_ckanext_metadata}; fi'
ARG clone_ckanext_accesscontrol='git clone https://github.com/SAEONData/ckanext-accesscontrol.git'
RUN /bin/bash -c 'if [[ ${SERVER_ENV} == development ]]; then ${clone_ckanext_accesscontrol} -b development; else ${clone_ckanext_accesscontrol}; fi'

RUN cd ckan && pip install -e .
RUN cd ckan && pip install -r requirements.txt
RUN cd ckanext-metadata && pip install -e .
RUN cd ckanext-metadata && pip install -r requirements.txt
RUN cd ckanext-jsonpatch && pip install -e .
RUN cd ckanext-jsonpatch && pip install -r requirements.txt
RUN cd ckanext-accesscontrol && pip install -e .
RUN cd ckanext-accesscontrol && pip install -r requirements.txt

WORKDIR /srv/ckan

ARG CKAN_DB_URL
ARG CKAN_URL
ARG CKAN_ADMIN_ORG
ARG CKAN_ADMIN_ROLE
ARG CKAN_CURATOR_ROLE
ARG CKAN_CONTRIBUTOR_ROLE
ARG DOI_PREFIX
ARG ELASTIC_AGENT_URL
ARG HYDRA_PUBLIC_URL
ARG OAUTH2_CLIENT_ID
ARG OAUTH2_CLIENT_SECRET
ARG OAUTH2_SCOPE
ARG IDENTITY_SERVICE_URL
ARG ODP_INTROSPECTION_URL
ARG SOLR_URL
ARG REDIS_URL
ARG RABBITMQ_HOST

RUN paster make-config ckan ckan.ini
RUN sed -i "s%sqlalchemy.url =.*%sqlalchemy.url = ${CKAN_DB_URL}%" ckan.ini
RUN sed -i "s%ckan.site_url =.*%ckan.site_url = ${CKAN_URL}%" ckan.ini
RUN sed -i "s/ckan.auth.user_create_groups =.*/ckan.auth.user_create_groups = true/" ckan.ini
RUN sed -i "s/ckan.auth.create_user_via_api =.*/ckan.auth.create_user_via_api = true/" ckan.ini
RUN sed -i "s%#solr_url =.*%solr_url = ${SOLR_URL}%" ckan.ini
RUN sed -i "s%#ckan.redis.url =.*%ckan.redis.url = ${REDIS_URL}%" ckan.ini
RUN sed -i "s/ckan.plugins =.*/ckan.plugins = metadata_framework openidconnect jsonpatch metadata_elasticsearch metadata_infrastructure_ui/" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.metadata.admin_org = ${CKAN_ADMIN_ORG}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.metadata.admin_role = ${CKAN_ADMIN_ROLE}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.metadata.curator_role = ${CKAN_CURATOR_ROLE}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.metadata.contributor_role = ${CKAN_CONTRIBUTOR_ROLE}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.metadata.doi_prefix = ${DOI_PREFIX}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.metadata.elastic.search_agent_url = ${ELASTIC_AGENT_URL}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.userinfo_endpoint = ${HYDRA_PUBLIC_URL}/userinfo" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.authorization_endpoint = ${HYDRA_PUBLIC_URL}/oauth2/auth" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.token_endpoint = ${HYDRA_PUBLIC_URL}/oauth2/token" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.endsession_endpoint = ${HYDRA_PUBLIC_URL}/oauth2/sessions/logout" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.introspection_endpoint = ${ODP_INTROSPECTION_URL}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.client_id = ${OAUTH2_CLIENT_ID}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.client_secret = ${OAUTH2_CLIENT_SECRET}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.api_scope = ${OAUTH2_SCOPE}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.api_id = not used" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.api_secret = not used" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.edit_url = ${IDENTITY_SERVICE_URL}/user/profile" ckan.ini
RUN /bin/bash -c 'if [[ ${SERVER_ENV} == development ]]; then sed -i "/\[app:main\]/a ckan.openidconnect.no_verify_ssl_cert = true" ckan.ini; fi'
RUN sed -i "s/ckan.site_title =.*/ckan.site_title = ODP Metadata/" ckan.ini
RUN sed -i "s%ckan.site_logo =.*%ckan.site_logo = /images/SAEON-NRF-LOGO.png%" ckan.ini
RUN sed -i "s%ckan.favicon =.*%ckan.favicon = /images/NRF-favicon.ico%" ckan.ini
RUN cat ckan.ini

RUN paster db init -c ckan.ini
RUN cd /srv/ckanext-metadata && paster metadata_framework initdb -c /srv/ckan/ckan.ini
RUN cd /srv/ckanext-jsonpatch && paster jsonpatch initdb -c /srv/ckan/ckan.ini

ARG CA_CERT_URL
RUN curl ${CA_CERT_URL} -k -o /usr/local/share/ca-certificates/saeon-ca.crt
RUN update-ca-certificates

COPY supervisord.conf /etc/supervisor/conf.d/
CMD ["supervisord"]
