FROM python:3.6

WORKDIR /srv

RUN git clone https://github.com/SAEONData/ODP-API.git
RUN git clone https://github.com/SAEONData/ODP-API-CKANAdapter.git
RUN git clone https://github.com/SAEONData/ODP-API-ElasticAdapter.git
RUN git clone https://github.com/SAEONData/ODP-AccountsLib.git

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN cd ODP-API && pip install .
RUN cd ODP-API-CKANAdapter && pip install .
RUN cd ODP-API-ElasticAdapter && pip install .
RUN cd ODP-AccountsLib && pip install .

COPY ../staging-ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

CMD ["python", "ODP-API/odpapi/main.py"]
