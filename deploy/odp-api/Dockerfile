FROM python:3.9

WORKDIR /srv/Open-Data-Platform

COPY odp odp/
COPY schema schema/
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["uvicorn", "odp.api:app", "--host", "0.0.0.0", "--port", "2020", "--workers", "4"]
