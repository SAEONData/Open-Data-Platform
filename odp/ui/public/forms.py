from wtforms import StringField

from odplib.ui.forms import BaseForm


class SearchForm(BaseForm):
    q = StringField()
