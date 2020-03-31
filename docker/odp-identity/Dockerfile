FROM python:3.6

WORKDIR /srv

RUN git clone https://github.com/SAEONData/ODP-Identity.git
RUN git clone https://github.com/SAEONData/ODP-AccountsLib.git
RUN git clone https://github.com/SAEONData/Hydra-Admin-Client.git
RUN git clone https://github.com/SAEONData/Hydra-OAuth2-Blueprint.git

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN cd ODP-Identity && pip install .
RUN cd ODP-AccountsLib && pip install .
RUN cd Hydra-Admin-Client && pip install .
RUN cd Hydra-OAuth2-Blueprint && pip install .

COPY ../staging-ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

ARG PROXY_IP
ENV GUNICORN_CMD_ARGS --forwarded-allow-ips=${PROXY_IP}

CMD ["gunicorn", "-b 0.0.0.0:9024", "odpidentity:create_app()"]
