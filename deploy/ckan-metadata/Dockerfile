FROM python:2.7
RUN apt-get update && apt-get install -y supervisor

WORKDIR /srv

RUN curl -OL https://github.com/ckan/ckan/archive/ckan-2.8.2.tar.gz
RUN tar xzf ckan-2.8.2.tar.gz
RUN mv ckan-ckan-2.8.2 ckan
RUN git clone https://github.com/SAEONData/ckanext-metadata.git
RUN git clone https://github.com/SAEONData/ckanext-jsonpatch.git
RUN git clone https://github.com/SAEONData/ckanext-accesscontrol.git

RUN cd ckan && pip install -e .
RUN cd ckan && pip install -r requirements.txt
RUN cd ckanext-metadata && pip install -e .
RUN cd ckanext-metadata && pip install -r requirements.txt
RUN cd ckanext-jsonpatch && pip install -e .
RUN cd ckanext-jsonpatch && pip install -r requirements.txt
RUN cd ckanext-accesscontrol && pip install -e .
RUN cd ckanext-accesscontrol && pip install -r requirements.txt

WORKDIR /srv/ckan

ARG SERVER_ENV
ARG CKAN_DB_URL
ARG CKAN_URL
ARG DOI_PREFIX
ARG ELASTIC_AGENT_URL
ARG HYDRA_PUBLIC_URL
ARG HYDRA_ADMIN_URL
ARG OAUTH2_CLIENT_SECRET
ARG IDENTITY_SERVICE_URL
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
RUN sed -i "/\[app:main\]/a ckan.metadata.doi_prefix = ${DOI_PREFIX}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.metadata.elastic.search_agent_url = ${ELASTIC_AGENT_URL}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.userinfo_endpoint = ${HYDRA_PUBLIC_URL}/userinfo" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.authorization_endpoint = ${HYDRA_PUBLIC_URL}/oauth2/auth" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.token_endpoint = ${HYDRA_PUBLIC_URL}/oauth2/token" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.endsession_endpoint = ${HYDRA_PUBLIC_URL}/oauth2/sessions/logout" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.introspection_endpoint = ${HYDRA_ADMIN_URL}/oauth2/introspect" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.client_id = ckan-ui" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.client_secret = ${OAUTH2_CLIENT_SECRET}" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.api_scope = ODP.Metadata" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.api_id = not used" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.api_secret = not used" ckan.ini
RUN sed -i "/\[app:main\]/a ckan.openidconnect.edit_url = ${IDENTITY_SERVICE_URL}/user/profile" ckan.ini
RUN /bin/bash -c 'if [[ ${SERVER_ENV} == development ]]; then sed -i "/\[app:main\]/a ckan.openidconnect.no_verify_ssl_cert = true" ckan.ini; fi'
RUN cat ckan.ini

RUN paster db init -c ckan.ini
RUN cd /srv/ckanext-metadata && paster metadata_framework initdb -c /srv/ckan/ckan.ini
RUN cd /srv/ckanext-jsonpatch && paster jsonpatch initdb -c /srv/ckan/ckan.ini

ARG CA_CERT_URL
RUN curl ${CA_CERT_URL} -f -o /usr/local/share/ca-certificates/saeon-internal-ca.crt; exit 0
RUN update-ca-certificates

COPY supervisord.conf /etc/supervisor/conf.d/
CMD ["supervisord"]
