FROM python:3.8

WORKDIR /srv

COPY odp Open-Data-Platform/odp/
COPY odp_api_adapters Open-Data-Platform/odp_api_adapters/
COPY setup.py requirements.txt Open-Data-Platform/
RUN git clone https://github.com/SAEONData/ODP-API-CKANAdapter.git
RUN git clone https://github.com/SAEONData/ODP-API-ElasticAdapter.git

RUN cd Open-Data-Platform && pip install -r requirements.txt
RUN cd Open-Data-Platform && pip install -e .[api]
RUN cd ODP-API-CKANAdapter && pip install -e .
RUN cd ODP-API-ElasticAdapter && pip install -e .

ARG CA_CERT_URL
RUN curl ${CA_CERT_URL} -k -o /usr/local/share/ca-certificates/saeon-ca.crt
RUN update-ca-certificates

CMD ["uvicorn", "odp.api.public:app", "--host", "0.0.0.0", "--port", "8888", "--workers", "4"]
