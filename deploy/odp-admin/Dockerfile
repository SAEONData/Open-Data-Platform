FROM python:3.8

WORKDIR /srv/Open-Data-Platform

COPY odp odp/
COPY requirements.txt ./
RUN pip install -r requirements.txt

ARG CA_CERT_URL
RUN curl ${CA_CERT_URL} -k -o /usr/local/share/ca-certificates/saeon-ca.crt
RUN update-ca-certificates

CMD ["gunicorn", "odp.admin.app:create_app()", "--bind=0.0.0.0:9025", "--workers=4"]
