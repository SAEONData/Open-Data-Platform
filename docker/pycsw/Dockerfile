FROM python:3.5
RUN apt-get update && apt-get install -y libgeos-dev libxml2-dev libxslt1-dev

ARG ELASTIC_AGENT_SEARCH_URL

WORKDIR /var/www
RUN git clone -b elastic https://github.com/SAEONData/pycsw.git

WORKDIR pycsw
RUN pip install -e .
RUN pip install -r requirements.txt

COPY default.cfg .
RUN sed -i "s%filter=.*%filter=${ELASTIC_AGENT_SEARCH_URL}%" default.cfg
RUN cat default.cfg

CMD ["python", "pycsw/wsgi.py"]
