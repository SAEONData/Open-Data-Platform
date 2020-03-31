FROM python:3.7

WORKDIR /srv

RUN git clone https://github.com/SAEONData/ODP-AccountsAPI.git
RUN git clone https://github.com/SAEONData/ODP-AccountsLib.git
RUN git clone https://github.com/SAEONData/Hydra-Admin-Client.git

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN cd ODP-AccountsAPI && pip install .
RUN cd ODP-AccountsLib && pip install .
RUN cd Hydra-Admin-Client && pip install .

COPY ../staging-ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

CMD ["python", "ODP-AccountsAPI/accountsapi/main.py"]
