FROM python:3.8

WORKDIR /srv

COPY odp Open-Data-Platform/odp/
COPY setup.py requirements.txt Open-Data-Platform/
RUN git clone https://github.com/SAEONData/Hydra-Admin-Client.git
RUN git clone https://github.com/SAEONData/Hydra-OAuth2-Blueprint.git

RUN cd Open-Data-Platform && pip install -r requirements.txt
RUN cd Open-Data-Platform && pip install -e .[ui]
RUN cd Hydra-Admin-Client && pip install -e .
RUN cd Hydra-OAuth2-Blueprint && pip install -e .

ARG CA_CERT_URL
RUN curl ${CA_CERT_URL} -k -o /usr/local/share/ca-certificates/saeon-ca.crt
RUN update-ca-certificates

CMD ["gunicorn", "odp.identity.app:create_app()", "--bind=0.0.0.0:9024"]
