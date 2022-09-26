import json
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask


def init_app(app: Flask):
    @app.template_filter()
    def format_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    @app.template_filter()
    def timestamp(value):
        dt = datetime.fromisoformat(value).astimezone(ZoneInfo('Africa/Johannesburg'))
        return dt.strftime('%d %b %Y, %H:%M %Z')

    @app.template_filter()
    def date(value):
        dt = datetime.strptime(value, '%Y-%m-%d')
        return dt.strftime('%d %b %Y')
