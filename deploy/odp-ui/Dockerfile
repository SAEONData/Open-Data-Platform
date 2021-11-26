FROM python:3.9

WORKDIR /srv/Open-Data-Platform

COPY odp odp/
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["gunicorn", "odp.ui:create_app()", "--bind=0.0.0.0:2021", "--workers=4"]
