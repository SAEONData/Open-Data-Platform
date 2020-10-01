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
RUN crontab odp-publisher

# use a FIFO to capture cron task output in the Docker log
RUN mkfifo /tmp/stdout

# ensure that the cron task gets our environment variables
# `cat <> fifo` ensures that the fifo pipe stays open
CMD env | grep -E 'ODP_|CKAN_|DATACITE_|TZ' >> /etc/environment && cron -L 7 && cat <> /tmp/stdout
