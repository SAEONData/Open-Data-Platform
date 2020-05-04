FROM python:3.6

WORKDIR /srv
RUN git clone https://github.com/SAEONData/elastic-search-agent

WORKDIR elastic-search-agent
RUN pip install .

CMD ["python", "bin/agentapi.py"]
