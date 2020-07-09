FROM python:3.8

WORKDIR /srv

COPY odp Open-Data-Platform/odp/
COPY setup.py requirements.txt Open-Data-Platform/

RUN cd Open-Data-Platform && pip install -r requirements.txt
RUN cd Open-Data-Platform && pip install -e .[api]

ARG CA_CERT_URL
RUN curl ${CA_CERT_URL} -k -o /usr/local/share/ca-certificates/saeon-ca.crt
RUN update-ca-certificates

CMD ["uvicorn", "odp.api.admin.app:app", "--host", "0.0.0.0", "--port", "9999"]
