FROM python:3.9

WORKDIR /srv/Open-Data-Platform
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY schema schema/
COPY odp odp/

ARG CA_CERT_URL
RUN if [ -n "${CA_CERT_URL}" ]; then curl ${CA_CERT_URL} -k -o /usr/local/share/ca-certificates/saeon-ca.crt; fi
RUN if [ -n "${CA_CERT_URL}" ]; then update-ca-certificates; fi

CMD ["uvicorn", "odp.api:app", "--host", "0.0.0.0", "--port", "4020", "--workers", "4"]
