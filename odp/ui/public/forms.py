from wtforms import StringField

from odp_uilib.forms import BaseForm


class SearchForm(BaseForm):
    q = StringField()
