FROM python:3.10

ARG CA_CERT_URL
RUN if [ -n "${CA_CERT_URL}" ]; then curl ${CA_CERT_URL} -k -o /usr/local/share/ca-certificates/saeon-ca.crt; fi
RUN if [ -n "${CA_CERT_URL}" ]; then update-ca-certificates; fi

WORKDIR /srv/Open-Data-Platform
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY odplib odplib/
COPY odp odp/

CMD ["gunicorn", "odp.identity.app:create_app()", "--bind=0.0.0.0:4019", "--workers=4"]
