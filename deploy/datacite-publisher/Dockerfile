FROM python:3.8
RUN apt-get update && apt-get install -y cron

WORKDIR /srv/Open-Data-Platform
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY odp odp/

WORKDIR /etc/cron.d
COPY deploy/datacite-publisher/crontab datacite-publisher
ARG DATACITE_PUBLISH_JOB_INTERVAL
RUN sed -i "s/DATACITE_PUBLISH_JOB_INTERVAL/${DATACITE_PUBLISH_JOB_INTERVAL}/" datacite-publisher
RUN crontab datacite-publisher

# use a FIFO to capture cron task output in the Docker log
RUN mkfifo /tmp/stdout

# ensure that the cron task gets our environment variables
# `cat <> fifo` ensures that the fifo pipe stays open
CMD env | grep -E 'ODP_|DATACITE_|TZ' >> /etc/environment && cron -L 7 && cat <> /tmp/stdout
