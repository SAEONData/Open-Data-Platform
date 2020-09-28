FROM python:3.8
RUN apt-get update && apt-get install -y cron

WORKDIR /srv

COPY odp Open-Data-Platform/odp/
COPY setup.py requirements.txt Open-Data-Platform/

RUN cd Open-Data-Platform && pip install -r requirements.txt
RUN cd Open-Data-Platform && pip install -e .

WORKDIR /etc/cron.d

COPY deploy/odp-publisher/crontab odp-publisher
ARG ODP_PUBLISH_JOB_INTERVAL
RUN sed -i "s/ODP_PUBLISH_JOB_INTERVAL/${ODP_PUBLISH_JOB_INTERVAL}/" odp-publisher
RUN chmod 0644 odp-publisher
RUN crontab odp-publisher

RUN touch /var/log/cron.log
CMD cron && tail -f /var/log/cron.log
