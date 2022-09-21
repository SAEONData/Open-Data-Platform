from flask import Flask
from wtforms import StringField

from odp.ui.forms import BaseForm


def init_app(app: Flask):
    BaseForm.init_app(app)


class SearchForm(BaseForm):
    q = StringField()
